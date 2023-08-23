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
    second_name = models.CharField(max_length=128, null=True)
    last_name = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    sign_image = models.ImageField(blank=True, upload_to=image_upload_path)
    job_position = models.CharField(max_length=255, blank=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def get_full_name(self):
        return f'{self.first_name} {self.second_name}'

    def get_initials(self):
        return f'{self.second_name} {self.first_name[0]}.{self.last_name[0]}'

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
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='approval_requests')
    receivers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='receivers', through='RequestReceivers')
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='approval_requests')
    requested_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender} approval request for {self.document.description}'


class RequestReceivers(models.Model):
    request = models.ForeignKey(ApprovalRequest, on_delete=models.CASCADE)
    receivers = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)

    @staticmethod
    def are_all_approved(request_instance):
        return RequestReceivers.objects.filter(request=request_instance, is_approved=False).count() == 0


class UserApprovalData(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    approval_request = models.ForeignKey(ApprovalRequest, on_delete=models.CASCADE)
    browser = models.CharField(max_length=255, blank=True)
    ip_address = models.CharField(max_length=255, blank=True)
    approval_time = models.DateTimeField()