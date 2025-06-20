# Foodgram Project

## Описание

**Foodgram** — это веб-приложение для любителей кулинарии. Оно позволяет пользователям:
- Публиковать рецепты.
- Просматривать рецепты других пользователей.
- Добавлять рецепты в избранное.
- Формировать список покупок на основе выбранных рецептов.

Проект разработан с использованием **Django** и **Django REST Framework**. Фронтенд приложения работает на **React**.

## Стек технологий

- **Backend**: Python 3, Django, Django REST Framework, PostgreSQL
- **Frontend**: React
- **API**: REST API
- **Контейнеризация**: Docker, Docker Compose
- **Web-сервер**: Nginx

## Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/Gurgunok/foodgram-st.git
cd foodgram-st
```
### 2. Запуск контейнеров

Перейдите в папку **infra** и запустите контейнеры с помощью Docker Compose:
```bash
cd infra
docker-compose up -d
```
Это развернет проект с базой данных **PostgreSQL**, бекендом на **Django** и веб-сервером **Nginx**.

### 3. Создание суперпользователя

Для доступа к админ-панели создайте суперпользователя:
```bash
docker-compose exec backend python manage.py createsuperuser
```

### 4. Загрузка ингредиентов

Приложение использует список ингредиентов, который можно загрузить из файла:
```bash
docker-compose exec backend python manage.py load_ingredients data/ingredients.json
```

### 5. Доступ к проекту

* Главная страница: http://localhost
* Админ-панель Django: http://localhost/admin или http://127.0.0.1:8000/admin
* API документация: http://localhost/api/docs/

### 6. Остановка сервисов
Для остановки контейнеров выполните:
```bash
docker-compose down
```

## Переменные окружения (ENV)

Для корректной работы проекта требуется настроить переменные окружения в файле .env. Создайте его в папке infra:
```bash
cd infra
touch .env
```
Добавьте в него:
```ini
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,foodgram-backend

POSTGRES_DB=your_database
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
DB_HOST=db
DB_PORT=5432

PAGE_SIZE=6
```
После этого перезапустите контейнеры:
```bash
docker-compose down
docker-compose up -d
```

## Примеры API-запросов

### Получение списка рецептов
```http
GET /api/recipes/
```

#### Пример ответа:
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Борщ",
      "author": "admin",
      "image": "http://localhost/media/recipes/1.jpg",
      "cooking_time": 90
    }
  ]
}
```

### Добавление рецепта (POST)
```http
POST /api/recipes/
```

#### Тело запроса:
```json
{
  "name": "Оливье",
  "ingredients": [
    {
      "id": 1,
      "amount": 200
    }
  ],
  "cooking_time": 30
} 
```

### Удаление рецепта (DELETE)
```http
DELETE /api/recipes/1/
```

## Автор

Разработано студентом САФУ Варакосиным Даниилом в рамках итогового проекта.
