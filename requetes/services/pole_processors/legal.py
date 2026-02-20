"""
Processeur Pôle Juridique : avocat, dossier judiciaire, procédure.
"""
from __future__ import annotations

from django.db import transaction

from requetes.models import (
    ActionHistorique,
    HistoriqueAction,
    Requete,
)

from .base import BasePoleProcessor
from .types import ActionDefinition, ActionResult


class LegalPoleProcessor(BasePoleProcessor):
    code = "legal"

    def get_action_definitions(self) -> list[ActionDefinition]:
        base = [
            ActionDefinition(
                id="request_info",
                label="Demander des informations",
                description="Demande d'éléments complémentaires au travailleur.",
                required_fields=("message",),
                allowed_statuses=("new", "processing", "info_needed"),
            ),
            ActionDefinition(
                id="assign_lawyer",
                label="Assigner un avocat",
                description="Désigner l'avocat en charge du dossier.",
                required_fields=("lawyer_name", "lawyer_contact"),
                optional_fields=("notes",),
                allowed_statuses=("new", "info_needed", "processing"),
            ),
            ActionDefinition(
                id="open_legal_file",
                label="Ouvrir un dossier judiciaire",
                description="Créer le suivi procédure (référence, tribunal).",
                required_fields=("court_reference",),
                optional_fields=("court_name", "expected_date"),
                allowed_statuses=("processing", "hr_escalated"),
            ),
            ActionDefinition(
                id="update_procedure",
                label="Mettre à jour la procédure",
                description="Enregistrer une étape procédurale.",
                required_fields=("step_description",),
                optional_fields=("step_date", "documents"),
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
        return base

    def execute_assign_lawyer(
        self,
        requete: Requete,
        *,
        user=None,
        lawyer_name: str = "",
        lawyer_contact: str = "",
        notes: str = "",
        **kwargs,
    ) -> ActionResult:
        self._validate_required_fields(
            {"lawyer_name": lawyer_name, "lawyer_contact": lawyer_contact},
            "assign_lawyer",
            ("lawyer_name", "lawyer_contact"),
        )
        with transaction.atomic():
            if user:
                HistoriqueAction.enregistrer_action(
                    content_object=requete,
                    utilisateur=user,
                    action=ActionHistorique.ASSIGNATION,
                    commentaire=f"Avocat assigné : {lawyer_name}",
                )
        return ActionResult.ok(
            f"Avocat {lawyer_name} assigné au dossier.",
            lawyer_name=lawyer_name,
        )

    def execute_open_legal_file(
        self,
        requete: Requete,
        *,
        user=None,
        court_reference: str = "",
        court_name: str = "",
        expected_date: str = "",
        **kwargs,
    ) -> ActionResult:
        self._validate_required_fields(
            {"court_reference": court_reference},
            "open_legal_file",
            ("court_reference",),
        )
        with transaction.atomic():
            if user:
                HistoriqueAction.enregistrer_action(
                    content_object=requete,
                    utilisateur=user,
                    action=ActionHistorique.MODIFICATION_STATUT,
                    commentaire=f"Dossier judiciaire ouvert : {court_reference}",
                )
        return ActionResult.ok(
            "Dossier judiciaire ouvert.",
            court_reference=court_reference,
        )

    def execute_update_procedure(
        self,
        requete: Requete,
        *,
        user=None,
        step_description: str = "",
        step_date: str = "",
        documents: str = "",
        **kwargs,
    ) -> ActionResult:
        self._validate_required_fields(
            {"step_description": step_description},
            "update_procedure",
            ("step_description",),
        )
        if user:
            HistoriqueAction.enregistrer_action(
                content_object=requete,
                utilisateur=user,
                action=ActionHistorique.MODIFICATION_STATUT,
                commentaire=step_description,
            )
        return ActionResult.ok("Procédure mise à jour.")
