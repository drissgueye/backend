from __future__ import annotations

from django.contrib import admin

from .models import (
    ActiviteTemplate,
    ActiviteTemplatePole,
    ChampActiviteTemplate,
    Dossier,
    DocumentSyndical,
    DelegueSyndical,
    CommunicationPost,
    CommunicationPieceJointe,
    Entreprise,
    HistoriqueAction,
    InteractionRH,
    MaquetteCompteRendu,
    NotationEntreprise,
    Notification,
    PieceJointe,
    Pole,
    PoleMembre,
    PoleWorkflow,
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


@admin.register(NotationEntreprise)
class NotationEntrepriseAdmin(admin.ModelAdmin):
    list_display = ["entreprise", "critere", "note", "created_by", "updated_at"]
    list_filter = ["critere", "entreprise"]
    search_fields = ["entreprise__nom", "commentaire"]
    autocomplete_fields = ["entreprise", "created_by"]


@admin.register(Pole)
class PoleAdmin(admin.ModelAdmin):
    search_fields = ["nom", "code"]
    list_display = ["nom", "code", "chef_de_pole"]
    list_editable = ["code"]


@admin.register(PoleWorkflow)
class PoleWorkflowAdmin(admin.ModelAdmin):
    list_display = ["pole", "from_status", "to_status", "action_id", "label", "ordre", "is_active"]
    list_filter = ["pole", "is_active"]
    list_editable = ["ordre", "is_active"]
    ordering = ["pole", "ordre", "from_status"]


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


@admin.register(MaquetteCompteRendu)
class MaquetteCompteRenduAdmin(admin.ModelAdmin):
    list_display = ["nom", "is_default", "ordre", "created_at"]
    list_filter = ["is_default"]
    ordering = ["ordre", "nom"]
    search_fields = ["nom"]


# ---------- Modèles d'activité dynamiques ----------

class ChampActiviteTemplateInline(admin.TabularInline):
    model = ChampActiviteTemplate
    extra = 0
    ordering = ["ordre", "nom"]


class ActiviteTemplatePoleInline(admin.TabularInline):
    model = ActiviteTemplatePole
    extra = 0
    autocomplete_fields = ["pole"]


@admin.register(ActiviteTemplate)
class ActiviteTemplateAdmin(admin.ModelAdmin):
    list_display = ["nom", "code", "is_active", "ordre", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["nom", "code", "description"]
    ordering = ["ordre", "nom"]
    inlines = [ChampActiviteTemplateInline, ActiviteTemplatePoleInline]


@admin.register(ActiviteTemplatePole)
class ActiviteTemplatePoleAdmin(admin.ModelAdmin):
    list_display = ["activite_template", "pole", "ordre"]
    list_filter = ["pole"]
    search_fields = ["activite_template__nom", "pole__nom"]
    autocomplete_fields = ["activite_template", "pole"]
    ordering = ["pole", "ordre", "activite_template"]
