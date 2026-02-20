"""
Processeurs métier par pôle (Strategy Pattern).
Chaque pôle dispose d'une logique spécifique sans if/elif sur le nom.
"""
from __future__ import annotations

from .base import BasePoleProcessor
from .exceptions import (
    PoleProcessorActionNotAllowedError,
    PoleProcessorError,
    PoleProcessorNotFoundError,
    PoleProcessorTransitionNotAllowedError,
    PoleProcessorValidationError,
)
from .factory import get_pole_processor, get_registered_codes, register_pole_processor
from .types import ActionDefinition, ActionResult, TransitionCheck

__all__ = [
    "BasePoleProcessor",
    "get_pole_processor",
    "register_pole_processor",
    "get_registered_codes",
    "ActionDefinition",
    "ActionResult",
    "TransitionCheck",
    "PoleProcessorError",
    "PoleProcessorValidationError",
    "PoleProcessorActionNotAllowedError",
    "PoleProcessorTransitionNotAllowedError",
    "PoleProcessorNotFoundError",
]
