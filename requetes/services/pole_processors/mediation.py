"""
Processeur Pôle Dialogue Social et Médiation : réunion, convocation RH, rapport.
"""
from __future__ import annotations

from requetes.models import ActionHistorique, HistoriqueAction, Requete

from .base import BasePoleProcessor
from .types import ActionDefinition, ActionResult


class MediationPoleProcessor(BasePoleProcessor):
    code = "mediation"

    def get_action_definitions(self) -> list[ActionDefinition]:
        return [
            ActionDefinition(
                id="request_info",
                label="Demander des informations",
                required_fields=("message",),
                allowed_statuses=("new", "processing", "info_needed"),
            ),
            ActionDefinition(
                id="schedule_meeting",
                label="Planifier une réunion",
                description="Planifier une réunion de médiation.",
                required_fields=("meeting_date", "meeting_type"),
                optional_fields=("location", "participants", "agenda"),
                allowed_statuses=("new", "info_needed", "processing"),
            ),
            ActionDefinition(
                id="convoke_hr",
                label="Convoquer les RH",
                description="Convoquer les RH pour une réunion.",
                required_fields=("convocation_date", "subject"),
                optional_fields=("message",),
                allowed_statuses=("processing", "hr_pending"),
            ),
            ActionDefinition(
                id="produce_mediation_report",
                label="Produire un rapport de médiation",
                description="Rédiger le compte rendu de médiation.",
                required_fields=("report_content",),
                optional_fields=("conclusions", "next_steps"),
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

    def execute_schedule_meeting(
        self,
        requete: Requete,
        *,
        user=None,
        meeting_date: str = "",
        meeting_type: str = "",
        location: str = "",
        participants: str = "",
        agenda: str = "",
        **kwargs,
    ) -> ActionResult:
        self._validate_required_fields(
            {"meeting_date": meeting_date, "meeting_type": meeting_type},
            "schedule_meeting",
            ("meeting_date", "meeting_type"),
        )
        if user:
            HistoriqueAction.enregistrer_action(
                content_object=requete,
                utilisateur=user,
                action=ActionHistorique.REUNION_PLANIFIEE,
                commentaire=f"Réunion planifiée : {meeting_type} le {meeting_date}",
            )
        return ActionResult.ok(
            "Réunion planifiée.",
            meeting_date=meeting_date,
        )

    def execute_convoke_hr(
        self,
        requete: Requete,
        *,
        user=None,
        convocation_date: str = "",
        subject: str = "",
        message: str = "",
        **kwargs,
    ) -> ActionResult:
        self._validate_required_fields(
            {"convocation_date": convocation_date, "subject": subject},
            "convoke_hr",
            ("convocation_date", "subject"),
        )
        if user:
            HistoriqueAction.enregistrer_action(
                content_object=requete,
                utilisateur=user,
                action=ActionHistorique.MODIFICATION_STATUT,
                commentaire=f"RH convoqués : {subject}",
            )
        return ActionResult.ok("Convocation enregistrée.")

    def execute_produce_mediation_report(
        self,
        requete: Requete,
        *,
        user=None,
        report_content: str = "",
        conclusions: str = "",
        next_steps: str = "",
        **kwargs,
    ) -> ActionResult:
        self._validate_required_fields(
            {"report_content": report_content},
            "produce_mediation_report",
            ("report_content",),
        )
        if user:
            HistoriqueAction.enregistrer_action(
                content_object=requete,
                utilisateur=user,
                action=ActionHistorique.MODIFICATION_STATUT,
                commentaire="Rapport de médiation produit.",
            )
        return ActionResult.ok("Rapport de médiation enregistré.")
