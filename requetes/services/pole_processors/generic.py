"""
Processeur générique : actions communes à tous les pôles.
Utilisé quand Pole.code est vide ou "generic".
"""
from __future__ import annotations

from .base import BasePoleProcessor
from .types import ActionDefinition


class GenericPoleProcessor(BasePoleProcessor):
    code = "generic"

    def get_action_definitions(self) -> list[ActionDefinition]:
        return [
            ActionDefinition(
                id="request_info",
                label="Demander des informations",
                description="Enregistrer une demande d'info complémentaire.",
                required_fields=("message",),
                allowed_statuses=("new", "processing", "info_needed"),
            ),
            ActionDefinition(
                id="assign",
                label="Assigner à un responsable",
                description="Assigner la requête à un membre du pôle.",
                required_fields=("assignee_id",),
                allowed_statuses=("new", "info_needed", "processing"),
            ),
            ActionDefinition(
                id="change_status",
                label="Changer le statut",
                description="Faire évoluer le statut de la requête.",
                required_fields=("new_status",),
                allowed_statuses=(
                    "new",
                    "info_needed",
                    "processing",
                    "hr_escalated",
                    "hr_pending",
                    "resolved",
                ),
            ),
        ]
