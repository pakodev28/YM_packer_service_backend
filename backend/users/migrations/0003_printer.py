# Generated by Django 4.2.1 on 2023-06-16 22:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_table_available'),
    ]

    operations = [
        migrations.CreateModel(
            name='Printer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('barcode', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('user', models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='printer', to=settings.AUTH_USER_MODEL, verbose_name='принтер')),
            ],
        ),
    ]
