from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
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
    ActiviteRequete,
    Dossier,
    DelegueSyndical,
    Entreprise,
    DocumentSyndical,
    HistoriqueAction,
    MaquetteCompteRendu,
    Notification,
    PoleMembre,
    PoleMembership,
    PieceJointe,
    Pole,
    ProfilUtilisateur,
    Requete,
    RequeteMessage,
    Reunion,
    TypeProbleme,
)
from requetes.services.pole_processors import (
    get_pole_processor,
    PoleProcessorActionNotAllowedError,
    PoleProcessorNotFoundError,
    PoleProcessorValidationError,
)

from .filters import (
    DossierFilter,
    MaquetteCompteRenduFilter,
    NotificationFilter,
    PieceJointeFilter,
    RequeteFilter,
    ReunionFilter,
)
from .permissions import (
    DossierAccessPermission,
    IsAuthenticatedAndHasRole,
    IsPoleManager,
    IsSuperAdminOrAdmin,
    PoleMembreAccessPermission,
    ReadOnlyUnlessAdmin,
    ReadOnlyUnlessAdminOrPoleManager,
    RequeteAccessPermission,
    _pole_ids_for_user,
)
from .serializers import (
    ActiviteRequeteSerializer,
    AdminUserCreateSerializer,
    DossierSerializer,
    DelegueSyndicalSerializer,
    DocumentSyndicalSerializer,
    EntrepriseSerializer,
    HistoriqueActionSerializer,
    NotificationSerializer,
    PoleMembreSerializer,
    PoleMembershipSerializer,
    PieceJointeSerializer,
    PoleSerializer,
    ProfilUtilisateurSerializer,
    RegisterSerializer,
    EmailOrUsernameTokenObtainPairSerializer,
    RequeteMessageCreateSerializer,
    RequeteMessageSerializer,
    RequeteSerializer,
    ReunionSerializer,
    MaquetteCompteRenduSerializer,
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
    """Pôles dont l'utilisateur est membre (PoleMembership + legacy Pole.membres / chef_de_pole)."""
    ids = set(_pole_ids_for_user(user))
    ids |= set(
        Pole.objects.filter(Q(membres=user) | Q(chef_de_pole=user)).values_list("id", flat=True)
    )
    return list(ids)


def _is_valid_choice(model, field_name: str, value: str) -> bool:
    field = model._meta.get_field(field_name)
    choices = {choice[0] for choice in field.choices}
    return value in choices


class TypeProblemeChoicesView(APIView):
    """
    Retourne les choix de type de problème (type d'activité) pour le formulaire requête.
    Si ?pole=<id> est fourni et que le pôle a types_problemes renseigné, seuls ces types sont renvoyés.
    Sinon tous les types sont renvoyés. Permet au frontend d'afficher les types en fonction du pôle choisi.
    """
    permission_classes = [IsAuthenticatedAndHasRole]

    def get(self, request):
        pole_id = request.query_params.get("pole")
        all_choices = [{"value": c[0], "label": c[1]} for c in TypeProbleme.choices]
        if not pole_id:
            return Response(all_choices)
        try:
            pole = Pole.objects.get(pk=pole_id)
        except (Pole.DoesNotExist, ValueError):
            return Response(all_choices)
        if not pole.types_problemes:
            return Response(all_choices)
        allowed = set(pole.types_problemes)
        filtered = [c for c in all_choices if c["value"] in allowed]
        return Response(filtered if filtered else all_choices)


def _entreprise_id_for_user(user: Any) -> int | None:
    """Retourne l'entreprise_id du profil de l'utilisateur, ou None."""
    if not getattr(user, "pk", None):
        return None
    profil = getattr(user, "profil", None)
    if isinstance(profil, ProfilUtilisateur):
        return getattr(profil, "entreprise_id", None)
    return None


def _pole_entreprise_ids(pole: Pole, exclude_user_id: int | None = None) -> list[int]:
    """
    Retourne les entreprise_id des membres déjà présents dans le pôle
    (PoleMembership + PoleMembre + chef_de_pole), sans compter exclude_user_id.
    """
    user_ids = set()
    user_ids.update(
        PoleMembership.objects.filter(pole=pole).values_list("user_id", flat=True)
    )
    user_ids.update(
        PoleMembre.objects.filter(pole=pole).values_list("user_id", flat=True)
    )
    if pole.chef_de_pole_id:
        user_ids.add(pole.chef_de_pole_id)
    if exclude_user_id is not None:
        user_ids.discard(exclude_user_id)
    return list(
        ProfilUtilisateur.objects.filter(user_id__in=user_ids)
        .exclude(entreprise_id__isnull=True)
        .values_list("entreprise_id", flat=True)
        .distinct()
    )


def _raise_if_same_company_in_pole(pole: Pole, user: Any, context: str = "") -> None:
    """
    Règle métier : deux personnes d'une même entreprise ne peuvent pas appartenir au même pôle.
    Lève ValidationError si l'utilisateur a une entreprise déjà représentée dans le pôle.
    """
    from rest_framework.exceptions import ValidationError

    entreprise_id = _entreprise_id_for_user(user)
    if entreprise_id is None:
        return
    existing = _pole_entreprise_ids(pole, exclude_user_id=getattr(user, "pk", None))
    if entreprise_id in existing:
        raise ValidationError(
            {"detail": "Deux personnes d'une même entreprise ne peuvent pas appartenir au même pôle."}
            if not context
            else {context: "Deux personnes d'une même entreprise ne peuvent pas appartenir au même pôle."}
        )


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
    queryset = DelegueSyndical.objects.filter(is_active=True).select_related("user", "entreprise")
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

        # Seuls admin et responsable de CE pôle (chef ou is_manager) peuvent ajouter ; pas un autre pôle.
        role = _get_role(request.user)
        is_responsible = (
            pole.chef_de_pole_id == request.user.id
            or PoleMembership.objects.filter(user=request.user, pole=pole, is_manager=True).exists()
        )
        if role != "admin" and not is_responsible:
            return Response(
                {"detail": "Seul l'administrateur ou le responsable de ce pôle peut ajouter un membre. Vous ne pouvez pas ajouter de membre à un autre pôle."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = PoleMembreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_to_add = serializer.validated_data.get("user")
        if user_to_add:
            _raise_if_same_company_in_pole(pole, user_to_add)
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
    permission_classes = [IsAuthenticatedAndHasRole, ReadOnlyUnlessAdminOrPoleManager, PoleMembreAccessPermission]
    filterset_fields = ["pole", "user", "role"]

    def get_queryset(self):
        qs = super().get_queryset()
        if _get_role(self.request.user) == "admin":
            return qs
        manager_pole_ids = list(
            PoleMembership.objects.filter(
                user=self.request.user, is_manager=True
            ).values_list("pole_id", flat=True)
        )
        manager_pole_ids += list(
            Pole.objects.filter(chef_de_pole=self.request.user).values_list("id", flat=True)
        )
        if not manager_pole_ids:
            return qs.none()
        return qs.filter(pole_id__in=manager_pole_ids)

    def perform_create(self, serializer):
        pole = serializer.validated_data.get("pole")
        if not pole and self.request.data:
            pole_id = self.request.data.get("pole") or self.request.data.get("pole_id")
            if pole_id:
                pole = Pole.objects.filter(pk=pole_id).first()
        if pole:
            # Seuls admin et responsable de CE pôle peuvent ajouter ; refus si autre pôle.
            role = _get_role(self.request.user)
            is_responsible = (
                pole.chef_de_pole_id == self.request.user.id
                or PoleMembership.objects.filter(user=self.request.user, pole=pole, is_manager=True).exists()
            )
            if role != "admin" and not is_responsible:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(
                    "Seul l'administrateur ou le responsable de ce pôle peut ajouter un membre. Vous ne pouvez pas ajouter de membre à un autre pôle."
                )
            user_to_add = serializer.validated_data.get("user")
            if user_to_add:
                _raise_if_same_company_in_pole(pole, user_to_add)
        serializer.save()

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


class PoleMembershipViewSet(BaseModelViewSet):
    """
    Gestion des appartenances aux pôles (User ↔ Pole, is_manager).
    Ajout/retrait de membres et modification du statut manager : réservé aux admins
    et aux responsables du pôle concerné (PoleMembership.is_manager ou chef_de_pole).
    """

    queryset = PoleMembership.objects.select_related("user", "pole").all()
    serializer_class = PoleMembershipSerializer
    permission_classes = [IsAuthenticatedAndHasRole, ReadOnlyUnlessAdminOrPoleManager]
    filterset_fields = ["pole", "user", "is_manager"]

    def get_queryset(self):
        qs = super().get_queryset()
        if _get_role(self.request.user) == "admin":
            return qs
        pole_ids = _user_pole_ids(self.request.user)
        manager_pole_ids = list(
            PoleMembership.objects.filter(
                user=self.request.user, is_manager=True
            ).values_list("pole_id", flat=True)
        )
        manager_pole_ids += list(
            Pole.objects.filter(chef_de_pole=self.request.user).values_list("id", flat=True)
        )
        if not manager_pole_ids:
            return qs.none()
        return qs.filter(pole_id__in=manager_pole_ids)

    def get_pole_from_request(self, request):
        """Pour IsPoleManager : récupère le pôle depuis le body (create) ou l'objet (update/delete)."""
        pole_id = (request.data or {}).get("pole") or (request.data or {}).get("pole_id")
        if pole_id is not None:
            return Pole.objects.filter(pk=pole_id).first()
        return None

    def perform_create(self, serializer):
        pole = serializer.validated_data.get("pole")
        if not pole:
            pole_id = self.request.data.get("pole") or self.request.data.get("pole_id")
            if pole_id:
                pole = Pole.objects.filter(pk=pole_id).first()
        # Seuls admin et responsable de CE pôle peuvent ajouter ; refus si autre pôle.
        if pole and _get_role(self.request.user) != "admin":
            is_responsible = (
                pole.chef_de_pole_id == self.request.user.id
                or PoleMembership.objects.filter(user=self.request.user, pole=pole, is_manager=True).exists()
            )
            if not is_responsible:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(
                    "Seul l'administrateur ou le responsable de ce pôle peut ajouter un membre. Vous ne pouvez pas ajouter de membre à un autre pôle."
                )
        user_to_add = serializer.validated_data.get("user")
        if pole and user_to_add:
            _raise_if_same_company_in_pole(pole, user_to_add)
        serializer.save()

    def check_object_permissions(self, request, obj):
        """Accès objet : admin ou responsable du pôle de cette appartenance."""
        if _get_role(request.user) == "admin":
            return
        if PoleMembership.objects.filter(
            user=request.user, pole=obj.pole, is_manager=True
        ).exists() or obj.pole.chef_de_pole_id == request.user.id:
            return
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied(
            "Seul l'administrateur ou le responsable de ce pôle peut modifier cette appartenance."
        )


class ProfilUtilisateurViewSet(BaseModelViewSet):
    queryset = ProfilUtilisateur.objects.select_related("user", "entreprise").all()
    serializer_class = ProfilUtilisateurSerializer
    permission_classes = [IsAuthenticatedAndHasRole, ReadOnlyUnlessAdmin]
    filterset_fields = ["role", "entreprise"]
    search_fields = ["user__username", "user__email"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        role = _get_role(self.request.user)
        if role == "delegate":
            delegue = DelegueSyndical.objects.filter(user=self.request.user).first()
            if delegue and delegue.entreprise_id:
                return qs.filter(entreprise_id=delegue.entreprise_id)
        return qs

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

    @action(detail=True, methods=["post"], url_path="set-password")
    def set_password(self, request, pk=None):
        """Permet à l'admin de changer le mot de passe d'un utilisateur."""
        if _get_role(request.user) != "admin":
            return Response(status=status.HTTP_403_FORBIDDEN)
        profil = self.get_object()
        new_password = request.data.get("new_password")
        if not new_password or not isinstance(new_password, str) or len(new_password.strip()) < 1:
            return Response(
                {"new_password": "Un mot de passe non vide est requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = profil.user
        user.set_password(new_password.strip())
        user.save(update_fields=["password"])
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="create-user")
    def create_user(self, request):
        if _get_role(request.user) != "admin":
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = AdminUserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        profil = getattr(user, "profil", None)
        if profil and profil.role == "delegate" and profil.entreprise_id:
            email = (getattr(profil, "email", None) or getattr(user, "email", None) or "").strip() or "contact@syndicat.local"
            telephone = (getattr(profil, "telephone", None) or "").strip() or "Non renseigné"
            DelegueSyndical.objects.get_or_create(
                user=user,
                entreprise_id=profil.entreprise_id,
                defaults={"email": email, "telephone": telephone[:30], "is_active": True},
            )
        if profil:
            return Response(
                ProfilUtilisateurSerializer(profil).data,
                status=status.HTTP_201_CREATED,
            )
        return Response({"id": user.id, "username": user.username}, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        profil = serializer.save()
        user = profil.user
        if profil.role == "delegate":
            if profil.entreprise_id:
                DelegueSyndical.objects.filter(user=user).exclude(entreprise_id=profil.entreprise_id).update(is_active=False)
                email = (profil.email or getattr(user, "email", None) or "").strip() or "contact@syndicat.local"
                telephone = (getattr(profil, "telephone", None) or "").strip() or "Non renseigné"
                DelegueSyndical.objects.update_or_create(
                    user=user,
                    entreprise_id=profil.entreprise_id,
                    defaults={"email": email, "telephone": telephone[:30], "is_active": True},
                )
            else:
                DelegueSyndical.objects.filter(user=user).update(is_active=True)
        else:
            DelegueSyndical.objects.filter(user=user).update(is_active=False)
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
    """
    ViewSet métier des requêtes (demandes).
    Filtrage par rôle/pôle dans get_queryset :
    - SUPER_ADMIN/ADMIN → voit tout
    - Responsable de pôle (PoleMembership.is_manager / chef_de_pole) → requêtes de son pôle
    - Membre de pôle → requêtes de son pôle + les siennes
    - Membre simple / délégué → selon règles métier (délégué = sa compagnie, membre = les siennes)
    """
    serializer_class = RequeteSerializer
    permission_classes = [IsAuthenticatedAndHasRole, RequeteAccessPermission]
    filterset_class = RequeteFilter
    search_fields = ["numero_reference", "titre", "description"]
    ordering_fields = ["created_at", "priorite", "statut"]

    def get_queryset(self):
        role = _get_role(self.request.user)
        qs = (
            Requete.objects.select_related("pole", "entreprise", "delegue_syndical", "dossier")
            .select_related("travailleur", "travailleur__profil")
            .all()
        )
        if role == "admin":
            return qs
        if role == "delegate":
            delegue = DelegueSyndical.objects.filter(user=self.request.user).first()
            if delegue and delegue.entreprise_id:
                return qs.filter(
                    Q(travailleur=self.request.user)
                    | Q(travailleur__profil__entreprise_id=delegue.entreprise_id)
                )
            return qs.filter(travailleur=self.request.user)
        if role == "member":
            return qs.filter(travailleur=self.request.user)
        pole_ids = _user_pole_ids(self.request.user)
        if pole_ids:
            return qs.filter(
                Q(pole_id__in=pole_ids) | Q(travailleur=self.request.user)
            )
        return qs.filter(travailleur=self.request.user)

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
        update_fields = ["statut", "updated_at"]
        if nouveau_statut == "closed" and not requete.date_cloture:
            from django.utils import timezone
            requete.date_cloture = timezone.now().date()
            update_fields.append("date_cloture")
        requete.save(update_fields=update_fields)
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

    @action(detail=True, methods=["get"], url_path="pole-actions")
    @extend_schema(description="Liste les actions métier disponibles pour cette requête (selon le pôle).")
    def pole_actions(self, request, pk=None):
        """Liste des actions proposées par le processeur du pôle de la requête."""
        requete = self.get_object()
        try:
            processor = get_pole_processor(requete.pole)
        except PoleProcessorNotFoundError as e:
            return Response(
                {"detail": e.message},
                status=status.HTTP_404_NOT_FOUND,
            )
        actions = processor.get_available_actions(requete)
        allowed_transitions = processor.get_allowed_transitions(requete)
        return Response(
            {
                "actions": [
                    {
                        "id": a.id,
                        "label": a.label,
                        "description": a.description or "",
                        "required_fields": list(a.required_fields),
                        "optional_fields": list(a.optional_fields),
                    }
                    for a in actions
                ],
                "allowed_transitions": allowed_transitions,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="execute-pole-action")
    @extend_schema(
        description="Exécute une action métier du pôle (ex: assigner avocat, planifier réunion).",
        examples=[
            OpenApiExample(
                "Action juridique",
                value={"action_id": "assign_lawyer", "lawyer_name": "Maître X", "lawyer_contact": "contact@cabinet.fr"},
            ),
        ],
    )
    def execute_pole_action(self, request, pk=None):
        """Exécution d'une action métier via le processeur du pôle."""
        requete = self.get_object()
        action_id = request.data.get("action_id")
        if not action_id:
            return Response(
                {"action_id": "Champ requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            processor = get_pole_processor(requete.pole)
        except PoleProcessorNotFoundError as e:
            return Response(
                {"detail": e.message},
                status=status.HTTP_404_NOT_FOUND,
            )
        payload = {k: v for k, v in request.data.items() if k != "action_id"}
        try:
            result = processor.execute_action(
                requete,
                action_id,
                user=request.user,
                **payload,
            )
        except PoleProcessorValidationError as e:
            return Response(
                {"detail": e.message, "errors": e.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except PoleProcessorActionNotAllowedError as e:
            return Response(
                {"detail": e.message},
                status=status.HTTP_403_FORBIDDEN,
            )
        if not result.success:
            return Response(
                {"detail": result.message, "errors": result.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"message": result.message, "data": result.data},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"], url_path="historique")
    def historique(self, request, pk=None):
        """Liste l'historique des actions (HistoriqueAction) pour cette requête."""
        requete = self.get_object()
        ct = ContentType.objects.get_for_model(Requete)
        qs = (
            HistoriqueAction.objects.filter(
                content_type=ct, object_id=requete.pk
            )
            .select_related("utilisateur")
            .order_by("-timestamp")
        )
        serializer = HistoriqueActionSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get", "post"], url_path="activites")
    def activites(self, request, pk=None):
        """Liste les activités planifiées de la requête ou en crée une (date affichée dans le calendrier)."""
        requete = self.get_object()
        if request.method == "GET":
            qs = ActiviteRequete.objects.filter(requete=requete).select_related("created_by").order_by("-date_planifiee")
            serializer = ActiviteRequeteSerializer(qs, many=True)
            return Response(serializer.data)
        data = request.data.copy()
        data.setdefault("requete_id", requete.pk)
        data.setdefault("created_by_id", request.user.pk)
        serializer = ActiviteRequeteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(requete=requete, created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"], url_path="messages")
    def messages(self, request, pk=None):
        """Liste les messages ou envoie un nouveau (réponse au besoin d'info)."""
        requete = self.get_object()
        if request.method == "POST":
            data = request.data.copy()
            serializer = RequeteMessageCreateSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            msg = RequeteMessage.objects.create(
                requete=requete,
                utilisateur=request.user,
                contenu=serializer.validated_data["contenu"].strip(),
                is_interne=serializer.validated_data.get("is_interne", False),
            )
            msg = RequeteMessage.objects.select_related("utilisateur", "utilisateur__profil").get(pk=msg.pk)
            return Response(RequeteMessageSerializer(msg).data, status=status.HTTP_201_CREATED)
        qs = (
            RequeteMessage.objects.filter(requete=requete)
            .select_related("utilisateur", "utilisateur__profil")
            .order_by("created_at")
        )
        serializer = RequeteMessageSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="assignable-members")
    def assignable_members(self, request, pk=None):
        """Liste les utilisateurs assignables (membres du pôle de la requête) pour l'action « Assigner un responsable »."""
        requete = self.get_object()
        pole = getattr(requete, "pole", None)
        if not pole:
            return Response([], status=status.HTTP_200_OK)
        user_ids = set(
            PoleMembre.objects.filter(pole=pole).values_list("user_id", flat=True)
        )
        user_ids |= set(
            PoleMembership.objects.filter(pole=pole).values_list("user_id", flat=True)
        )
        if pole.chef_de_pole_id:
            user_ids.add(pole.chef_de_pole_id)
        if not user_ids:
            return Response([], status=status.HTTP_200_OK)
        User = get_user_model()
        users = User.objects.filter(pk__in=user_ids).order_by("first_name", "last_name")
        data = [
            {
                "id": u.pk,
                "user_id_read": u.pk,
                "user_first_name": getattr(u, "first_name", "") or "",
                "user_last_name": getattr(u, "last_name", "") or "",
                "user_email": getattr(u, "email", "") or "",
            }
            for u in users
        ]
        return Response(data, status=status.HTTP_200_OK)

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

    @action(detail=True, methods=["get"], url_path="compte-rendu-pdf")
    def compte_rendu_pdf(self, request, pk=None):
        """Exporte le compte rendu de clôture en PDF (requête clôturée)."""
        requete = self.get_object()
        if requete.statut != "closed":
            return Response(
                {"detail": "La requête n'est pas clôturée. Impossible d'exporter le compte rendu en PDF."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            from api.pdf_utils import build_compte_rendu_pdf
            pdf_bytes = build_compte_rendu_pdf(requete)
        except RuntimeError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        filename = f"compte-rendu-{requete.numero_reference}.pdf"
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


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
                return qs.filter(requetes__travailleur__profil__entreprise_id=delegue.entreprise_id).distinct()
            return qs.none()
        if role == "member":
            return qs.filter(requetes__travailleur=self.request.user).distinct()
        pole_ids = _user_pole_ids(self.request.user)
        if pole_ids:
            return qs.filter(
                Q(pole_id__in=pole_ids) | Q(requetes__travailleur=self.request.user)
            ).distinct()
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
                return qs.filter(requete__travailleur__profil__entreprise_id=delegue.entreprise_id)
            return qs.none()
        if role == "member":
            return qs.filter(requete__travailleur=self.request.user)
        pole_ids = _user_pole_ids(self.request.user)
        if pole_ids:
            return qs.filter(
                Q(requete__pole_id__in=pole_ids) | Q(requete__travailleur=self.request.user)
            )
        return qs.filter(requete__travailleur=self.request.user)


class MaquetteCompteRenduViewSet(viewsets.ReadOnlyModelViewSet):
    """Maquettes de compte rendu (lecture seule). Filtre ?is_default=true pour la maquette par défaut."""
    queryset = MaquetteCompteRendu.objects.all()
    serializer_class = MaquetteCompteRenduSerializer
    permission_classes = [IsAuthenticatedAndHasRole]
    filter_backends = [DjangoFilterBackend]
    filterset_class = MaquetteCompteRenduFilter
    ordering = ["ordre", "nom"]


class ReunionViewSet(BaseModelViewSet):
    serializer_class = ReunionSerializer
    permission_classes = [IsAuthenticatedAndHasRole]
    filterset_class = ReunionFilter
    search_fields = ["ordre_du_jour", "compte_rendu"]
    ordering_fields = ["date_heure", "statut"]

    @action(detail=False, methods=["get"], url_path="calendar-events")
    def calendar_events(self, request):
        """
        Liste les événements calendrier : réunions (dossiers) + activités des requêtes (dates choisies dans le suivi).
        Query params optionnels : start, end (ISO datetime). event_type=reunion|activite pour filtrer.
        """
        from django.utils import timezone as django_tz
        from django.utils.dateparse import parse_datetime

        start_param = request.query_params.get("start")
        end_param = request.query_params.get("end")
        start_dt = parse_datetime(start_param) if start_param else None
        end_dt = parse_datetime(end_param) if end_param else None
        now = django_tz.now()
        if not start_dt:
            start_dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if django_tz.is_naive(start_dt):
                start_dt = django_tz.make_aware(start_dt)
        if not end_dt:
            from calendar import monthrange
            last_day = monthrange(now.year, now.month)[1]
            end_dt = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
            if django_tz.is_naive(end_dt):
                end_dt = django_tz.make_aware(end_dt)
        if start_dt and django_tz.is_naive(start_dt):
            start_dt = django_tz.make_aware(start_dt)
        if end_dt and django_tz.is_naive(end_dt):
            end_dt = django_tz.make_aware(end_dt)
        event_type_filter = request.query_params.get("event_type")

        events = []

        # Réunions (dossiers)
        if event_type_filter != "activite":
            qs = self.filter_queryset(self.get_queryset()).order_by("date_heure")
            qs = qs.filter(date_heure__gte=start_dt, date_heure__lte=end_dt)
            for r in qs:
                start = r.date_heure
                end = start + timedelta(hours=1)
                titre = f"{r.get_type_reunion_display()} – {r.dossier.numero_dossier}"
                if r.lieu:
                    titre += f" – {r.lieu}"
                events.append({
                    "id": f"reunion-{r.id}",
                    "event_type": "reunion",
                    "title": titre,
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "type_reunion": r.type_reunion,
                    "type_reunion_display": r.get_type_reunion_display(),
                    "statut": r.statut,
                    "statut_display": r.get_statut_display(),
                    "dossier_id": r.dossier_id,
                    "dossier_numero": r.dossier.numero_dossier,
                    "lieu": r.lieu or "",
                    "ordre_du_jour": r.ordre_du_jour or "",
                    "reunion_id": r.id,
                })

        # Activités des requêtes (programmées lors du traitement des requêtes par les pôles)
        requete_ids = []
        if event_type_filter != "reunion":
            try:
                role = _get_role(request.user)
                req_qs = Requete.objects.all()
                if role == "admin":
                    pass
                elif role == "delegate":
                    delegue = DelegueSyndical.objects.filter(user=request.user).first()
                    if delegue and delegue.entreprise_id:
                        req_qs = req_qs.filter(
                            Q(travailleur=request.user)
                            | Q(travailleur__profil__entreprise_id=delegue.entreprise_id)
                        )
                    else:
                        req_qs = req_qs.filter(travailleur=request.user)
                elif role == "member":
                    req_qs = req_qs.filter(travailleur=request.user)
                else:
                    pids = _user_pole_ids(request.user)
                    if pids:
                        req_qs = req_qs.filter(
                            Q(pole_id__in=pids) | Q(travailleur=request.user)
                        )
                    else:
                        req_qs = req_qs.filter(travailleur=request.user)
                requete_ids = list(req_qs.values_list("id", flat=True))
                if requete_ids:
                    activites = ActiviteRequete.objects.filter(
                        requete_id__in=requete_ids,
                        date_planifiee__gte=start_dt,
                        date_planifiee__lte=end_dt,
                        statut__in=["planned", "completed"],
                    ).select_related("requete", "created_by").order_by("date_planifiee")
                    for a in activites:
                        start = a.date_planifiee
                        end = start + timedelta(hours=1)
                        events.append({
                            "id": f"activite-{a.id}",
                            "event_type": "activite",
                            "title": a.titre,
                            "start": start.isoformat(),
                            "end": end.isoformat(),
                            "type_activite": a.type_activite,
                            "type_activite_display": a.get_type_activite_display(),
                            "statut": a.statut,
                            "statut_display": a.get_statut_display(),
                            "requete_id": a.requete_id,
                            "numero_reference": a.requete.numero_reference,
                            "description": a.description or "",
                            "activite_id": a.id,
                        })
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                err_str = str(e).lower()
                if "no such table" in err_str or "activite_requete" in err_str:
                    logger.info(
                        "Calendrier: table ActiviteRequete absente. Exécuter: python manage.py migrate requetes"
                    )
                else:
                    logger.exception("Calendrier: erreur chargement activités requêtes")
        events.sort(key=lambda e: e["start"])
        resp = Response(events)
        if request.query_params.get("debug") == "1":
            try:
                n_activites_total = ActiviteRequete.objects.count()
                n_reunions = sum(1 for e in events if e.get("event_type") == "reunion")
                n_activites = sum(1 for e in events if e.get("event_type") == "activite")
                resp["X-Calendar-Debug"] = (
                    f"requetes_vues={len(requete_ids)}; "
                    f"activites_en_base={n_activites_total}; "
                    f"reunions={n_reunions}; activites_retournees={n_activites}"
                )
            except Exception:
                pass
        return resp

    def get_queryset(self):
        role = _get_role(self.request.user)
        qs = Reunion.objects.select_related("dossier", "created_by").prefetch_related("participants").all()
        if role == "admin":
            return qs
        if role == "delegate":
            delegue = DelegueSyndical.objects.filter(user=self.request.user).first()
            if delegue and delegue.entreprise_id:
                return qs.filter(dossier__requetes__travailleur__profil__entreprise_id=delegue.entreprise_id).distinct()
            return qs.none()
        if role == "member":
            return qs.filter(dossier__requetes__travailleur=self.request.user).distinct()
        pole_ids = _user_pole_ids(self.request.user)
        if pole_ids:
            return qs.filter(
                Q(dossier__pole_id__in=pole_ids)
                | Q(dossier__requetes__travailleur=self.request.user)
            ).distinct()
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
            if not delegue or not delegue.entreprise_id:
                return qs.none()
            pole_ids = list(
                Pole.objects.filter(requetes__travailleur__profil__entreprise_id=delegue.entreprise_id)
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
