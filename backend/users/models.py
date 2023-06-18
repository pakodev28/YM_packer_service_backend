import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField("Имя", help_text="Введите имя", max_length=150)
    last_name = models.CharField("Фамилия", help_text="Ведите фамилию", max_length=150)
    created_date = models.DateTimeField("Дата регистрации", auto_now_add=True)
    table = models.OneToOneField(
            'Table',
            on_delete=models.SET_NULL,
            verbose_name='стол',
            related_name='user',
            null=True,
            blank=True)
    printer = models.OneToOneField(
            'Printer',
            on_delete=models.SET_NULL,
            verbose_name='принтер',
            related_name='user',
            null=True,
            blank=True)

    class Meta:
        ordering = ("id",)
        verbose_name = "Упаковщики"
        verbose_name_plural = "Упаковщики"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Table(models.Model):

    name = models.CharField("Название", max_length=32, unique=True)
    description = models.TextField("Описание", max_length=128)
    available = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Стол"
        verbose_name_plural = "Столы"

    def __str__(self):
        return self.name


class Printer(models.Model):
    barcode = models.UUIDField(default=uuid.uuid4, unique=True)

    def __str__(self):
        return str(self.barcode)
