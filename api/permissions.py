from __future__ import annotations

from typing import Any

from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import BasePermission, SAFE_METHODS

from requetes.models import ProfilUtilisateur, Requete, Dossier


def _get_role(user: Any) -> str | None:
    if isinstance(user, AnonymousUser) or not user.is_authenticated:
        return None
    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return "admin"
    profil = getattr(user, "profil", None)
    if isinstance(profil, ProfilUtilisateur):
        return profil.role
    return None


class IsAuthenticatedAndHasRole(BasePermission):
    """Refuse l'accès si l'utilisateur n'a pas de rôle métier."""

    def has_permission(self, request, view) -> bool:
        role = _get_role(request.user)
        return role is not None


class RequeteAccessPermission(BasePermission):
    """Contrôle l'accès aux requêtes selon rôle et rattachements."""

    def has_object_permission(self, request, view, obj: Requete) -> bool:
        role = _get_role(request.user)
        if role is None:
            return False
        if role == "admin":
            return True
        if role == "pole_manager":
            return obj.pole.membres.filter(id=request.user.id).exists() or obj.pole.chef_de_pole_id == request.user.id
        if role == "delegate":
            return obj.delegue_syndical and obj.delegue_syndical.user_id == request.user.id
        if role == "member":
            return obj.travailleur_id == request.user.id
        return False


class DossierAccessPermission(BasePermission):
    """Contrôle l'accès aux dossiers selon rôle et rattachements."""

    def has_object_permission(self, request, view, obj: Dossier) -> bool:
        role = _get_role(request.user)
        if role is None:
            return False
        if role == "admin":
            return True
        if role == "pole_manager":
            return obj.pole.membres.filter(id=request.user.id).exists() or obj.pole.chef_de_pole_id == request.user.id
        if role == "delegate":
            return obj.requetes.filter(delegue_syndical__user_id=request.user.id).exists()
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
