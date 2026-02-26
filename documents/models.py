"""
Gestion des documents : upload, classification par pôle, confidentialité,
lien optionnel avec une requête, statut et historique des actions.
Intégration avec l'API requêtes : un document de suivi par requête avec
historique automatique (création, modification, transfert, clôture).
"""
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

# Import des modèles requetes pour FK (éviter circulaire : pas d'import inverse)
# Pole et Requete sont dans requetes.models
def document_fichier_upload_to(instance: "Document", filename: str) -> str:
    """Chemin de stockage des fichiers document par année/mois."""
    base = timezone.now().strftime("documents/%Y/%m/")
    if instance.pk:
        return f"{base}doc_{instance.pk}_{filename}"
    return f"{base}{filename}"


class ConfidentialiteChoices(models.TextChoices):
    PUBLIC = "PUBLIC", "Public"
    POLE = "POLE", "Pôle"
    BUREAU = "BUREAU", "Bureau"
    CONFIDENTIEL = "CONFIDENTIEL", "Confidentiel"


class StatutDocumentChoices(models.TextChoices):
    ACTIF = "ACTIF", "Actif"
    TRANSFERE = "TRANSFERE", "Transféré"
    CLOTURE = "CLOTURE", "Clôturé"
    ARCHIVE = "ARCHIVE", "Archivé"


class TypeActionDocumentChoices(models.TextChoices):
    CREATION = "CREATION", "Création"
    MODIFICATION = "MODIFICATION", "Modification"
    TRANSFERT = "TRANSFERT", "Transfert"
    ARCHIVAGE = "ARCHIVAGE", "Archivage"


class Document(models.Model):
    """
    Document avec upload, classification par pôle, niveau de confidentialité,
    lien optionnel à une requête et statut. Les responsables de pôle ne voient
    que les documents de leur pôle ; l'admin a un accès global.
    Si is_suivi_requete=True, le document est le "suivi" automatique d'une requête
    (créé et alimenté par les signaux à partir de HistoriqueAction).
    """
    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    fichier = models.FileField(
        upload_to=document_fichier_upload_to,
        null=True,
        blank=True,
        help_text="Optionnel pour les documents de suivi requête (générés automatiquement).",
    )
    is_suivi_requete = models.BooleanField(
        default=False,
        db_index=True,
        help_text="True si ce document est le suivi automatique d'une requête (un seul par requête).",
    )
    pole = models.ForeignKey(
        "requetes.Pole",
        on_delete=models.PROTECT,
        related_name="documents_gestion",
        null=True,
        blank=True,
        db_index=True,
    )
    confidentialite = models.CharField(
        max_length=20,
        choices=ConfidentialiteChoices.choices,
        default=ConfidentialiteChoices.POLE,
        db_index=True,
    )
    requete = models.ForeignKey(
        "requetes.Requete",
        on_delete=models.SET_NULL,
        related_name="documents_lies",
        null=True,
        blank=True,
        db_index=True,
    )
    statut = models.CharField(
        max_length=20,
        choices=StatutDocumentChoices.choices,
        default=StatutDocumentChoices.ACTIF,
        db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="documents_crees",
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Document (gestion)"
        verbose_name_plural = "Documents (gestion)"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["pole", "statut"]),
            models.Index(fields=["confidentialite", "statut"]),
            models.Index(fields=["requete"]),
            models.Index(fields=["is_suivi_requete"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["requete"],
                condition=Q(is_suivi_requete=True),
                name="documents_unique_suivi_per_requete",
            ),
        ]

    def __str__(self) -> str:
        return self.titre


class DocumentHistorique(models.Model):
    """Historique des actions sur un document (création, modification, transfert, archivage)."""
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="historique",
        db_index=True,
    )
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="actions_documents",
        db_index=True,
    )
    action = models.CharField(
        max_length=20,
        choices=TypeActionDocumentChoices.choices,
        db_index=True,
    )
    champ_modifie = models.CharField(max_length=120, null=True, blank=True)
    ancienne_valeur = models.TextField(null=True, blank=True)
    nouvelle_valeur = models.TextField(null=True, blank=True)
    commentaire = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Historique document"
        verbose_name_plural = "Historiques documents"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["document", "timestamp"]),
        ]

    def __str__(self) -> str:
        return f"{self.document_id} - {self.get_action_display()}"
