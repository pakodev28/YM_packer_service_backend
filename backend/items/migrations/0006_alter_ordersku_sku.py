# Generated by Django 4.2.1 on 2023-06-15 03:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0005_alter_ordersku_sku'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordersku',
            name='sku',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='items.sku'),
        ),
    ]