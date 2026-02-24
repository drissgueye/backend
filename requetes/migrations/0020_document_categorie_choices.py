# Generated manually: assign existing documents to valid CategorieDocument choices.

from django.db import migrations

# Valeurs valides (CategorieDocument)
CATEGORIES = {
    "administratifs_officiels",
    "documents_membres",
    "documents_poles",
    "communication",
    "juridiques_contentieux",
}


def map_categorie(current: str) -> str:
    """Assigne une catégorie valide à partir de l'ancienne valeur (vide ou libre)."""
    if not current or not current.strip():
        return "administratifs_officiels"
    c = current.strip().lower()
    if c in CATEGORIES:
        return c
    if "membre" in c or "adhesion" in c or "adhésion" in c or "carte" in c:
        return "documents_membres"
    if "pôle" in c or "pole" in c or "habitat" in c:
        return "documents_poles"
    if "communication" in c or "circulaire" in c or "note" in c or "annonce" in c or "formulaire" in c or "guide" in c:
        return "communication"
    if "juridique" in c or "contentieux" in c or "convention" in c or "plainte" in c or "courrier" in c:
        return "juridiques_contentieux"
    return "administratifs_officiels"


def assign_categorie_to_existing_documents(apps, schema_editor):
    DocumentSyndical = apps.get_model("requetes", "DocumentSyndical")
    for doc in DocumentSyndical.objects.all():
        new_cat = map_categorie(doc.categorie or "")
        if doc.categorie != new_cat:
            doc.categorie = new_cat
            doc.save(update_fields=["categorie"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("requetes", "0019_pole_habitat_code_habitat"),
    ]

    operations = [
        migrations.RunPython(assign_categorie_to_existing_documents, noop),
    ]
