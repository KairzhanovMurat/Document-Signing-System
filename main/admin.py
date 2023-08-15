from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from . import models


# Register your models here.

class DefaultUserAdmin(UserAdmin):
    ordering = ['id']
    list_display = ['email', 'first_name', 'last_name']
    fieldsets = (
        (None, {'fields':
                    ('email',
                     'first_name',
                     'last_name',
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
                     'last_name',
                     'email',
                     'password1',
                     'password2',
                     'is_active',
                     'is_staff',
                     'is_superuser'
                 )}),
    )


admin.site.register(models.DefaultUser, DefaultUserAdmin)
admin.site.register(models.Document)
admin.site.register(models.ApprovalRequest)
