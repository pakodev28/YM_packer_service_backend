# Generated by Django 4.2.1 on 2023-06-17 21:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("items", "0002_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="order",
            old_name="sku",
            new_name="skus",
        ),
    ]