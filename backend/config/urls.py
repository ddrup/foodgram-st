# urls.py

# Импортируем настройки и утилиты с псевдонимами для «раскладки»
from django.conf import settings as _settings
from django.conf.urls.static import static as _serve_static
from django.contrib import admin as _admin
from django.urls import include as _inc
from django.urls import path as _route

# -------------------------------
# Основные маршруты приложения
# -------------------------------
routes = [
    # Все API-эндпоинты
    _route("api/", _inc("api.urls")),
    # Административная панель
    _route("admin/", _admin.site.urls),
]

# -----------------------------------------------------
# В режиме отладки (DEBUG) подключаем статику и медиа
# -----------------------------------------------------
if _settings.DEBUG:
    # Медиа-файлы пользователя
    media_patterns = _serve_static(
        _settings.MEDIA_URL,
        document_root=_settings.MEDIA_ROOT,
    )
    # Статические ассеты фронтенда
    static_patterns = _serve_static(
        _settings.STATIC_URL,
        document_root=_settings.STATIC_ROOT,
    )
    # Добавляем их к основным маршрутам
    routes += media_patterns + static_patterns

# Финальный список URL-конфигурации
urlpatterns = routes
