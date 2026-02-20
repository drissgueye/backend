"""
Processeur Pôle Santé : enquête, visite, recommandation.
"""
from __future__ import annotations

from django.db import transaction

from requetes.models import ActionHistorique, HistoriqueAction, Requete

from .base import BasePoleProcessor
from .types import ActionDefinition, ActionResult


class HealthPoleProcessor(BasePoleProcessor):
    code = "health"

    def get_action_definitions(self) -> list[ActionDefinition]:
        return [
            ActionDefinition(
                id="request_info",
                label="Demander des informations",
                required_fields=("message",),
                allowed_statuses=("new", "processing", "info_needed"),
            ),
            ActionDefinition(
                id="launch_investigation",
                label="Lancer une enquête",
                description="Démarrer une enquête santé / sécurité.",
                required_fields=("scope",),
                optional_fields=("deadline", "assignee_id"),
                allowed_statuses=("new", "info_needed", "processing"),
            ),
            ActionDefinition(
                id="schedule_visit",
                label="Planifier une visite",
                description="Planifier une visite sur site ou un entretien.",
                required_fields=("visit_date", "visit_type"),
                optional_fields=("location", "notes"),
                allowed_statuses=("processing", "info_needed"),
            ),
            ActionDefinition(
                id="emit_recommendation",
                label="Émettre une recommandation",
                description="Rédiger une recommandation officielle.",
                required_fields=("recommendation_text",),
                optional_fields=("priority", "deadline_response"),
                allowed_statuses=("processing", "hr_escalated", "hr_pending"),
            ),
            ActionDefinition(
                id="change_status",
                label="Changer le statut",
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

    def execute_launch_investigation(
        self,
        requete: Requete,
        *,
        user=None,
        scope: str = "",
        deadline: str = "",
        assignee_id: str = "",
        **kwargs,
    ) -> ActionResult:
        self._validate_required_fields(
            {"scope": scope}, "launch_investigation", ("scope",)
        )
        if user:
            HistoriqueAction.enregistrer_action(
                content_object=requete,
                utilisateur=user,
                action=ActionHistorique.MODIFICATION_STATUT,
                commentaire=f"Enquête lancée : {scope}",
            )
        return ActionResult.ok("Enquête lancée.", scope=scope)

    def execute_schedule_visit(
        self,
        requete: Requete,
        *,
        user=None,
        visit_date: str = "",
        visit_type: str = "",
        location: str = "",
        notes: str = "",
        **kwargs,
    ) -> ActionResult:
        self._validate_required_fields(
            {"visit_date": visit_date, "visit_type": visit_type},
            "schedule_visit",
            ("visit_date", "visit_type"),
        )
        if user:
            HistoriqueAction.enregistrer_action(
                content_object=requete,
                utilisateur=user,
                action=ActionHistorique.REUNION_PLANIFIEE,
                commentaire=f"Visite planifiée : {visit_type} le {visit_date}",
            )
        return ActionResult.ok("Visite planifiée.", visit_date=visit_date)

    def execute_emit_recommendation(
        self,
        requete: Requete,
        *,
        user=None,
        recommendation_text: str = "",
        priority: str = "",
        deadline_response: str = "",
        **kwargs,
    ) -> ActionResult:
        self._validate_required_fields(
            {"recommendation_text": recommendation_text},
            "emit_recommendation",
            ("recommendation_text",),
        )
        if user:
            HistoriqueAction.enregistrer_action(
                content_object=requete,
                utilisateur=user,
                action=ActionHistorique.MODIFICATION_STATUT,
                commentaire="Recommandation émise.",
            )
        return ActionResult.ok("Recommandation enregistrée.")
