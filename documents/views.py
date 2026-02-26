"""
ViewSet pour la gestion des documents : upload, filtres par pôle/statut/confidentialité,
historique des actions. Permissions : admin global, responsables de pôle = documents de leur pôle.
"""
from __future__ import annotations

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from requetes.models import Pole, PoleMembership

from .models import (
    Document,
    DocumentHistorique,
    ConfidentialiteChoices,
    StatutDocumentChoices,
    TypeActionDocumentChoices,
)
from .permissions import DocumentAccessPermission
from .serializers import (
    DocumentSerializer,
    DocumentCreateUpdateSerializer,
    DocumentListSerializer,
    DocumentHistoriqueSerializer,
)


def _is_admin(user) -> bool:
    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return True
    profil = getattr(user, "profil", None)
    if profil is not None:
        return getattr(profil, "role", None) in ("admin", "super_admin")
    return False


def _pole_ids_manager(user) -> list[int]:
    ids = list(
        PoleMembership.objects.filter(user=user, is_manager=True).values_list("pole_id", flat=True)
    )
    ids += list(Pole.objects.filter(chef_de_pole=user).values_list("id", flat=True))
    return list(set(ids))


class DocumentViewSet(viewsets.ModelViewSet):
    """
    CRUD des documents avec upload de fichier.
    - Admin : voit tous les documents.
    - Responsable de pôle : voit les documents de son/ses pôle(s).
    - Autres utilisateurs : voient au moins les documents liés à leurs requêtes
      (ex. suivi automatique des requêtes qu'ils ont déposées).
    """
    permission_classes = [IsAuthenticated, DocumentAccessPermission]
    pagination_class = None  # liste non paginée : retourne un tableau [] pour la page /documents
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["pole", "confidentialite", "statut", "requete"]
    search_fields = ["titre", "description"]
    ordering_fields = ["created_at", "updated_at", "titre"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = Document.objects.select_related("pole", "requete", "created_by")
        user = self.request.user
        if _is_admin(user):
            return qs
        pole_ids = _pole_ids_manager(user)
        # Responsable de pôle : documents de son/ses pôle(s) OU documents des requêtes dont il est travailleur
        # Sinon : uniquement documents liés aux requêtes dont l'utilisateur est le travailleur (ex. suivi)
        if pole_ids:
            return qs.filter(
                Q(pole_id__in=pole_ids) | Q(requete__travailleur=user)
            ).distinct()
        return qs.filter(requete__travailleur=user)

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return DocumentCreateUpdateSerializer
        if self.action == "list":
            return DocumentListSerializer
        return DocumentSerializer

    def perform_create(self, serializer):
        doc = serializer.save(created_by=self.request.user)
        DocumentHistorique.objects.create(
            document=doc,
            utilisateur=self.request.user,
            action=TypeActionDocumentChoices.CREATION,
            commentaire="Création du document",
        )

    def perform_update(self, serializer):
        instance = serializer.instance
        old_statut = instance.statut
        old_pole_id = instance.pole_id
        doc = serializer.save()
        action_type = TypeActionDocumentChoices.MODIFICATION
        commentaire = "Modification"
        if old_statut != doc.statut:
            if doc.statut == "ARCHIVE":
                action_type = TypeActionDocumentChoices.ARCHIVAGE
                commentaire = "Archivage"
            elif doc.statut == "TRANSFERE":
                action_type = TypeActionDocumentChoices.TRANSFERT
                commentaire = "Transfert"
            else:
                commentaire = f"Changement de statut : {old_statut} → {doc.statut}"
        if old_pole_id != doc.pole_id:
            commentaire = (commentaire or "Modification") + f" ; pôle modifié (ex: {old_pole_id})"
        DocumentHistorique.objects.create(
            document=doc,
            utilisateur=self.request.user,
            action=action_type,
            champ_modifie="statut" if old_statut != doc.statut else None,
            ancienne_valeur=old_statut if old_statut != doc.statut else None,
            nouvelle_valeur=doc.statut if old_statut != doc.statut else None,
            commentaire=commentaire or "Modification",
        )

    @action(detail=True, methods=["get"])
    def historique(self, request, pk=None):
        """Liste l'historique des actions sur ce document."""
        doc = self.get_object()
        qs = doc.historique.select_related("utilisateur").order_by("-timestamp")
        serializer = DocumentHistoriqueSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="choices")
    def choices(self, request):
        """Retourne les choix pour confidentialité, statut et type d'action (pour formulaires)."""
        return Response({
            "confidentialite": [{"value": c[0], "label": c[1]} for c in ConfidentialiteChoices.choices],
            "statut": [{"value": s[0], "label": s[1]} for s in StatutDocumentChoices.choices],
            "type_action": [{"value": t[0], "label": t[1]} for t in TypeActionDocumentChoices.choices],
        })

    @action(detail=False, methods=["post"], url_path="ensure-suivi")
    def ensure_suivi(self, request):
        """
        Crée les documents de suivi pour les requêtes qui n'en ont pas encore.
        Réservé aux admins. Utile quand la liste est vide car les requêtes existaient avant les signaux.
        """
        if not _is_admin(request.user):
            return Response(
                {"detail": "Action réservée aux administrateurs."},
                status=status.HTTP_403_FORBIDDEN,
            )
        from requetes.models import Requete
        from .models import TypeActionDocumentChoices
        from .services import ensure_suivi_document_for_requete

        ids_avec_suivi = set(
            Document.objects.filter(is_suivi_requete=True).values_list("requete_id", flat=True)
        )
        requetes = Requete.objects.filter(
            pk__in=set(Requete.objects.values_list("pk", flat=True)) - ids_avec_suivi
        ).select_related("pole", "travailleur")
        created = 0
        for requete in requetes:
            doc = ensure_suivi_document_for_requete(requete, default_created_by=requete.travailleur)
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
        return Response({"created": created, "detail": f"{created} document(s) de suivi créé(s)."})
