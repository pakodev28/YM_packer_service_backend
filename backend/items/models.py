import uuid

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from .cargotypes_constants import BUBBLE_WRAP, PACKET, STRETCH
from users.models import Table

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
        default=uuid.uuid4,
        editable=False,
        unique=True,
        primary_key=True,
        verbose_name="ID заказа",
    )  # id заказа
    who = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        blank=True,
        null=True,
        verbose_name="Пользователь",
    )
    skus = models.ManyToManyField(
        "Sku",
        through="OrderSku",
        verbose_name="Товары",
        help_text="Выберите товары",
        related_name="orders",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, verbose_name="Статус заказа"
    )
    whs = models.PositiveSmallIntegerField(
        default=0, verbose_name="Код сортировочного центра"
    )
    total_packages = models.PositiveSmallIntegerField(
        blank=True, null=True, verbose_name="Количество упаковок в заказе"
    )
    selected_cartontypes = models.ManyToManyField(
        "CartonType",
        blank=True,
        related_name="selected_orders",
        verbose_name="Выбранные типы упаковки",
    )
    recommended_cartontype = models.ForeignKey(
        "CartonType",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="recommended_orders",
        verbose_name="Рекомендуемый тип упаковки",
    )
    sel_calc_cube = models.FloatField(
        null=True, blank=True, verbose_name="Объем выбранной упаковки"
    )
    pack_volume = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Рассчитанный объем упакованных товаров",
    )
    tracking_id = models.UUIDField(
        editable=False,
        unique=True,
        null=True,
        blank=True,
        verbose_name="ID доставки",
    )
    goods_weight = models.FloatField(
        blank=True, null=True, verbose_name="Общий вес товаров"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    class Meta:
        ordering = ["status"]
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

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
    length = models.FloatField(verbose_name="Длина")
    width = models.FloatField(verbose_name="Ширина")
    height = models.FloatField(verbose_name="Высота")
    quantity = models.PositiveIntegerField(
        default=0, verbose_name="Количество на складе"
    )
    goods_wght = models.FloatField(default=0.0, verbose_name="Вес товара")
    cargotypes = models.ManyToManyField("CargoType", verbose_name="Карготипы")
    image = models.ImageField(
        upload_to="sku_images/",
        blank=True,
        null=True,
        verbose_name="Изображение",
    )
    name = models.CharField(max_length=255, verbose_name="Название товара")

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

    cargotype = models.PositiveIntegerField(
        unique=True, verbose_name="Карготип"
    )
    description = models.CharField(max_length=255, verbose_name="Описание")

    class Meta:
        ordering = ["cargotype"]
        verbose_name = "Карготип"
        verbose_name_plural = "Карготипы"

    def __str__(self):
        return str(self.cargotype)


class CartonType(models.Model):
    """Характеристики упаковок."""

    barcode = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        primary_key=True,
        verbose_name="Штрихкод",
    )
    cartontype = models.CharField(
        max_length=255, verbose_name="Тип упаковки"
    )  # идентификатор (код) упаковки
    length = models.FloatField(verbose_name="Длина")
    width = models.FloatField(verbose_name="Ширина")
    height = models.FloatField(verbose_name="Высота")

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
        Order,
        on_delete=models.CASCADE,
        related_name="order_skus",
        verbose_name="Заказ",
    )
    sku = models.ForeignKey(
        Sku, on_delete=models.CASCADE, verbose_name="Товар"
    )
    amount = models.PositiveIntegerField(
        verbose_name="Количество товара в заказе"
    )  # Количество товара в заказе
    packaging_number = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name="Номер упаковки в которой находится товар",
    )

    class Meta:
        verbose_name = "Товары в заказе"
        verbose_name_plural = "Товары в заказе"


# class Table(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#     user = models.OneToOneField(
#         User,
#         on_delete=models.SET_NULL,
#         related_name="table",
#         blank=True,
#         null=True,
#     )

#     def __str__(self):
#         return self.name

#     class Meta:
#         verbose_name = "Стол"
#         verbose_name_plural = "Столы"
#         constraints = [
#             models.UniqueConstraint(
#                 fields=["name", "user"], name="unique_name_user"
#             )
#         ]


# class Printer(models.Model):
#     barcode = models.UUIDField(default=uuid.uuid4, unique=True)
#     user = models.OneToOneField(
#         User,
#         on_delete=models.SET_NULL,
#         related_name="printer",
#         blank=True,
#         null=True,
#     )

#     class Meta:
#         verbose_name = "Принтер"
#         verbose_name_plural = "Принтеры"

#     def __str__(self):
#         return str(self.barcode)


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
        if not self.order.skus.filter(pk=self.sku.pk).exists():
            raise ValidationError("SKU does not belong to the current order")

        super().save(*args, **kwargs)
