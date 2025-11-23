from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import laboratory
from .models import LabResult

@receiver(post_save, sender=LabResult)
def lab_result(sender, instance, created, **kwargs):
    if created:
        laboratory(
            instance.user.name,
            instance.serial_number,
            instance.user.phone_number,
        )