from django.contrib import admin
from .models import (
    Order,
    Sku,
    CargoType,
    CartonType,
    OrderSku,
    Table,
    Printer,
    Cell,
    CellOrderSku,
)


class OrderSkuInline(admin.TabularInline):
    model = OrderSku
    extra = 1
    verbose_name_plural = "Order Skus"


class SkuInline(admin.TabularInline):
    model = Sku.cargotypes.through
    extra = 1
    verbose_name_plural = "Skus in Cargo Type"


class CellOrderSkuInline(admin.TabularInline):
    model = CellOrderSku
    extra = 1
    verbose_name_plural = "Skus in Cell"


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderSkuInline]
    exclude = ("sku",)
    list_display = ("orderkey", "status", "whs", "box_num")
    list_filter = ("status",)
    search_fields = ("orderkey",)


class SkuAdmin(admin.ModelAdmin):
    inlines = [SkuInline]
    list_display = ("sku", "length", "width", "height", "quantity")
    list_filter = ("cargotypes",)
    search_fields = ("sku",)


class CellAdmin(admin.ModelAdmin):
    inlines = [CellOrderSkuInline]
    list_display = ("code", "order", "table")
    search_fields = ("code",)


admin.site.register(Order, OrderAdmin)
admin.site.register(Sku, SkuAdmin)
admin.site.register(CargoType)
admin.site.register(CartonType)
admin.site.register(Table)
admin.site.register(Printer)
admin.site.register(Cell, CellAdmin)
