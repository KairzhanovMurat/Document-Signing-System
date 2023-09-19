from django.apps import AppConfig
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        import main.signals

        from .signals import delete_document_file, delete_image_file
