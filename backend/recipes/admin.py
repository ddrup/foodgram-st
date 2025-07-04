# admin.py

# Django admin imported с псевдонимом
from django.contrib import admin as _admin_pkg

# Локальные модели с новыми алиасами
from .models import Favorite as _Favorite
from .models import Ingredient as _Ingredient
from .models import Recipe as _Recipe
from .models import RecipeIngredient as _RecipeIngr
from .models import ShoppingCart as _Cart


class RecipeIngrInline(_admin_pkg.TabularInline):
    """
    Inline для управления ингредиентами в редакторе рецепта.
    Позволяет добавить минимум одну связь.
    """

    model = _RecipeIngr
    extra = 1
    min_num = 1


@_admin_pkg.register(_Ingredient)
class IngredientAdmin(_admin_pkg.ModelAdmin):
    """
    Конфигурация админки Ingredient:
    выводит список полей и поддерживает поиск по имени.
    """

    list_display = ("id", "name", "measurement_unit")
    search_fields = ("name",)
    ordering = ("name",)


@_admin_pkg.register(_Recipe)
class RecipeAdmin(_admin_pkg.ModelAdmin):
    """
    Настройки админки Recipe:
    • Отображает ключевые поля и счётчик избранного;
    • Встраивает Inline для ингредиентов.
    """

    list_display = ("id", "name", "author", "cooking_time", "favorites_count")
    search_fields = ("name", "author__username")
    inlines = [RecipeIngrInline]
    fieldsets = (
        (
            None,
            {"fields": ("name", "author", "image", "text", "cooking_time")},
        ),
    )

    def favorites_count(self, obj):
        """
        Подсчитывает, сколько раз рецепт добавлен в избранное.
        """
        return _Favorite.objects.filter(recipe=obj).count()

    favorites_count.short_description = "Добавлено в избранное"


@_admin_pkg.register(_RecipeIngr)
class RecipeIngrAdmin(_admin_pkg.ModelAdmin):
    """
    Админка модели RecipeIngredient:
    позволяет редактировать связи рецепта и ингредиента.
    """

    list_display = ("id", "recipe", "ingredient", "amount")
    search_fields = ("recipe__name", "ingredient__name")


@_admin_pkg.register(_Favorite)
class FavoriteAdmin(_admin_pkg.ModelAdmin):
    """
    Административный интерфейс для избранного:
    связь пользователь–рецепт.
    """

    list_display = ("id", "user", "recipe")
    search_fields = ("user__username", "recipe__name")


@_admin_pkg.register(_Cart)
class ShoppingCartAdmin(_admin_pkg.ModelAdmin):
    """
    Админка для корзины покупок:
    связь пользователь–рецепт.
    """

    list_display = ("id", "user", "recipe")
    search_fields = ("user__username", "recipe__name")
