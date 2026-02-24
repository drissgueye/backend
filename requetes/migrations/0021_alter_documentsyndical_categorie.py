# Migration: champ categorie avec choices et default (aligné sur CategorieDocument)

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("requetes", "0020_document_categorie_choices"),
    ]

    operations = [
        migrations.AlterField(
            model_name="documentsyndical",
            name="categorie",
            field=models.CharField(
                blank=True,
                choices=[
                    ("administratifs_officiels", "Documents administratifs officiels"),
                    ("documents_membres", "Documents des membres"),
                    ("documents_poles", "Documents liés aux pôles"),
                    ("communication", "Documents de communication"),
                    ("juridiques_contentieux", "Documents juridiques et contentieux"),
                ],
                default="administratifs_officiels",
                max_length=120,
            ),
        ),
    ]
