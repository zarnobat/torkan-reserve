from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Warehouse(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="نام انبار"
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="موقعیت / آدرس انبار"
    )
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="مدیر انبار"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    class Meta:
        verbose_name = "انبار"
        verbose_name_plural = "انبارها"

    def __str__(self):
        return self.name


class Product(models.Model):
    UNIT_CHOICES = [
        ("PCS", "عدد"),
        ("GR", "گرم"),
        ("KG", "کیلوگرم"),
        ("LTR", "لیتر"),
        ("M", "متر"),
        ("CM", "سانتی‌متر"),
        ("BOX", "بسته"),
    ]
    
    name = models.CharField(
        max_length=100,
        verbose_name="نام کالا"
    )
    unit = models.CharField(
        max_length=20,
        choices=UNIT_CHOICES,
        default="PCS",
        verbose_name="واحد اندازه‌گیری"
    ) 
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    class Meta:
        unique_together = ("name",)
        verbose_name = "کالا"
        verbose_name_plural = "کالاها"

    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="انبار"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="inventory_records",
        verbose_name="کالا"
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="موجودی فعلی"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ آخرین بروزرسانی"
    )

    class Meta:
        unique_together = ("warehouse", "product")
        verbose_name = "موجودی انبار"
        verbose_name_plural = "موجودی انبارها"

    def __str__(self):
        return f"{self.product.name} در {self.warehouse.name}: {self.quantity}"


class StockMovement(models.Model):
    """Any change in inventory (input, output, transfer) is recorded here."""

    IN = "IN"
    OUT = "OUT"
    TRANSFER = "TRANSFER"
    MOVEMENT_TYPE_CHOICES = [
        (IN, "ورود"),
        (OUT, "خروج"),
        (TRANSFER, "انتقال"),
    ]

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        verbose_name="انبار مبدا"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="کالا"
    )
    movement_type = models.CharField(
        max_length=10,
        choices=MOVEMENT_TYPE_CHOICES,
        verbose_name="نوع عملیات"
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="تعداد / مقدار"
    )
    related_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transfers",
        verbose_name="انبار مقصد (در صورت انتقال)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت عملیات"
    )
    note = models.TextField(
        blank=True,
        verbose_name="توضیحات"
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="ثبت‌کننده",
    )



    class Meta:
        verbose_name = "تغییر موجودی"
        verbose_name_plural = "تغییرات موجودی"

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} ({self.quantity})"
