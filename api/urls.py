from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    ActiviteTemplateViewSet,
    CommunicationPostViewSet,
    DelegueSyndicalViewSet,
    DossierViewSet,
    DocumentSyndicalViewSet,
    EntrepriseViewSet,
    LogoutViewSet,
    MaquetteCompteRenduViewSet,
    NotationEntrepriseViewSet,
    NotificationViewSet,
    PoleMembreViewSet,
    PoleMembershipViewSet,
    PieceJointeViewSet,
    PoleViewSet,
    ProfilUtilisateurViewSet,
    RegisterAPIView,
    ReportsAPIView,
    CustomTokenObtainPairView,
    RequeteViewSet,
    ReunionViewSet,
    TypeProblemeChoicesView,
)

router = DefaultRouter()
router.register("entreprises", EntrepriseViewSet, basename="entreprise")
router.register("notations-entreprises", NotationEntrepriseViewSet, basename="notation-entreprise")
router.register("delegues", DelegueSyndicalViewSet, basename="delegue")
router.register("poles", PoleViewSet, basename="pole")
router.register("pole-members", PoleMembreViewSet, basename="pole-member")
router.register("pole-memberships", PoleMembershipViewSet, basename="pole-membership")
router.register("profils", ProfilUtilisateurViewSet, basename="profil")
router.register("communications", CommunicationPostViewSet, basename="communication")
router.register("documents", DocumentSyndicalViewSet, basename="document")
router.register("requetes", RequeteViewSet, basename="requete")
router.register("maquettes-compte-rendu", MaquetteCompteRenduViewSet, basename="maquette-compte-rendu")
router.register("activite-templates", ActiviteTemplateViewSet, basename="activite-template")
router.register("dossiers", DossierViewSet, basename="dossier")
router.register("pieces-jointes", PieceJointeViewSet, basename="piece-jointe")
router.register("reunions", ReunionViewSet, basename="reunion")
router.register("notifications", NotificationViewSet, basename="notification")
router.register("auth", LogoutViewSet, basename="auth")

urlpatterns = [
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/register/", RegisterAPIView.as_view(), name="register"),
    path("type-probleme-choices/", TypeProblemeChoicesView.as_view(), name="type-probleme-choices"),
    path("reports/", ReportsAPIView.as_view(), name="reports"),
    path("gestion-documents/", include("documents.urls")),
    path("", include(router.urls)),
]
