# Migration : libellés des rôles pour éviter la confusion
# - Rôle global "member" → "Adhérent" (et non "Membre")
# - Rôle dans un pôle "member" → "Membre du pôle", "head" → "Responsable du pôle"

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("requetes", "0009_remove_pole_manager_from_global_role"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profilutilisateur",
            name="role",
            field=models.CharField(
                choices=[
                    ("super_admin", "Super Administrateur"),
                    ("admin", "Administrateur Syndical"),
                    ("delegate", "Délégué Syndical"),
                    ("member", "Adhérent"),
                    ("comptable", "Comptable"),
                ],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="polemembre",
            name="role",
            field=models.CharField(
                choices=[
                    ("head", "Responsable du pôle"),
                    ("assistant", "Adjoint"),
                    ("member", "Membre du pôle"),
                ],
                default="member",
                max_length=20,
            ),
        ),
    ]
