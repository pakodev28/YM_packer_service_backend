from django.contrib import admin

from .models import *


class OrderSkuInline(admin.StackedInline):
    model = OrderSku
    min_num = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['orderkey', 'who', 'status']  # TODO разобраться с картинками
    list_per_page = 6
    inlines = (OrderSkuInline,)


admin.site.register(Sku)
admin.site.register(CartonType)
admin.site.register(CargoType)
