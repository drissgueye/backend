"""
Services pour l'intégration documents ↔ requêtes.
Un document de suivi (is_suivi_requete=True) est créé par requête et reçoit
automatiquement les entrées d'historique lorsque la requête est créée, modifiée,
transférée ou clôturée (via HistoriqueAction).
"""
from __future__ import annotations

from django.contrib.contenttypes.models import ContentType

from .models import (
    Document,
    DocumentHistorique,
    ConfidentialiteChoices,
    StatutDocumentChoices,
    TypeActionDocumentChoices,
)


def ensure_suivi_document_for_requete(requete, default_created_by=None):
    """
    Récupère ou crée le document de suivi pour cette requête.
    Le document hérite du pôle de la requête et respecte les permissions existantes.
    """
    if requete is None or not getattr(requete, "pk", None):
        return None
    created_by = default_created_by or getattr(requete, "travailleur", None)
    if not created_by:
        return None
    doc, created = Document.objects.get_or_create(
        requete=requete,
        is_suivi_requete=True,
        defaults={
            "titre": f"Suivi requête {requete.numero_reference}",
            "description": f"Historique automatique des actions sur la requête {requete.numero_reference} - {getattr(requete, 'titre', '')}.",
            "pole_id": requete.pole_id,
            "confidentialite": ConfidentialiteChoices.POLE,
            "statut": StatutDocumentChoices.ACTIF,
            "created_by": created_by,
            "fichier": None,
        },
    )
    return doc


def map_action_historique_to_document_action(action_historique_value, nouvelle_valeur=None):
    """
    Map requetes.ActionHistorique vers documents.TypeActionDocumentChoices.
    Prend en compte la nouvelle valeur de statut pour distinguer clôture / transfert.
    """
    if action_historique_value == "CREATION":
        return TypeActionDocumentChoices.CREATION
    if action_historique_value == "CLOTURE":
        return TypeActionDocumentChoices.ARCHIVAGE
    if action_historique_value == "TRANSMISSION":
        return TypeActionDocumentChoices.TRANSFERT
    if action_historique_value == "MODIFICATION_STATUT":
        if nouvelle_valeur in ("resolved", "closed"):
            return TypeActionDocumentChoices.ARCHIVAGE
        if nouvelle_valeur == "hr_escalated":
            return TypeActionDocumentChoices.TRANSFERT
        return TypeActionDocumentChoices.MODIFICATION
    return TypeActionDocumentChoices.MODIFICATION


def sync_historique_action_to_document(historique_action):
    """
    À partir d'une HistoriqueAction sur une Requete, crée une entrée DocumentHistorique
    sur le document de suivi de cette requête. Ne fait rien si l'objet n'est pas une Requete.
    """
    from requetes.models import Requete, ActionHistorique

    if not getattr(historique_action, "content_type_id", None):
        return
    ct = ContentType.objects.get_for_id(historique_action.content_type_id)
    if ct.model != "requete":
        return
    try:
        requete = Requete.objects.get(pk=historique_action.object_id)
    except Requete.DoesNotExist:
        return
    doc = ensure_suivi_document_for_requete(
        requete, default_created_by=historique_action.utilisateur
    )
    if not doc:
        return
    action_doc = map_action_historique_to_document_action(
        historique_action.action,
        nouvelle_valeur=historique_action.nouvelle_valeur,
    )
    commentaire = historique_action.commentaire or ""
    if historique_action.champ_modifie:
        commentaire = f"{historique_action.champ_modifie}: {historique_action.ancienne_valeur or ''} → {historique_action.nouvelle_valeur or ''}. {commentaire}".strip()
    DocumentHistorique.objects.create(
        document=doc,
        utilisateur=historique_action.utilisateur,
        action=action_doc,
        champ_modifie=historique_action.champ_modifie,
        ancienne_valeur=historique_action.ancienne_valeur,
        nouvelle_valeur=historique_action.nouvelle_valeur,
        commentaire=commentaire or f"Action requête: {historique_action.get_action_display()}",
    )
