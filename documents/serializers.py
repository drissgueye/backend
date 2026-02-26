"""
Serializers pour l'app documents (gestion des documents avec confidentialité, statut, historique).
"""
from rest_framework import serializers

from .models import (
    Document,
    DocumentHistorique,
    ConfidentialiteChoices,
    StatutDocumentChoices,
    TypeActionDocumentChoices,
)


class DocumentHistoriqueSerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source="get_action_display", read_only=True)
    utilisateur_display = serializers.SerializerMethodField()

    class Meta:
        model = DocumentHistorique
        fields = [
            "id",
            "action",
            "action_display",
            "champ_modifie",
            "ancienne_valeur",
            "nouvelle_valeur",
            "commentaire",
            "timestamp",
            "utilisateur",
            "utilisateur_display",
        ]
        read_only_fields = fields

    def get_utilisateur_display(self, obj):
        if obj.utilisateur:
            return getattr(obj.utilisateur, "username", str(obj.utilisateur))
        return None


class DocumentSerializer(serializers.ModelSerializer):
    pole_nom = serializers.CharField(source="pole.nom", read_only=True, allow_null=True)
    requete_numero = serializers.CharField(source="requete.numero_reference", read_only=True, allow_null=True)
    confidentialite_display = serializers.CharField(source="get_confidentialite_display", read_only=True)
    statut_display = serializers.CharField(source="get_statut_display", read_only=True)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "titre",
            "description",
            "fichier",
            "is_suivi_requete",
            "pole",
            "pole_nom",
            "confidentialite",
            "confidentialite_display",
            "requete",
            "requete_numero",
            "statut",
            "statut_display",
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]

    def validate_confidentialite(self, value):
        if value not in ConfidentialiteChoices.values:
            raise serializers.ValidationError("Confidentialité invalide.")
        return value

    def validate_statut(self, value):
        if value not in StatutDocumentChoices.values:
            raise serializers.ValidationError("Statut invalide.")
        return value


class DocumentCreateUpdateSerializer(serializers.ModelSerializer):
    """Pour create/update : fichier peut être envoyé en multipart."""

    class Meta:
        model = Document
        fields = [
            "titre",
            "description",
            "fichier",
            "pole",
            "confidentialite",
            "requete",
            "statut",
        ]

    def validate_confidentialite(self, value):
        if value not in ConfidentialiteChoices.values:
            raise serializers.ValidationError("Confidentialité invalide.")
        return value

    def validate_statut(self, value):
        if value not in StatutDocumentChoices.values:
            raise serializers.ValidationError("Statut invalide.")
        return value


class DocumentListSerializer(serializers.ModelSerializer):
    """Liste légère."""
    pole_nom = serializers.CharField(source="pole.nom", read_only=True, allow_null=True)
    requete_numero = serializers.CharField(source="requete.numero_reference", read_only=True, allow_null=True)
    confidentialite_display = serializers.CharField(source="get_confidentialite_display", read_only=True)
    statut_display = serializers.CharField(source="get_statut_display", read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "titre",
            "fichier",
            "is_suivi_requete",
            "pole",
            "pole_nom",
            "confidentialite",
            "confidentialite_display",
            "requete",
            "requete_numero",
            "statut",
            "statut_display",
            "created_at",
        ]
