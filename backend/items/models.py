import uuid

from django.db import models
from django.core.validators import MinValueValidator


class CartonType(models.Model):
    cartontype = models.CharField(max_length=255)
    length = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()

    def __str__(self):
        return self.cartontype


class CargoType(models.Model):
    cargotype = models.IntegerField(unique=True)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.cargotype


class Sku(models.Model):
    sku = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True
    )
    length = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    cargotypes = models.ManyToManyField(CargoType)

    def __str__(self):
        return self.sku


class Order(models.Model):
    STATUS_CHOICES = (
        ("forming", "Being Formed"),
        ("collecting", "Being Collected"),
        ("collected", "Collected"),
    )

    orderkey = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True
    )
    skus = models.ManyToManyField(Sku, through="OrderSku")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)


class OrderSku(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    sku = models.ForeignKey(Sku, on_delete=models.CASCADE)
