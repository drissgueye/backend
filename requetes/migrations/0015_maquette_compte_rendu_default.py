# Migration : maquette de compte rendu par défaut

from django.db import migrations


def create_default_maquette(apps, schema_editor):
    MaquetteCompteRendu = apps.get_model("requetes", "MaquetteCompteRendu")
    if not MaquetteCompteRendu.objects.filter(is_default=True).exists():
        MaquetteCompteRendu.objects.create(
            nom="Compte rendu de clôture (par défaut)",
            contenu="""COMPTE RENDU DE CLÔTURE
Requête : [REFERENCE] - [TITRE]

Date de clôture : [DATE_CLOTURE]

1. Contexte
   - Demandeur : [DEMANDEUR]
   - Entreprise : [ENTREPRISE]
   - Pôle : [POLE]
   - Date d'ouverture : [DATE_OUVERTURE]

2. Objet de la requête
   [DESCRIPTION]

3. Déroulement et actions menées
   (À compléter)

4. Résolution / Conclusion
   (À compléter)

5. Recommandations éventuelles
   (À compléter)

Rédigé le : [DATE]
""",
            is_default=True,
            ordre=0,
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("requetes", "0014_compte_rendu_et_maquette"),
    ]

    operations = [
        migrations.RunPython(create_default_maquette, noop),
    ]
