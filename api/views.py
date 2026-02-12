from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import OpenApiExample, extend_schema

from requetes.models import (
    ActionHistorique,
    Dossier,
    DelegueSyndical,
    Entreprise,
    DocumentSyndical,
    HistoriqueAction,
    Notification,
    PoleMembre,
    PieceJointe,
    Pole,
    ProfilUtilisateur,
    Requete,
    Reunion,
)

from .filters import DossierFilter, NotificationFilter, PieceJointeFilter, RequeteFilter, ReunionFilter
from .permissions import (
    DossierAccessPermission,
    IsAuthenticatedAndHasRole,
    ReadOnlyUnlessAdmin,
    ReadOnlyUnlessAdminOrPoleManager,
    RequeteAccessPermission,
)
from .serializers import (
    AdminUserCreateSerializer,
    DossierSerializer,
    DelegueSyndicalSerializer,
    DocumentSyndicalSerializer,
    EntrepriseSerializer,
    NotificationSerializer,
    PoleMembreSerializer,
    PieceJointeSerializer,
    PoleSerializer,
    ProfilUtilisateurSerializer,
    RegisterSerializer,
    EmailOrUsernameTokenObtainPairSerializer,
    RequeteSerializer,
    ReunionSerializer,
)

User = get_user_model()


def _get_role(user: User) -> str | None:
    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return "admin"
    profil = getattr(user, "profil", None)
    if isinstance(profil, ProfilUtilisateur):
        return profil.role
    return None


def _user_pole_ids(user: User) -> list[int]:
    return list(
        Pole.objects.filter(Q(membres=user) | Q(chef_de_pole=user)).values_list("id", flat=True)
    )


def _is_valid_choice(model, field_name: str, value: str) -> bool:
    field = model._meta.get_field(field_name)
    choices = {choice[0] for choice in field.choices}
    return value in choices


class BaseModelViewSet(viewsets.ModelViewSet):
    """Base ViewSet avec filtres standards."""

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering = ["-id"]


class EntrepriseViewSet(BaseModelViewSet):
    queryset = Entreprise.objects.all()
    serializer_class = EntrepriseSerializer
    permission_classes = [IsAuthenticatedAndHasRole, ReadOnlyUnlessAdmin]
    search_fields = ["nom", "code", "secteur_activite"]
    ordering_fields = ["nom", "code"]

    def get_permissions(self):
        if getattr(self, "action", None) in ["list", "retrieve"]:
            return [AllowAny()]
        return super().get_permissions()


class DelegueSyndicalViewSet(BaseModelViewSet):
    queryset = DelegueSyndical.objects.select_related("user", "entreprise").all()
    serializer_class = DelegueSyndicalSerializer
    permission_classes = [IsAuthenticatedAndHasRole, ReadOnlyUnlessAdmin]
    filterset_fields = ["user", "entreprise", "is_active"]
    search_fields = ["email", "telephone", "user__username", "user__email"]
    ordering_fields = ["created_at"]

    def perform_create(self, serializer):
        delegue = serializer.save()
        profil = getattr(delegue.user, "profil", None)
        if profil and profil.role != "delegate":
            profil.role = "delegate"
            profil.save(update_fields=["role"])

    def perform_update(self, serializer):
        delegue = serializer.save()
        profil = getattr(delegue.user, "profil", None)
        if profil and profil.role != "delegate":
            profil.role = "delegate"
            profil.save(update_fields=["role"])


class PoleViewSet(BaseModelViewSet):
    queryset = Pole.objects.select_related("chef_de_pole").all()
    serializer_class = PoleSerializer
    permission_classes = [IsAuthenticatedAndHasRole, ReadOnlyUnlessAdminOrPoleManager]
    search_fields = ["nom", "description"]
    ordering_fields = ["nom"]

    def perform_create(self, serializer):
        serializer.save(chef_de_pole=self.request.user)

    @action(detail=True, methods=["get", "post"], url_path="members")
    def members(self, request, pk=None):
        pole = self.get_object()
        if request.method.lower() == "get":
            qs = PoleMembre.objects.select_related("user").filter(pole=pole)
            return Response(PoleMembreSerializer(qs, many=True).data, status=status.HTTP_200_OK)

        serializer = PoleMembreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            member = serializer.save(pole=pole)
        except IntegrityError:
            return Response(
                {"detail": "Ce membre est déjà associé à ce pôle."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        profil = getattr(member.user, "profil", None)
        if profil:
            role_map = {"head": "head", "assistant": "assistant", "member": "member"}
            new_role = role_map.get(member.role)
            if new_role and profil.role != new_role:
                profil.role = new_role
                profil.save(update_fields=["role"])
        return Response(PoleMembreSerializer(member).data, status=status.HTTP_201_CREATED)


class PoleMembreViewSet(BaseModelViewSet):
    queryset = PoleMembre.objects.select_related("pole", "user").all()
    serializer_class = PoleMembreSerializer
    permission_classes = [IsAuthenticatedAndHasRole, ReadOnlyUnlessAdminOrPoleManager]
    filterset_fields = ["pole", "user", "role"]

    def perform_update(self, serializer):
        member = serializer.save()
        profil = getattr(member.user, "profil", None)
        if not profil:
            return
        role_map = {"head": "head", "assistant": "assistant", "member": "member"}
        new_role = role_map.get(member.role)
        if new_role and profil.role != new_role:
            profil.role = new_role
            profil.save(update_fields=["role"])


class ProfilUtilisateurViewSet(BaseModelViewSet):
    queryset = ProfilUtilisateur.objects.select_related("user", "entreprise").all()
    serializer_class = ProfilUtilisateurSerializer
    permission_classes = [IsAuthenticatedAndHasRole, ReadOnlyUnlessAdmin]
    filterset_fields = ["role", "entreprise"]
    search_fields = ["user__username", "user__email"]
    ordering_fields = ["created_at"]

    def get_permissions(self):
        if getattr(self, "action", None) == "me":
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request):
        profil, _ = ProfilUtilisateur.objects.get_or_create(
            user=request.user, defaults={"role": "member"}
        )
        if request.method.lower() == "patch":
            serializer = self.get_serializer(profil, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(profil)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="create-user")
    def create_user(self, request):
        if _get_role(request.user) != "admin":
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = AdminUserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        profil = getattr(user, "profil", None)
        if profil:
            return Response(
                ProfilUtilisateurSerializer(profil).data,
                status=status.HTTP_201_CREATED,
            )
        return Response({"id": user.id, "username": user.username}, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        profil = serializer.save()
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
        is_active = serializer.validated_data.get("user", {}).get("is_active")
        if is_active is not None:
            user.is_active = is_active
            updated = True
        if updated:
            try:
                user.save()
            except IntegrityError:
                raise serializers.ValidationError(
                    {"email": "Cet email est déjà utilisé."}
                )

        role_to_pole_role = {
            "pole_manager": "head",
            "head": "head",
            "assistant": "assistant",
            "delegate": "assistant",
            "member": "member",
            "admin": "head",
        }
        pole_role = role_to_pole_role.get(profil.role)
        if pole_role:
            PoleMembre.objects.filter(user=user).update(role=pole_role)

    def perform_destroy(self, instance):
        user = instance.user
        instance.delete()
        user.delete()


class RequeteViewSet(BaseModelViewSet):
    serializer_class = RequeteSerializer
    permission_classes = [IsAuthenticatedAndHasRole, RequeteAccessPermission]
    filterset_class = RequeteFilter
    search_fields = ["numero_reference", "titre", "description"]
    ordering_fields = ["created_at", "priorite", "statut"]

    def get_queryset(self):
        role = _get_role(self.request.user)
        qs = (
            Requete.objects.select_related("pole", "entreprise", "delegue_syndical", "dossier")
            .select_related("travailleur")
            .all()
        )
        if role == "admin":
            return qs
        if role == "delegate":
            delegue = DelegueSyndical.objects.filter(user=self.request.user).first()
            if delegue and delegue.entreprise_id:
                return qs.filter(entreprise_id=delegue.entreprise_id)
        pole_ids = _user_pole_ids(self.request.user)
        if pole_ids:
            return qs.filter(pole_id__in=pole_ids)
        return qs.filter(travailleur=self.request.user)
        return qs.none()

    def perform_create(self, serializer):
        with transaction.atomic():
            requete = serializer.save()
            HistoriqueAction.enregistrer_action(
                content_object=requete,
                utilisateur=self.request.user,
                action=ActionHistorique.CREATION,
                commentaire="Création de la requête.",
            )
            Notification.objects.create(
                utilisateur=requete.travailleur,
                titre="Requête créée",
                message=f"Votre requête {requete.numero_reference} a été créée.",
                type_notification="ticket_update",
                requete=requete,
            )

    def perform_update(self, serializer):
        requete = self.get_object()
        ancien_statut = requete.statut
        with transaction.atomic():
            updated = serializer.save()
            HistoriqueAction.enregistrer_action(
                content_object=updated,
                utilisateur=self.request.user,
                action=ActionHistorique.MODIFICATION_STATUT
                if ancien_statut != updated.statut
                else ActionHistorique.MODIFICATION_STATUT,
                champ_modifie="statut" if ancien_statut != updated.statut else None,
                ancienne_valeur=ancien_statut if ancien_statut != updated.statut else None,
                nouvelle_valeur=updated.statut if ancien_statut != updated.statut else None,
                commentaire="Mise à jour de la requête.",
            )
            if ancien_statut != updated.statut:
                Notification.objects.create(
                    utilisateur=updated.travailleur,
                    titre="Mise à jour de requête",
                    message=f"Statut mis à jour: {updated.get_statut_display()}",
                    type_notification="ticket_update",
                    requete=updated,
                )

    @action(detail=True, methods=["post"], url_path="change-status")
    @extend_schema(
        examples=[
            OpenApiExample(
                "Changement de statut",
                value={"statut": "processing"},
            )
        ]
    )
    def change_status(self, request, pk=None):
        requete = self.get_object()
        nouveau_statut = request.data.get("statut")
        if not nouveau_statut:
            return Response({"statut": "Champ requis."}, status=status.HTTP_400_BAD_REQUEST)
        if not _is_valid_choice(Requete, "statut", nouveau_statut):
            return Response({"statut": "Valeur invalide."}, status=status.HTTP_400_BAD_REQUEST)
        ancien_statut = requete.statut
        requete.statut = nouveau_statut
        requete.save(update_fields=["statut", "updated_at"])
        HistoriqueAction.enregistrer_action(
            content_object=requete,
            utilisateur=request.user,
            action=ActionHistorique.MODIFICATION_STATUT,
            champ_modifie="statut",
            ancienne_valeur=ancien_statut,
            nouvelle_valeur=nouveau_statut,
        )
        Notification.objects.create(
            utilisateur=requete.travailleur,
            titre="Mise à jour de requête",
            message=f"Statut mis à jour: {requete.get_statut_display()}",
            type_notification="ticket_update",
            requete=requete,
        )
        return Response(self.get_serializer(requete).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="pieces-jointes")
    @extend_schema(
        examples=[
            OpenApiExample(
                "Ajout pièce jointe",
                value={
                    "fichier": "<file>",
                    "type_document": "CONTRAT",
                    "description": "Contrat signé",
                },
            )
        ]
    )
    def add_piece_jointe(self, request, pk=None):
        requete = self.get_object()
        data = request.data.copy()
        data["requete_id"] = requete.id
        data["uploaded_by_id"] = request.user.id
        serializer = PieceJointeSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        HistoriqueAction.enregistrer_action(
            content_object=requete,
            utilisateur=request.user,
            action=ActionHistorique.PIECE_JOINTE_AJOUTEE,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DossierViewSet(BaseModelViewSet):
    serializer_class = DossierSerializer
    permission_classes = [IsAuthenticatedAndHasRole, DossierAccessPermission]
    filterset_class = DossierFilter
    search_fields = ["numero_dossier", "titre"]
    ordering_fields = ["created_at", "statut"]

    def get_queryset(self):
        role = _get_role(self.request.user)
        qs = (
            Dossier.objects.select_related("pole", "responsable")
            .prefetch_related("requetes")
            .all()
        )
        if role == "admin":
            return qs
        if role == "delegate":
            delegue = DelegueSyndical.objects.filter(user=self.request.user).first()
            if delegue and delegue.entreprise_id:
                return qs.filter(requetes__entreprise_id=delegue.entreprise_id).distinct()
        pole_ids = _user_pole_ids(self.request.user)
        if pole_ids:
            return qs.filter(pole_id__in=pole_ids)
        return qs.filter(requetes__travailleur=self.request.user).distinct()

    def perform_create(self, serializer):
        with transaction.atomic():
            dossier = serializer.save()
            HistoriqueAction.enregistrer_action(
                content_object=dossier,
                utilisateur=self.request.user,
                action=ActionHistorique.CREATION,
                commentaire="Création du dossier.",
            )

    def perform_update(self, serializer):
        dossier = self.get_object()
        ancien_statut = dossier.statut
        with transaction.atomic():
            updated = serializer.save()
            HistoriqueAction.enregistrer_action(
                content_object=updated,
                utilisateur=self.request.user,
                action=ActionHistorique.MODIFICATION_STATUT
                if ancien_statut != updated.statut
                else ActionHistorique.MODIFICATION_STATUT,
                champ_modifie="statut" if ancien_statut != updated.statut else None,
                ancienne_valeur=ancien_statut if ancien_statut != updated.statut else None,
                nouvelle_valeur=updated.statut if ancien_statut != updated.statut else None,
                commentaire="Mise à jour du dossier.",
            )

    @action(detail=True, methods=["post"], url_path="change-status")
    @extend_schema(
        examples=[
            OpenApiExample(
                "Changement de statut dossier",
                value={"statut": "EN_INSTRUCTION"},
            )
        ]
    )
    def change_status(self, request, pk=None):
        dossier = self.get_object()
        nouveau_statut = request.data.get("statut")
        if not nouveau_statut:
            return Response({"statut": "Champ requis."}, status=status.HTTP_400_BAD_REQUEST)
        if not _is_valid_choice(Dossier, "statut", nouveau_statut):
            return Response({"statut": "Valeur invalide."}, status=status.HTTP_400_BAD_REQUEST)
        ancien_statut = dossier.statut
        dossier.statut = nouveau_statut
        dossier.save(update_fields=["statut", "updated_at"])
        HistoriqueAction.enregistrer_action(
            content_object=dossier,
            utilisateur=request.user,
            action=ActionHistorique.MODIFICATION_STATUT,
            champ_modifie="statut",
            ancienne_valeur=ancien_statut,
            nouvelle_valeur=nouveau_statut,
        )
        return Response(self.get_serializer(dossier).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="transmettre-bureau")
    @extend_schema(
        examples=[
            OpenApiExample(
                "Transmission au bureau",
                value={},
            )
        ]
    )
    def transmettre_bureau(self, request, pk=None):
        dossier = self.get_object()
        ancien_statut = dossier.statut
        dossier.statut = "TRANSMIS_BUREAU"
        dossier.save(update_fields=["statut", "updated_at"])
        HistoriqueAction.enregistrer_action(
            content_object=dossier,
            utilisateur=request.user,
            action=ActionHistorique.TRANSMISSION,
            champ_modifie="statut",
            ancienne_valeur=ancien_statut,
            nouvelle_valeur=dossier.statut,
        )
        return Response(self.get_serializer(dossier).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="planifier-reunion")
    @extend_schema(
        examples=[
            OpenApiExample(
                "Planifier réunion",
                value={
                    "type_reunion": "PRESENTIEL",
                    "date_heure": "2026-02-15T10:00:00Z",
                    "lieu": "Siège",
                    "ordre_du_jour": "Point d'avancement",
                },
            )
        ]
    )
    def planifier_reunion(self, request, pk=None):
        dossier = self.get_object()
        serializer = ReunionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(dossier=dossier, created_by=request.user)
        HistoriqueAction.enregistrer_action(
            content_object=dossier,
            utilisateur=request.user,
            action=ActionHistorique.REUNION_PLANIFIEE,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PieceJointeViewSet(BaseModelViewSet):
    serializer_class = PieceJointeSerializer
    permission_classes = [IsAuthenticatedAndHasRole]
    filterset_class = PieceJointeFilter
    search_fields = ["description"]
    ordering_fields = ["uploaded_at"]

    def get_queryset(self):
        role = _get_role(self.request.user)
        qs = PieceJointe.objects.select_related("requete", "uploaded_by").all()
        if role == "admin":
            return qs
        if role == "delegate":
            delegue = DelegueSyndical.objects.filter(user=self.request.user).first()
            if delegue and delegue.entreprise_id:
                return qs.filter(requete__entreprise_id=delegue.entreprise_id)
        pole_ids = _user_pole_ids(self.request.user)
        if pole_ids:
            return qs.filter(requete__pole_id__in=pole_ids)
        return qs.filter(requete__travailleur=self.request.user)


class ReunionViewSet(BaseModelViewSet):
    serializer_class = ReunionSerializer
    permission_classes = [IsAuthenticatedAndHasRole]
    filterset_class = ReunionFilter
    search_fields = ["ordre_du_jour", "compte_rendu"]
    ordering_fields = ["date_heure", "statut"]

    def get_queryset(self):
        role = _get_role(self.request.user)
        qs = Reunion.objects.select_related("dossier", "created_by").prefetch_related("participants").all()
        if role == "admin":
            return qs
        if role == "delegate":
            delegue = DelegueSyndical.objects.filter(user=self.request.user).first()
            if delegue and delegue.entreprise_id:
                return qs.filter(dossier__requetes__entreprise_id=delegue.entreprise_id).distinct()
        pole_ids = _user_pole_ids(self.request.user)
        if pole_ids:
            return qs.filter(dossier__pole_id__in=pole_ids)
        return qs.filter(dossier__requetes__travailleur=self.request.user).distinct()


class DocumentSyndicalViewSet(BaseModelViewSet):
    queryset = DocumentSyndical.objects.select_related("pole", "uploaded_by").all()
    serializer_class = DocumentSyndicalSerializer
    permission_classes = [IsAuthenticatedAndHasRole]
    search_fields = ["nom", "categorie", "description"]
    ordering_fields = ["annee", "created_at"]

    def get_queryset(self):
        role = _get_role(self.request.user)
        qs = DocumentSyndical.objects.select_related("pole", "uploaded_by").all()
        if role == "admin":
            return qs
        if role == "delegate":
            delegue = DelegueSyndical.objects.filter(user=self.request.user).first()
            if delegue and delegue.entreprise_id:
                pole_ids = list(
                    Pole.objects.filter(requetes__entreprise_id=delegue.entreprise_id)
                    .values_list("id", flat=True)
                    .distinct()
                )
                if pole_ids:
                    return qs.filter(pole_id__in=pole_ids)
                return qs.none()
        pole_ids = _user_pole_ids(self.request.user)
        if pole_ids:
            return qs.filter(pole_id__in=pole_ids)
        return qs.none()

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class NotificationViewSet(BaseModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticatedAndHasRole]
    filterset_class = NotificationFilter
    search_fields = ["titre", "message"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        role = _get_role(self.request.user)
        qs = Notification.objects.select_related("utilisateur", "requete").all()
        if role == "admin":
            return qs
        return qs.filter(utilisateur=self.request.user)


class LogoutViewSet(viewsets.ViewSet):
    """Révocation du refresh token."""

    permission_classes = [IsAuthenticatedAndHasRole]

    @action(detail=False, methods=["post"])
    def logout(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response({"refresh": "Champ requis."}, status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken(refresh)
        token.blacklist()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailOrUsernameTokenObtainPairSerializer


class RegisterAPIView(APIView):
    """Inscription utilisateur."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"id": user.id, "username": user.username},
            status=status.HTTP_201_CREATED,
        )
