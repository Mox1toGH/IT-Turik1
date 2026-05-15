# IT-Turik1

Інструкція з запуску проєкту у двох варіантах: **вручну** та через **Docker**.

---

## 1. Що потрібно встановити

### Для ручного запуску
- Python 3.11+
- Node.js 20.19+ або 22.12+
- npm
- PostgreSQL 15+

### Для Docker
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (включає Docker та Docker Compose)

---

## 2. Налаштування `.env`

### Backend

1. Скопіюй приклад:

```powershell
Copy-Item backend\.env.example backend\.env
```

2. Заповни `backend/.env`:

```env
DJANGO_SECRET_KEY=replace-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,backend
CORS_ALLOWED_ORIGINS=http://localhost:5173

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

GOOGLE_OAUTH_CLIENT_ID=your-google-web-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
GOOGLE_CALENDAR_REDIRECT_URI=http://localhost:5173/calendar/google-callback

DB_ENGINE=django.db.backends.postgresql
DB_NAME=itturik
DB_USER=itturik
DB_PASSWORD=itturik
DB_HOST=db        # для Docker: db / для ручного: localhost
DB_PORT=5432
```

Як отримати значення:

- `DJANGO_SECRET_KEY`: згенеруй командою

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

- `DJANGO_DEBUG`: `True` для локальної розробки, `False` для продакшну.
- `DJANGO_ALLOWED_HOSTS`: список хостів через кому. Для Docker обов'язково додай `backend`.
- `CORS_ALLOWED_ORIGINS`: адреса фронтенду (локально: `http://localhost:5173`).
- `EMAIL_HOST_PASSWORD`: App Password у Google Account — `Security → App passwords`.
- `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET`: у Google Cloud Console → `APIs & Services → Credentials → OAuth client ID → Web application`.
- `DB_HOST`: **`db`** для Docker, **`localhost`** для ручного запуску.

### Frontend

1. Скопіюй приклад:

```powershell
Copy-Item frontend\.env.example frontend\.env
```

2. Перевір значення:

```env
VITE_GOOGLE_CLIENT_ID=your-google-web-client-id.apps.googleusercontent.com
VITE_API_BASE_URL=http://localhost:8000
```

`VITE_GOOGLE_CLIENT_ID` має збігатися зі значенням `GOOGLE_OAUTH_CLIENT_ID` у backend.

### Google Calendar Integration

Для роботи інтеграції з Google Calendar:

1. Увімкни **Google Calendar API** у Google Cloud Console (`APIs & Services → Library`).
2. Додай `http://localhost:5173/calendar/google-callback` до **Authorized redirect URIs** в OAuth client.
3. Заповни `GOOGLE_OAUTH_CLIENT_SECRET` та `GOOGLE_CALENDAR_REDIRECT_URI` у `backend/.env`.

---

## 3. Варіант A — Ручний запуск

### Передумови

Створи базу даних PostgreSQL вручну:

```sql
CREATE DATABASE itturik;
CREATE USER itturik WITH PASSWORD 'itturik';
GRANT ALL PRIVILEGES ON DATABASE itturik TO itturik;
```

У `backend/.env` встанови `DB_HOST=localhost`.

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
```

#### З WebSocket — рекомендовано (realtime notifications)

```powershell
daphne -b 0.0.0.0 -p 8000 backend.asgi:application
```

#### Без WebSocket (тільки REST API)

```powershell
python manage.py runserver
```

> WebSocket-нотифікації (`/ws/notifications/`, `/ws/leaderboards/`) доступні лише з Daphne.

Backend буде доступний на `http://localhost:8000`.

### Frontend (в новому терміналі)

```powershell
cd frontend
nvm use
npm install
```


#### Генерація API (OpenAPI & Orval):

Якщо змінились або додались нові ендпоінти в backend, оновіть згенерований API-клієнт на frontend. (Перший запуск)

> Запускати лише з запущеним backend-сервером!

```powershell
npm run generate-api
```

Оновлені хуки з'являться у `frontend/src/api/`.

#### Запуск Vite (frontend - серверу):

```powershell
npm run dev
```

Frontend буде доступний на `http://localhost:5173`.

---

### Superuser (ручний варіант)

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py createsuperuser
```

### Тести (ручний варіант)

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py test
```

```powershell
cd frontend
npm run lint
```

---

## 4. Варіант B — Docker

### Передумови

- Встановлений і запущений Docker Desktop.
- Заповнені `backend/.env` та `frontend/.env` (див. розділ 2).
- У `backend/.env` встановлено `DB_HOST=db`.

### Перший запуск

```bash
docker compose up --build
```

Docker автоматично:
- запустить PostgreSQL
- виконає міграції
- запустить backend і frontend

### Наступні запуски

```bash
docker compose up
```

### Зупинка

```bash
docker compose down
```

### Superuser (Docker)

Поки контейнери запущені, виконай в окремому терміналі:

```bash
docker compose exec backend python manage.py createsuperuser
```

### Тести (Docker)

```bash
docker compose exec backend python manage.py test
```

### Корисні команди

```bash
# Переглянути логи
docker compose logs -f

# Логи конкретного сервісу
docker compose logs -f backend

# Виконати будь-яку manage.py команду
docker compose exec backend python manage.py <команда>

# Перебудувати образи після змін у Dockerfile або requirements.txt
docker compose up --build

# Оновити API-клієнт після змін в ендпоінтах (backend має бути запущений)
docker compose exec frontend npm run generate-api
# Оновлені хуки з'являться у frontend/src/api/

# Видалити всі дані БД (повний скид)
docker compose down -v
```

---



## 6. Правила розробки

- Не генерувати описи комітів за допомогою ШІ.
- Генерувати код за допомогою ШІ можна, але перед комітом код має бути обов'язково прочитаний і перевірений розробником.
- Під час розробки дотримуватися наявної структури та архітектури проєкту.
- Змінювати структуру або архітектуру можна, але притримуватися цілісності проекту, щоб код не виглядав різнобійним.

---

## 7. Git Workflow

### Гілки

- `main` — стабільний код (продакшн), напряму не пушимо.
- `dev` — основна гілка розробки.
- `feature/*` — гілки для нових задач.
- `bugfix/*` — гілки для виправлень.

### Початок роботи

```bash
git checkout dev
git pull
git checkout -b feature/task-name
```

### Робота над задачею

```bash
git add .
git commit -m "feat: короткий опис"
git push origin feature/task-name
```

### Оновлення гілки

```bash
git checkout dev
git pull

git checkout feature/task-name
git pull origin dev
```

### Pull Request

- Створити PR: `feature/*` → `dev`.
- Пройти code review.
- Після approval виконати merge.

### Заборонено

- Пушити напряму в `main` або `dev`.
- Працювати кільком людям в одній гілці.
- Робити великі неперевірені коміти.

### Правила

- 1 задача = 1 гілка.
- Робити часті невеликі коміти.
- Використовувати зрозумілі повідомлення (просто порада і не є обов'язковою):
  - `feat:` новий функціонал
  - `fix:` виправлення
  - `refactor:` рефакторинг
  - `add:` додавання нового функціоналу
  - `update:` оновлення
  - `remove:` видалення
  - `docs:` оновлення документації

### Реліз

- Merge `dev` → `main` через Pull Request.