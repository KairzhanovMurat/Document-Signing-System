import os
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from .models import Document


@receiver(pre_delete, sender=Document)
def delete_document_file(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
