"""
Validation des valeurs extra_data (champs personnalisés) pour une ActiviteRequete
créée à partir d'un ActiviteTemplate.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Any

from rest_framework import serializers

from requetes.models import TypeChampActivite

if TYPE_CHECKING:
    from requetes.models import ActiviteTemplate


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def _valid_value_for_type(value: Any, type_champ: str, options: list) -> tuple[bool, str | None]:
    """
    Vérifie que value est acceptable pour le type_champ.
    Retourne (ok, message_erreur).
    """
    if _is_empty(value):
        return True, None  # required est géré ailleurs

    if type_champ == TypeChampActivite.TEXT or type_champ == TypeChampActivite.TEXTAREA:
        if not isinstance(value, str):
            return False, "Doit être un texte."
        return True, None

    if type_champ == TypeChampActivite.NUMBER:
        if isinstance(value, bool):
            return False, "Doit être un nombre."
        if isinstance(value, (int, float)):
            return True, None
        if isinstance(value, str):
            try:
                float(value)
                return True, None
            except ValueError:
                pass
        return False, "Doit être un nombre."

    if type_champ == TypeChampActivite.DATE:
        if isinstance(value, str):
            # Accepter YYYY-MM-DD
            if len(value) >= 10 and value[4] == "-" and value[7] == "-":
                try:
                    datetime.strptime(value[:10], "%Y-%m-%d")
                    return True, None
                except ValueError:
                    pass
        if isinstance(value, date):
            return True, None
        return False, "Doit être une date (format AAAA-MM-JJ)."

    if type_champ == TypeChampActivite.DATETIME:
        if isinstance(value, str):
            try:
                datetime.fromisoformat(value.replace("Z", "+00:00"))
                return True, None
            except (ValueError, TypeError):
                pass
        if isinstance(value, datetime):
            return True, None
        return False, "Doit être une date/heure (ISO 8601)."

    if type_champ == TypeChampActivite.BOOLEAN:
        if isinstance(value, bool):
            return True, None
        if value in ("true", "false", "1", "0", 1, 0):
            return True, None
        return False, "Doit être vrai ou faux."

    if type_champ == TypeChampActivite.FILE:
        # En API on reçoit souvent une URL ou un chemin après upload ; accepter chaîne.
        if isinstance(value, str):
            return True, None
        return False, "Doit être une référence fichier (chaîne)."

    if type_champ == TypeChampActivite.CHOICE:
        if not options:
            return True, None
        allowed = [opt.get("value") for opt in options if isinstance(opt, dict) and "value" in opt]
        if not allowed:
            return True, None
        if value in allowed:
            return True, None
        return False, f"Valeur non autorisée. Attendues : {allowed}."

    return True, None


def validate_extra_data_for_template(
    extra_data: dict[str, Any],
    template: ActiviteTemplate,
) -> None:
    """
    Valide extra_data par rapport aux champs actifs du template.
    Lève serializers.ValidationError en cas d'erreur.
    """
    if not isinstance(extra_data, dict):
        raise serializers.ValidationError({"extra_data": "Doit être un objet (clé-valeur)."})

    champs = template.champs.filter(is_active=True).order_by("ordre", "nom")
    errors: dict[str, list[str]] = {}

    for champ in champs:
        key = champ.nom
        value = extra_data.get(key)
        if champ.required and _is_empty(value):
            errors.setdefault("extra_data", []).append(
                f"Le champ « {champ.label} » ({key}) est obligatoire."
            )
            continue
        if _is_empty(value):
            continue
        ok, msg = _valid_value_for_type(value, champ.type_champ, champ.options or [])
        if not ok and msg:
            errors.setdefault("extra_data", []).append(f"{champ.label} ({key}) : {msg}")

    if errors:
        raise serializers.ValidationError(errors)
