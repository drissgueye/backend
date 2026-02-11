from __future__ import annotations

from django.contrib import admin

from .models import (
    Dossier,
    DocumentSyndical,
    DelegueSyndical,
    CommunicationPost,
    CommunicationPieceJointe,
    Entreprise,
    HistoriqueAction,
    InteractionRH,
    Notification,
    PieceJointe,
    Pole,
    PoleMembre,
    ProfilUtilisateur,
    Requete,
    RequeteMessage,
    Reunion,
    TemplateDocument,
)


@admin.register(Entreprise)
class EntrepriseAdmin(admin.ModelAdmin):
    search_fields = ["nom", "secteur_activite"]
    list_display = ["nom", "code", "secteur_activite"]


@admin.register(Pole)
class PoleAdmin(admin.ModelAdmin):
    search_fields = ["nom"]
    list_display = ["nom", "chef_de_pole"]


@admin.register(Requete)
class RequeteAdmin(admin.ModelAdmin):
    list_display = ["numero_reference", "titre", "statut", "priorite", "pole", "created_at"]
    list_filter = ["statut", "priorite", "pole", "type_probleme"]
    search_fields = ["numero_reference", "titre", "description"]
    autocomplete_fields = ["travailleur", "delegue_syndical", "entreprise", "pole", "dossier"]
    date_hierarchy = "created_at"


@admin.register(Dossier)
class DossierAdmin(admin.ModelAdmin):
    list_display = ["numero_dossier", "titre", "statut", "pole", "created_at"]
    list_filter = ["statut", "pole"]
    search_fields = ["numero_dossier", "titre"]
    autocomplete_fields = ["pole", "responsable"]
    filter_horizontal = ["requetes"]
    date_hierarchy = "created_at"


@admin.register(PieceJointe)
class PieceJointeAdmin(admin.ModelAdmin):
    list_display = ["requete", "type_document", "uploaded_by", "uploaded_at"]
    list_filter = ["type_document", "uploaded_at"]
    search_fields = ["description"]
    autocomplete_fields = ["requete", "uploaded_by"]


@admin.register(Reunion)
class ReunionAdmin(admin.ModelAdmin):
    list_display = ["dossier", "type_reunion", "date_heure", "statut", "created_by"]
    list_filter = ["type_reunion", "statut"]
    search_fields = ["ordre_du_jour", "compte_rendu"]
    autocomplete_fields = ["dossier", "created_by"]
    filter_horizontal = ["participants"]
    date_hierarchy = "date_heure"


@admin.register(HistoriqueAction)
class HistoriqueActionAdmin(admin.ModelAdmin):
    list_display = ["action", "utilisateur", "timestamp", "content_type", "object_id"]
    list_filter = ["action", "timestamp"]
    search_fields = ["champ_modifie", "ancienne_valeur", "nouvelle_valeur", "commentaire"]
    autocomplete_fields = ["utilisateur"]


@admin.register(ProfilUtilisateur)
class ProfilUtilisateurAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "entreprise", "created_at"]
    list_filter = ["role", "entreprise"]
    search_fields = ["user__username", "user__email"]
    autocomplete_fields = ["user", "entreprise"]
    fieldsets = (
        (
            "Informations personnelles",
            {
                "fields": (
                    "user",
                    "role",
                    "nom",
                    "prenom",
                    "date_naissance",
                    "lieu_naissance",
                    "sexe",
                    "nationalite",
                    "numero_piece_identite",
                    "adresse_residence",
                    "telephone",
                    "email",
                    "photo",
                )
            },
        ),
        (
            "Informations professionnelles",
            {
                "fields": (
                    "entreprise",
                    "poste",
                    "departement",
                    "type_contrat",
                    "date_embauche",
                    "matricule_interne",
                    "lieu_travail",
                )
            },
        ),
        (
            "Situation syndicale",
            {
                "fields": (
                    "premiere_adhesion",
                    "ancien_syndicat",
                    "nom_ancien_syndicat",
                    "motivation_adhesion",
                )
            },
        ),
        (
            "Engagement et acceptation",
            {
                "fields": (
                    "engagement_statuts",
                    "consentement_donnees",
                    "date_adhesion",
                    "signature",
                )
            },
        ),
        (
            "Pièces à fournir",
            {
                "fields": (
                    "piece_identite",
                    "contrat_travail",
                    "photo_identite",
                    "dernier_bulletin_salaire",
                )
            },
        ),
    )


@admin.register(DelegueSyndical)
class DelegueSyndicalAdmin(admin.ModelAdmin):
    list_display = ["user", "entreprise", "telephone", "is_active"]
    list_filter = ["entreprise", "is_active"]
    search_fields = ["user__username", "email", "telephone"]
    autocomplete_fields = ["user", "entreprise"]


@admin.register(PoleMembre)
class PoleMembreAdmin(admin.ModelAdmin):
    list_display = ["pole", "user", "role", "created_at"]
    list_filter = ["pole", "role"]
    search_fields = ["user__username"]
    autocomplete_fields = ["pole", "user"]


@admin.register(RequeteMessage)
class RequeteMessageAdmin(admin.ModelAdmin):
    list_display = ["requete", "utilisateur", "is_interne", "created_at"]
    list_filter = ["is_interne", "created_at"]
    search_fields = ["contenu"]
    autocomplete_fields = ["requete", "utilisateur"]


@admin.register(InteractionRH)
class InteractionRHAdmin(admin.ModelAdmin):
    list_display = ["requete", "contact_nom", "contact_role", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["contact_nom", "notes"]
    autocomplete_fields = ["requete", "utilisateur"]


@admin.register(CommunicationPost)
class CommunicationPostAdmin(admin.ModelAdmin):
    list_display = ["titre", "visibilite", "created_at"]
    list_filter = ["visibilite", "created_at"]
    search_fields = ["titre", "contenu"]
    autocomplete_fields = ["auteur", "entreprise_cible", "pole_cible"]


@admin.register(CommunicationPieceJointe)
class CommunicationPieceJointeAdmin(admin.ModelAdmin):
    list_display = ["communication", "uploaded_by", "uploaded_at"]
    list_filter = ["uploaded_at"]
    search_fields = ["description"]
    autocomplete_fields = ["communication", "uploaded_by"]


@admin.register(DocumentSyndical)
class DocumentSyndicalAdmin(admin.ModelAdmin):
    list_display = ["nom", "categorie", "annee", "version", "created_at"]
    list_filter = ["categorie", "annee"]
    search_fields = ["nom", "description"]
    autocomplete_fields = ["pole", "uploaded_by"]


@admin.register(TemplateDocument)
class TemplateDocumentAdmin(admin.ModelAdmin):
    list_display = ["nom", "type_template", "is_global", "is_active", "version"]
    list_filter = ["type_template", "is_global", "is_active"]
    search_fields = ["nom", "contenu"]
    autocomplete_fields = ["pole"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["utilisateur", "type_notification", "is_read", "created_at"]
    list_filter = ["type_notification", "is_read", "created_at"]
    search_fields = ["titre", "message"]
    autocomplete_fields = ["utilisateur", "requete"]
