from __future__ import annotations

from typing import Any

from django.urls import NoReverseMatch
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .models import (
    Dossier,
    Entreprise,
    HistoriqueAction,
    PieceJointe,
    Pole,
    Requete,
    Reunion,
)


class BaseListView(ListView):
    """Vue liste générique avec pagination standard."""

    paginate_by = 25


class BaseCreateView(CreateView):
    """Vue création générique avec redirection sûre."""

    success_url = "/"

    def get_success_url(self) -> str:
        if hasattr(self.object, "get_absolute_url"):
            try:
                return self.object.get_absolute_url()  # type: ignore[no-any-return]
            except NoReverseMatch:
                return self.success_url
        return self.success_url


class BaseUpdateView(UpdateView):
    """Vue modification générique avec redirection sûre."""

    success_url = "/"

    def get_success_url(self) -> str:
        if hasattr(self.object, "get_absolute_url"):
            try:
                return self.object.get_absolute_url()  # type: ignore[no-any-return]
            except NoReverseMatch:
                return self.success_url
        return self.success_url


class BaseDeleteView(DeleteView):
    """Vue suppression générique avec redirection sûre."""

    success_url = "/"


class EntrepriseListView(BaseListView):
    """Liste des entreprises."""

    model = Entreprise


class EntrepriseDetailView(DetailView):
    """Détail d'une entreprise."""

    model = Entreprise


class EntrepriseCreateView(BaseCreateView):
    """Création d'une entreprise."""

    model = Entreprise
    fields = ["nom", "adresse", "secteur_activite"]


class EntrepriseUpdateView(BaseUpdateView):
    """Modification d'une entreprise."""

    model = Entreprise
    fields = ["nom", "adresse", "secteur_activite"]


class EntrepriseDeleteView(BaseDeleteView):
    """Suppression d'une entreprise."""

    model = Entreprise


class PoleListView(BaseListView):
    """Liste des pôles."""

    model = Pole


class PoleDetailView(DetailView):
    """Détail d'un pôle."""

    model = Pole


class PoleCreateView(BaseCreateView):
    """Création d'un pôle."""

    model = Pole
    fields = ["nom", "description", "chef_de_pole", "membres", "types_problemes"]


class PoleUpdateView(BaseUpdateView):
    """Modification d'un pôle."""

    model = Pole
    fields = ["nom", "description", "chef_de_pole", "membres", "types_problemes"]


class PoleDeleteView(BaseDeleteView):
    """Suppression d'un pôle."""

    model = Pole


class RequeteListView(BaseListView):
    """Liste des requêtes."""

    model = Requete
    ordering = ["-created_at"]


class RequeteDetailView(DetailView):
    """Détail d'une requête."""

    model = Requete


class RequeteCreateView(BaseCreateView):
    """Création d'une requête."""

    model = Requete
    fields = [
        "travailleur",
        "pole",
        "type_probleme",
        "titre",
        "description",
        "delegue_syndical",
        "entreprise",
        "dossier",
        "statut",
        "priorite",
    ]


class RequeteUpdateView(BaseUpdateView):
    """Modification d'une requête."""

    model = Requete
    fields = [
        "travailleur",
        "pole",
        "type_probleme",
        "titre",
        "description",
        "delegue_syndical",
        "entreprise",
        "dossier",
        "statut",
        "priorite",
    ]


class RequeteDeleteView(BaseDeleteView):
    """Suppression d'une requête."""

    model = Requete


class DossierListView(BaseListView):
    """Liste des dossiers."""

    model = Dossier
    ordering = ["-created_at"]


class DossierDetailView(DetailView):
    """Détail d'un dossier."""

    model = Dossier


class DossierCreateView(BaseCreateView):
    """Création d'un dossier."""

    model = Dossier
    fields = [
        "pole",
        "titre",
        "requetes",
        "responsable",
        "statut",
        "date_ouverture",
        "date_cloture",
        "synthese",
    ]


class DossierUpdateView(BaseUpdateView):
    """Modification d'un dossier."""

    model = Dossier
    fields = [
        "pole",
        "titre",
        "requetes",
        "responsable",
        "statut",
        "date_ouverture",
        "date_cloture",
        "synthese",
    ]


class DossierDeleteView(BaseDeleteView):
    """Suppression d'un dossier."""

    model = Dossier


class PieceJointeListView(BaseListView):
    """Liste des pièces jointes."""

    model = PieceJointe


class PieceJointeDetailView(DetailView):
    """Détail d'une pièce jointe."""

    model = PieceJointe


class PieceJointeCreateView(BaseCreateView):
    """Création d'une pièce jointe."""

    model = PieceJointe
    fields = ["requete", "fichier", "type_document", "description", "uploaded_by"]


class PieceJointeUpdateView(BaseUpdateView):
    """Modification d'une pièce jointe."""

    model = PieceJointe
    fields = ["requete", "fichier", "type_document", "description", "uploaded_by"]


class PieceJointeDeleteView(BaseDeleteView):
    """Suppression d'une pièce jointe."""

    model = PieceJointe


class ReunionListView(BaseListView):
    """Liste des réunions."""

    model = Reunion


class ReunionDetailView(DetailView):
    """Détail d'une réunion."""

    model = Reunion


class ReunionCreateView(BaseCreateView):
    """Création d'une réunion."""

    model = Reunion
    fields = [
        "dossier",
        "type_reunion",
        "date_heure",
        "lieu",
        "participants",
        "ordre_du_jour",
        "compte_rendu",
        "statut",
        "created_by",
    ]


class ReunionUpdateView(BaseUpdateView):
    """Modification d'une réunion."""

    model = Reunion
    fields = [
        "dossier",
        "type_reunion",
        "date_heure",
        "lieu",
        "participants",
        "ordre_du_jour",
        "compte_rendu",
        "statut",
        "created_by",
    ]


class ReunionDeleteView(BaseDeleteView):
    """Suppression d'une réunion."""

    model = Reunion


class HistoriqueActionListView(BaseListView):
    """Liste des actions d'historique."""

    model = HistoriqueAction
    ordering = ["-timestamp"]


class HistoriqueActionDetailView(DetailView):
    """Détail d'une action d'historique."""

    model = HistoriqueAction


# TODO: Ajouter des permissions par rôle et filtrer selon l'utilisateur connecté.
# TODO: Restreindre les champs exposés dans les vues de modification.
