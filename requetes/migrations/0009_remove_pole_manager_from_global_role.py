# Migration : retrait de POLE_MANAGER / head / assistant des rôles globaux.
# 1) Données : tout profil avec role in (pole_manager, head, assistant) → member,
#    et création/mise à jour de PoleMembership.is_manager pour leurs pôles.
# 2) Choix du champ role : uniquement super_admin, admin, delegate, member, comptable.

from django.db import migrations, models


def migrate_pole_roles_to_member_and_membership(apps, schema_editor):
    """Passe les profils pole_manager/head/assistant en member et assure PoleMembership.is_manager."""
    ProfilUtilisateur = apps.get_model("requetes", "ProfilUtilisateur")
    Pole = apps.get_model("requetes", "Pole")
    PoleMembre = apps.get_model("requetes", "PoleMembre")
    PoleMembership = apps.get_model("requetes", "PoleMembership")

    for profil in ProfilUtilisateur.objects.filter(
        role__in=("pole_manager", "head", "assistant")
    ).select_related("user"):
        user_id = profil.user_id
        # (pole_id -> is_manager) : chef de pôle ou PoleMembre.role head → True
        pole_to_manager = {}
        for pole_id in Pole.objects.filter(chef_de_pole_id=user_id).values_list("id", flat=True):
            pole_to_manager[pole_id] = True
        for pm in PoleMembre.objects.filter(user_id=user_id).only("pole_id", "role"):
            if pm.pole_id not in pole_to_manager:
                pole_to_manager[pm.pole_id] = getattr(pm, "role", None) == "head"
            elif getattr(pm, "role", None) == "head":
                pole_to_manager[pm.pole_id] = True
        for pole_id, is_manager in pole_to_manager.items():
            PoleMembership.objects.update_or_create(
                user_id=user_id,
                pole_id=pole_id,
                defaults={"is_manager": is_manager},
            )
        profil.role = "member"
        profil.save(update_fields=["role"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("requetes", "0008_polemembership_and_role_choices"),
    ]

    operations = [
        migrations.RunPython(migrate_pole_roles_to_member_and_membership, noop),
        migrations.AlterField(
            model_name="profilutilisateur",
            name="role",
            field=models.CharField(
                choices=[
                    ("super_admin", "Super Administrateur"),
                    ("admin", "Administrateur Syndical"),
                    ("delegate", "Délégué Syndical"),
                    ("member", "Membre"),
                    ("comptable", "Comptable"),
                ],
                max_length=20,
            ),
        ),
    ]
