# recipes/filters.py

"""
Набор фильтров для приложения recipes,
позволяет фильтровать ингредиенты по начальным символам имени.
"""

# Сторонняя библиотека фильтрации
from django_filters import rest_framework as _df_filters

# Локальный импорт модели
from .models import Ingredient as _Ing


class IngredientFilter(_df_filters.FilterSet):
    """
    Фильтр ингредиентов по полю name с учётом регистра.
    Использует lookup_expr 'istartswith' для начала строки.
    """
    name = _df_filters.CharFilter(
        field_name="name",
        lookup_expr="istartswith",
        label="Начало названия",
    )

    class Meta:
        """Метаданные фильтра: модель и доступные поля."""
        model = _Ing
        fields = ("name",)
