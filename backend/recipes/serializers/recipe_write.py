from constants import MIN_COOKING_TIME as _MIN_TIME
from django.db import transaction as _transaction
from rest_framework import serializers as _serializers
from rest_framework.exceptions import ValidationError as _ValErr

from ..fields import Base64ImageField as _ImgField
from ..models import Ingredient as _Ingredient
from ..models import Recipe as _Recipe
from ..models import RecipeIngredient as _RecIng


class IngredientInRecipeSerializer(_serializers.Serializer):
    """
    Вложенный сериализатор для ингредиента в рецепте:
    принимает id и amount.
    """

    id = _serializers.IntegerField()
    amount = _serializers.IntegerField(min_value=1)


class RecipeWriteSerializer(_serializers.ModelSerializer):
    """
    Сериализатор записи рецепта:
    обрабатывает изображение в Base64, поля ингредиентов и валидацию.
    """

    image = _ImgField()
    ingredients = IngredientInRecipeSerializer(many=True)

    class Meta:
        model = _Recipe
        fields = (
            "id",
            "name",
            "image",
            "text",
            "cooking_time",
            "ingredients",
        )

    def validate_cooking_time(self, value):
        """
        Проверяет минимальное время готовки (_MIN_TIME).
        """
        if value < _MIN_TIME:
            raise _ValErr(f"Время готовки минимум {_MIN_TIME} минут.")
        return value

    def validate_ingredients(self, items):
        """
        Валидация поля ingredients:
        - не пустой список;
        - уникальность id;
        - существование ингредиента в БД.
        """
        if not items:
            raise _ValErr({"ingredients": "Поле 'ingredients' не может быть пустым."})

        seen_ids = set()
        for element in items:
            idx = element.get("id")
            if not _Ingredient.objects.filter(id=idx).exists():
                raise _ValErr({"ingredients": f"Ингредиент с id {idx} не существует."})
            if idx in seen_ids:
                raise _ValErr(
                    {"ingredients": f"Ингредиент с id {idx} указан несколько раз."}
                )
            seen_ids.add(idx)
        return items

    def validate(self, attrs):
        """
        Проверка при обновлении: ingredients не должны быть пустыми.
        """
        req = self.context.get("request")
        if req and req.method in ("PUT", "PATCH"):
            raw = self.initial_data.get("ingredients", None)
            if raw is not None and not raw:
                raise _ValErr(
                    {"ingredients": "Поле 'ingredients' обязательно при обновлении."}
                )
        return attrs

    @_transaction.atomic
    def create(self, validated_data):
        """
        Создание рецепта и сохранение ингредиентов.
        """
        ing_list = validated_data.pop("ingredients")
        recipe = _Recipe.objects.create(
            author=self.context["request"].user, **validated_data
        )
        self._save_ings(recipe, ing_list)
        return recipe

    def _save_ings(self, recipe_obj, ing_list):
        """
        Вспомогательный метод для сохранения связей RecipeIngredient.
        """
        relations = []
        for data in ing_list:
            relations.append(
                _RecIng(
                    recipe=recipe_obj,
                    ingredient=_Ingredient.objects.get(id=data["id"]),
                    amount=data["amount"],
                )
            )
        _RecIng.objects.bulk_create(relations)

    @_transaction.atomic
    def update(self, instance, validated_data):
        """
        Обновление рецепта: удаление старых ингредиентов и добавление новых.
        """
        ing_list = validated_data.pop("ingredients", None)
        recipe = super().update(instance, validated_data)
        if ing_list:
            recipe.recipeingredient_set.all().delete()
            self._save_ings(recipe, ing_list)
        return recipe

    def to_representation(self, instance):
        """
        Возвращает данные через RecipeReadSerializer после записи.
        """
        from .recipe_read import RecipeReadSerializer

        return RecipeReadSerializer(instance, context=self.context).data
