from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from .forms import validate_meal_count, validate_zip_code


class Registrar(models.Model):
    """
    Model for meal registrars
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_registrar(sender, instance, created, **kwargs):
    """
    Receiver to ensure Registrars get instantiated when Users are created
    """
    if created:
        Registrar.objects.create(user=instance)


class Registration(models.Model):
    """
    Model for meal registration entry
    """
    registrar = models.ForeignKey(Registrar, on_delete=models.CASCADE)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    # currently no validator for phone number
    phone = models.CharField(max_length=20)
    town = models.CharField(max_length=100)
    zip_code = models.CharField(
        max_length=5,
        validators=[validate_zip_code]
    )
    address = models.CharField(max_length=100)
    unit = models.CharField(max_length=100)
    meal_count = models.IntegerField(
        validators=[validate_meal_count]
    )
    details = models.CharField(max_length=1000)

    def __str__(self):
        return "%s, %s (%s)" % (self.last_name, self.first_name, self.town)
