"""
Signaux pour lier automatiquement le module documents à l'API requêtes.
Chaque fois qu'une HistoriqueAction est enregistrée pour une Requete (création,
modification statut, transmission, clôture), une entrée DocumentHistorique
est créée sur le document de suivi de cette requête.
"""
from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save)
def on_historique_action_saved(sender, instance, created, **kwargs):
    """
    Dès qu'une HistoriqueAction est créée, si elle concerne une Requete,
    on crée ou met à jour le document de suivi et on y ajoute une entrée d'historique.
    """
    from requetes.models import HistoriqueAction

    if sender != HistoriqueAction or not created:
        return
    from .services import sync_historique_action_to_document

    sync_historique_action_to_document(instance)
