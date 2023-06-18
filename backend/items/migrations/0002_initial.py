# Generated by Django 4.2.1 on 2023-06-18 00:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0001_initial"),
        ("items", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="who",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="orders",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Пользователь",
            ),
        ),
        migrations.AddField(
            model_name="cellordersku",
            name="cell",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="cellorder_skus",
                to="items.cell",
            ),
        ),
        migrations.AddField(
            model_name="cellordersku",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="cellorder_skus",
                to="items.order",
            ),
        ),
        migrations.AddField(
            model_name="cellordersku",
            name="sku",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="cellorder_skus",
                to="items.sku",
            ),
        ),
        migrations.AddField(
            model_name="cell",
            name="table",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="users.table",
            ),
        ),
        migrations.AddConstraint(
            model_name="cell",
            constraint=models.UniqueConstraint(
                fields=("name", "table"), name="unique_cell_table"
            ),
        ),
    ]
