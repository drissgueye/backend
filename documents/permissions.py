"""
Permissions pour la gestion des documents :
- Admin : accès global (tous les documents).
- Responsable de pôle : uniquement les documents de son/ses pôle(s).
"""
from __future__ import annotations

from typing import Any

from rest_framework.permissions import BasePermission

from requetes.models import Pole, PoleMembership


def _is_admin(user: Any) -> bool:
    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return True
    profil = getattr(user, "profil", None)
    if profil is not None:
        role = getattr(profil, "role", None)
        return role in ("admin", "super_admin")
    return False


def _pole_ids_manager(user: Any) -> list[int]:
    """IDs des pôles dont l'utilisateur est responsable (chef_de_pole ou is_manager)."""
    ids = list(
        PoleMembership.objects.filter(
            user=user, is_manager=True
        ).values_list("pole_id", flat=True)
    )
    ids += list(
        Pole.objects.filter(chef_de_pole=user).values_list("id", flat=True)
    )
    return list(set(ids))


class DocumentAccessPermission(BasePermission):
    """
    - Admin : accès à tout.
    - Responsable de pôle : accès uniquement aux documents dont document.pole_id
      est dans les pôles qu'il gère.
    - Autres : pas d'accès.
    """

    def has_permission(self, request, view) -> bool:
        if not getattr(request.user, "is_authenticated", False):
            return False
        return True

    def has_object_permission(self, request, view, obj) -> bool:
        if _is_admin(request.user):
            return True
        # Document lié à une requête dont je suis le travailleur
        requete = getattr(obj, "requete", None)
        if requete is not None and getattr(requete, "travailleur_id", None) == request.user.pk:
            return True
        pole_id = getattr(obj, "pole_id", None)
        if pole_id is None:
            return False
        return pole_id in _pole_ids_manager(request.user)
