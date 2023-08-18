from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.urls import reverse

from . import validators
from .managers import DefaultUserManager


def file_upload_path(instance, filename):
    return f'{instance.user.email}/files/{filename}'


def image_upload_path(instance, filename):
    return f'{instance.email}/image/{filename}'


# Create your models here.

class DefaultUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    sign_image = models.ImageField(blank=True, upload_to=image_upload_path)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.email

    USERNAME_FIELD = 'email'
    objects = DefaultUserManager()


class Document(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to=file_upload_path,
                            validators=[validators.validate_pdf], unique=True)
    description = models.CharField(max_length=128)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.description

    def get_absolute_url(self):
        return reverse('detail', args=[str(self.pk)])


class ApprovalRequest(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sender')
    receivers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='receivers')
    initial_receivers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='initial_receivers')
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    requested_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender} approval request for {self.document.description}'
