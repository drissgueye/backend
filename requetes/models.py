from __future__ import annotations

from typing import Any

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

User = get_user_model()


class RoleUtilisateur(models.TextChoices):
    ADMIN = "admin", "Administrateur"
    POLE_MANAGER = "pole_manager", "Chef de pôle"
    DELEGATE = "delegate", "Délégué"
    MEMBER = "member", "Membre"


class RolePoleMembre(models.TextChoices):
    HEAD = "head", "Responsable"
    ASSISTANT = "assistant", "Adjoint"
    MEMBER = "member", "Membre"


class TypeProbleme(models.TextChoices):
    WORKING_CONDITIONS_REMUNERATION = (
        "working_conditions_remuneration",
        "Conditions de travail et rémunération",
    )
    TRAINING_CAREER = "training_career", "Formation et carrière"
    SOCIAL_MEDIATION = "social_mediation", "Dialogue social et médiation"
    HEALTH_SAFETY_WELLBEING = "health_safety_wellbeing", "Santé et sécurité"
    LEGAL_COMPLIANCE = "legal_compliance", "Juridique et conformité"
    COMMUNICATION_AWARENESS = "communication_awareness", "Communication"
    INNOVATION_DIGITAL_TRANSFORMATION = (
        "innovation_digital_transformation",
        "Innovation et transformation digitale",
    )
    EXTERNAL_RELATIONS_PARTNERSHIPS = (
        "external_relations_partnerships",
        "Relations extérieures et partenariats",
    )
    YOUTH_NEW_EMPLOYEES = "youth_new_employees", "Jeunesse et nouveaux employés"
    SPORT_WELLBEING = "sport_wellbeing", "Sport et bien-être"
    AUTRE = "other", "Autre"


class StatutRequete(models.TextChoices):
    NEW = "new", "Nouveau"
    INFO_NEEDED = "info_needed", "Besoin d'infos"
    PROCESSING = "processing", "En traitement"
    HR_ESCALATED = "hr_escalated", "Escaladé RH"
    HR_PENDING = "hr_pending", "En attente RH"
    RESOLVED = "resolved", "Résolu"
    CLOSED = "closed", "Clôturé"


class PrioriteRequete(models.TextChoices):
    LOW = "low", "Faible"
    MEDIUM = "medium", "Moyenne"
    HIGH = "high", "Élevée"
    CRITICAL = "critical", "Critique"


class TypeDocument(models.TextChoices):
    CONTRAT = "CONTRAT", "Contrat"
    ATTESTATION = "ATTESTATION", "Attestation"
    COURRIER = "COURRIER", "Courrier"
    PHOTO = "PHOTO", "Photo"
    AUTRE = "AUTRE", "Autre"


class StatutDossier(models.TextChoices):
    OUVERT = "OUVERT", "Ouvert"
    EN_INSTRUCTION = "EN_INSTRUCTION", "En instruction"
    ATTENTE_REUNION = "ATTENTE_REUNION", "Attente réunion"
    TRANSMIS_BUREAU = "TRANSMIS_BUREAU", "Transmis au bureau"
    CLOTURE = "CLOTURE", "Clôturé"
    ARCHIVE = "ARCHIVE", "Archivé"


class TypeReunion(models.TextChoices):
    TELEPHONIQUE = "TELEPHONIQUE", "Téléphonique"
    PRESENTIEL = "PRESENTIEL", "Présentiel"
    VISIOCONFERENCE = "VISIOCONFERENCE", "Visioconférence"


class StatutReunion(models.TextChoices):
    PLANIFIEE = "PLANIFIEE", "Planifiée"
    TERMINEE = "TERMINEE", "Terminée"
    ANNULEE = "ANNULEE", "Annulée"


class ActionHistorique(models.TextChoices):
    CREATION = "CREATION", "Création"
    MODIFICATION_STATUT = "MODIFICATION_STATUT", "Modification statut"
    AJOUT_COMMENTAIRE = "AJOUT_COMMENTAIRE", "Ajout commentaire"
    ASSIGNATION = "ASSIGNATION", "Assignation"
    REUNION_PLANIFIEE = "REUNION_PLANIFIEE", "Réunion planifiée"
    PIECE_JOINTE_AJOUTEE = "PIECE_JOINTE_AJOUTEE", "Pièce jointe ajoutée"
    TRANSMISSION = "TRANSMISSION", "Transmission"
    CLOTURE = "CLOTURE", "Clôture"


class VisibiliteCommunication(models.TextChoices):
    GLOBAL = "global", "Global"
    COMPANY = "company", "Entreprise"
    POLE = "pole", "Pôle"


class TypeNotification(models.TextChoices):
    TICKET_UPDATE = "ticket_update", "Mise à jour requête"
    NEW_MESSAGE = "new_message", "Nouveau message"
    INFO_REQUEST = "info_request", "Demande d'information"
    GENERAL = "general", "Générale"


class TypeTemplate(models.TextChoices):
    CONVOCATION = "convocation", "Convocation"
    PV = "pv", "Procès-verbal"
    COMPTE_RENDU = "compte_rendu", "Compte rendu"
    LETTRE = "lettre", "Lettre"


class SexeUtilisateur(models.TextChoices):
    MASCULIN = "masculin", "Masculin"
    FEMININ = "feminin", "Féminin"
    AUTRE = "autre", "Autre"


class TypeContrat(models.TextChoices):
    CDI = "cdi", "CDI"
    CDD = "cdd", "CDD"
    STAGE = "stage", "Stage"
    JOURNALIER = "journalier", "Journalier"
    INTERIM = "interim", "Intérim"
    AUTRE = "autre", "Autre"


def piece_jointe_upload_to(instance: PieceJointe, filename: str) -> str:
    """Construit le chemin de stockage des pièces jointes par année/mois."""
    return timezone.now().strftime(f"pieces_jointes/%Y/%m/{filename}")


class Entreprise(models.Model):
    """Représente une entreprise liée à des requêtes syndicales."""

    nom = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    adresse = models.TextField()
    secteur_activite = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Entreprise"
        verbose_name_plural = "Entreprises"

    def __str__(self) -> str:
        return self.nom


class Pole(models.Model):
    """Décrit un pôle du syndicat et ses membres."""

    nom = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    chef_de_pole = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="poles_diriges",
        db_index=True,
    )
    membres = models.ManyToManyField(
        User, through="PoleMembre", related_name="poles", blank=True
    )
    # JSON pour rester flexible sur les types de problèmes gérés.
    types_problemes = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name = "Pôle"
        verbose_name_plural = "Pôles"
        constraints = [
            models.CheckConstraint(
                condition=Q(chef_de_pole__isnull=False),
                name="pole_chef_de_pole_not_null",
            ),
        ]

    def __str__(self) -> str:
        return self.nom


class Dossier(models.Model):
    """Regroupe des requêtes similaires au sein d'un pôle."""

    pole = models.ForeignKey(
        Pole, on_delete=models.PROTECT, related_name="dossiers", db_index=True
    )
    numero_dossier = models.CharField(max_length=20, unique=True, editable=False)
    titre = models.CharField(max_length=200)
    # M2M pour regrouper plusieurs requêtes; Requete.dossier garde un dossier principal.
    requetes = models.ManyToManyField(
        "Requete", related_name="dossiers", blank=True
    )
    responsable = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="dossiers_responsables",
        db_index=True,
    )
    statut = models.CharField(
        max_length=30, choices=StatutDossier.choices, default=StatutDossier.OUVERT
    )
    date_ouverture = models.DateField(default=timezone.now)
    date_cloture = models.DateField(null=True, blank=True)
    synthese = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dossier"
        verbose_name_plural = "Dossiers"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["pole", "statut"]),
            models.Index(fields=["numero_dossier"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["numero_dossier"], name="unique_numero_dossier"
            )
        ]
        permissions = [
            ("peut_valider_dossier", "Peut valider un dossier"),
        ]

    def __str__(self) -> str:
        return f"{self.numero_dossier} - {self.titre}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Génère automatiquement le numéro de dossier."""
        if not self.numero_dossier:
            with transaction.atomic():
                year = timezone.now().year
                prefix = f"DOS-{year}-"
                last = (
                    Dossier.objects.select_for_update()
                    .filter(numero_dossier__startswith=prefix)
                    .order_by("-numero_dossier")
                    .first()
                )
                last_number = 0
                if last and last.numero_dossier:
                    last_number = int(last.numero_dossier.split("-")[-1])
                self.numero_dossier = f"{prefix}{last_number + 1:05d}"
        super().save(*args, **kwargs)

    @property
    def peut_etre_cloture(self) -> bool:
        """Retourne True si toutes les requêtes liées sont résolues."""
        requetes = self.requetes.all()
        if not requetes.exists():
            return False
        return not requetes.exclude(
            statut__in=[StatutRequete.RESOLVED, StatutRequete.CLOSED]
        ).exists()

    def generer_synthese(self) -> str:
        """Compile une synthèse textuelle du dossier."""
        lignes = [f"Dossier {self.numero_dossier} - {self.titre}"]
        lignes.append(f"Pôle: {self.pole.nom}")
        lignes.append(f"Statut: {self.get_statut_display()}")
        for requete in self.requetes.all():
            lignes.append(f"- {requete.numero_reference}: {requete.titre}")
        synthese = "\n".join(lignes)
        self.synthese = synthese
        return synthese


class Requete(models.Model):
    """Requête syndicale déposée par un travailleur."""

    travailleur = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="requetes", db_index=True
    )
    pole = models.ForeignKey(
        Pole, on_delete=models.PROTECT, related_name="requetes", db_index=True
    )
    type_probleme = models.CharField(
        max_length=40, choices=TypeProbleme.choices
    )
    titre = models.CharField(max_length=200)
    description = models.TextField()
    delegue_syndical = models.ForeignKey(
        "DelegueSyndical",
        on_delete=models.PROTECT,
        related_name="requetes_deleguees",
        null=True,
        blank=True,
        db_index=True,
    )
    entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.PROTECT,
        related_name="requetes",
        db_index=True,
    )
    # Dossier principal (compatibilité avec un flux 1->1), en plus du M2M.
    dossier = models.ForeignKey(
        Dossier,
        on_delete=models.SET_NULL,
        related_name="requetes_principales",
        null=True,
        blank=True,
        db_index=True,
    )
    statut = models.CharField(
        max_length=30, choices=StatutRequete.choices, default=StatutRequete.NEW
    )
    priorite = models.CharField(
        max_length=20, choices=PrioriteRequete.choices, default=PrioriteRequete.MEDIUM
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    numero_reference = models.CharField(max_length=20, unique=True, editable=False)

    class Meta:
        verbose_name = "Requête"
        verbose_name_plural = "Requêtes"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["statut", "pole", "created_at"]),
            models.Index(fields=["travailleur", "statut"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["numero_reference"], name="unique_numero_reference"
            )
        ]

    def __str__(self) -> str:
        return f"{self.numero_reference} - {self.titre}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Génère automatiquement le numéro de référence."""
        if not self.numero_reference:
            with transaction.atomic():
                year = timezone.now().year
                prefix = f"REQ-{year}-"
                last = (
                    Requete.objects.select_for_update()
                    .filter(numero_reference__startswith=prefix)
                    .order_by("-numero_reference")
                    .first()
                )
                last_number = 0
                if last and last.numero_reference:
                    last_number = int(last.numero_reference.split("-")[-1])
                self.numero_reference = f"{prefix}{last_number + 1:05d}"
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Retourne l'URL canonique de la requête."""
        return reverse("requetes:detail", kwargs={"pk": self.pk})


class PieceJointe(models.Model):
    """Fichier attaché à une requête syndicale."""

    requete = models.ForeignKey(
        Requete,
        on_delete=models.CASCADE,
        related_name="pieces_jointes",
        db_index=True,
    )
    fichier = models.FileField(upload_to=piece_jointe_upload_to)
    type_document = models.CharField(
        max_length=20, choices=TypeDocument.choices, default=TypeDocument.AUTRE
    )
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="pieces_jointes", db_index=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pièce jointe"
        verbose_name_plural = "Pièces jointes"

    def __str__(self) -> str:
        return f"{self.requete.numero_reference} - {self.get_type_document_display()}"


class ProfilUtilisateur(models.Model):
    """Profil métier pour enrichir l'utilisateur Django."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profil"
    )
    role = models.CharField(max_length=20, choices=RoleUtilisateur.choices)
    # Informations personnelles
    nom = models.CharField(max_length=150, blank=True)
    prenom = models.CharField(max_length=150, blank=True)
    date_naissance = models.DateField(null=True, blank=True)
    lieu_naissance = models.CharField(max_length=255, blank=True)
    sexe = models.CharField(
        max_length=20, choices=SexeUtilisateur.choices, blank=True
    )
    nationalite = models.CharField(max_length=100, blank=True)
    numero_piece_identite = models.CharField(
        max_length=120, unique=True, null=True, blank=True
    )
    adresse_residence = models.TextField(blank=True)
    entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.SET_NULL,
        related_name="profils",
        null=True,
        blank=True,
        db_index=True,
    )
    photo = models.ImageField(upload_to="profils/%Y/%m/", default="profils/default.png")
    telephone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    # Informations professionnelles
    poste = models.CharField(max_length=150, blank=True)
    departement = models.CharField(max_length=150, blank=True)
    type_contrat = models.CharField(
        max_length=20, choices=TypeContrat.choices, blank=True
    )
    date_embauche = models.DateField(null=True, blank=True)
    matricule_interne = models.CharField(max_length=120, blank=True)
    lieu_travail = models.CharField(max_length=255, blank=True)
    # Situation syndicale
    premiere_adhesion = models.BooleanField(default=True)
    ancien_syndicat = models.BooleanField(default=False)
    nom_ancien_syndicat = models.CharField(max_length=255, blank=True)
    motivation_adhesion = models.TextField(blank=True)
    # Engagement et conformité
    engagement_statuts = models.BooleanField(default=False)
    consentement_donnees = models.BooleanField(default=False)
    date_adhesion = models.DateField(null=True, blank=True)
    signature = models.ImageField(upload_to="signatures/%Y/%m/", null=True, blank=True)
    # Pièces à fournir
    piece_identite = models.FileField(
        upload_to="pieces_identite/%Y/%m/", null=True, blank=True
    )
    contrat_travail = models.FileField(
        upload_to="contrats/%Y/%m/", null=True, blank=True
    )
    photo_identite = models.ImageField(
        upload_to="photos_identite/%Y/%m/", null=True, blank=True
    )
    dernier_bulletin_salaire = models.FileField(
        upload_to="bulletins/%Y/%m/", null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"
        indexes = [models.Index(fields=["role", "entreprise"])]

    def __str__(self) -> str:
        return f"{self.user} - {self.get_role_display()}"


class DelegueSyndical(models.Model):
    """Délégué syndical rattaché à une entreprise."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="mandats_delegue"
    )
    entreprise = models.ForeignKey(
        Entreprise, on_delete=models.CASCADE, related_name="delegues", db_index=True
    )
    telephone = models.CharField(max_length=30)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Délégué syndical"
        verbose_name_plural = "Délégués syndicaux"
        indexes = [models.Index(fields=["entreprise", "is_active"])]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "entreprise"], name="unique_delegue_par_entreprise"
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} - {self.entreprise.nom}"


class PoleMembre(models.Model):
    """Membre d'un pôle avec rôle précis."""

    pole = models.ForeignKey(
        Pole, on_delete=models.CASCADE, related_name="membres_detail", db_index=True
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="membres_poles", db_index=True
    )
    role = models.CharField(
        max_length=20, choices=RolePoleMembre.choices, default=RolePoleMembre.MEMBER
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Membre de pôle"
        verbose_name_plural = "Membres de pôle"
        constraints = [
            models.UniqueConstraint(
                fields=["pole", "user"], name="unique_pole_membre"
            )
        ]

    def __str__(self) -> str:
        return f"{self.pole.nom} - {self.user}"


class Reunion(models.Model):
    """Réunion liée à un dossier."""

    dossier = models.ForeignKey(
        Dossier, on_delete=models.CASCADE, related_name="reunions", db_index=True
    )
    type_reunion = models.CharField(
        max_length=20, choices=TypeReunion.choices
    )
    date_heure = models.DateTimeField()
    lieu = models.CharField(max_length=255, null=True, blank=True)
    participants = models.ManyToManyField(
        User, related_name="reunions_participees", blank=True
    )
    ordre_du_jour = models.TextField()
    compte_rendu = models.TextField(null=True, blank=True)
    statut = models.CharField(
        max_length=20, choices=StatutReunion.choices, default=StatutReunion.PLANIFIEE
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="reunions_creees",
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Réunion"
        verbose_name_plural = "Réunions"

    def __str__(self) -> str:
        return f"{self.dossier.numero_dossier} - {self.get_type_reunion_display()}"


class RequeteMessage(models.Model):
    """Message lié à une requête."""

    requete = models.ForeignKey(
        Requete, on_delete=models.CASCADE, related_name="messages", db_index=True
    )
    utilisateur = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="messages_requetes"
    )
    contenu = models.TextField()
    is_interne = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Message de requête"
        verbose_name_plural = "Messages de requête"
        ordering = ["created_at"]
        indexes = [models.Index(fields=["requete", "created_at"])]

    def __str__(self) -> str:
        return f"{self.requete.numero_reference} - {self.utilisateur}"


class InteractionRH(models.Model):
    """Interaction RH associée à une requête."""

    requete = models.ForeignKey(
        Requete, on_delete=models.CASCADE, related_name="interactions_rh", db_index=True
    )
    utilisateur = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="interactions_rh"
    )
    contact_nom = models.CharField(max_length=120)
    contact_role = models.CharField(max_length=120)
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Interaction RH"
        verbose_name_plural = "Interactions RH"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["requete", "created_at"])]

    def __str__(self) -> str:
        return f"{self.requete.numero_reference} - {self.contact_nom}"


class CommunicationPost(models.Model):
    """Communication syndicale interne."""

    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    visibilite = models.CharField(
        max_length=20, choices=VisibiliteCommunication.choices
    )
    entreprise_cible = models.ForeignKey(
        Entreprise,
        on_delete=models.SET_NULL,
        related_name="communications",
        null=True,
        blank=True,
        db_index=True,
    )
    pole_cible = models.ForeignKey(
        Pole,
        on_delete=models.SET_NULL,
        related_name="communications",
        null=True,
        blank=True,
        db_index=True,
    )
    auteur = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="communications"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Communication"
        verbose_name_plural = "Communications"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["visibilite", "created_at"])]

    def __str__(self) -> str:
        return self.titre


class CommunicationPieceJointe(models.Model):
    """Pièce jointe liée à une communication."""

    communication = models.ForeignKey(
        CommunicationPost,
        on_delete=models.CASCADE,
        related_name="pieces_jointes",
        db_index=True,
    )
    fichier = models.FileField(upload_to=piece_jointe_upload_to)
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="pieces_jointes_communications"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pièce jointe communication"
        verbose_name_plural = "Pièces jointes communication"

    def __str__(self) -> str:
        return f"{self.communication.titre} - {self.uploaded_by}"


class DocumentSyndical(models.Model):
    """Document interne du syndicat."""

    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    pole = models.ForeignKey(
        Pole,
        on_delete=models.SET_NULL,
        related_name="documents",
        null=True,
        blank=True,
        db_index=True,
    )
    annee = models.PositiveIntegerField()
    categorie = models.CharField(max_length=120)
    fichier = models.FileField(upload_to=piece_jointe_upload_to)
    version = models.PositiveIntegerField(default=1)
    uploaded_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="documents_televerses"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["annee", "categorie"]),
            models.Index(fields=["pole"]),
        ]

    def __str__(self) -> str:
        return self.nom


class TemplateDocument(models.Model):
    """Template de document pour les pôles."""

    nom = models.CharField(max_length=200)
    type_template = models.CharField(
        max_length=20, choices=TypeTemplate.choices
    )
    contenu = models.TextField()
    pole = models.ForeignKey(
        Pole,
        on_delete=models.SET_NULL,
        related_name="templates",
        null=True,
        blank=True,
        db_index=True,
    )
    is_global = models.BooleanField(default=False)
    version = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Template"
        verbose_name_plural = "Templates"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_global", "is_active"]),
            models.Index(fields=["pole"]),
        ]

    def __str__(self) -> str:
        return self.nom


class Notification(models.Model):
    """Notification utilisateur liée aux requêtes et communications."""

    utilisateur = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications", db_index=True
    )
    titre = models.CharField(max_length=200)
    message = models.TextField()
    type_notification = models.CharField(
        max_length=20, choices=TypeNotification.choices
    )
    requete = models.ForeignKey(
        Requete,
        on_delete=models.SET_NULL,
        related_name="notifications",
        null=True,
        blank=True,
        db_index=True,
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["utilisateur", "is_read"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.utilisateur} - {self.titre}"


class HistoriqueAction(models.Model):
    """Historique des actions pour audit et traçabilité."""

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, db_index=True
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    utilisateur = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="actions", db_index=True
    )
    action = models.CharField(max_length=40, choices=ActionHistorique.choices)
    champ_modifie = models.CharField(max_length=120, null=True, blank=True)
    ancienne_valeur = models.TextField(null=True, blank=True)
    nouvelle_valeur = models.TextField(null=True, blank=True)
    commentaire = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Historique d'action"
        verbose_name_plural = "Historique des actions"
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self) -> str:
        return f"{self.get_action_display()} - {self.utilisateur}"

    @classmethod
    def enregistrer_action(
        cls,
        *,
        content_object: models.Model,
        utilisateur: User,
        action: ActionHistorique,
        champ_modifie: str | None = None,
        ancienne_valeur: str | None = None,
        nouvelle_valeur: str | None = None,
        commentaire: str | None = None,
    ) -> "HistoriqueAction":
        """Crée une entrée d'historique simplifiée."""
        return cls.objects.create(
            content_object=content_object,
            utilisateur=utilisateur,
            action=action,
            champ_modifie=champ_modifie,
            ancienne_valeur=ancienne_valeur,
            nouvelle_valeur=nouvelle_valeur,
            commentaire=commentaire,
        )


# Signals recommandés:
# - post_save sur Requete -> créer HistoriqueAction automatiquement
# - pre_save sur Dossier -> vérifier cohérence avant sauvegarde

# TODO: Ajouter un système de notifications par rôle.
# TODO: Ajouter des indicateurs/statistiques par pôle.
