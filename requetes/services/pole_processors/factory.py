"""
Factory : retourne le processeur adapté à un pôle.
Évite tout if/elif sur le nom du pôle ; utilise Pole.code.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from .communication import CommunicationPoleProcessor
from .exceptions import PoleProcessorNotFoundError
from .generic import GenericPoleProcessor
from .health import HealthPoleProcessor
from .legal import LegalPoleProcessor
from .mediation import MediationPoleProcessor
from .training import TrainingPoleProcessor

if TYPE_CHECKING:
    from requetes.models import Pole

from .base import BasePoleProcessor

# Registry : code (Pole.code) -> classe processeur
_REGISTRY: dict[str, type[BasePoleProcessor]] = {
    LegalPoleProcessor.code: LegalPoleProcessor,
    HealthPoleProcessor.code: HealthPoleProcessor,
    MediationPoleProcessor.code: MediationPoleProcessor,
    TrainingPoleProcessor.code: TrainingPoleProcessor,
    CommunicationPoleProcessor.code: CommunicationPoleProcessor,
    GenericPoleProcessor.code: GenericPoleProcessor,
}


def get_pole_processor(pole: "Pole") -> BasePoleProcessor:
    """
    Retourne le processeur métier associé au pôle.
    Utilise pole.code ; si vide ou inconnu, retourne GenericPoleProcessor.
    """
    code = (pole.code or "").strip().lower() or "generic"
    processor_class = _REGISTRY.get(code)
    if processor_class is None:
        raise PoleProcessorNotFoundError(
            f"Aucun processeur enregistré pour le code '{code}'.",
            pole_code=code,
        )
    return processor_class(pole)


def register_pole_processor(code: str, processor_class: type[BasePoleProcessor]) -> None:
    """Enregistre un processeur pour un code (extension / tests)."""
    _REGISTRY[code] = processor_class


def get_registered_codes() -> list[str]:
    """Retourne la liste des codes de processeurs enregistrés."""
    return list(_REGISTRY.keys())
