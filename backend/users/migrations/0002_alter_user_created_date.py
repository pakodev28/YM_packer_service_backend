# Generated by Django 4.2.1 on 2023-06-09 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации'),
        ),
    ]
