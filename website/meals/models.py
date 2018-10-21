from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


class Registrar(models.Model):
    """
    Model for meal registrars
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.CharField(max_length=100)
    registration_count = models.IntegerField(default=0)
    phone = models.CharField(max_length=10)


@receiver(post_save, sender=User)
def create_registrar(sender, instance, created, **kwargs):
    """
    Receiver to ensure Registrars get instantiated when Users are created
    """
    if created:
        Registrar.objects.create(user=instance)
