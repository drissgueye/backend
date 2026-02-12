from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from requetes.models import (
    DelegueSyndical,
    Dossier,
    Entreprise,
    DocumentSyndical,
    Notification,
    PoleMembre,
    PieceJointe,
    Pole,
    ProfilUtilisateur,
    Requete,
    Reunion,
)

User = get_user_model()


class EntrepriseSerializer(serializers.ModelSerializer):
    """Serializer Entreprise."""

    class Meta:
        model = Entreprise
        fields = ["id", "nom", "code", "adresse", "secteur_activite"]
        read_only_fields = ["id"]


class PoleSerializer(serializers.ModelSerializer):
    """Serializer Pôle."""

    class Meta:
        model = Pole
        fields = ["id", "nom", "description", "chef_de_pole", "types_problemes"]
        read_only_fields = ["id", "chef_de_pole"]


class PoleMembreSerializer(serializers.ModelSerializer):
    """Serializer Membre de pôle."""

    user_id = serializers.PrimaryKeyRelatedField(
        source="user", queryset=User.objects.all(), write_only=True
    )
    user_first_name = serializers.CharField(source="user.first_name", read_only=True)
    user_last_name = serializers.CharField(source="user.last_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = PoleMembre
        fields = [
            "id",
            "pole",
            "user_id",
            "user_first_name",
            "user_last_name",
            "user_email",
            "role",
            "created_at",
        ]
        read_only_fields = ["id", "pole", "created_at", "user_first_name", "user_last_name", "user_email"]


class ProfilUtilisateurSerializer(serializers.ModelSerializer):
    """Serializer ProfilUtilisateur."""

    user_id = serializers.PrimaryKeyRelatedField(
        source="user", queryset=User.objects.all(), write_only=True, required=False
    )
    user_id_read = serializers.IntegerField(source="user.id", read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    entreprise_id = serializers.PrimaryKeyRelatedField(
        source="entreprise", queryset=Entreprise.objects.all(), required=False, allow_null=True
    )
    entreprise = EntrepriseSerializer(read_only=True)
    is_active = serializers.BooleanField(source="user.is_active", required=False)
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = ProfilUtilisateur
        fields = [
            "id",
            "user",
            "user_id",
            "user_id_read",
            "username",
            "first_name",
            "last_name",
            "user_email",
            "is_active",
            "role",
            "nom",
            "prenom",
            "date_naissance",
            "lieu_naissance",
            "sexe",
            "nationalite",
            "numero_piece_identite",
            "adresse_residence",
            "entreprise",
            "entreprise_id",
            "photo",
            "telephone",
            "email",
            "poste",
            "departement",
            "type_contrat",
            "date_embauche",
            "matricule_interne",
            "lieu_travail",
            "premiere_adhesion",
            "ancien_syndicat",
            "nom_ancien_syndicat",
            "motivation_adhesion",
            "engagement_statuts",
            "consentement_donnees",
            "date_adhesion",
            "signature",
            "piece_identite",
            "contrat_travail",
            "photo_identite",
            "dernier_bulletin_salaire",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "user"]

    def validate_email(self, value: str) -> str:
        if not value:
            return value
        queryset = User.objects.filter(email=value)
        if self.instance and getattr(self.instance, "user_id", None):
            queryset = queryset.exclude(id=self.instance.user_id)
        if queryset.exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value

    def update(self, instance: ProfilUtilisateur, validated_data: dict[str, Any]) -> ProfilUtilisateur:
        user_data = validated_data.pop("user", {})
        is_active = user_data.get("is_active")
        if is_active is not None:
            instance.user.is_active = is_active
            instance.user.save(update_fields=["is_active"])
        return super().update(instance, validated_data)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        ancien_syndicat = attrs.get(
            "ancien_syndicat", getattr(self.instance, "ancien_syndicat", False)
        )
        nom_ancien = attrs.get(
            "nom_ancien_syndicat", getattr(self.instance, "nom_ancien_syndicat", "")
        )
        if ancien_syndicat and not nom_ancien:
            raise serializers.ValidationError(
                {"nom_ancien_syndicat": "Champ requis si ancien syndiqué."}
            )

        if self.instance is None:
            required_fields = [
                "nom",
                "prenom",
                "date_naissance",
                "lieu_naissance",
                "sexe",
                "nationalite",
                "numero_piece_identite",
                "adresse_residence",
                "email",
                "poste",
                "departement",
                "type_contrat",
                "date_embauche",
                "lieu_travail",
                "motivation_adhesion",
                "engagement_statuts",
                "consentement_donnees",
                "date_adhesion",
                "signature",
                "piece_identite",
                "contrat_travail",
                "photo_identite",
            ]
            missing = [field for field in required_fields if not attrs.get(field)]
            if missing:
                raise serializers.ValidationError(
                    {field: "Champ requis." for field in missing}
                )
        return attrs


class PieceJointeSerializer(serializers.ModelSerializer):
    """Serializer PieceJointe."""

    requete_id = serializers.PrimaryKeyRelatedField(
        source="requete", queryset=Requete.objects.all(), write_only=True, required=False
    )
    requete = serializers.StringRelatedField(read_only=True)
    uploaded_by_id = serializers.PrimaryKeyRelatedField(
        source="uploaded_by", queryset=User.objects.all(), write_only=True, required=False
    )
    uploaded_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = PieceJointe
        fields = [
            "id",
            "requete",
            "requete_id",
            "fichier",
            "type_document",
            "description",
            "uploaded_by",
            "uploaded_by_id",
            "uploaded_at",
        ]
        read_only_fields = ["id", "uploaded_at"]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if not attrs.get("requete"):
            raise serializers.ValidationError({"requete_id": "Champ requis."})
        if not attrs.get("uploaded_by"):
            raise serializers.ValidationError({"uploaded_by_id": "Champ requis."})
        return attrs


class RequeteSerializer(serializers.ModelSerializer):
    """Serializer Requete avec relations."""

    travailleur_id = serializers.PrimaryKeyRelatedField(
        source="travailleur", queryset=User.objects.all(), write_only=True
    )
    travailleur = serializers.StringRelatedField(read_only=True)
    pole_id = serializers.PrimaryKeyRelatedField(
        source="pole", queryset=Pole.objects.all(), write_only=True
    )
    pole = PoleSerializer(read_only=True)
    entreprise_id = serializers.PrimaryKeyRelatedField(
        source="entreprise", queryset=Entreprise.objects.all(), write_only=True
    )
    entreprise = EntrepriseSerializer(read_only=True)
    delegue_syndical_id = serializers.PrimaryKeyRelatedField(
        source="delegue_syndical",
        queryset=DelegueSyndical.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    delegue_syndical = serializers.StringRelatedField(read_only=True)
    dossier_id = serializers.PrimaryKeyRelatedField(
        source="dossier", queryset=Dossier.objects.all(), required=False, allow_null=True, write_only=True
    )
    dossier = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Requete
        fields = [
            "id",
            "numero_reference",
            "travailleur",
            "travailleur_id",
            "pole",
            "pole_id",
            "type_probleme",
            "titre",
            "description",
            "delegue_syndical",
            "delegue_syndical_id",
            "entreprise",
            "entreprise_id",
            "dossier",
            "dossier_id",
            "statut",
            "priorite",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "numero_reference", "created_at", "updated_at"]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        entreprise = attrs.get("entreprise") or getattr(self.instance, "entreprise", None)
        delegue = attrs.get("delegue_syndical") or getattr(self.instance, "delegue_syndical", None)
        if delegue and entreprise and delegue.entreprise_id != entreprise.id:
            raise serializers.ValidationError(
                {"delegue_syndical": "Le délégué ne correspond pas à l'entreprise."}
            )
        return attrs


class DossierSerializer(serializers.ModelSerializer):
    """Serializer Dossier."""

    pole_id = serializers.PrimaryKeyRelatedField(
        source="pole", queryset=Pole.objects.all(), write_only=True
    )
    pole = PoleSerializer(read_only=True)
    responsable_id = serializers.PrimaryKeyRelatedField(
        source="responsable", queryset=User.objects.all(), write_only=True
    )
    responsable = serializers.StringRelatedField(read_only=True)
    requetes_ids = serializers.PrimaryKeyRelatedField(
        source="requetes", queryset=Requete.objects.all(), many=True, write_only=True, required=False
    )
    requetes = RequeteSerializer(many=True, read_only=True)

    class Meta:
        model = Dossier
        fields = [
            "id",
            "numero_dossier",
            "pole",
            "pole_id",
            "titre",
            "requetes",
            "requetes_ids",
            "responsable",
            "responsable_id",
            "statut",
            "date_ouverture",
            "date_cloture",
            "synthese",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "numero_dossier", "created_at", "updated_at"]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        pole = attrs.get("pole") or getattr(self.instance, "pole", None)
        requetes = attrs.get("requetes")
        if pole and requetes:
            invalid = [r for r in requetes if r.pole_id != pole.id]
            if invalid:
                raise serializers.ValidationError(
                    {"requetes_ids": "Toutes les requêtes doivent appartenir au même pôle."}
                )
        return attrs


class ReunionSerializer(serializers.ModelSerializer):
    """Serializer Reunion."""

    dossier_id = serializers.PrimaryKeyRelatedField(
        source="dossier", queryset=Dossier.objects.all(), write_only=True
    )
    dossier = serializers.StringRelatedField(read_only=True)
    participants_ids = serializers.PrimaryKeyRelatedField(
        source="participants", queryset=User.objects.all(), many=True, write_only=True, required=False
    )
    participants = serializers.StringRelatedField(many=True, read_only=True)
    created_by_id = serializers.PrimaryKeyRelatedField(
        source="created_by", queryset=User.objects.all(), write_only=True
    )
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Reunion
        fields = [
            "id",
            "dossier",
            "dossier_id",
            "type_reunion",
            "date_heure",
            "lieu",
            "participants",
            "participants_ids",
            "ordre_du_jour",
            "compte_rendu",
            "statut",
            "created_by",
            "created_by_id",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        type_reunion = attrs.get("type_reunion") or getattr(self.instance, "type_reunion", None)
        lieu = attrs.get("lieu") or getattr(self.instance, "lieu", None)
        if type_reunion == "TELEPHONIQUE" and lieu:
            raise serializers.ValidationError({"lieu": "Le lieu doit être vide pour une réunion téléphonique."})
        return attrs


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer Notification."""

    utilisateur_id = serializers.PrimaryKeyRelatedField(
        source="utilisateur", queryset=User.objects.all(), write_only=True
    )
    utilisateur = serializers.StringRelatedField(read_only=True)
    requete_id = serializers.PrimaryKeyRelatedField(
        source="requete", queryset=Requete.objects.all(), required=False, allow_null=True, write_only=True
    )
    requete = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "utilisateur",
            "utilisateur_id",
            "titre",
            "message",
            "type_notification",
            "requete",
            "requete_id",
            "is_read",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class DelegueSyndicalSerializer(serializers.ModelSerializer):
    """Serializer Délégué syndical."""

    user_id = serializers.PrimaryKeyRelatedField(
        source="user", queryset=User.objects.all(), write_only=True
    )
    user = serializers.StringRelatedField(read_only=True)
    user_first_name = serializers.CharField(source="user.first_name", read_only=True)
    user_last_name = serializers.CharField(source="user.last_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)
    entreprise_id = serializers.PrimaryKeyRelatedField(
        source="entreprise", queryset=Entreprise.objects.all(), write_only=True
    )
    entreprise = EntrepriseSerializer(read_only=True)

    class Meta:
        model = DelegueSyndical
        fields = [
            "id",
            "user",
            "user_id",
            "user_first_name",
            "user_last_name",
            "user_email",
            "entreprise",
            "entreprise_id",
            "telephone",
            "email",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "user", "entreprise"]


class DocumentSyndicalSerializer(serializers.ModelSerializer):
    """Serializer Document syndical."""

    pole = PoleSerializer(read_only=True)
    pole_id = serializers.PrimaryKeyRelatedField(
        source="pole", queryset=Pole.objects.all(), required=False, allow_null=True, write_only=True
    )

    class Meta:
        model = DocumentSyndical
        fields = [
            "id",
            "nom",
            "description",
            "pole",
            "pole_id",
            "annee",
            "categorie",
            "fichier",
            "version",
            "uploaded_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "uploaded_by", "pole"]


class RegisterSerializer(serializers.Serializer):
    """Serializer pour l'inscription utilisateur."""

    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    telephone = serializers.CharField(max_length=30, required=False, allow_blank=True)
    entreprise_id = serializers.PrimaryKeyRelatedField(
        source="entreprise", queryset=Entreprise.objects.all(), required=False, allow_null=True
    )
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value

    def create(self, validated_data: dict[str, Any]) -> User:
        entreprise = validated_data.pop("entreprise", None)
        telephone = validated_data.pop("telephone", "")
        password = validated_data.pop("password")
        email = validated_data["email"]
        user = User.objects.create(
            username=email,
            email=email,
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        user.set_password(password)
        user.save(update_fields=["password"])

        profil = getattr(user, "profil", None)
        if profil:
            profil.nom = validated_data.get("last_name", "")
            profil.prenom = validated_data.get("first_name", "")
            profil.email = email
            profil.telephone = telephone
            if entreprise:
                profil.entreprise = entreprise
            profil.save()
        return user


class AdminUserCreateSerializer(serializers.Serializer):
    """Création d'utilisateur par un admin."""

    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    telephone = serializers.CharField(max_length=30, required=False, allow_blank=True)
    entreprise_id = serializers.PrimaryKeyRelatedField(
        source="entreprise", queryset=Entreprise.objects.all(), required=False, allow_null=True
    )
    role = serializers.ChoiceField(
        choices=["admin", "pole_manager", "head", "assistant", "delegate", "member"]
    )
    password = serializers.CharField(write_only=True, min_length=8)
    is_active = serializers.BooleanField(required=False, default=True)

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value

    def create(self, validated_data: dict[str, Any]) -> User:
        entreprise = validated_data.pop("entreprise", None)
        telephone = validated_data.pop("telephone", "")
        password = validated_data.pop("password")
        role = validated_data.pop("role")
        is_active = validated_data.pop("is_active", True)
        email = validated_data["email"]
        user = User.objects.create(
            username=email,
            email=email,
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            is_active=is_active,
        )
        user.set_password(password)
        user.save(update_fields=["password"])

        profil = getattr(user, "profil", None)
        if profil:
            profil.nom = validated_data.get("last_name", "")
            profil.prenom = validated_data.get("first_name", "")
            profil.email = email
            profil.telephone = telephone
            profil.role = role
            if entreprise:
                profil.entreprise = entreprise
            profil.save()
        return user


class EmailOrUsernameTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Autorise l'authentification via email ou username."""

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        username = attrs.get("username", "")
        if username and "@" in username:
            user = User.objects.filter(email__iexact=username).first()
            if user:
                attrs["username"] = user.username
        return super().validate(attrs)
