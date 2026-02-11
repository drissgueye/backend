from __future__ import annotations

from django.conf import settings
from django.db import migrations


def create_profils_for_existing_users(apps, schema_editor) -> None:
    ProfilUtilisateur = apps.get_model("requetes", "ProfilUtilisateur")
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_model(app_label, model_name)

    existing_user_ids = set(
        ProfilUtilisateur.objects.values_list("user_id", flat=True)
    )
    to_create = []
    for user in User.objects.all():
        if user.id in existing_user_ids:
            continue
        to_create.append(
            ProfilUtilisateur(
                user_id=user.id,
                role="member",
            )
        )

    if to_create:
        ProfilUtilisateur.objects.bulk_create(to_create)


class Migration(migrations.Migration):
    dependencies = [
        ("requetes", "0004_seed_poles"),
    ]

    operations = [
        migrations.RunPython(create_profils_for_existing_users, migrations.RunPython.noop),
    ]
