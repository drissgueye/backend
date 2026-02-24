# Crée des dossiers pour les requêtes qui ont un pôle mais pas de dossier.

from django.core.management.base import BaseCommand
from django.db import transaction

from requetes.models import Dossier, Requete


class Command(BaseCommand):
    help = "Crée un dossier pour chaque requête qui a un pôle mais pas de dossier, et rattache la requête."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Affiche les requêtes concernées sans créer les dossiers.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        requetes = Requete.objects.select_related("pole", "travailleur").filter(
            dossier_id__isnull=True, pole_id__isnull=False
        )
        count = requetes.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS("Aucune requête sans dossier à traiter."))
            return
        if dry_run:
            self.stdout.write(f"{count} requête(s) sans dossier (pôle renseigné) :")
            for r in requetes:
                self.stdout.write(f"  - {r.numero_reference} (pôle: {r.pole.nom})")
            return
        created = 0
        with transaction.atomic():
            for requete in requetes:
                dossier = Dossier.objects.create(
                    pole=requete.pole,
                    titre=f"Dossier - {requete.pole.nom} - {requete.numero_reference}",
                    responsable=requete.travailleur,
                )
                dossier.requetes.add(requete)
                requete.dossier = dossier
                requete.save(update_fields=["dossier"])
                created += 1
                self.stdout.write(f"  Créé {dossier.numero_dossier} pour {requete.numero_reference}")
        self.stdout.write(self.style.SUCCESS(f"{created} dossier(s) créé(s)."))
