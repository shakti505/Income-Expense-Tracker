# Generated by Django 5.1.3 on 2025-01-13 06:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_alter_user_first_name_alter_user_last_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activetokens',
            name='token',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='activetokens',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='token', to=settings.AUTH_USER_MODEL),
        ),
    ]
