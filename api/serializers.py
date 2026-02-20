from __future__ import annotations

from typing import Any

from django.db import IntegrityError
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from requetes.models import (
    ActiviteRequete,
    DelegueSyndical,
    Dossier,
    Entreprise,
    HistoriqueAction,
    DocumentSyndical,
    MaquetteCompteRendu,
    Notification,
    Pole,
    PoleMembre,
    PoleMembership,
    PieceJointe,
    ProfilUtilisateur,
    Requete,
    RequeteMessage,
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


class PoleMembershipSerializer(serializers.ModelSerializer):
    """
    Appartenance à un pôle : user en lecture seule, is_manager éditable.
    Utilisé pour l’ajout/retrait de membres et la gestion des responsables.
    """
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    user_display = serializers.SerializerMethodField()
    pole = serializers.PrimaryKeyRelatedField(queryset=Pole.objects.all(), required=False)
    pole_display = serializers.SerializerMethodField()

    class Meta:
        model = PoleMembership
        fields = ["id", "user", "user_display", "pole", "pole_display", "is_manager"]
        read_only_fields = ["id"]

    def get_user_display(self, obj):
        u = obj.user
        return {"id": u.id, "username": getattr(u, "username", ""), "email": getattr(u, "email", "")}

    def get_pole_display(self, obj):
        return {"id": obj.pole.id, "nom": obj.pole.nom}

    def validate(self, attrs):
        if not self.instance and (not attrs.get("user") or not attrs.get("pole")):
            raise serializers.ValidationError(
                {"user": "Requis à la création.", "pole": "Requis à la création."}
                if not attrs.get("user") and not attrs.get("pole")
                else {"user": "Requis."} if not attrs.get("user") else {"pole": "Requis."}
            )
        return attrs

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["user"] = instance.user_id
        ret["pole"] = instance.pole_id
        return ret


class UserWithPolesSerializer(serializers.Serializer):
    """
    Lecture seule : liste les pôles d’un utilisateur avec son statut (is_manager) dans chacun.
    Utilise PoleMembership comme source de vérité.
    """
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    poles = serializers.SerializerMethodField()

    def get_poles(self, obj):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if isinstance(obj, User):
            user = obj
        else:
            user = getattr(obj, "user", obj)
        if not user or not getattr(user, "pk", None):
            return []
        memberships = PoleMembership.objects.filter(user=user).select_related("pole")
        return [
            {"pole_id": m.pole_id, "pole_nom": m.pole.nom, "is_manager": m.is_manager}
            for m in memberships
        ]


class PoleMembreSerializer(serializers.ModelSerializer):
    """Serializer Membre de pôle (legacy PoleMembre)."""

    user_id = serializers.PrimaryKeyRelatedField(
        source="user", queryset=User.objects.all(), write_only=True
    )
    user_id_read = serializers.IntegerField(source="user.id", read_only=True)
    user_first_name = serializers.CharField(source="user.first_name", read_only=True)
    user_last_name = serializers.CharField(source="user.last_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = PoleMembre
        fields = [
            "id",
            "pole",
            "user_id",
            "user_id_read",
            "user_first_name",
            "user_last_name",
            "user_email",
            "role",
            "created_at",
        ]
        read_only_fields = ["id", "pole", "created_at", "user_id_read", "user_first_name", "user_last_name", "user_email"]


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

    def to_representation(self, instance: ProfilUtilisateur) -> dict:
        """Expose le rôle effectif et la liste des pôles avec statut (appartenance + is_manager)."""
        from api.permissions import _get_role

        data = super().to_representation(instance)
        effective_role = _get_role(instance.user)
        if effective_role is not None:
            data["role"] = effective_role
        user = instance.user
        if getattr(user, "pk", None):
            poles_list = []
            seen_pole_ids = set()
            for m in PoleMembership.objects.filter(user=user).select_related("pole"):
                seen_pole_ids.add(m.pole_id)
                poles_list.append({
                    "pole_id": m.pole_id,
                    "pole_nom": m.pole.nom,
                    "is_manager": m.is_manager,
                })
            for pole in Pole.objects.filter(chef_de_pole=user):
                if pole.id not in seen_pole_ids:
                    seen_pole_ids.add(pole.id)
                    poles_list.append({
                        "pole_id": pole.id,
                        "pole_nom": pole.nom,
                        "is_manager": True,
                    })
            for pm in PoleMembre.objects.filter(user=user).select_related("pole"):
                if pm.pole_id not in seen_pole_ids:
                    seen_pole_ids.add(pm.pole_id)
                    poles_list.append({
                        "pole_id": pm.pole_id,
                        "pole_nom": pm.pole.nom,
                        "is_manager": getattr(pm, "role", None) == "head",
                    })
            data["poles"] = poles_list
        else:
            data["poles"] = []
        return data

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
        profil = super().update(instance, validated_data)
        user = profil.user
        updated = False
        if profil.prenom is not None:
            user.first_name = profil.prenom
            updated = True
        if profil.nom is not None:
            user.last_name = profil.nom
            updated = True
        if profil.email:
            user.email = profil.email
            user.username = profil.email
            updated = True
        if is_active is not None:
            user.is_active = is_active
            updated = True
        if updated:
            try:
                user.save(update_fields=["first_name", "last_name", "email", "username", "is_active"])
            except IntegrityError:
                raise serializers.ValidationError({"email": "Cet email est déjà utilisé."})
        return profil

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


class HistoriqueActionSerializer(serializers.ModelSerializer):
    """Lecture seule : historique des actions sur un objet (ex. requête)."""

    action_display = serializers.SerializerMethodField()
    utilisateur_display = serializers.SerializerMethodField()

    class Meta:
        model = HistoriqueAction
        fields = [
            "id",
            "action",
            "action_display",
            "utilisateur_display",
            "commentaire",
            "champ_modifie",
            "ancienne_valeur",
            "nouvelle_valeur",
            "timestamp",
        ]
        read_only_fields = fields

    def get_action_display(self, obj: HistoriqueAction) -> str:
        return obj.get_action_display()

    def get_utilisateur_display(self, obj: HistoriqueAction) -> str:
        name = obj.utilisateur.get_full_name() if obj.utilisateur else ""
        return name.strip() or (getattr(obj.utilisateur, "username", "") or "")


class RequeteMessageSerializer(serializers.ModelSerializer):
    """Lecture des messages d'une requête (dont demandes d'information)."""

    auteur = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = RequeteMessage
        fields = ["id", "contenu", "is_interne", "created_at", "auteur"]

    def get_auteur(self, obj: RequeteMessage) -> str:
        user = getattr(obj, "utilisateur", None)
        if not user:
            return ""
        profil = getattr(user, "profil", None)
        if profil and (getattr(profil, "prenom", "") or getattr(profil, "nom", "")):
            parts = [getattr(profil, "prenom", "") or "", getattr(profil, "nom", "") or ""]
            return " ".join(p for p in parts if p).strip()
        return getattr(user, "get_full_name", lambda: "")() or getattr(user, "username", "") or ""


class MaquetteCompteRenduSerializer(serializers.ModelSerializer):
    """Lecture des maquettes de compte rendu."""

    class Meta:
        model = MaquetteCompteRendu
        fields = ["id", "nom", "contenu", "is_default", "ordre", "created_at"]


class RequeteMessageCreateSerializer(serializers.ModelSerializer):
    """Création d'un message (réponse au besoin d'info, etc.)."""

    contenu = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = RequeteMessage
        fields = ["contenu", "is_interne"]


class RequeteSerializer(serializers.ModelSerializer):
    """Serializer Requete avec relations."""

    travailleur_id = serializers.PrimaryKeyRelatedField(
        source="travailleur", queryset=User.objects.all(), write_only=True
    )
    travailleur = serializers.SerializerMethodField(read_only=True)
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
    delegue_syndical_id_read = serializers.IntegerField(
        source="delegue_syndical_id", read_only=True, allow_null=True
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
            "delegue_syndical_id_read",
            "entreprise",
            "entreprise_id",
            "dossier",
            "dossier_id",
            "statut",
            "priorite",
            "created_at",
            "updated_at",
            "date_cloture",
            "compte_rendu",
        ]
        read_only_fields = ["id", "numero_reference", "created_at", "updated_at"]

    def get_travailleur(self, obj: Requete) -> str | None:
        """Nom affichable du demandeur : profil (prénom nom), sinon get_full_name(), sinon username."""
        user = getattr(obj, "travailleur", None)
        if not user:
            return None
        profil = getattr(user, "profil", None)
        if profil and (getattr(profil, "prenom", "") or getattr(profil, "nom", "")):
            parts = [getattr(profil, "prenom", "") or "", getattr(profil, "nom", "") or ""]
            return " ".join(p for p in parts if p).strip() or None
        full = getattr(user, "get_full_name", lambda: "")()
        if full and full.strip():
            return full.strip()
        return getattr(user, "username", "") or None

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        from api.permissions import _get_role

        request = self.context.get("request")
        # Accepter "pole" (id) en plus de "pole_id" pour la classification (frontend peut envoyer l'un ou l'autre)
        if request and getattr(request, "data", None):
            data = request.data
            if "pole" in data and "pole" not in attrs:
                try:
                    pid = data["pole"]
                    if pid is not None and pid != "":
                        attrs["pole"] = Pole.objects.get(pk=int(pid))
                except (TypeError, ValueError, Pole.DoesNotExist):
                    pass
        if request and "travailleur" in attrs:
            role = _get_role(request.user)
            if role not in ("admin", "delegate") and attrs["travailleur"] != request.user:
                raise serializers.ValidationError(
                    {"travailleur_id": "Vous ne pouvez créer une requête que pour vous-même."}
                )
            if role == "delegate":
                mandat = DelegueSyndical.objects.filter(user=request.user).first()
                if not mandat or not mandat.entreprise_id:
                    raise serializers.ValidationError(
                        {"travailleur_id": "Vous n'êtes pas délégué d'une entreprise."}
                    )
                travailleur = attrs["travailleur"]
                profil_travailleur = getattr(travailleur, "profil", None)
                if not profil_travailleur or getattr(profil_travailleur, "entreprise_id", None) != mandat.entreprise_id:
                    raise serializers.ValidationError(
                        {"travailleur_id": "Vous ne pouvez envoyer une requête que pour des personnes de votre entreprise."}
                    )
                entreprise_req = attrs.get("entreprise")
                if entreprise_req and entreprise_req.id != mandat.entreprise_id:
                    raise serializers.ValidationError(
                        {"entreprise_id": "Vous ne pouvez créer une requête que pour votre entreprise."}
                    )
        # Ne valider délégué/entreprise que si l'un des deux est modifié (évite 400 en PATCH classification seule)
        if "entreprise" in attrs or "delegue_syndical" in attrs:
            entreprise = attrs.get("entreprise") or (self.instance and getattr(self.instance, "entreprise", None))
            delegue = attrs.get("delegue_syndical") or (self.instance and getattr(self.instance, "delegue_syndical", None))
            if delegue and entreprise and delegue.entreprise_id != entreprise.id:
                raise serializers.ValidationError(
                    {"delegue_syndical": "Le délégué ne correspond pas à l'entreprise."}
                )
        pole = attrs.get("pole") or (self.instance and getattr(self.instance, "pole", None))
        type_probleme = attrs.get("type_probleme") or (self.instance and getattr(self.instance, "type_probleme", None))
        types_problemes = getattr(pole, "types_problemes", None) if pole else None
        # Optionnel : restreindre le type au pôle. Désactivé pour permettre l'enregistrement même si le front
        # n'utilise pas encore /api/type-probleme-choices/?pole=<id>. Réactiver en décommentant le bloc ci-dessous.
        # if pole and type_probleme and types_problemes and type_probleme not in types_problemes:
        #     from requetes.models import TypeProbleme
        #     allowed_labels = [dict(TypeProbleme.choices).get(v, v) for v in types_problemes]
        #     raise serializers.ValidationError({"type_probleme": "…", "allowed_types": types_problemes})
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


class ActiviteRequeteSerializer(serializers.ModelSerializer):
    """Serializer pour les activités planifiées sur une requête (suivi d'activités, calendrier)."""

    requete_id = serializers.PrimaryKeyRelatedField(
        source="requete", queryset=Requete.objects.all(), write_only=True
    )
    requete = serializers.StringRelatedField(read_only=True)
    created_by_id = serializers.PrimaryKeyRelatedField(
        source="created_by", queryset=User.objects.all(), write_only=True, required=False
    )
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ActiviteRequete
        fields = [
            "id",
            "requete",
            "requete_id",
            "type_activite",
            "titre",
            "description",
            "date_planifiee",
            "statut",
            "date_realisation",
            "commentaire",
            "created_by",
            "created_by_id",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


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
