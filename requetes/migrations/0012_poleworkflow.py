# Migration : configuration optionnelle des transitions par pôle (PoleWorkflow)

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("requetes", "0011_pole_code"),
    ]

    operations = [
        migrations.CreateModel(
            name="PoleWorkflow",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("from_status", models.CharField(db_index=True, max_length=30)),
                ("to_status", models.CharField(db_index=True, max_length=30)),
                ("action_id", models.CharField(blank=True, max_length=60)),
                ("label", models.CharField(blank=True, max_length=120)),
                ("ordre", models.PositiveSmallIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "pole",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="workflow_transitions",
                        to="requetes.pole",
                        db_index=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "Transition de workflow (pôle)",
                "verbose_name_plural": "Transitions de workflow (pôle)",
                "ordering": ["pole", "ordre", "from_status", "to_status"],
            },
        ),
        migrations.AddIndex(
            model_name="poleworkflow",
            index=models.Index(
                fields=["pole", "from_status", "is_active"],
                name="poleworkflow_pole_from_active_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="poleworkflow",
            constraint=models.UniqueConstraint(
                fields=("pole", "from_status", "to_status"),
                name="unique_pole_workflow_transition",
            ),
        ),
    ]
