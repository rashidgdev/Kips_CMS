from django.apps import AppConfig


class DaybookConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.daybook'
    label = 'daybook'
    verbose_name = 'Faculty Day Book'

    def ready(self):
        from . import signals  # noqa: F401
