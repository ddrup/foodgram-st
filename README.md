# FoodGram

## Описание
FoodGram — полноценная платформа для поиска, публикации и обмена кулинарными рецептами. Проект задуман как «личная кулинарная книга + социальная сеть»: пользователи могут сохранять понравившиеся блюда, формировать список покупок, а шеф‑повара — делиться авторскими шедеврами. 

## Быстрый старт

1. **Клонировать репозиторий**  
    ```bash
    git clone
    cd foodgram-st
    ```

2. **Создать файл окружения**  
    Перейдите в папку `infra` и создайте `.env`:
    ```bash
    cd infra
    ```
    создай файл .env
    Отредактируйте `.env`, указав свои значения:
    ```ini
    # .env
    SECRET_KEY=your_secret_key
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1,foodgram-backend

    POSTGRES_DB=foodgram-db
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    DB_HOST=db
    DB_PORT=5432

    PAGE_SIZE=6
    ```

3. **Создать суперпользователя**  
    ```bash
    docker compose exec backend \
      python manage.py createsuperuser
    ```

4. **Загрузить данные ингредиентов**  
    ```bash
    docker compose exec backend \
      python manage.py load_ingredients data/ingredients.json
    ```

5. **Запустить сервисы**  
    ```bash
    docker compose up --build -d
    ```

6. **Готово!**  
    - Основная страница: [http://localhost/](http://localhost/)  
    - Админка Django : [http://localhost/admin/](http://localhost/admin/)  