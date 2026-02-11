from __future__ import annotations

from django.conf import settings
from django.db import migrations


def seed_poles(apps, schema_editor) -> None:
    Pole = apps.get_model("requetes", "Pole")
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_model(app_label, model_name)

    admin_user = User.objects.first()
    if admin_user is None:
        admin_user = User.objects.create(
            username="admin",
            is_staff=True,
            is_superuser=True,
        )
        admin_user.set_unusable_password()
        admin_user.save(update_fields=["password"])

    poles = [
        {
            "nom": "Pôle Habitat",
            "description": "Logement, aides, partenariats et amélioration des conditions de vie.",
            "types_problemes": ["other"],
        },
        {
            "nom": "Pôle Conditions de Travail et Rémunération",
            "description": "Salaires, primes, contrats, environnement et ergonomie.",
            "types_problemes": ["working_conditions_remuneration"],
        },
        {
            "nom": "Pôle Formation et Carrière",
            "description": "Formations continues, certifications, mobilité et promotion.",
            "types_problemes": ["training_career"],
        },
        {
            "nom": "Pôle Dialogue Social et Médiation",
            "description": "Dialogue social, médiation, comités et doléances.",
            "types_problemes": ["social_mediation"],
        },
        {
            "nom": "Pôle Santé, Sécurité et Bien-être au travail",
            "description": "Prévention santé, sécurité, bien-être et assurance.",
            "types_problemes": ["health_safety_wellbeing"],
        },
        {
            "nom": "Pôle Juridique et Conformité",
            "description": "Assistance juridique, conformité et contentieux.",
            "types_problemes": ["legal_compliance"],
        },
        {
            "nom": "Pôle Communication et Sensibilisation",
            "description": "Communication interne/externe et sensibilisation.",
            "types_problemes": ["communication_awareness"],
        },
        {
            "nom": "Pôle Innovation, Digitalisation et Transformation",
            "description": "Outils numériques, digitalisation et conduite du changement.",
            "types_problemes": ["innovation_digital_transformation"],
        },
        {
            "nom": "Pôle Relations Extérieures et Partenariats",
            "description": "Partenariats, relations externes et représentation.",
            "types_problemes": ["external_relations_partnerships"],
        },
        {
            "nom": "Pôle Jeunesse et Intégration des Nouveaux Employés",
            "description": "Accueil, mentorat et intégration des nouveaux employés.",
            "types_problemes": ["youth_new_employees"],
        },
    ]

    for data in poles:
        Pole.objects.update_or_create(
            nom=data["nom"],
            defaults={
                "description": data["description"],
                "chef_de_pole": admin_user,
                "types_problemes": data["types_problemes"],
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("requetes", "0003_profilutilisateur_adresse_residence_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_poles, migrations.RunPython.noop),
    ]
