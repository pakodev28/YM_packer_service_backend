from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# Заказы
class Order(models.Model):
    who = models.ForeignKey(User, on_delete=models.CASCADE)  # упаковщик
    selected_cartontype = models.ForeignKey('Carton', on_delete=models.CASCADE)  # код упаковки, которая была выбрана пользователем
    selected_carton = models.ForeignKey('Carton', on_delete=models.CASCADE)  # код упаковки, которая была выбрана пользователем (дубль)
    recommended_cartontype = models.ForeignKey('Carton', on_delete=models.CASCADE)  # код упаковки, рекомендованной алгоритмом
    recommended_carton = models.ForeignKey('Carton', on_delete=models.CASCADE)  # код упаковки, рекомендованной алгоритмом (дубль)
    sku = models.ForeignKey('SKU', on_delete=models.CASCADE)  # id товара
    vhs = models.IntegerField()  # код сортировочного центра
    orderkey = models.IntegerField()  # id заказа
    box_num = models.PositiveIntegerField()  # количество коробок
    sel_calc_cube = models.IntegerField()  # объём выбранной упаковки
    pack_volume = models.IntegerField()  # рассчитанный объём упакованных товаров
    rec_calc_cube = models.IntegerField()  # ???
    goods_wght = models.FloatField()  # вес товара
    trackingid = models.IntegerField()  # id доставки


# Карготипы товаров
class SkuCargotypes(models.Model):
    sku = models.ForeignKey('SKU', on_delete=models.CASCADE)  # id товара
    cargotype = models.ForeignKey('CargotypeInfo', on_delete=models.CASCADE)  # карготип товара


# Описание карготипов
class CargotypeInfo(models.Model):
    cargotype = models.CharField(max_length=128)  # карготип
    description = models.CharField(max_length=128)  # описание


# Товары
class SKU(models.Model):
    sku_id = models.IntegerField()  # id товара
    a = models.IntegerField()  # размеры
    b = models.IntegerField()  # размеры
    c = models.IntegerField()  # размеры


# Характеристики упаковок
# (Таблица с идентификаторами и линейными размерами упаковок)
class Carton(models.Model):
    cartontype = models.IntegerField()  # идентификатор (код) упаковки
    length = models.IntegerField()  # линейные размеры упаковки
    width = models.IntegerField()  # линейные размеры упаковки
    heigth = models.IntegerField()  # линейные размеры упаковки
    displayfrack = models.IntegerField()  # коробка есть на складе (не учитывать для наших целей)


# Стоимость упаковок
class CartonPrice(models.Model):
    ...
