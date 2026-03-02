# Migration: ajout du statut "Non résolu" (StatutRequete.NON_RESOLU)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("requetes", "0024_migrate_criteres_notation"),
    ]

    operations = [
        migrations.AlterField(
            model_name="requete",
            name="statut",
            field=models.CharField(
                choices=[
                    ("new", "Nouveau"),
                    ("info_needed", "Besoin d'infos"),
                    ("processing", "En traitement"),
                    ("hr_escalated", "Escaladé RH"),
                    ("hr_pending", "En attente RH"),
                    ("resolved", "Résolu"),
                    ("non_resolu", "Non résolu"),
                    ("closed", "Clôturé"),
                ],
                default="new",
                max_length=30,
            ),
        ),
    ]
