# Migration : modèle PoleMembership et choix de rôles globaux
# - PoleMembership : table User ↔ Pole avec is_manager (CASCADE, unique_together)
# - Rétrocompatibilité : rôles pole_manager/head/assistant conservés dans RoleUtilisateur
# - Backfill optionnel : créer des PoleMembership à partir de PoleMembre (head→is_manager)
#    et de Pole.chef_de_pole

from django.conf import settings
from django.db import migrations, models


def backfill_pole_memberships(apps, schema_editor):
    """Crée des PoleMembership à partir des chefs de pôle et des PoleMembre avec role=head."""
    Pole = apps.get_model("requetes", "Pole")
    PoleMembre = apps.get_model("requetes", "PoleMembre")
    PoleMembership = apps.get_model("requetes", "PoleMembership")
    created = 0
    for pole in Pole.objects.all():
        if pole.chef_de_pole_id and not PoleMembership.objects.filter(
            user_id=pole.chef_de_pole_id, pole=pole
        ).exists():
            PoleMembership.objects.create(
                user_id=pole.chef_de_pole_id, pole=pole, is_manager=True
            )
            created += 1
    for pm in PoleMembre.objects.select_related("pole").all():
        is_manager = getattr(pm, "role", None) == "head"
        if not PoleMembership.objects.filter(user_id=pm.user_id, pole=pm.pole).exists():
            PoleMembership.objects.create(
                user_id=pm.user_id, pole=pm.pole, is_manager=is_manager
            )
            created += 1
    # Pas de log nécessaire en migration


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("requetes", "0007_alter_profilutilisateur_role"),
    ]

    operations = [
        migrations.CreateModel(
            name="PoleMembership",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_manager", models.BooleanField(default=False)),
                (
                    "pole",
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        related_name="memberships",
                        to="requetes.pole",
                        db_index=True,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        related_name="pole_memberships",
                        to=settings.AUTH_USER_MODEL,
                        db_index=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "Appartenance au pôle",
                "verbose_name_plural": "Appartenances aux pôles",
            },
        ),
        migrations.AddConstraint(
            model_name="polemembership",
            constraint=models.UniqueConstraint(
                fields=("user", "pole"),
                name="unique_user_pole_membership",
            ),
        ),
        migrations.RunPython(backfill_pole_memberships, noop),
    ]
