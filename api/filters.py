from __future__ import annotations

import django_filters

from requetes.models import Dossier, Notification, PieceJointe, Requete, Reunion


class RequeteFilter(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Requete
        fields = ["statut", "pole", "entreprise", "priorite", "type_probleme", "created_at"]


class DossierFilter(django_filters.FilterSet):
    date_ouverture = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Dossier
        fields = ["statut", "pole", "date_ouverture"]


class PieceJointeFilter(django_filters.FilterSet):
    uploaded_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = PieceJointe
        fields = ["type_document", "requete", "uploaded_at"]


class ReunionFilter(django_filters.FilterSet):
    date_heure = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Reunion
        fields = ["type_reunion", "statut", "dossier", "date_heure"]


class NotificationFilter(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Notification
        fields = ["type_notification", "is_read", "created_at"]
