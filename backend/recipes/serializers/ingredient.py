from rest_framework import serializers as _serializers

from ..models import Ingredient as _Ingredient


class IngredientSerializer(_serializers.ModelSerializer):
    """
    Сериализатор модели Ingredient:
    возвращает поля id, name и measurement_unit.
    """

    class Meta:
        model = _Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )

    # Дополнительные методы сериализатора можно разместить здесь
