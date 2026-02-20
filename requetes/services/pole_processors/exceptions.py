"""
Exceptions pour les processeurs de pôle.
Séparation claire des erreurs métier (validation, action non autorisée, etc.).
"""
from __future__ import annotations


class PoleProcessorError(Exception):
    """Erreur générique du processeur de pôle."""

    def __init__(self, message: str, code: str | None = None) -> None:
        self.message = message
        self.code = code or "pole_processor_error"
        super().__init__(self.message)


class PoleProcessorValidationError(PoleProcessorError):
    """Données invalides pour l'action demandée."""

    def __init__(self, message: str, errors: dict | None = None) -> None:
        super().__init__(message, code="validation_error")
        self.errors = errors or {}


class PoleProcessorActionNotAllowedError(PoleProcessorError):
    """Action non disponible pour ce pôle ou cette requête."""

    def __init__(self, message: str, action_id: str | None = None) -> None:
        super().__init__(message, code="action_not_allowed")
        self.action_id = action_id


class PoleProcessorTransitionNotAllowedError(PoleProcessorError):
    """Transition de statut non autorisée."""

    def __init__(
        self,
        message: str,
        from_status: str | None = None,
        to_status: str | None = None,
    ) -> None:
        super().__init__(message, code="transition_not_allowed")
        self.from_status = from_status
        self.to_status = to_status


class PoleProcessorNotFoundError(PoleProcessorError):
    """Aucun processeur enregistré pour ce pôle."""

    def __init__(self, message: str, pole_code: str | None = None) -> None:
        super().__init__(message, code="processor_not_found")
        self.pole_code = pole_code
