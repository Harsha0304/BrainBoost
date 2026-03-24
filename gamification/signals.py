from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserPoints


@receiver(post_save, sender=get_user_model())
def create_user_points(sender, instance, created, **kwargs):
    if created:
        UserPoints.objects.get_or_create(user=instance)
