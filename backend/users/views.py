import base64 as _b64
import logging as _logging
import uuid as _uuid

from http import HTTPStatus as _HTTPStatus

# Django utilities
from django.contrib.auth.hashers import check_password as _check_password
from django.core.files.base import ContentFile as _ContentFile
from django.db.models import Count as _Count
from django.shortcuts import get_object_or_404 as _gof

# DRF components
from rest_framework import status as _status, viewsets as _viewsets
from rest_framework.authtoken.models import Token as _Token
from rest_framework.authtoken.views import ObtainAuthToken as _ObtainAuth
from rest_framework.decorators import action as _action
from rest_framework.permissions import AllowAny as _AllowAny, IsAuthenticated as _IsAuth
from rest_framework.response import Response as _Resp
from rest_framework.views import APIView as _APIView

# Local imports
from recipes.models import Recipe as _Recipe
from .models import Subscription as _Sub, User as _User
from .paginations import UserPagination as _UserPage
from .serializers import (
    EmailAuthTokenSerializer as _EmailAuthSer,
    UserCreateSerializer as _UserCreateSer,
    UserSerializer as _UserSer,
)

# Logger for error tracking
_logger = _logging.getLogger(__name__)


class UserViewSet(_viewsets.ModelViewSet):
    """
    ViewSet для работы с пользователями: CRUD, авторизация и подписки.
    """
    queryset = _User.objects.order_by("email")
    serializer_class = _UserSer
    pagination_class = _UserPage

    def get_permissions(self):
        """
        Выбирает права доступа: для создания AllowAny, иначе стандартные.
        """
        if self.action == 'create':
            return [_AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        """
        Возвращает класс сериализатора: UserCreateSer для create, иначе UserSer.
        """
        return _UserCreateSer if self.action == 'create' else _UserSer

    @_action(detail=False, methods=['get'], permission_classes=[_IsAuth])
    def me(self, request):
        """
        Получение данных текущего пользователя.
        """
        data = self.get_serializer(request.user).data
        return _Resp(data, status=_HTTPStatus.OK)

    @_action(detail=False, methods=['post'], permission_classes=[_IsAuth])
    def set_password(self, request):
        """
        Смена пароля: проверка старого, валидация нового и сохранение.
        """
        user_obj = request.user
        old_pw = request.data.get('current_password')
        new_pw = request.data.get('new_password')

        if not (old_pw and new_pw):
            return _Resp({'error': "Поля 'current_password' и 'new_password' обязательны."}, status=_status.HTTP_400_BAD_REQUEST)
        if not _check_password(old_pw, user_obj.password):
            return _Resp({'error': 'Текущий пароль указан неверно.'}, status=_status.HTTP_400_BAD_REQUEST)
        if old_pw == new_pw:
            return _Resp({'error': 'Новый пароль не должен совпадать с текущим.'}, status=_status.HTTP_400_BAD_REQUEST)

        user_obj.set_password(new_pw)
        user_obj.save()
        return _Resp(status=_status.HTTP_204_NO_CONTENT)

    @_action(detail=False, methods=['put', 'delete'], url_path='me/avatar', permission_classes=[_IsAuth])
    def update_avatar(self, request):
        """
        PUT: загрузка аватара из base64; DELETE: удаление существующего.
        """
        user_obj = request.user
        if request.method == 'PUT':
            avatar_data = request.data.get('avatar')
            if not avatar_data:
                return _Resp({'error': "Поле 'avatar' обязательно."}, status=_status.HTTP_400_BAD_REQUEST)
            try:
                prefix, b64str = avatar_data.split(';base64,')
                ext = prefix.split('/')[-1]
                fname = f"{_uuid.uuid4()}.{ext}"
                user_obj.avatar.save(fname, _ContentFile(_b64.b64decode(b64str)), save=True)
                url = request.build_absolute_uri(user_obj.avatar.url)
                return _Resp({'avatar': url}, status=_status.HTTP_200_OK)
            except Exception as e:
                _logger.error(f"Ошибка при обновлении аватара: {e}")
                return _Resp({'error': 'Не удалось обновить аватар.'}, status=_status.HTTP_500_INTERNAL_SERVER_ERROR)

        # DELETE branch
        if not user_obj.avatar:
            return _Resp({'detail': 'Аватар отсутствует.'}, status=_status.HTTP_400_BAD_REQUEST)
        user_obj.avatar.delete()
        user_obj.save()
        return _Resp(status=_status.HTTP_204_NO_CONTENT)

    @_action(detail=True, methods=['post', 'delete'], permission_classes=[_IsAuth])
    def subscribe(self, request, pk=None):
        """
        POST: подписаться на автора; DELETE: отписаться.
        """
        user_obj = request.user
        author_obj = self.get_object()

        if request.method == 'DELETE':
            sub_qs = _Sub.objects.filter(user=user_obj, author=author_obj)
            if not sub_qs.exists():
                return _Resp({'error': 'Вы не подписаны на этого пользователя.'}, status=_HTTPStatus.BAD_REQUEST)
            sub_qs.delete()
            return _Resp(status=_HTTPStatus.NO_CONTENT)

        if user_obj == author_obj:
            return _Resp({'error': 'Нельзя подписаться на себя.'}, status=_HTTPStatus.BAD_REQUEST)
        sub, created = _Sub.objects.get_or_create(user=user_obj, author=author_obj)
        if not created:
            return _Resp({'error': 'Уже подписаны на этого пользователя.'}, status=_HTTPStatus.BAD_REQUEST)

        limit = request.query_params.get('recipes_limit')
        try:
            limit = int(limit) if limit else None
        except ValueError:
            limit = None

        author_data = _UserSer(author_obj, context={'request': request}).data
        count = _Recipe.objects.filter(author=author_obj).count()
        author_data['recipes_count'] = count
        recipes_qs = _Recipe.objects.filter(author=author_obj)[:limit] if limit else _Recipe.objects.filter(author=author_obj)
        author_data['recipes'] = [
            {'id': r.id, 'name': r.name, 'image': request.build_absolute_uri(r.image.url) if request else r.image.url, 'cooking_time': r.cooking_time}
            for r in recipes_qs
        ]
        return _Resp(author_data, status=_HTTPStatus.CREATED)

    @_action(detail=True, methods=['delete'])
    def unsubscribe(self, request, pk=None):
        """
        Удаление подписки пользователя на автора.
        """
        _Sub.objects.filter(user=request.user, author=self.get_object()).delete()
        return _Resp({'status': 'unsubscribed'})

    @_action(detail=False, methods=['get'], permission_classes=[_IsAuth])
    def subscriptions(self, request):
        """
        Список подписок с постраничным выводом и ограничением рецептов.
        """
        user_obj = request.user
        subs = _User.objects.filter(subscribers__user=user_obj).annotate(recipes_count=_Count('recipes'))
        paginator = _UserPage()
        page = paginator.paginate_queryset(subs, request)

        recipes_limit = request.query_params.get('recipes_limit')
        try:
            recipes_limit = int(recipes_limit) if recipes_limit else None
        except ValueError:
            recipes_limit = None

        result = []
        for auth in page:
            data = _UserSer(auth, context={'request': request}).data
            data['recipes_count'] = auth.recipes_count
            qs = _Recipe.objects.filter(author=auth)[:recipes_limit] if recipes_limit else _Recipe.objects.filter(author=auth)
            data['recipes'] = [
                {'id': r.id, 'name': r.name, 'image': request.build_absolute_uri(r.image.url) if request else r.image.url, 'cooking_time': r.cooking_time}
                for r in qs
            ]
            result.append(data)
        return paginator.get_paginated_response(result)


class LogoutView(_APIView):
    """
    Выход пользователя: удаление токена.
    """
    permission_classes = [_IsAuth]

    def post(self, request):
        """
        Удаляет токен текущего пользователя или возвращает ошибку, если нет.
        """
        try:
            _Token.objects.get(user=request.user).delete()
            return _Resp(status=_HTTPStatus.NO_CONTENT)
        except _Token.DoesNotExist:
            return _Resp({'detail': 'Токен не найден.'}, status=_HTTPStatus.BAD_REQUEST)
        except Exception as err:
            _logger.error(f"Ошибка при выходе: {err}")
            return _Resp({'detail': str(err)}, status=_HTTPStatus.INTERNAL_SERVER_ERROR)


class AuthTokenView(_ObtainAuth):
    """
    Выдача токена по email и password.
    """
    serializer_class = _EmailAuthSer

    def post(self, request, *args, **kwargs):
        """
        Создает или возвращает существующий токен пользователя.
        """
        ser = self.serializer_class(data=request.data, context={'request': request})
        ser.is_valid(raise_exception=True)
        usr = ser.validated_data['user']
        tkn, _ = _Token.objects.get_or_create(user=usr)
        return _Resp({'auth_token': tkn.key})
