from django import forms
from django.core.exceptions import ValidationError
from .models import StockMovement, InventoryItem

class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        movement_type = cleaned_data.get("movement_type")
        quantity = cleaned_data.get("quantity")
        warehouse = cleaned_data.get("warehouse")
        product = cleaned_data.get("product")
        related_warehouse = cleaned_data.get("related_warehouse")

        if not warehouse or not product or not quantity:
            return cleaned_data

        """Goods departure"""
        if movement_type == StockMovement.OUT:
            item, _ = InventoryItem.objects.get_or_create(
                warehouse=warehouse,
                product=product,
                defaults={"quantity": 0}
            )
            if item.quantity < quantity:
                raise ValidationError(
                    f"موجودی کافی برای خروج کالا '{product.name}' در انبار '{warehouse.name}' وجود ندارد."
                )

        """Transfer of goods"""
        if movement_type == StockMovement.TRANSFER and related_warehouse:
            item, _ = InventoryItem.objects.get_or_create(
                warehouse=warehouse,
                product=product,
                defaults={"quantity": 0}
            )
            if item.quantity < quantity:
                raise ValidationError(
                    f"موجودی کافی برای انتقال کالا '{product.name}' از انبار '{warehouse.name}' وجود ندارد."
                )

        return cleaned_data