# Migration: aligner les choices de NotationEntreprise.critere avec CritereNotation

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("requetes", "0025_requete_statut_non_resolu"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notationentreprise",
            name="critere",
            field=models.CharField(
                choices=[
                    ("conformite_contrats", "Conformité des contrats"),
                    ("remuneration_avantages", "Rémunération et avantages"),
                    ("securite_sante", "Sécurité et santé"),
                    ("relations_sociales", "Relations sociales"),
                    ("rupture_contrat", "Rupture du contrat"),
                    ("rupture_communication", "Rupture de communication"),
                    ("classification_professionnelle", "Classification professionnelle"),
                    ("primes_specifiques", "Primes spécifiques"),
                    ("conditions_travail_cca", "Conditions de travail (CCA)"),
                    ("formation", "Formation"),
                    ("traitement_equitable", "Traitement équitable"),
                ],
                db_index=True,
                max_length=40,
            ),
        ),
    ]
