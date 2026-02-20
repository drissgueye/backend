"""
Processeur Pôle Communication : campagne, publication d'action.
"""
from __future__ import annotations

from requetes.models import ActionHistorique, HistoriqueAction, Requete

from .base import BasePoleProcessor
from .types import ActionDefinition, ActionResult


class CommunicationPoleProcessor(BasePoleProcessor):
    code = "communication"

    def get_action_definitions(self) -> list[ActionDefinition]:
        return [
            ActionDefinition(
                id="request_info",
                label="Demander des informations",
                required_fields=("message",),
                allowed_statuses=("new", "processing", "info_needed"),
            ),
            ActionDefinition(
                id="launch_campaign",
                label="Lancer une campagne",
                description="Démarrer une campagne de communication.",
                required_fields=("campaign_name", "channel"),
                optional_fields=("target_audience", "start_date", "end_date"),
                allowed_statuses=("new", "info_needed", "processing"),
            ),
            ActionDefinition(
                id="publish_action",
                label="Publier une action",
                description="Publier une action de communication (article, communiqué).",
                required_fields=("title", "content"),
                optional_fields=("visibility", "publish_date"),
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

    def execute_launch_campaign(
        self,
        requete: Requete,
        *,
        user=None,
        campaign_name: str = "",
        channel: str = "",
        target_audience: str = "",
        start_date: str = "",
        end_date: str = "",
        **kwargs,
    ) -> ActionResult:
        self._validate_required_fields(
            {"campaign_name": campaign_name, "channel": channel},
            "launch_campaign",
            ("campaign_name", "channel"),
        )
        if user:
            HistoriqueAction.enregistrer_action(
                content_object=requete,
                utilisateur=user,
                action=ActionHistorique.MODIFICATION_STATUT,
                commentaire=f"Campagne lancée : {campaign_name}",
            )
        return ActionResult.ok("Campagne lancée.", campaign_name=campaign_name)

    def execute_publish_action(
        self,
        requete: Requete,
        *,
        user=None,
        title: str = "",
        content: str = "",
        visibility: str = "",
        publish_date: str = "",
        **kwargs,
    ) -> ActionResult:
        self._validate_required_fields(
            {"title": title, "content": content},
            "publish_action",
            ("title", "content"),
        )
        if user:
            HistoriqueAction.enregistrer_action(
                content_object=requete,
                utilisateur=user,
                action=ActionHistorique.MODIFICATION_STATUT,
                commentaire=f"Action publiée : {title}",
            )
        return ActionResult.ok("Action publiée.")
