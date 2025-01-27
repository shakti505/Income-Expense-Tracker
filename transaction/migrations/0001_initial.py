# Generated by Django 5.1.3 on 2025-01-27 04:55

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('category', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField(blank=True)),
                ('type', models.CharField(choices=[('credit', 'Credit'), ('debit', 'Debit')], max_length=10)),
                ('is_deleted', models.BooleanField(default=False)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='category.category')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
