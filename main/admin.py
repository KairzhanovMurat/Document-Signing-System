from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from . import models


# Register your models here.

class RequestReceivers(admin.TabularInline):
    model = models.RequestReceivers
    extra = 1


class DefaultUserAdmin(UserAdmin, admin.ModelAdmin):
    ordering = ['id']
    list_display = ['email', 'first_name', 'second_name']
    inlines = (RequestReceivers,)
    fieldsets = (
        (None, {'fields':
                    ('email',
                     'first_name',
                     'second_name',
                     'last_name',
                     'job_position',
                     'sign_image',
                     'password')}),
        (_('Permissions'), {'fields':
                                ('is_active',
                                 'is_staff',
                                 'is_superuser')}),
        (_('Important dates'), {'fields':
                                    ('last_login',)})

    )
    add_fieldsets = (
        (None,
         {
             'classes': ('wide',),
             'fields':
                 (
                     'first_name',
                     'second_name',
                     'last_name',
                     'email',
                     'sign_image',
                     'job_position',
                     'password1',
                     'password2',
                     'is_active',
                     'is_staff',
                     'is_superuser'
                 )}),
    )


admin.site.register(models.DefaultUser, DefaultUserAdmin)
admin.site.register(models.Document)


class ApprovalRequestAdmin(admin.ModelAdmin):
    inlines = (RequestReceivers,)


admin.site.register(models.ApprovalRequest, ApprovalRequestAdmin)
