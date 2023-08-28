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
    first_name = models.CharField(max_length=128, verbose_name='Имя')
    second_name = models.CharField(max_length=128, null=True, verbose_name='Фамилия')
    last_name = models.CharField(max_length=128, verbose_name='Отчество')
    email = models.EmailField(unique=True, verbose_name='внутренняя почта')
    sign_image = models.ImageField(blank=True, upload_to=image_upload_path, verbose_name='Изображение подписи')
    job_position = models.CharField(max_length=255, blank=True, verbose_name='Должность')

    is_staff = models.BooleanField(default=False, verbose_name='Доступ к админ панели')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    def get_full_name(self):
        return f'{self.first_name} {self.second_name}'

    def get_initials(self):
        return f'{self.second_name} {self.first_name[0]}. {self.last_name[0]}'

    def __str__(self):
        return f'{self.get_initials()} - {self.job_position}'

    USERNAME_FIELD = 'email'
    objects = DefaultUserManager()

    class Meta:
        verbose_name_plural = 'Пользователи'


class Document(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Владелец')
    file = models.FileField(upload_to=file_upload_path,
                            validators=[validators.validate_pdf], unique=True, verbose_name='Документ')
    description = models.CharField(max_length=128, verbose_name='Описание')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')
    is_approved = models.BooleanField(default=False, verbose_name='Статус подтверждения')

    def __str__(self):
        return self.description

    def get_absolute_url(self):
        return reverse('detail_doc', args=[str(self.pk)])

    class Meta:
        verbose_name_plural = 'Документы'


class ApprovalRequest(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='approval_requests',
                               verbose_name='Отправитель')
    receivers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='receivers', through='RequestReceivers',
                                       verbose_name='Получатели')
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='approval_requests',
                                 verbose_name='Документ')
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата запроса')
    is_approved = models.BooleanField(default=False, verbose_name='Статус подтверждения')

    def __str__(self):
        return f'Отправитель: {self.sender}.  Документ: {self.document.description}'

    class Meta:
        verbose_name_plural = 'Заявки на согласование'


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
