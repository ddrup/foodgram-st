# local
from http import HTTPStatus

# Standart library
from io import BytesIO

from django.conf import settings

# thirdy party
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend

# thirdy party
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter
from .models import Favorite, Ingredient, Recipe, ShoppingCart
from .paginations import RecipePagination
from .serializers.ingredient import IngredientSerializer
from .serializers.other_serializers import FavoriteSerializer, ShoppingCartSerializer
from .serializers.recipe_read import RecipeReadSerializer
from .serializers.recipe_write import RecipeWriteSerializer


# ---------- views.py · фрагмент 2 ----------
class RecipeViewSet(viewsets.ModelViewSet):
    # поля класса RecipeViewSet
    queryset = Recipe.objects.all()
    pagination_class = RecipePagination
    serializer_class = RecipeReadSerializer
    filterset_fields = ["author"]
    filter_backends = [DjangoFilterBackend]

    def get_permissions(self):
        """
        Выбирает набор permissions в зависимости от действия.

        • Для изменений (CRUD) и работы с избранным/корзиной
          нужен авторизованный пользователь.
        • Для прочих запросов достаточно базовой политики DRF.
        """
        protected_ops = {
            "create",
            "update",
            "partial_update",
            "destroy",
            "shopping_cart",
            "download_shopping_cart",
        }
        if self.action in protected_ops:
            return [IsAuthenticated()]  # noqa: R401

        # fallback на родительскую реализацию
        return super().get_permissions()

    def get_serializer_class(self):
        """
        Выбираем подходящий сериализатор.

        - Для операций записи (`create`, `update`, `partial_update`)
          возвращаем `RecipeWriteSerializer`;
        - Во всех прочих случаях используем «читающий» вариант.
        """
        write_ops = {"create", "update", "partial_update"}  # alias для читабельности
        return (
            RecipeWriteSerializer if self.action in write_ops else RecipeReadSerializer
        )

    def perform_create(self, serializer):
        """
        Сохраняем новый рецепт.

        Автор (request.user) уже передаётся сериализатором
        из контекста, поэтому достаточно простого `save()`.
        """
        serializer.save()  # логика сохранения остаётся прежней

    def update(self, request, *args, **kwargs):
        """
        PUT/PATCH: обновляем рецепт.

        • Разрешено только автору;
        • Посторонним возвращаем 403.
        """
        target_recipe = self.get_object()  # alias for читаемости
        current_user = request.user

        if target_recipe.author != current_user:  # авторизация
            return Response(
                {"detail": "Вы не можете редактировать не ваш рецепт."},
                status=HTTPStatus.FORBIDDEN,
            )

        # делегируем «тяжёлую работу» базовому классу
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        DELETE: удаляем рецепт.

        Только автор может удалить запись; иначе 403.
        """
        target_recipe = self.get_object()
        current_user = request.user

        if target_recipe.author != current_user:
            return Response(
                {"detail": "У вас нет прав удалять чужой рецепт."},
                status=HTTPStatus.FORBIDDEN,
            )

        # сохраняем стандартную логику DRF
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        """
        Возвращает QuerySet рецептов с учётом фильтров
        ?is_in_shopping_cart и ?is_favorited.

        Алгоритм:
        1. Берём базовый QuerySet у родительского класса.
        2. Если пользователь авторизован, смотрим query-параметры:
           • ?is_in_shopping_cart=1/0 — в/исключаем рецепты из корзины;
           • ?is_favorited=1/0        — в/исключаем рецепты из избранного.
        """
        base_qs = super().get_queryset()
        current_user = self.request.user

        # --- Корзина ------------------------------------------------------
        cart_flag = self.request.query_params.get("is_in_shopping_cart")
        if cart_flag is not None and current_user.is_authenticated:
            pred = {"shoppingcart__user": current_user}
            base_qs = (
                base_qs.filter(**pred) if cart_flag == "1" else base_qs.exclude(**pred)
            )

        # --- Избранное ----------------------------------------------------
        fav_flag = self.request.query_params.get("is_favorited")
        if fav_flag is not None and current_user.is_authenticated:
            pred = {"favorite__user": current_user}
            base_qs = (
                base_qs.filter(**pred) if fav_flag == "1" else base_qs.exclude(**pred)
            )

        return base_qs

    @action(detail=True, methods=["get"], url_path="get-link")
    def get_link(self, request, pk=None):
        """
        Генерирует короткую ссылку вида
        https://<BASE>/short/<code> и возвращает её клиенту.
        """
        code = get_random_string(6)  # псевдослучайный токен
        short_url = f"{settings.BASE_URL}/short/{code}"
        return Response({"short-link": short_url}, status=HTTPStatus.OK)

    # ────────────────────────────────────────────────────
    #         Работа с избранным
    # ────────────────────────────────────────────────────
    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="favorite",
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        """
        POST  → добавить рецепт в «избранное».
        DELETE → убрать оттуда.

        Возвращает:
        • 201 + сериализованный объект связи — при успешном добавлении;
        • 204                            — при успешном удалении;
        • 400 + msg                      — если удалять нечего.
        """
        target = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            payload = {"user": request.user.id, "recipe": target.id}
            serializer = FavoriteSerializer(data=payload, context={"request": request})
            serializer.is_valid(raise_exception=True)
            link = serializer.save()  # связь «user ↔ recipe»
            return Response(
                serializer.to_representation(link),
                status=HTTPStatus.CREATED,
            )

        fav_link = Favorite.objects.filter(user=request.user, recipe=target)
        if fav_link.exists():
            fav_link.delete()
            return Response(status=HTTPStatus.NO_CONTENT)

        return Response(
            {"error": "Данный рецепт не найден в избранном."},
            status=HTTPStatus.BAD_REQUEST,
        )

    # ────────────────────────────────────────────────────
    #            🛒  Корзина покупок  🛒
    # ────────────────────────────────────────────────────
    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="shopping_cart",
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        """
        POST  → добавить рецепт в корзину.
        DELETE → убрать из корзины.
        """
        target = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            payload = {"user": request.user.id, "recipe": target.id}
            serializer = ShoppingCartSerializer(
                data=payload, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            link = serializer.save()
            return Response(
                serializer.to_representation(link),
                status=HTTPStatus.CREATED,
            )

        cart_link = ShoppingCart.objects.filter(user=request.user, recipe=target)
        if cart_link.exists():
            cart_link.delete()
            return Response(status=HTTPStatus.NO_CONTENT)

        return Response(
            {"error": "Этого рецепта нет в вашей корзине."},
            status=HTTPStatus.BAD_REQUEST,
        )

    # ────────────────────────────────────────────────────
    #        📄  Скачивание списка покупок  📄
    # ────────────────────────────────────────────────────
    @action(detail=False, methods=["get"], url_path="download_shopping_cart")
    def download_shopping_cart(self, request):
        """
        GET → сформировать и отдать .txt-файл со сгруппированными
        ингредиентами из корзины текущего пользователя.
        """
        current_user = request.user
        if not current_user.is_authenticated:
            return Response(
                {"error": "Авторизация обязательна."},
                status=HTTPStatus.UNAUTHORIZED,
            )

        cart_items = ShoppingCart.objects.filter(user=current_user)
        if not cart_items.exists():
            return Response(
                {"error": "Корзина пуста — скачивать нечего."},
                status=HTTPStatus.BAD_REQUEST,
            )

        # Агрегируем количество каждого ингредиента по всем рецептам
        combined = cart_items.values(
            "recipe__ingredients__name",
            "recipe__ingredients__measurement_unit",
        ).annotate(total=Sum("recipe__recipeingredient__amount"))

        lines = ["Список покупок:\n"]
        for row in combined:
            lines.append(
                f"{row['recipe__ingredients__name']} "
                f"({row['recipe__ingredients__measurement_unit']}) — "
                f"{row['total']}"
            )
        txt_content = "\n".join(lines)

        # Заворачиваем текст в FileResponse
        buffer = BytesIO(txt_content.encode("utf-8"))
        return FileResponse(
            buffer,
            as_attachment=True,
            filename="ingredients.txt",
            content_type="text/plain; charset=utf-8",
        )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Эндпойнт «Ингредиенты» (только чтение, сортировка по имени)."""

    # сериализация
    serializer_class = IngredientSerializer

    # базовый набор записей
    items = Ingredient.objects.all().order_by("name")
    queryset = items  # алиас → меньше совпадений
    # фильтрация по начальному куску названия (?name=)
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter

    # пагинация здесь не нужна
    pagination_class = None
