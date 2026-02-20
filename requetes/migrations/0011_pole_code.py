# Migration : champ code sur Pole pour le processeur métier (Strategy Pattern)

from django.db import migrations, models


def backfill_pole_codes(apps, schema_editor):
    """Renseigne le code à partir du nom pour les pôles existants."""
    Pole = apps.get_model("requetes", "Pole")
    mapping = {
        "Pôle Juridique et Conformité": "legal",
        "Pôle Santé, Sécurité et Bien-être au travail": "health",
        "Pôle Dialogue Social et Médiation": "mediation",
        "Pôle Formation et Carrière": "training",
        "Pôle Communication et Sensibilisation": "communication",
        "Pôle Habitat": "generic",
        "Pôle Conditions de Travail et Rémunération": "generic",
        "Pôle Innovation, Digitalisation et Transformation": "generic",
        "Pôle Relations Extérieures et Partenariats": "generic",
        "Pôle Jeunesse et Intégration des Nouveaux Employés": "generic",
    }
    for pole in Pole.objects.all():
        code = mapping.get(pole.nom, "").strip()
        if code and pole.code != code:
            pole.code = code
            pole.save(update_fields=["code"])


class Migration(migrations.Migration):

    dependencies = [
        ("requetes", "0010_rename_role_labels_member_to_adherent"),
    ]

    operations = [
        migrations.AddField(
            model_name="pole",
            name="code",
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text="Identifiant du processeur métier (legal, health, mediation, training, communication). Vide = processeur générique.",
                max_length=40,
            ),
        ),
        migrations.RunPython(backfill_pole_codes, migrations.RunPython.noop),
    ]
