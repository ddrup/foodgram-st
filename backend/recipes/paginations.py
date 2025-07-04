# local
from constants import DEFAULT_PAGE_SIZE
from rest_framework.pagination import PageNumberPagination


class RecipePagination(PageNumberPagination):
    """
    Пагинатор рецептов.

    Возвращает по умолчанию PAGE_SIZE объектов
    Позволяет клиенту задать количество через ?limit=
    """

    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = "limit"
