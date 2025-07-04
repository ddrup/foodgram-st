# users/fields.py

"""
Поле для сериализаторов: обработка изображений в Base64.
Обёртка над классом из drf_extra_fields.
"""

# Импорт оригинального поля с псевдонимом
from drf_extra_fields.fields import Base64ImageField as _DRF_Base64ImageField

# Локальный алиас для удобства использования в приложениях
_CustomBase64Field = _DRF_Base64ImageField

# Экспортируем под привычным именем для сериализаторов
Base64ImageField = _CustomBase64Field
