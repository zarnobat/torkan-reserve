from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Warehouse, Product, InventoryItem, StockMovement
from .forms import StockMovementForm
from config.admin_site import custom_admin_site
from django.urls import reverse
from django.utils.html import format_html
from jalali_date import date2jalali


class InventoryItemInline(admin.TabularInline):
    model = InventoryItem
    extra = 0
    can_delete = False
    readonly_fields = ("get_shamsi_date",)

    @admin.display(description='تاریخ ایجاد')
    def get_shamsi_date(self, obj):
        return date2jalali(obj.updated_at).strftime('%Y/%m/%d')


@admin.register(Warehouse, site=custom_admin_site)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "get_shamsi_date", "view_inventory_link")
    search_fields = ("name",)
    inlines = [InventoryItemInline]

    @admin.display(description='تاریخ ایجاد')
    def get_shamsi_date(self, obj):
        return date2jalali(obj.created_at).strftime('%Y/%m/%d')

    def view_inventory_link(self, obj):
        url = (
            reverse("admin:warehouse_inventoryitem_changelist")
            + f"?warehouse__id__exact={obj.id}"
        )
        return format_html(f"<a href='{url}'>مشاهده موجودی‌ها</a>")
    
    view_inventory_link.short_description = "موجودی‌ها"


@admin.register(Product, site=custom_admin_site)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "unit", "get_shamsi_date")
    list_filter = ("unit",)
    search_fields = ("name",)
    inlines = [InventoryItemInline]

    @admin.display(description='تاریخ ایجاد')
    def get_shamsi_date(self, obj):
        return date2jalali(obj.created_at).strftime('%Y/%m/%d')


@admin.register(InventoryItem, site=custom_admin_site)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("product", "warehouse", "colored_quantity", "get_unit_display")
    list_filter = ("warehouse", "product")

    def get_unit_display(self, obj):
        return obj.product.get_unit_display()
    get_unit_display.short_description = "واحد اندازه گیری"

    def colored_quantity(self, obj):
        color="red" if obj.quantity < 5 else "black" 
        return format_html(f"<span style='color:{color}'>{obj.quantity}</span>")
    colored_quantity.short_description = "موجودی"


@admin.register(StockMovement, site=custom_admin_site)
class StockMovementAdmin(admin.ModelAdmin):
    form = StockMovementForm
    list_display = ("warehouse", "product", "movement_type_emoji", "quantity", "get_unit_display", "get_shamsi_date")
    list_filter = ("movement_type", "warehouse", "product", "created_at")
    search_fields = ("product__name", "warehouse__name", "note")

    def get_unit_display(self, obj):
        return obj.product.get_unit_display()
    get_unit_display.short_description = "واحد اندازه گیری"

    @admin.display(description='تاریخ ایجاد')
    def get_shamsi_date(self, obj):
        return date2jalali(obj.created_at).strftime('%Y/%m/%d')
    

    def movement_type_emoji(self, obj):
        if obj.movement_type == StockMovement.IN:
            return "✅ ورود"
        elif obj.movement_type == StockMovement.OUT:
            return "❌ خروج"
        else:
            return "🔁 انتقال"
    movement_type_emoji.short_description = "نوع عملیات"

    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)