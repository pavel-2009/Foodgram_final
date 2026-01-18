# Foodgram - Продуктовый помощник

Приложение для управления рецептами, ингредиентами и списками покупок.

## Стек технологий

**Backend:**
- Django 6.0
- Django REST Framework
- PostgreSQL / SQLite
- Gunicorn

**Frontend:**
- React 17
- React Router

**DevOps:**
- Docker & Docker Compose
- GitHub Actions CI/CD
- Nginx

## Быстрый старт

### Требования
- Docker и Docker Compose
- Python 3.13+ (для локальной разработки)

### Запуск с Docker Compose

```bash
cd infra
docker-compose up -d
```

После запуска создайте суперпользователя:
```bash
docker-compose exec backend python manage.py createsuperuser
```

Приложение будет доступно по адресу `http://localhost`
Админ-панель: `http://localhost/admin`

### Локальная разработка

**Backend:**
```bash
cd backend/foodgram
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

## Структура проекта

```
.
├── backend/              # Django приложение
│   ├── foodgram/        # Основной проект
│   ├── ingredients/     # Приложение ингредиентов
│   ├── recipes/         # Приложение рецептов
│   ├── tags/            # Приложение тегов
│   └── users/           # Приложение пользователей
├── frontend/             # React приложение
├── infra/               # Docker & Nginx конфигурация
└── docs/                # Документация API
```

## Переменные окружения

Создайте `.env` файл в директории `infra/`:

```env
POSTGRES_DB=foodgram
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_PORT=5432

DJANGO_SECRET_KEY=your-secret-key
DEBUG=False
```

## API

API документация доступна по адресу `/api/docs/`

**Основные endpoints:**
- `GET /api/recipes/` - список рецептов
- `POST /api/recipes/` - создание рецепта
- `GET /api/ingredients/` - список ингредиентов
- `GET /api/tags/` - список тегов
- `GET /api/users/` - список пользователей

## Тестирование

Запуск тестов:
```bash
cd backend/foodgram
python manage.py test
```

Проверка покрытия:
```bash
coverage run manage.py test
coverage report -m
```

**Покрытие кода: 96%**

Проверка кода:
```bash
flake8 backend --max-line-length=120
mypy backend
```

## CI/CD

GitHub Actions автоматически запускает:
- Юнит тесты
- Lint проверки (flake8)
- Type checking (mypy)
- Docker build и push (при push в main)

## Администраторская панель

Доступна по адресу `/admin/` после авторизации суперпользователя.

## Лицензия

MIT
        - backend

