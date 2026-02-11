from django.apps import AppConfig


class RequetesConfig(AppConfig):
    name = 'requetes'

    def ready(self) -> None:
        from . import signals  # noqa: F401