from django.db.models.signals import post_save
from django.db import transaction
from django.dispatch import receiver
from .models import StockMovement
from .services import apply_stock_movement


@receiver(post_save, sender=StockMovement)
def stock_movement_post_save(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            apply_stock_movement(instance)