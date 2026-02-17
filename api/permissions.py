from __future__ import annotations

from typing import Any

from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import BasePermission, SAFE_METHODS

from requetes.models import DelegueSyndical, PoleMembre, ProfilUtilisateur, Requete, Dossier


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
        if role in ["pole_manager", "head", "assistant"]:
            return obj.pole.membres.filter(id=request.user.id).exists() or obj.pole.chef_de_pole_id == request.user.id
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
            if obj.travailleur_id == request.user.id:
                return True
            return obj.pole.membres.filter(id=request.user.id).exists()
        return False


class DossierAccessPermission(BasePermission):
    """Contrôle l'accès aux dossiers selon rôle et rattachements."""

    def has_object_permission(self, request, view, obj: Dossier) -> bool:
        role = _get_role(request.user)
        if role is None:
            return False
        if role == "admin":
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
            if obj.requetes.filter(travailleur_id=request.user.id).exists():
                return True
            return obj.pole.membres.filter(id=request.user.id).exists()
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
