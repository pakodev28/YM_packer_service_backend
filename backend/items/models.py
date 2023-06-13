import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Order(models.Model):
    """
    Заказ.
    """

    STATUS_CHOICES = (
        ("forming", "Being Formed"),
        ("collecting", "Being Collected"),
        ("collected", "Collected"),
    )
    orderkey = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True
    )  # id заказа
    who = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        blank=True,
        null=True,
    )
    sku = models.ManyToManyField(
        "Sku",
        through="OrderSku",
        verbose_name="Товары",
        help_text="Выберите товары",
        related_name="orders",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES
    )  # Статус заказа
    whs = models.PositiveSmallIntegerField(
        default=0
    )  # код сортировочного центра
    box_num = models.PositiveSmallIntegerField(
        blank=True, null=True
    )  # количество коробок
    selected_cartontype = models.ForeignKey(
        "CartonType",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="selected_orders",
    )  # код упаковки, которая была выбрана пользователем
    recommended_cartontype = models.ForeignKey(
        "CartonType",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="recommended_orders",
    )  # код упаковки, рекомендованной алгоритмом
    sel_calc_cube = models.FloatField(
        null=True, blank=True
    )  # объём выбранной упаковки
    pack_volume = models.FloatField(
        null=True, blank=True
    )  # рассчитанный объём упакованных товаров
    tracking_id = models.UUIDField(
        editable=False, unique=True, null=True, blank=True
    )
    goods_weight = models.FloatField(
        blank=True, null=True
    )  # Общий вес товаров

    class Meta:
        ordering = ["status"]
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class Sku(models.Model):
    """
    Товар.
    """

    sku = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    length = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    quantity = models.PositiveIntegerField(default=0)  # Количество на складе
    goods_wght = models.FloatField(default=0.0)  # Вес товара
    cargotypes = models.ManyToManyField("CargoType")
    image = models.ImageField(upload_to="sku_images/", blank=True, null=True)

    class Meta:
        ordering = ["sku"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    @property
    def volume(self):
        return self.length * self.width * self.height

    def __str__(self):
        return str(self.sku)


class CargoType(models.Model):
    """
    Описание карготипов.
    """

    cargotype = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=255)

    class Meta:
        ordering = ["cargotype"]
        verbose_name = "Карготип"
        verbose_name_plural = "Карготипы"

    def __str__(self):
        return str(self.cargotype)


class CartonType(models.Model):
    """Характеристики упаковок."""

    cartontype = models.CharField(
        max_length=255
    )  # идентификатор (код) упаковки
    length = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()

    class Meta:
        ordering = ["cartontype"]
        verbose_name = "Упаковка"
        verbose_name_plural = "Упаковки"

    @property
    def get_volume(self):
        return self.length * self.width * self.height

    def __str__(self):
        return self.cartontype


class OrderSku(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    sku = models.ForeignKey(Sku, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()  # Количество товара в заказе


class Table(models.Model):
    name = models.CharField(max_length=100, unique=True)
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, related_name="table"
    )

    def __str__(self):
        return self.name


class Printer(models.Model):
    barcode = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, related_name="printer"
    )

    def __str__(self):
        return str(self.barcode)
