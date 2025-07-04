from rest_framework import serializers as _ser
from users.serializers import UserSerializer as _UserSer
from ..fields import Base64ImageField as _ImgField
from ..models import Recipe as _RecipeModel


class RecipeReadSerializer(_ser.ModelSerializer):
    """
    Сериализатор для чтения данных рецепта:
    • Включает автора, изображение и статус избранного/корзины;
    • Формирует список ингредиентов.
    """
    author = _UserSer(read_only=True)
    image = _ImgField()
    is_favorited = _ser.SerializerMethodField()
    is_in_shopping_cart = _ser.SerializerMethodField()
    ingredients = _ser.SerializerMethodField()

    class Meta:
        model = _RecipeModel
        fields = (
            "id",
            "author",
            "name",
            "image",
            "text",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart",
            "ingredients",
            "created_at",
        )

    def get_is_favorited(self, recipe_obj):
        """
        Проверяет, добавлен ли рецепт в избранное текущим пользователем.
        """
        req = self.context.get("request")
        return bool(
            req
            and req.user.is_authenticated
            and recipe_obj.favorite_set.filter(user=req.user).exists()
        )

    def get_is_in_shopping_cart(self, recipe_obj):
        """
        Определяет наличие рецепта в корзине текущего пользователя.
        """
        req = self.context.get("request")
        return bool(
            req
            and req.user.is_authenticated
            and recipe_obj.shoppingcart_set.filter(user=req.user).exists()
        )

    def get_ingredients(self, recipe_obj):
        """
        Возвращает список ингредиентов с полями:
        id, name, measurement_unit, amount.
        """
        relations = recipe_obj.recipeingredient_set.select_related("ingredient")
        ingredients_list = []
        for rel in relations:
            ing = rel.ingredient
            ingredients_list.append({
                "id": ing.id,
                "name": ing.name,
                "measurement_unit": ing.measurement_unit,
                "amount": rel.amount,
            })
        return ingredients_list
