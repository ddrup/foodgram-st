from django.apps import AppConfig as _AppConfig

_DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
_APP_LABEL = "users"

class UsersConfig(_AppConfig):
    """
    Настройки приложения users:
    - default_auto_field: тип поля для ключей моделей;
    - name: ярлык приложения для регистрации в INSTALLED_APPS.
    """
    name = _APP_LABEL
    default_auto_field = _DEFAULT_AUTO_FIELD