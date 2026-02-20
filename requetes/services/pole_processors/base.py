"""
Classe abstraite de base pour les processeurs métier par pôle.
Chaque pôle dispose d'une logique spécifique sans if/elif sur le nom.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from .exceptions import (
    PoleProcessorActionNotAllowedError,
    PoleProcessorValidationError,
)
from .types import ActionDefinition, ActionResult, TransitionCheck

if TYPE_CHECKING:
    from django.contrib.auth import get_user_model

    from requetes.models import Pole, Requete

    User = get_user_model()


class BasePoleProcessor(ABC):
    """
    Processeur métier pour un type de pôle.
    Sous-classes : LegalProcessor, HealthProcessor, MediationProcessor, etc.
    """

    code: str = "generic"
    """Identifiant du processeur (doit correspondre à Pole.code)."""

    def __init__(self, pole: "Pole") -> None:
        self.pole = pole

    # -------------------------------------------------------------------------
    # Actions disponibles
    # -------------------------------------------------------------------------

    def get_available_actions(self, requete: "Requete") -> list[ActionDefinition]:
        """
        Retourne les actions proposées pour cette requête.
        Peut dépendre du statut, du pôle, de la configuration (ex. PoleWorkflow).
        """
        base = self.get_action_definitions()
        status = requete.statut
        return [
            a
            for a in base
            if not a.allowed_statuses or status in a.allowed_statuses
        ]

    @abstractmethod
    def get_action_definitions(self) -> list[ActionDefinition]:
        """Définit la liste des actions offertes par ce processeur."""
        ...

    def is_action_available(self, requete: "Requete", action_id: str) -> bool:
        """Vérifie si une action est disponible pour cette requête."""
        return any(
            a.id == action_id for a in self.get_available_actions(requete)
        )

    # -------------------------------------------------------------------------
    # Exécution d'action
    # -------------------------------------------------------------------------

    def execute_action(
        self,
        requete: "Requete",
        action_id: str,
        *,
        user: "User | None" = None,
        **kwargs: Any,
    ) -> ActionResult:
        """
        Exécute une action métier sur la requête.
        Délegue à des méthodes spécifiques (execute_<action_id>) ou à handle_action.
        """
        if not self.is_action_available(requete, action_id):
            raise PoleProcessorActionNotAllowedError(
                f"L'action '{action_id}' n'est pas disponible pour cette requête.",
                action_id=action_id,
            )
        handler = getattr(
            self,
            f"execute_{action_id}",
            None,
        )
        if callable(handler):
            result = handler(requete, user=user, **kwargs)
        else:
            result = self.handle_action(requete, action_id, user=user, **kwargs)
        if not isinstance(result, ActionResult):
            return ActionResult.ok(str(result))
        return result

    def execute_request_info(
        self,
        requete: "Requete",
        *,
        user: "User | None" = None,
        message: str = "",
        **kwargs: Any,
    ) -> ActionResult:
        """
        Demande d'informations complémentaires au travailleur.
        Enregistre un message sur la requête, met à jour le statut si besoin, et trace l'action.
        """
        from requetes.models import (
            ActionHistorique,
            HistoriqueAction,
            RequeteMessage,
            StatutRequete,
        )

        if not (message and message.strip()):
            return ActionResult.fail(
                "Le message de la demande d'information est requis.",
                errors={"message": ["Ce champ est obligatoire."]},
            )
        if not user:
            return ActionResult.fail("Utilisateur requis pour enregistrer la demande.")

        RequeteMessage.objects.create(
            requete=requete,
            utilisateur=user,
            contenu=message.strip(),
            is_interne=False,
        )
        ancien_statut = requete.statut
        if requete.statut != StatutRequete.INFO_NEEDED:
            transition = self.validate_transition(requete, StatutRequete.INFO_NEEDED)
            if transition.allowed:
                requete.statut = StatutRequete.INFO_NEEDED
                requete.save(update_fields=["statut", "updated_at"])
                HistoriqueAction.enregistrer_action(
                    content_object=requete,
                    utilisateur=user,
                    action=ActionHistorique.MODIFICATION_STATUT,
                    ancienne_valeur=ancien_statut,
                    nouvelle_valeur=StatutRequete.INFO_NEEDED,
                    commentaire=message.strip()[:500],
                )
            else:
                HistoriqueAction.enregistrer_action(
                    content_object=requete,
                    utilisateur=user,
                    action=ActionHistorique.AJOUT_COMMENTAIRE,
                    commentaire=message.strip()[:500],
                )
        else:
            HistoriqueAction.enregistrer_action(
                content_object=requete,
                utilisateur=user,
                action=ActionHistorique.AJOUT_COMMENTAIRE,
                commentaire=message.strip()[:500],
            )
        return ActionResult.ok(
            "Demande d'information enregistrée. Le travailleur sera notifié."
        )

    def execute_change_status(
        self,
        requete: "Requete",
        *,
        user: "User | None" = None,
        new_status: str = "",
        **kwargs: Any,
    ) -> ActionResult:
        """Change le statut de la requête après validation de la transition."""
        from requetes.models import (
            ActionHistorique,
            HistoriqueAction,
            Notification,
            StatutRequete,
        )

        if not (new_status and new_status.strip()):
            return ActionResult.fail(
                "Le nouveau statut est requis.",
                errors={"new_status": ["Ce champ est obligatoire."]},
            )
        new_status = new_status.strip()
        transition = self.validate_transition(requete, new_status)
        if not transition.allowed:
            return ActionResult.fail(transition.message or "Transition non autorisée.")
        if not user:
            return ActionResult.fail("Utilisateur requis.")

        ancien_statut = requete.statut
        requete.statut = new_status
        requete.save(update_fields=["statut", "updated_at"])
        HistoriqueAction.enregistrer_action(
            content_object=requete,
            utilisateur=user,
            action=ActionHistorique.MODIFICATION_STATUT,
            champ_modifie="statut",
            ancienne_valeur=ancien_statut,
            nouvelle_valeur=new_status,
        )
        Notification.objects.create(
            utilisateur=requete.travailleur,
            titre="Mise à jour de requête",
            message=f"Statut mis à jour : {requete.get_statut_display()}",
            type_notification="ticket_update",
            requete=requete,
        )
        return ActionResult.ok(
            f"Statut mis à jour : {requete.get_statut_display()}."
        )

    def execute_assign(
        self,
        requete: "Requete",
        *,
        user: "User | None" = None,
        assignee_id: str = "",
        **kwargs: Any,
    ) -> ActionResult:
        """Assigne la requête à un responsable (membre du pôle). Trace dans l'historique."""
        from django.contrib.auth import get_user_model
        from requetes.models import (
            ActionHistorique,
            HistoriqueAction,
            PoleMembre,
            PoleMembership,
        )

        if not (assignee_id and str(assignee_id).strip()):
            return ActionResult.fail(
                "Veuillez sélectionner un responsable.",
                errors={"assignee_id": ["Ce champ est obligatoire."]},
            )
        try:
            uid = int(str(assignee_id).strip())
        except (TypeError, ValueError):
            return ActionResult.fail(
                "Identifiant du responsable invalide.",
                errors={"assignee_id": ["Valeur invalide."]},
            )
        User = get_user_model()
        try:
            assignee = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return ActionResult.fail(
                "Utilisateur introuvable.",
                errors={"assignee_id": ["Ce responsable n'existe pas."]},
            )
        is_member = (
            PoleMembership.objects.filter(user=assignee, pole=self.pole).exists()
            or PoleMembre.objects.filter(user=assignee, pole=self.pole).exists()
            or self.pole.chef_de_pole_id == assignee.pk
        )
        if not is_member:
            return ActionResult.fail(
                "Le responsable doit être membre du pôle assigné.",
                errors={"assignee_id": ["Personne non membre de ce pôle."]},
            )
        if not user:
            return ActionResult.fail("Utilisateur requis.")

        display_name = (
            getattr(assignee, "get_full_name", lambda: "")()
            or getattr(assignee, "username", "")
            or str(assignee.pk)
        )
        if not display_name.strip():
            display_name = f"Utilisateur #{assignee.pk}"
        HistoriqueAction.enregistrer_action(
            content_object=requete,
            utilisateur=user,
            action=ActionHistorique.ASSIGNATION,
            commentaire=f"Assigné à : {display_name}",
        )
        return ActionResult.ok(f"Requête assignée à {display_name}.")

    def handle_action(
        self,
        requete: "Requete",
        action_id: str,
        *,
        user: "User | None" = None,
        **kwargs: Any,
    ) -> ActionResult:
        """
        Gestion par défaut des actions non surchargées.
        Les sous-classes peuvent surcharger pour des actions custom.
        """
        return ActionResult.fail(
            f"Action '{action_id}' non implémentée pour le processeur {self.code}."
        )

    # -------------------------------------------------------------------------
    # Transitions de statut (optionnel : PoleWorkflow en base)
    # -------------------------------------------------------------------------

    def validate_transition(
        self, requete: "Requete", new_status: str
    ) -> TransitionCheck:
        """
        Indique si le passage au nouveau statut est autorisé pour ce pôle.
        Si PoleWorkflow est renseigné pour ce pôle, seules ces transitions sont autorisées.
        """
        from requetes.models import PoleWorkflow, StatutRequete

        if new_status not in list(StatutRequete.values):
            return TransitionCheck(
                allowed=False,
                message=f"Statut invalide : {new_status}.",
            )
        # Config dynamique en base
        configured = PoleWorkflow.objects.filter(
            pole=self.pole,
            from_status=requete.statut,
            to_status=new_status,
            is_active=True,
        ).exists()
        if configured:
            return TransitionCheck(allowed=True)
        # Pas de config : on autorise par défaut (comportement processeur)
        allowed_list = self.get_allowed_transitions(requete)
        if allowed_list and new_status not in allowed_list:
            return TransitionCheck(
                allowed=False,
                message=f"Transition {requete.statut} → {new_status} non prévue pour ce pôle.",
            )
        return TransitionCheck(allowed=True)

    def get_allowed_transitions(self, requete: "Requete") -> list[str]:
        """
        Liste des statuts vers lesquels on peut faire évoluer la requête.
        Si PoleWorkflow est renseigné, on retourne uniquement les to_status configurés.
        """
        from requetes.models import PoleWorkflow, StatutRequete

        qs = PoleWorkflow.objects.filter(
            pole=self.pole,
            from_status=requete.statut,
            is_active=True,
        ).order_by("ordre").values_list("to_status", flat=True)
        configured = list(qs)
        if configured:
            return list(configured)
        return list(StatutRequete.values)

    # -------------------------------------------------------------------------
    # Utilitaires
    # -------------------------------------------------------------------------

    def _validate_required_fields(
        self, data: dict, action_id: str, required: tuple[str, ...]
    ) -> None:
        """Lève PoleProcessorValidationError si des champs requis manquent."""
        missing = [f for f in required if not data.get(f)]
        if missing:
            raise PoleProcessorValidationError(
                f"Champs requis manquants pour l'action {action_id} : {', '.join(missing)}.",
                errors={f: ["Requis."] for f in missing},
            )
