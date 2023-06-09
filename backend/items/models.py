import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class CartonType(models.Model):
    cartontype = models.CharField(max_length=255)
    length = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()

    def __str__(self):
        return self.cartontype


class CargoType(models.Model):
    cargotype = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=255)

    def __str__(self):
        return str(self.cargotype)


class Sku(models.Model):
    sku = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    length = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    available_quantity = models.PositiveIntegerField(default=0)
    goods_wght = models.FloatField(default=0.0)
    cargotypes = models.ManyToManyField(CargoType)

    @property
    def volume(self):
        return self.length * self.width * self.height

    def __str__(self):
        return str(self.sku)


class Order(models.Model):
    STATUS_CHOICES = (
        ("forming", "Being Formed"),
        ("collecting", "Being Collected"),
        ("collected", "Collected"),
    )

    orderkey = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    whs = models.PositiveSmallIntegerField(default=0)
    box_num = models.PositiveSmallIntegerField(default=0)
    selected_cartontype = models.ForeignKey(
        CartonType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="selected_orders",
    )
    recommended_cartontype = models.ForeignKey(
        CartonType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="recommended_orders",
    )
    sel_calc_cube = models.FloatField(null=True, blank=True)
    pack_volume = models.FloatField(null=True, blank=True)
    who = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )
    trackingid = models.UUIDField(
        default=uuid.uuid4, editable=False, null=True, blank=True
    )


class OrderSku(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="orderskus"
    )
    sku = models.ForeignKey(Sku, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
