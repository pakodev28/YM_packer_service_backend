import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .cargotypes_constants import PACKET, BUBBLE_WRAP, STRETCH

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
    created_at = models.DateTimeField(
        "Дата создания заказа",
        auto_now_add=True,
    )

    class Meta:
        ordering = ["status"]
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def save(self, *args, **kwargs):
        # Не работает
        total_volume = 0.0
        for order_sku in self.order_skus.all():
            sku_volume = order_sku.sku.volume
            total_volume += sku_volume * order_sku.amount
        self.pack_volume = total_volume
        super().save(*args, **kwargs)

    @property
    def total_skus_quantity(self):
        """Возвращеает общее количество всех видов sku в заказе"""
        total = 0
        for order_sku in self.order_skus.all():
            total += order_sku.amount
        return total


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
    name = models.CharField("Название товара", max_length=255)

    class Meta:
        ordering = ["sku"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    @property
    def volume(self):
        """Возвращает объем sku"""
        return self.length * self.width * self.height

    @property
    def help_text(self):
        """Возвращает подсказку для Sku на основе cargotypes"""
        cargotypes = self.cargotypes.values_list("cargotype", flat=True)

        cargotype_help_text = []

        if cargotypes:
            if any(cargotype in cargotypes for cargotype in PACKET):
                cargotype_help_text.append("packet")

            if any(cargotype in cargotypes for cargotype in BUBBLE_WRAP):
                cargotype_help_text.append("bubble_wrap")

            if any(cargotype in cargotypes for cargotype in STRETCH):
                cargotype_help_text.append("stretch")

        return cargotype_help_text

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
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_skus"
    )
    sku = models.ForeignKey(Sku, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()  # Количество товара в заказе

    class Meta:
        verbose_name = "Товары в заказе"
        verbose_name_plural = "Товары в заказе"


class Table(models.Model):
    name = models.CharField(max_length=100, unique=True)
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        related_name="table",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Стол"
        verbose_name_plural = "Столы"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "user"], name="unique_name_user"
            )
        ]


class Printer(models.Model):
    barcode = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        related_name="printer",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Принтер"
        verbose_name_plural = "Принтеры"

    def __str__(self):
        return str(self.barcode)


class Cell(models.Model):
    """
    Ячейка.
    """

    barcode = models.UUIDField(
        default=uuid.uuid4, unique=True, primary_key=True
    )
    name = models.CharField(max_length=4)
    table = models.ForeignKey(
        Table, on_delete=models.SET_NULL, blank=True, null=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Ячейка"
        verbose_name_plural = "Ячейки"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "table"], name="unique_cell_table"
            )
        ]

    def __str__(self):
        return self.name


class CellOrderSku(models.Model):
    cell = models.ForeignKey(
        Cell, on_delete=models.CASCADE, related_name="cellorder_skus"
    )
    sku = models.ForeignKey(
        Sku, on_delete=models.CASCADE, related_name="cellorder_skus"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="cellorder_skus"
    )
    quantity = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Ячейка с товарами из заказа"
        verbose_name_plural = "Ячейки с товарами из заказа"

    def save(self, *args, **kwargs):
        if not self.order.sku.filter(pk=self.sku.pk).exists():
            raise ValidationError("SKU does not belong to the current order")

        super().save(*args, **kwargs)
