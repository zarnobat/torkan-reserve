from .models import InventoryItem, StockMovement
from django.core.exceptions import ValidationError


def apply_stock_movement(instance: StockMovement):

    item, _ = InventoryItem.objects.get_or_create(
        warehouse = instance.warehouse,
        product = instance.product,
    )

    if instance.movement_type == StockMovement.IN:
        item.quantity += instance.quantity

    elif instance.movement_type == StockMovement.OUT:
        if item.quantity < instance.quantity:
            raise ValidationError(
                f"موجودی کافی برای خروج کالا '{instance.product.name}' در انبار '{instance.warehouse.name}' وجود ندارد."
            )
        item.quantity -= instance.quantity

    elif instance.movement_type == StockMovement.TRANSFER and instance.related_warehouse:
        """Subtract from the origin."""
        item.quantity -= instance.quantity
        item.save()

        """add to destination"""
        related_item, _ = InventoryItem.objects.get_or_create(
            warehouse=instance.related_warehouse,
            product=instance.product,
            defaults={"quantity": 0}
        )
        related_item.quantity += instance.quantity
        related_item.save()

    item.save() 