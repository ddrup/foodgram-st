# recipes/models.py

# Стандартные средства Django и валидация
# Общие константы проекта
from constants import NAME_MAX_LENGTH as _NAME_MAX
from constants import UNIT_MAX_LENGTH as _UNIT_MAX
from django.contrib.auth import get_user_model as _get_user
from django.core.validators import MinValueValidator as _MinVal
from django.db import models as _models

# Получаем модель пользователя
User = _get_user()


class Ingredient(_models.Model):
    """
    Модель ингредиента:
    имя и единица измерения с ограничениями длины.
    """

    name = _models.CharField(
        max_length=_NAME_MAX,
        verbose_name="Название",
    )
    measurement_unit = _models.CharField(
        max_length=_UNIT_MAX,
        verbose_name="Единица измерения",
    )

    class Meta:
        """
        Настройки мета-класса:
        - уникальность по имени и единице;
        - сортировка по имени;
        - человекочитаемые имена.
        """

        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ["name"]
        constraints = [
            _models.UniqueConstraint(
                fields=["name", "measurement_unit"], name="unique_ingredient_name_unit"
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


class Recipe(_models.Model):
    """
    Основная модель рецепта:
    автор, название, изображение, текст, время приготовления и связь с ингредиентами.
    """

    author = _models.ForeignKey(
        User,
        on_delete=_models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    name = _models.CharField(
        max_length=_NAME_MAX,
        verbose_name="Название",
    )
    image = _models.ImageField(
        upload_to="recipes/images/",
        verbose_name="Изображение",
    )
    text = _models.TextField(
        verbose_name="Описание",
    )
    ingredients = _models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        related_name="recipes",
    )
    cooking_time = _models.PositiveIntegerField(
        verbose_name="Время приготовления (мин)",
        validators=[_MinVal(1)],
    )
    created_at = _models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    class Meta:
        """
        Мета-настройки рецепта:
        - сортировка по дате создания (по убыванию);
        - человекочитаемые имена.
        """

        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class RecipeIngredient(_models.Model):
    """
    Промежуточная модель рецепта и ингредиента:
    хранит количество ингредиента в рецепте.
    """

    recipe = _models.ForeignKey(
        Recipe,
        on_delete=_models.CASCADE,
        verbose_name="Рецепт",
    )
    ingredient = _models.ForeignKey(
        Ingredient,
        on_delete=_models.CASCADE,
        verbose_name="Ингредиент",
    )
    amount = _models.PositiveIntegerField(
        verbose_name="Количество",
        validators=[_MinVal(1)],
    )

    class Meta:
        """
        Настройки промежуточной модели:
        - уникальность связи recipe-ingredient;
        - сортировка по recipe и ingredient;
        - человекочитаемые имена.
        """

        verbose_name = "Ингредиент рецепта"
        verbose_name_plural = "Ингредиенты рецепта"
        ordering = ["recipe", "ingredient"]
        constraints = [
            _models.UniqueConstraint(
                fields=["recipe", "ingredient"], name="unique_recipe_ingredient"
            )
        ]

    def __str__(self):
        return f"{self.recipe.name} — {self.ingredient.name} [{self.amount}]"


class UserRecipeRelation(_models.Model):
    """
    Абстрактная модель связи пользователь-рецепт:
    используется как базовый класс для Favorite и ShoppingCart.
    """

    user = _models.ForeignKey(
        User,
        on_delete=_models.CASCADE,
        verbose_name="Пользователь",
    )
    recipe = _models.ForeignKey(
        Recipe,
        on_delete=_models.CASCADE,
        verbose_name="Рецепт",
    )

    class Meta:
        abstract = True
        ordering = ["user"]
        constraints = [
            _models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_user_recipe"
            )
        ]

    def __str__(self):
        return f"{self.user} -> {self.recipe}"


class Favorite(UserRecipeRelation):
    """
    Модель избранного, унаследована от UserRecipeRelation.
    """

    class Meta(UserRecipeRelation.Meta):
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        ordering = ["user"]
        constraints = [
            _models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_user_recipe_in_favorite"
            )
        ]


class ShoppingCart(UserRecipeRelation):
    """
    Модель корзины покупок, унаследована от UserRecipeRelation.
    """

    class Meta(UserRecipeRelation.Meta):
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        ordering = ["user"]
        constraints = [
            _models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_user_recipe_in_shopping_cart"
            )
        ]
