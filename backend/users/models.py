from django.contrib.auth.models import AbstractUser as _AuthUser
from django.db import models as _models
from django.db.models import UniqueConstraint as _Unique

# Локальные значения для настройки полей модели
_USERNAME_FIELD = "email"
_REQUIRED_FIELDS = ["username"]

class User(_AuthUser):
    """
    Пользовательское расширение модели AbstractUser.
    Использует email в качестве логина и хранит аватар.
    """
    USERNAME_FIELD = _USERNAME_FIELD
    REQUIRED_FIELDS = _REQUIRED_FIELDS

    # Email — уникальный идентификатор
    email = _models.EmailField(unique=True)

    # Изображение профиля
    avatar = _models.ImageField(
        upload_to="users/avatars/",
        blank=True,
        null=True,
        verbose_name="Аватар",
    )

    # Группы и права с переопределённым related_name
    groups = _models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_groups",
        blank=True,
        verbose_name="Группы",
    )
    user_permissions = _models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions",
        blank=True,
        verbose_name="Права пользователя",
    )

    class Meta:
        """
        Настройки мета-класса:
        - verbose_name: человекочитаемое название модели;
        - ordering: сортировка по email;
        - уникальное ограничение подписок реализовано в другой модели.
        """
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["email"]

    def __str__(self):
        """Возвращает email пользователя как строковое представление."""
        return self.email


class Subscription(_models.Model):
    """
    Модель «Подписка»: пользователь подписывается на автора (также User).
    Гарантируется уникальность пары (user, author).
    """
    user = _models.ForeignKey(
        User,
        on_delete=_models.CASCADE,
        related_name="subscriptions",
        verbose_name="Подписчик",
    )
    author = _models.ForeignKey(
        User,
        on_delete=_models.CASCADE,
        related_name="subscribers",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ["user"]
        constraints = [
            _Unique(
                fields=["user", "author"],
                name="unique_user_author_subscribe",
            )
        ]

    def __str__(self):
        """Человекочитаемое отображение связи подписки: user -> author."""
        return f"Subscription: {self.user.email} -> {self.author.email}"
