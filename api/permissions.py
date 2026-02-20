from __future__ import annotations

from typing import Any

from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import BasePermission, SAFE_METHODS

from requetes.models import (
    DelegueSyndical,
    Pole,
    PoleMembre,
    PoleMembership,
    ProfilUtilisateur,
    Requete,
    Dossier,
)


def _get_role(user: Any) -> str | None:
    """
    Retourne le rôle effectif pour l'affichage : admin, delegate (si mandat actif), ou rôle du profil.
    Ainsi un utilisateur avec profil.role=member mais un DelegueSyndical actif s'affiche comme « Délégué ».
    Si l'utilisateur est authentifié mais n'a pas encore de ProfilUtilisateur, on retourne "member" pour
    permettre l'accès à /profils/me/ (qui crée le profil à la volée).
    """
    if isinstance(user, AnonymousUser) or not user.is_authenticated:
        return None
    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return "admin"
    if getattr(user, "pk", None) and DelegueSyndical.objects.filter(user=user, is_active=True).exists():
        return "delegate"
    profil = getattr(user, "profil", None)
    if isinstance(profil, ProfilUtilisateur):
        return profil.role
    # Utilisateur authentifié sans profil : traiter comme "member" pour que /profils/me/ soit accessible
    return "member"


def _is_super_admin_or_admin(user: Any) -> bool:
    """Vrai si l'utilisateur a un rôle global SUPER_ADMIN ou ADMIN (is_staff/superuser ou role admin)."""
    if getattr(user, "is_superuser", False):
        return True
    if getattr(user, "is_staff", False):
        return True
    role = _get_role(user)
    return role in ("admin", "super_admin")


def _pole_ids_for_user(user: Any) -> list[int]:
    """Identifiants des pôles dont l'utilisateur est membre (PoleMembership) ou chef (legacy)."""
    if not getattr(user, "is_authenticated", True) or not user:
        return []
    ids = set(
        PoleMembership.objects.filter(user=user).values_list("pole_id", flat=True)
    )
    ids |= set(
        Pole.objects.filter(chef_de_pole=user).values_list("id", flat=True)
    )
    return list(ids)


def _is_pole_manager(user: Any, pole: Pole) -> bool:
    """Vrai si l'utilisateur est responsable du pôle (PoleMembership.is_manager ou chef_de_pole)."""
    if not getattr(user, "pk", None) or not getattr(pole, "pk", None):
        return False
    if pole.chef_de_pole_id == user.pk:
        return True
    return PoleMembership.objects.filter(
        user=user, pole=pole, is_manager=True
    ).exists()


def _is_pole_member(user: Any, pole: Pole) -> bool:
    """Vrai si l'utilisateur est membre du pôle (PoleMembership ou legacy Pole.membres)."""
    if not getattr(user, "pk", None) or not getattr(pole, "pk", None):
        return False
    if PoleMembership.objects.filter(user=user, pole=pole).exists():
        return True
    return pole.membres.filter(pk=user.pk).exists() or pole.chef_de_pole_id == user.pk


class IsAuthenticatedAndHasRole(BasePermission):
    """Refuse l'accès si l'utilisateur n'a pas de rôle métier."""

    def has_permission(self, request, view) -> bool:
        role = _get_role(request.user)
        return role is not None


class IsSuperAdminOrAdmin(BasePermission):
    """
    Accès réservé aux rôles globaux Super Administrateur ou Administrateur Syndical.
    Correspond à is_superuser, is_staff ou profil.role in (admin, super_admin).
    """

    def has_permission(self, request, view) -> bool:
        return _is_super_admin_or_admin(request.user)


class IsPoleManager(BasePermission):
    """
    Accès si l'utilisateur est responsable du pôle concerné (PoleMembership.is_manager=True
    ou chef_de_pole). Le pôle peut venir de l'objet (obj.pole) ou du view (get_pole_from_request).
    """

    def has_object_permission(self, request, view, obj) -> bool:
        pole = getattr(obj, "pole", None)
        if pole is None and hasattr(view, "get_pole_from_request"):
            pole = view.get_pole_from_request(request)
        if pole is None:
            return False
        return _is_pole_manager(request.user, pole)

    def has_permission(self, request, view) -> bool:
        if hasattr(view, "get_pole_from_request"):
            pole = view.get_pole_from_request(request)
            if pole is not None:
                return _is_pole_manager(request.user, pole)
        return True


class IsPoleMember(BasePermission):
    """
    Accès si l'utilisateur est membre du pôle de la ressource (requête, dossier, etc.).
    """

    def has_object_permission(self, request, view, obj) -> bool:
        pole = getattr(obj, "pole", None)
        if pole is None and hasattr(view, "get_pole_from_request"):
            pole = view.get_pole_from_request(request)
        if pole is None:
            return False
        return _is_pole_member(request.user, pole)


class IsOwner(BasePermission):
    """
    Accès si l'utilisateur est l'auteur/propriétaire de la ressource.
    Pour une Requete : travailleur_id == request.user.id.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        owner_id = getattr(obj, "travailleur_id", None) or getattr(obj, "user_id", None)
        if owner_id is not None:
            return owner_id == request.user.pk
        user = getattr(obj, "travailleur", None) or getattr(obj, "user", None)
        if user is not None:
            return getattr(user, "pk", None) == request.user.pk
        return False


class RequeteAccessPermission(BasePermission):
    """Contrôle l'accès aux requêtes selon rôle et rattachements (dont PoleMembership)."""

    def has_object_permission(self, request, view, obj: Requete) -> bool:
        role = _get_role(request.user)
        if role is None:
            return False
        # Le demandeur (travailleur) a toujours accès à sa requête (lecture + mise à jour statut, etc.)
        if getattr(obj, "travailleur_id", None) == request.user.pk:
            return True
        if role == "admin":
            return True
        pole = getattr(obj, "pole", None)
        if pole is not None and _is_pole_member(request.user, pole):
            return True
        if pole is not None and pole.id in _pole_ids_for_user(request.user):
            return True
        if pole is not None and role in ["pole_manager", "head", "assistant"]:
            return pole.membres.filter(id=request.user.id).exists() or pole.chef_de_pole_id == request.user.id
        if role == "delegate":
            if obj.delegue_syndical and obj.delegue_syndical.user_id == request.user.id:
                return True
            mandat = DelegueSyndical.objects.filter(user=request.user).first()
            if mandat and mandat.entreprise_id:
                profil_travailleur = getattr(obj.travailleur, "profil", None)
                if profil_travailleur and getattr(profil_travailleur, "entreprise_id", None) == mandat.entreprise_id:
                    return True
            return False
        if role == "member":
            return False  # déjà traité par le check travailleur_id ci-dessus
        return False


class DossierAccessPermission(BasePermission):
    """Contrôle l'accès aux dossiers selon rôle et rattachements."""

    def has_object_permission(self, request, view, obj: Dossier) -> bool:
        role = _get_role(request.user)
        if role is None:
            return False
        if role == "admin":
            return True
        if _is_pole_member(request.user, obj.pole):
            return True
        if role in ["pole_manager", "head", "assistant"]:
            return obj.pole.membres.filter(id=request.user.id).exists() or obj.pole.chef_de_pole_id == request.user.id
        if role == "delegate":
            if obj.requetes.filter(delegue_syndical__user_id=request.user.id).exists():
                return True
            mandat = DelegueSyndical.objects.filter(user=request.user).first()
            if mandat and mandat.entreprise_id:
                if obj.requetes.filter(travailleur__profil__entreprise_id=mandat.entreprise_id).exists():
                    return True
            return False
        if role == "member":
            return obj.requetes.filter(travailleur_id=request.user.id).exists()
        return False


class ReadOnlyUnlessAdmin(BasePermission):
    """Autorise la lecture pour tous les rôles, écriture pour admin."""

    def has_permission(self, request, view) -> bool:
        role = _get_role(request.user)
        if role is None:
            return False
        if request.method in SAFE_METHODS:
            return True
        return role == "admin"


class ReadOnlyUnlessAdminOrPoleManager(BasePermission):
    """Autorise la lecture pour tous les rôles, écriture pour admin ou chef de pôle."""

    def has_permission(self, request, view) -> bool:
        role = _get_role(request.user)
        if role is None:
            return False
        if request.method in SAFE_METHODS:
            return True
        return role in ["admin", "pole_manager"]


class PoleMembreAccessPermission(BasePermission):
    """Ajout/suppression de membres : admin ou responsable du pôle (chef_de_pole) uniquement."""

    def has_object_permission(self, request, view, obj: PoleMembre) -> bool:
        if request.method in SAFE_METHODS:
            return True
        role = _get_role(request.user)
        if role == "admin":
            return True
        return obj.pole.chef_de_pole_id == request.user.id
