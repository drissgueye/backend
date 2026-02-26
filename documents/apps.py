from django.apps import AppConfig


class DocumentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "documents"
    verbose_name = "Gestion des documents"

    def ready(self):
        import documents.signals  # noqa: F401 - enregistre les signaux (HistoriqueAction → DocumentHistorique)
