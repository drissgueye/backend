"""
Processeur Pôle Formation : plan de formation, suivi d'évolution.
"""
from __future__ import annotations

from requetes.models import ActionHistorique, HistoriqueAction, Requete

from .base import BasePoleProcessor
from .types import ActionDefinition, ActionResult


class TrainingPoleProcessor(BasePoleProcessor):
    code = "training"

    def get_action_definitions(self) -> list[ActionDefinition]:
        return [
            ActionDefinition(
                id="request_info",
                label="Demander des informations",
                required_fields=("message",),
                allowed_statuses=("new", "processing", "info_needed"),
            ),
            ActionDefinition(
                id="propose_training_plan",
                label="Proposer un plan de formation",
                description="Élaborer et enregistrer un plan de formation.",
                required_fields=("plan_summary",),
                optional_fields=("modules", "deadline", "budget_notes"),
                allowed_statuses=("new", "info_needed", "processing"),
            ),
            ActionDefinition(
                id="update_progress",
                label="Suivre l'évolution",
                description="Mettre à jour l'avancement du suivi formation.",
                required_fields=("progress_notes",),
                optional_fields=("completion_percent", "next_steps"),
                allowed_statuses=("processing", "hr_pending"),
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

    def execute_propose_training_plan(
        self,
        requete: Requete,
        *,
        user=None,
        plan_summary: str = "",
        modules: str = "",
        deadline: str = "",
        budget_notes: str = "",
        **kwargs,
    ) -> ActionResult:
        self._validate_required_fields(
            {"plan_summary": plan_summary},
            "propose_training_plan",
            ("plan_summary",),
        )
        if user:
            HistoriqueAction.enregistrer_action(
                content_object=requete,
                utilisateur=user,
                action=ActionHistorique.MODIFICATION_STATUT,
                commentaire=f"Plan de formation proposé : {plan_summary[:100]}",
            )
        return ActionResult.ok("Plan de formation enregistré.")

    def execute_update_progress(
        self,
        requete: Requete,
        *,
        user=None,
        progress_notes: str = "",
        completion_percent: str = "",
        next_steps: str = "",
        **kwargs,
    ) -> ActionResult:
        self._validate_required_fields(
            {"progress_notes": progress_notes},
            "update_progress",
            ("progress_notes",),
        )
        if user:
            HistoriqueAction.enregistrer_action(
                content_object=requete,
                utilisateur=user,
                action=ActionHistorique.MODIFICATION_STATUT,
                commentaire="Suivi formation mis à jour.",
            )
        return ActionResult.ok("Évolution enregistrée.")
