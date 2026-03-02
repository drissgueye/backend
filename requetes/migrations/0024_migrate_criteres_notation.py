# Migration: mapper les anciens critères de notation vers les nouveaux

from django.db import migrations


OLD_TO_NEW_CRITERE = {
    "respect_accords": "conformite_contrats",
    "conditions_travail": "conditions_travail_cca",
    "remuneration": "remuneration_avantages",
    "formation": "formation",
    "sante_securite": "securite_sante",
}


def migrate_criteres_forward(apps, schema_editor):
    NotationEntreprise = apps.get_model("requetes", "NotationEntreprise")
    for old, new in OLD_TO_NEW_CRITERE.items():
        NotationEntreprise.objects.filter(critere=old).update(critere=new)
    NotationEntreprise.objects.filter(critere="dialogue_social").update(critere="relations_sociales")
    for row in list(NotationEntreprise.objects.filter(critere="relation_syndicat")):
        if NotationEntreprise.objects.filter(
            entreprise_id=row.entreprise_id,
            created_by_id=row.created_by_id,
            critere="relations_sociales",
        ).exists():
            row.delete()
        else:
            row.critere = "relations_sociales"
            row.save()


def migrate_criteres_backward(apps, schema_editor):
    NotationEntreprise = apps.get_model("requetes", "NotationEntreprise")
    new_to_old = {
        "relations_sociales": "dialogue_social",
        "conformite_contrats": "respect_accords",
        "conditions_travail_cca": "conditions_travail",
        "remuneration_avantages": "remuneration",
        "formation": "formation",
        "securite_sante": "sante_securite",
    }
    for new, old in new_to_old.items():
        NotationEntreprise.objects.filter(critere=new).update(critere=old)


class Migration(migrations.Migration):

    dependencies = [
        ("requetes", "0023_activites_dynamiques"),
    ]

    operations = [
        migrations.RunPython(migrate_criteres_forward, migrate_criteres_backward),
    ]
