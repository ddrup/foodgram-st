from recipes.models import Recipe as _RecipeModel
from rest_framework import serializers as _ser

from ..models import Favorite as _FavModel
from ..models import ShoppingCart as _CartModel


class FavoriteSerializer(_ser.ModelSerializer):
    """
    Сериализатор для модели Favorite:
    возвращает данные рецепта при добавлении в избранное.
    """

    class Meta:
        model = _FavModel
        fields = (
            "user",
            "recipe",
        )

    def to_representation(self, inst):
        """
        Преобразует связь Favorite в данные рецепта:
        id, name, ссылка на изображение и время готовки.
        """
        rec = inst.recipe
        req = self.context.get("request")
        img_url = req.build_absolute_uri(rec.image.url) if req else rec.image.url
        return {
            "id": rec.id,
            "name": rec.name,
            "image": img_url,
            "cooking_time": rec.cooking_time,
        }


class ShoppingCartSerializer(_ser.ModelSerializer):
    """
    Сериализатор для модели ShoppingCart:
    возвращает представление рецепта в корзине покупок.
    """

    class Meta:
        model = _CartModel
        fields = (
            "user",
            "recipe",
        )

    def to_representation(self, inst):
        """
        Возвращает словарь с ключами: id, name, image и cooking_time рецепта.
        """
        rec_item = inst.recipe
        req_ctx = self.context.get("request")
        url = (
            req_ctx.build_absolute_uri(rec_item.image.url)
            if req_ctx
            else rec_item.image.url
        )
        return {
            "id": rec_item.id,
            "name": rec_item.name,
            "image": url,
            "cooking_time": rec_item.cooking_time,
        }
