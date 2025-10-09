from django.apps import AppConfig

class CrossAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.crossapp'
    verbose_name = 'Cross Application'
