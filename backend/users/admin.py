from django.contrib import admin as _admin
from django.contrib.auth.admin import UserAdmin as _BaseUserAdmin

from .models import Subscription, User


@_admin.register(User)
class UserAdmin(_BaseUserAdmin):
    """
    Админка модели User: отображает ключевые поля и поддерживает поиск.
    """
    # Колонки, отображаемые в списке пользователей
    _cols = ("username", "email", "is_active", "is_staff")
    list_display = _cols

    # Поля для поиска
    _search = ("username", "email")
    search_fields = _search

    # Группировка полей для отображения и редактирования
    _fieldset_groups = (
        (None, {"fields": ("username", "email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {"fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )},
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    fieldsets = _fieldset_groups

    # Поля при создании нового пользователя в админке
    _add_groups = (
        (
            None,
            {"classes": ("wide",), "fields": ("username", "email", "password1", "password2")},
        ),
    )
    add_fieldsets = _add_groups


@_admin.register(Subscription)
class SubscriptionAdmin(_admin.ModelAdmin):
    """
    Админка для моделей Subscription: связь пользователя и автора.
    """
    # Список колонок для модели Subscription
    _subs_list = ("id", "user", "author")
    list_display = _subs_list

    # Поля для поиска подписок
    _subs_search = ("user__username", "author__username")
    search_fields = _subs_search
