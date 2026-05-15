# Backend (Django + DRF + Channels)

Backend частина проєкту `IT-Turik1`: REST API, WebSocket події, OpenAPI схема, адмінка.

## Технології

- Python 3.11+
- Django
- Django REST Framework
- drf-spectacular (OpenAPI)
- Django Channels + Daphne (WebSocket)
- SQLite (за замовчуванням) або PostgreSQL (через `DB_*` env)

## Структура (ключові файли)

- `manage.py` — Django CLI.
- `backend/settings.py` — конфігурація застосунку, env, DB, CORS, JWT, OpenAPI.
- `backend/urls.py` — REST роутинг + OpenAPI endpoints.
- `backend/asgi.py` — ASGI app + WebSocket routing (`/ws/notifications/`, `/ws/leaderboards/`).
- `backend/wsgi.py` — WSGI app (без WebSocket).
- `requirements.txt` — Python залежності.
- `.env.example` — шаблон env.
- `schema.yml` — збережена схема OpenAPI (snapshot, може застарівати).
- `entrypoint.sh` — docker entrypoint (очікування БД, міграції, запуск Daphne).

Ключові доменні модулі:

- `accounts`, `teams`, `tournaments`, `evaluation`, `certificates`, `notifications`, `stats`, `news`, `points`, `shop`, `inventory`.

## Документація API: що вважати джерелом правди

Основне джерело контракту API:

- OpenAPI schema: `GET /api/schema/`
- Swagger UI: `GET /api/schema/swagger-ui/`
- ReDoc: `GET /api/schema/redoc/`

`api_cheat_sheet` використовувати як допоміжну/історичну документацію (частково валідна після переходу на OpenAPI):

- [api_cheat_sheet/api_cheat_sheet.md](/C:/Users/Cougar/Programing/IT-Turik1/api_cheat_sheet/api_cheat_sheet.md)
- [api_cheat_sheet/access_updates.md](/C:/Users/Cougar/Programing/IT-Turik1/api_cheat_sheet/access_updates.md)
- [api_cheat_sheet/leaderboard.md](/C:/Users/Cougar/Programing/IT-Turik1/api_cheat_sheet/leaderboard.md)
- [api_cheat_sheet/notifications.md](/C:/Users/Cougar/Programing/IT-Turik1/api_cheat_sheet/notifications.md)
- [api_cheat_sheet/stats.md](/C:/Users/Cougar/Programing/IT-Turik1/api_cheat_sheet/stats.md)
- [api_cheat_sheet/points.md](/C:/Users/Cougar/Programing/IT-Turik1/api_cheat_sheet/points.md)
- [api_cheat_sheet/shop.md](/C:/Users/Cougar/Programing/IT-Turik1/api_cheat_sheet/shop.md)
- [api_cheat_sheet/inventory.md](/C:/Users/Cougar/Programing/IT-Turik1/api_cheat_sheet/inventory.md)

Правило:

- Для нової розробки та інтеграцій орієнтуйся на OpenAPI.
- Cheat sheet використовуй для контексту, бізнес-нюансів та legacy-випадків.

## Локальний запуск (без Docker)

```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
```

Режими запуску:

- З WebSocket (рекомендовано):
```bash
daphne -b 0.0.0.0 -p 8000 backend.asgi:application
```
- Тільки REST:
```bash
python manage.py runserver
```

## Docker запуск

Із кореня репозиторію:

```bash
docker-compose up --build
```

Сервіси:

- `db` — PostgreSQL
- `backend` — Django + Daphne
- `frontend` — Vite dev server

## Базові команди

```bash
# Міграції
python manage.py makemigrations
python manage.py migrate

# Адмін
python manage.py createsuperuser

# Тести
python manage.py test

# Перевірка конфігурації
python manage.py check
```

Для Docker:

```bash
docker-compose exec backend python manage.py <command>
```

## WebSocket

Активні ws-маршрути:

- `/ws/notifications/`
- `/ws/leaderboards/`

Працюють через ASGI (`backend/asgi.py`) і запуск `daphne`.

## Підходи та архітектурні принципи

- Domain-first структура: окремий Django app на кожний бізнес-домен.
- API-first: зміни в endpoint-ах мають бути відображені в OpenAPI.
- Єдине джерело API-контракту — `drf-spectacular` схема.
- Env-driven config: секрети/хости/БД не хардкодити.
- Realtime окремо від REST: Channels consumers + JWT middleware для ws.

## Якщо додаєш/міняєш endpoint

1. Онови serializers/views/urls у відповідному app.
2. Перевір Swagger/ReDoc (`/api/schema/swagger-ui/`).
3. Якщо треба, онови записи в `api_cheat_sheet` (тільки валідні частини).
4. Узгодь зміни з frontend (генерація клієнта через Orval).

## Змінні середовища (мінімум)

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `GOOGLE_CALENDAR_REDIRECT_URI`
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`

