# Generated by Django 5.1.3 on 2025-01-09 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0002_transaction_is_deleted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]