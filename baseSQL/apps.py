from django.apps import AppConfig


class BasesqlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'baseSQL'

    def ready(self):
        import baseSQL.signal    

