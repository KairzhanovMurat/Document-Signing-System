from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from .managers import DefaultUserManager
from django.conf import settings
from . import validators
from django.urls import reverse


def user_upload_path(instance, filename):
    return f'user_{instance.user.email}/{filename}'


# Create your models here.

class DefaultUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
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
    file = models.FileField(upload_to=user_upload_path,
                            validators=[validators.validate_pdf])
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
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    requested_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender} approval request for {self.document.description}'