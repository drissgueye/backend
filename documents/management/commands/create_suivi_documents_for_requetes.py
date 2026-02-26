"""
Crée les documents de suivi pour les requêtes qui n'en ont pas encore.
Utile après déploiement du module documents : les requêtes créées avant n'ont
pas déclenché le signal, donc pas de document de suivi.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from requetes.models import Requete

from documents.models import Document, DocumentHistorique
from documents.services import ensure_suivi_document_for_requete
from documents.models import TypeActionDocumentChoices


class Command(BaseCommand):
    help = "Crée le document de suivi (et une entrée historique Création) pour chaque requête qui n'en a pas."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Affiche ce qui serait fait sans créer les documents.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        ids_avec_suivi = set(
            Requete.objects.filter(documents_lies__is_suivi_requete=True).values_list("pk", flat=True)
        )
        all_ids = set(Requete.objects.values_list("pk", flat=True))
        ids_sans_suivi = all_ids - ids_avec_suivi
        requetes = Requete.objects.filter(pk__in=ids_sans_suivi).select_related("pole", "travailleur")
        count = requetes.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS("Toutes les requêtes ont déjà un document de suivi."))
            return
        if dry_run:
            self.stdout.write(f"[DRY-RUN] {count} requête(s) sans document de suivi seraient traitées.")
            return
        created = 0
        for requete in requetes:
            with transaction.atomic():
                doc = ensure_suivi_document_for_requete(
                    requete, default_created_by=requete.travailleur
                )
                if doc:
                    DocumentHistorique.objects.get_or_create(
                        document=doc,
                        action=TypeActionDocumentChoices.CREATION,
                        defaults={
                            "utilisateur": requete.travailleur,
                            "commentaire": "Création de la requête (rattrapage).",
                        },
                    )
                    created += 1
        self.stdout.write(self.style.SUCCESS(f"{created} document(s) de suivi créé(s)."))
