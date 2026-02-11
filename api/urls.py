from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    DelegueSyndicalViewSet,
    DossierViewSet,
    EntrepriseViewSet,
    LogoutViewSet,
    NotificationViewSet,
    PoleMembreViewSet,
    PieceJointeViewSet,
    PoleViewSet,
    ProfilUtilisateurViewSet,
    RegisterAPIView,
    CustomTokenObtainPairView,
    RequeteViewSet,
    ReunionViewSet,
)

router = DefaultRouter()
router.register("entreprises", EntrepriseViewSet, basename="entreprise")
router.register("delegues", DelegueSyndicalViewSet, basename="delegue")
router.register("poles", PoleViewSet, basename="pole")
router.register("pole-members", PoleMembreViewSet, basename="pole-member")
router.register("profils", ProfilUtilisateurViewSet, basename="profil")
router.register("requetes", RequeteViewSet, basename="requete")
router.register("dossiers", DossierViewSet, basename="dossier")
router.register("pieces-jointes", PieceJointeViewSet, basename="piece-jointe")
router.register("reunions", ReunionViewSet, basename="reunion")
router.register("notifications", NotificationViewSet, basename="notification")
router.register("auth", LogoutViewSet, basename="auth")

urlpatterns = [
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/register/", RegisterAPIView.as_view(), name="register"),
    path("", include(router.urls)),
]
