from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomUser, Customer

@receiver(post_save, sender=CustomUser)
def create_customer(sender, instance, created, **kwargs):
    if created:
        full_name = instance.first_name + " " + instance.last_name
        Customer.objects.create(user=instance, full_name = full_name)

@receiver(post_save, sender=CustomUser)
def save_customer(sender, instance, **kwargs):
    instance.customer.full_name = instance.first_name + " " + instance.last_name
    instance.customer.save()