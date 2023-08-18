# Generated by Django 4.2.4 on 2023-08-17 10:43

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_approvalrequest_is_approved'),
    ]

    operations = [
        migrations.AddField(
            model_name='approvalrequest',
            name='initial_receivers',
            field=models.ManyToManyField(related_name='initial_receivers', to=settings.AUTH_USER_MODEL),
        ),
    ]
