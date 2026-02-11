from __future__ import annotations

from django.db import migrations


def seed_entreprises(apps, schema_editor) -> None:
    Entreprise = apps.get_model("requetes", "Entreprise")

    entreprises = [
        {"nom": "Axa Assurance", "code": "AXA"},
        {"nom": "SanlamAllianz Sénégal Assurances", "code": "SANLAMALLIANZ"},
        {"nom": "Amsa assurances", "code": "AMSA"},
        {"nom": "ASKIA Assurances", "code": "ASKIA"},
        {"nom": "Salama Assurances Sénégal - Finafrica Assurances", "code": "SALAMA"},
        {"nom": "Assurances La Providence", "code": "PROVIDENCE"},
        {"nom": "ASS Assurances la Sécurité Sénégalaise", "code": "ASS"},
        {"nom": "SAAR SENEGAL", "code": "SAAR"},
        {"nom": "Sen Assurance Vie", "code": "SEN_VIE"},
        {"nom": "Sunu Assurances Sénégal", "code": "SUNU"},
        {"nom": "Assurance Sénégal", "code": "ASSURANCE_SN"},
    ]

    for data in entreprises:
        Entreprise.objects.update_or_create(
            nom=data["nom"],
            defaults={
                "code": data["code"],
                "adresse": "N/A",
                "secteur_activite": "Assurance",
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("requetes", "0005_create_profils_existing"),
    ]

    operations = [
        migrations.RunPython(seed_entreprises, migrations.RunPython.noop),
    ]
