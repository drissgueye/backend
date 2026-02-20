"""
Types et structures de données pour les processeurs de pôle.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ActionDefinition:
    """
    Définition d'une action disponible pour un pôle.
    Utilisée pour exposer les actions possibles au frontend ou aux API.
    """

    id: str
    label: str
    description: str = ""
    required_fields: tuple[str, ...] = ()
    optional_fields: tuple[str, ...] = ()
    allowed_statuses: tuple[str, ...] = ()  # vide = tous
    """Statuts de requête pour lesquels l'action est proposée."""


@dataclass
class ActionResult:
    """
    Résultat d'une exécution d'action (succès ou échec explicite).
    """

    success: bool
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    errors: dict[str, list[str]] = field(default_factory=dict)

    @classmethod
    def ok(cls, message: str = "", **data: Any) -> "ActionResult":
        return cls(success=True, message=message, data=dict(data))

    @classmethod
    def fail(cls, message: str, errors: dict | None = None) -> "ActionResult":
        return cls(
            success=False,
            message=message,
            errors=dict(errors) if errors else {},
        )


@dataclass
class TransitionCheck:
    """Résultat de la validation d'une transition de statut."""

    allowed: bool
    message: str = ""
    suggested_actions: tuple[str, ...] = ()
