# Migration : compte rendu de clôture et maquette

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("requetes", "0013_rename_poleworkflow_pole_from_active_idx_requetes_po_pole_id_5f6e2a_idx"),
    ]

    operations = [
        migrations.AddField(
            model_name="requete",
            name="date_cloture",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="requete",
            name="compte_rendu",
            field=models.TextField(blank=True),
        ),
        migrations.CreateModel(
            name="MaquetteCompteRendu",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nom", models.CharField(max_length=200)),
                (
                    "contenu",
                    models.TextField(
                        help_text="Texte de la maquette avec éventuels repères : [REFERENCE], [DATE], [TITRE], etc."
                    ),
                ),
                ("is_default", models.BooleanField(default=False)),
                ("ordre", models.PositiveSmallIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Maquette de compte rendu",
                "verbose_name_plural": "Maquettes de compte rendu",
                "ordering": ["ordre", "nom"],
            },
        ),
    ]
