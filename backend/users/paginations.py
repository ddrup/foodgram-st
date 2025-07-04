# users/paginations.py

"""
Кастомный пагинатор для работы с пользователями через DRF.
Использует параметр `limit` для задания размера страницы.
"""

# Сторонние зависимости с псевдонимом
from rest_framework.pagination import PageNumberPagination as _BasePaginator

# Локальная константа для размера страницы из общих настроек
from constants import DEFAULT_PAGE_SIZE as _DEFAULT_SIZE


class UserPagination(_BasePaginator):
    """
    Пагинация списка пользователей:
    - По умолчанию возвращает `_DEFAULT_SIZE` записей на страницу.
    - Клиент может переопределить через query-параметр `_PARAM_NAME`.
    """
    # Название GET-параметра для переопределения page_size
    _param_name = "limit"
    page_size_query_param = _param_name
    # Базовый размер страницы
    _default_limit = _DEFAULT_SIZE
    page_size = _default_limit

