from django.contrib import admin

from .models import (
    CargoType,
    CartonType,
    Cell,
    CellOrderSku,
    Order,
    OrderSku,
    Printer,
    Sku,
    Table,
)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("orderkey", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("orderkey", "status")
    readonly_fields = ("orderkey", "created_at")
    filter_horizontal = ("sku",)
    ordering = ("status",)


@admin.register(Sku)
class SkuAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "quantity")
    list_filter = ("quantity",)
    search_fields = ("sku", "name")


@admin.register(CargoType)
class CargoTypeAdmin(admin.ModelAdmin):
    list_display = ("cargotype", "description")
    search_fields = ("cargotype", "description")


@admin.register(CartonType)
class CartonTypeAdmin(admin.ModelAdmin):
    list_display = ("cartontype", "length", "width", "height")
    search_fields = ("cartontype",)


@admin.register(OrderSku)
class OrderSkuAdmin(admin.ModelAdmin):
    list_display = ("order", "sku", "amount")
    list_filter = ("order", "sku")
    search_fields = ("order__orderkey", "sku__sku")


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("name", "user")
    list_filter = ("user",)
    search_fields = ("name", "user__username")


@admin.register(Printer)
class PrinterAdmin(admin.ModelAdmin):
    list_display = ("barcode", "user")
    list_filter = ("user",)
    search_fields = ("barcode", "user__username")


@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ("barcode", "name", "table")
    list_filter = ("table",)
    search_fields = ("barcode", "name")


@admin.register(CellOrderSku)
class CellOrderSkuAdmin(admin.ModelAdmin):
    list_display = ("cell", "sku", "order", "quantity")
    list_filter = ("cell", "sku", "order")
    search_fields = ("cell__barcode", "sku__sku", "order__orderkey")
