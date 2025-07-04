import re as _re

from django.contrib.auth import authenticate as _authenticate
from rest_framework import serializers as _serializers
from rest_framework.exceptions import ValidationError as _ValErr

from .fields import Base64ImageField as _B64Field
from .models import Subscription as _SubModel, User as _UserModel

from constants import (
    ERROR_MESSAGES as _ERR,
    MAX_LENGTH_FIRSTNAME as _MAX_FN,
    MAX_LENGTH_LASTNAME as _MAX_LN,
    MAX_LENGTH_USERNAME as _MAX_UN,
)

class EmailAuthTokenSerializer(_serializers.Serializer):
    """
    Сериализатор для логина по email+паролю:
    • Проверяет наличие полей;
    • Аутентифицирует через Django;
    • Проверяет, что пользователь активен.
    """
    email = _serializers.EmailField(label="Email")
    password = _serializers.CharField(
        label="Password",
        style={"input_type": "password"},
        write_only=True,
    )

    def validate(self, data):
        """Основная проверка: поля, учётные данные, статус."""
        mail = data.get("email")
        pwd = data.get("password")
        if not (mail and pwd):
            raise _serializers.ValidationError(
                "Требуется email и password",
                code="authorization",
            )
        usr = _authenticate(username=mail, password=pwd)
        if not usr:
            raise _serializers.ValidationError(
                "Неверные учётные данные",
                code="authorization",
            )
        if not usr.is_active:
            raise _serializers.ValidationError(
                "Пользователь деактивирован",
                code="authorization",
            )
        data["user"] = usr
        return data


class UserSerializer(_serializers.ModelSerializer):
    """
    Отдаёт данные пользователя и флаг is_subscribed.
    """
    avatar = _B64Field(required=False, allow_null=True)
    is_subscribed = _serializers.SerializerMethodField()

    class Meta:
        model = _UserModel
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "avatar",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        """
        True, если текущий пользователь (из context) подписан на obj.
        """
        req = self.context.get("request")
        return bool(
            req
            and hasattr(req, "user")
            and req.user.is_authenticated
            and obj.subscribers.filter(user=req.user).exists()
        )


class SubscriptionSerializer(_serializers.ModelSerializer):
    """
    Сериализует модель подписки и возвращает
    subscriber_id, author_id и author_email.
    """
    class Meta:
        model = _SubModel
        fields = ("id", "user", "author")

    def to_representation(self, inst):
        auth = inst.author
        return {
            "subscriber_id": inst.user.id,
            "author_id": auth.id,
            "author_email": auth.email,
        }


class UserCreateSerializer(_serializers.ModelSerializer):
    """
    Регистрация нового пользователя:
    валидация username, first_name, last_name и хеширование пароля.
    """
    password = _serializers.CharField(write_only=True)
    username = _serializers.CharField(
        max_length=_MAX_UN,
        error_messages={"max_length": _ERR["username_max_length"]},
    )
    first_name = _serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=_MAX_FN,
        error_messages={
            "required": _ERR["first_name_required"],
            "blank": _ERR["first_name_blank"],
            "max_length": _ERR["first_name_max_length"],
        },
    )
    last_name = _serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=_MAX_LN,
        error_messages={
            "required": _ERR["last_name_required"],
            "blank": _ERR["last_name_blank"],
            "max_length": _ERR["last_name_max_length"],
        },
    )

    class Meta:
        model = _UserModel
        fields = (
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
        )

    def validate_username(self, value):
        """
        Проверка формата и уникальности username,
        запрет значения 'me' (регистр не важен).
        """
        if not _re.match(r"^[\w.@+-]+$", value):
            raise _ValErr("Неверный формат username.")
        if value.lower() == "me":
            raise _ValErr("Использовать 'me' как username запрещено.")
        if _UserModel.objects.filter(username__iexact=value).exists():
            raise _ValErr("Такой username уже зарегистрирован.")
        return value

    def create(self, validated_data):
        """Создаёт пользователя и хеширует пароль."""
        user = _UserModel(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user
