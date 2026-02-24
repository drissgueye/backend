# Migration : Pôle Habitat utilise le code "habitat" pour les types d'activité dédiés

from django.db import migrations


def set_habitat_pole_code(apps, schema_editor):
    """Assigne le code 'habitat' au Pôle Habitat pour le suivi des activités."""
    Pole = apps.get_model("requetes", "Pole")
    Pole.objects.filter(nom="Pôle Habitat").update(code="habitat")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("requetes", "0018_activite_requete_piece_jointe_compte_rendu"),
    ]

    operations = [
        migrations.RunPython(set_habitat_pole_code, noop),
    ]
