"""
Crée en base les modèles d'activité (ActiviteTemplate + champs) à partir des types
définis dans activity_types_by_pole.py et les affecte aux pôles concernés.
À exécuter une fois après la migration activites_dynamiques pour que les activités
existantes des requêtes continuent d'exister dynamiquement (via la base) au lieu du dict Python.

Usage:
    python manage.py seed_activite_templates
"""
from __future__ import annotations

import json
from django.core.management.base import BaseCommand
from django.db import transaction

from requetes.activity_types_by_pole import (
    ACTIVITY_TYPES_BY_POLE,
    POLE_NOM_TO_CODE,
    get_pole_activity_code,
)
from requetes.models import (
    ActiviteTemplate,
    ChampActiviteTemplate,
    ActiviteTemplatePole,
    Pole,
    TypeChampActivite,
)


def _field_type_to_model(ft: str) -> str:
    """Mappe le type du dict (text, date, etc.) vers TypeChampActivite."""
    m = {
        "text": TypeChampActivite.TEXT,
        "textarea": TypeChampActivite.TEXTAREA,
        "number": TypeChampActivite.NUMBER,
        "date": TypeChampActivite.DATE,
        "datetime": TypeChampActivite.DATETIME,
    }
    return m.get(ft, TypeChampActivite.TEXT)


def _fields_signature(fields: list) -> str:
    """Signature pour dédupliquer les définitions de champs."""
    return json.dumps(
        [(f.get("name"), f.get("label"), f.get("type"), f.get("required")) for f in fields],
        sort_keys=True,
    )


class Command(BaseCommand):
    help = (
        "Crée les ActiviteTemplate (et champs) à partir de activity_types_by_pole.py "
        "et les affecte aux pôles concernés."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Affiche ce qui serait fait sans écrire en base.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Supprime toutes les affectations et les modèles créés par un précédent seed (avant de recréer).",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        clear = options["clear"]

        if dry_run:
            self.stdout.write("Mode dry-run : aucune modification en base.")

        # 1) Construire la liste des types uniques (code -> label, fields)
        #    On prend la première occurrence de chaque code pour label/fields.
        unique_by_code = {}
        for pole_code, types_list in ACTIVITY_TYPES_BY_POLE.items():
            for t in types_list:
                value = t.get("value") or ""
                if not value:
                    continue
                if value not in unique_by_code:
                    unique_by_code[value] = {
                        "label": t.get("label") or value,
                        "fields": list(t.get("fields") or []),
                    }

        self.stdout.write(f"Types d'activité uniques à créer : {len(unique_by_code)}")

        if clear and not dry_run:
            with transaction.atomic():
                ActiviteTemplatePole.objects.all().delete()
                for t in ActiviteTemplate.objects.all():
                    if t.code in unique_by_code:
                        t.delete()
            self.stdout.write("Anciens modèles/affectations supprimés.")

        # 2) Récupérer tous les pôles et leur code d'activité
        poles = list(Pole.objects.all())
        pole_code_to_poles = {}  # pole_code -> [Pole]
        for pole in poles:
            code = get_pole_activity_code(pole)
            pole_code_to_poles.setdefault(code, []).append(pole)
        # S'assurer que "generic" existe pour les pôles sans code dédié
        if "generic" not in pole_code_to_poles:
            pole_code_to_poles["generic"] = []

        # 3) Créer ou récupérer chaque ActiviteTemplate et ses champs
        created_templates = 0
        created_champs = 0
        created_affectations = 0

        def do_seed():
            nonlocal created_templates, created_champs, created_affectations
            for code, data in unique_by_code.items():
                label = data["label"]
                fields_def = data["fields"]

                if dry_run:
                    exists = ActiviteTemplate.objects.filter(code=code).exists()
                    if not exists:
                        created_templates += 1
                        self.stdout.write(f"  [dry-run] Créerait template : {code} ({label})")
                    for i, f in enumerate(fields_def):
                        name = (f.get("name") or "").strip() or f"field_{i}"
                        created_champs += 1
                    continue

                template, created = ActiviteTemplate.objects.get_or_create(
                    code=code,
                    defaults={
                        "nom": label,
                        "description": "",
                        "is_active": True,
                        "ordre": 0,
                    },
                )
                if created:
                    created_templates += 1
                    self.stdout.write(f"  Créé template : {code} ({label})")
                else:
                    if template.nom != label:
                        template.nom = label
                        template.save(update_fields=["nom"])

                existing_champ_names = set(
                    template.champs.values_list("nom", flat=True)
                )
                for i, f in enumerate(fields_def):
                    name = (f.get("name") or "").strip() or f"field_{i}"
                    if name in existing_champ_names:
                        continue
                    type_champ = _field_type_to_model(f.get("type") or "text")
                    ChampActiviteTemplate.objects.create(
                        activite_template=template,
                        nom=name[:80],
                        label=f.get("label") or name,
                        type_champ=type_champ,
                        required=bool(f.get("required")),
                        ordre=i,
                        options=[],
                        is_active=True,
                    )
                    created_champs += 1
                    existing_champ_names.add(name)

            if dry_run:
                for pole_code, types_list in ACTIVITY_TYPES_BY_POLE.items():
                    pole_list = pole_code_to_poles.get(pole_code, [])
                    for _ in types_list:
                        for _ in pole_list:
                            created_affectations += 1
                return

            # 4) Affecter chaque template aux pôles qui ont ce type dans leur liste
            for pole_code, types_list in ACTIVITY_TYPES_BY_POLE.items():
                pole_list = pole_code_to_poles.get(pole_code, [])
                for t in types_list:
                    value = t.get("value")
                    if not value:
                        continue
                    try:
                        template = ActiviteTemplate.objects.get(code=value)
                    except ActiviteTemplate.DoesNotExist:
                        continue
                    for pole in pole_list:
                        _, created = ActiviteTemplatePole.objects.get_or_create(
                            activite_template=template,
                            pole=pole,
                            defaults={"ordre": 0},
                        )
                        if created:
                            created_affectations += 1

            # 5) Pôles dont le code n'est pas dans ACTIVITY_TYPES_BY_POLE : affecter les types "generic"
            generic_codes = {t.get("value") for t in ACTIVITY_TYPES_BY_POLE.get("generic", [])}
            for pole in poles:
                code = get_pole_activity_code(pole)
                if code not in ACTIVITY_TYPES_BY_POLE:
                    for value in generic_codes:
                        if not value:
                            continue
                        try:
                            template = ActiviteTemplate.objects.get(code=value)
                        except ActiviteTemplate.DoesNotExist:
                            continue
                        _, created = ActiviteTemplatePole.objects.get_or_create(
                            activite_template=template,
                            pole=pole,
                            defaults={"ordre": 0},
                        )
                        if created:
                            created_affectations += 1

        with transaction.atomic():
            do_seed()

        self.stdout.write(
            f"Résumé : {created_templates} template(s) créé(s), "
            f"{created_champs} champ(s) créé(s), {created_affectations} affectation(s) créée(s)."
        )
        if dry_run:
            self.stdout.write("(Aucune modification réelle en base.)")
