from django.apps import AppConfig as _AppConfig

# Локальные константы для настройки AppConfig
_DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
_APP_NAME = "recipes"


class RecipesConfig(_AppConfig):
    """
    Конфигурация приложения recipes:

    Атрибуты:
    - default_auto_field: тип поля для новых моделей;
    - name: уникальное имя приложения в проекте.
    """

    default_auto_field = _DEFAULT_AUTO_FIELD
    name = _APP_NAME
