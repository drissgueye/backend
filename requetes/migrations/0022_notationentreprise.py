# Migration: notation des entreprises par critères

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("requetes", "0021_alter_documentsyndical_categorie"),
    ]

    operations = [
        migrations.CreateModel(
            name="NotationEntreprise",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "critere",
                    models.CharField(
                        choices=[
                            ("dialogue_social", "Dialogue social"),
                            ("respect_accords", "Respect des accords et conformité"),
                            ("conditions_travail", "Conditions de travail"),
                            ("remuneration", "Rémunération et avantages"),
                            ("formation", "Formation et évolution"),
                            ("sante_securite", "Santé et sécurité au travail"),
                            ("relation_syndicat", "Relation avec le syndicat"),
                        ],
                        db_index=True,
                        max_length=40,
                    ),
                ),
                (
                    "note",
                    models.PositiveSmallIntegerField(
                        help_text="Note de 1 à 5 (1 = très insuffisant, 5 = excellent)",
                        validators=[
                        django.core.validators.MinValueValidator(1),
                        django.core.validators.MaxValueValidator(5),
                    ],
                    ),
                ),
                ("commentaire", models.TextField(blank=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notations_entreprise",
                        to=settings.AUTH_USER_MODEL,
                        db_index=True,
                    ),
                ),
                (
                    "entreprise",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notations",
                        to="requetes.entreprise",
                        db_index=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "Notation entreprise",
                "verbose_name_plural": "Notations entreprises",
            },
        ),
        migrations.AddConstraint(
            model_name="notationentreprise",
            constraint=models.UniqueConstraint(
                fields=("entreprise", "critere", "created_by"),
                name="notation_entreprise_unique_user_critere",
            ),
        ),
    ]
