from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from .models import Customer


@receiver(post_save, sender=Customer)
def generate_magento_sku(sender, instance, created, **kwargs):
    if created and not instance.magento_sku:
        instance.magento_sku = get_random_string(length=10)
        instance.save()