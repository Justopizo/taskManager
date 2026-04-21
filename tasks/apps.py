"""Application configuration for the tasks app."""

from django.apps import AppConfig


class TasksConfig(AppConfig):
    """Configure the tasks application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "tasks"

    def ready(self) -> None:
        """Import signals when the app is ready."""
        from . import signals  # noqa: F401
