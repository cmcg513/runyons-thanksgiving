from django.contrib.admin import register, StackedInline, site, ModelAdmin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from website.meals.models import Registrar, Registration
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Sum

# unregister User admin interface so we can redefine
site.unregister(User)


class RegistrarInline(StackedInline):
    """
    Inline for Registrar
    """
    model = Registrar


@register(User)
class UserRegistrarAdmin(UserAdmin):
    """
    Admin interface for user
    """
    list_display = (
        'username',
        'first_name',
        'last_name',
        'organization',
        'registration_count',
        'meal_count',
        'is_staff'
    )
    inlines = [
        RegistrarInline
    ]

    # functions to derive foreign key properties
    def organization(self, user):
        return user.registrar.organization

    def registration_count(self, user):
        return Registration.objects.filter(registrar=user.registrar).count()

    def meal_count(self, user):
        agg = Registration.objects.filter(registrar=user.registrar).aggregate(Sum('meal_count'))
        return agg['meal_count__sum']


@register(Registrar)
class RegistrarAdmin(ModelAdmin):
    list_display = [
        'username',
        'first_name',
        'last_name',
        'organization'
    ]

    def username(self, registrar):
        return registrar.user.username

    def first_name(self, registrar):
        return registrar.user.first_name

    def last_name(self, registrar):
        return registrar.user.last_name


@register(Registration)
class RegistrationAdmin(ModelAdmin):
    list_display = [
        'first_name',
        'last_name',
        'phone',
        'town',
        'zip_code',
        'address',
        'meal_count',
        'registered_by'
    ]

    def registered_by(self, obj):
        link = reverse("admin:auth_user_change", args=[obj.registrar.user.id])
        return format_html('<a href="{}"><b>{}</b></a>', link, obj.registrar.user.username)

