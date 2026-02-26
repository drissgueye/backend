from django.contrib import admin
from .models import Document, DocumentHistorique


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["titre", "pole", "confidentialite", "statut", "requete", "is_suivi_requete", "created_by", "created_at"]
    list_filter = ["confidentialite", "statut", "pole", "is_suivi_requete"]
    search_fields = ["titre", "description"]
    raw_id_fields = ["pole", "requete", "created_by"]


@admin.register(DocumentHistorique)
class DocumentHistoriqueAdmin(admin.ModelAdmin):
    list_display = ["document", "action", "utilisateur", "timestamp"]
    list_filter = ["action"]
    raw_id_fields = ["document", "utilisateur"]
