from django.contrib.admin import register, StackedInline, site
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from website.meals.models import Registrar

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
    list_display = ('username', 'first_name', 'last_name', 'organization', 'registration_count', 'is_staff')
    inlines = [
        RegistrarInline
    ]

    # functions to derive foreign key properties
    def organization(self, user):
        return user.registrar.organization

    def registration_count(self, user):
        return user.registrar.registration_count