# IT-Turik1

Коротка інструкція з запуску проєкту, тестів та налаштування `.env`.

## 1. Що потрібно встановити

- Python 3.11+
- Node.js 20.19+ або 22.12+
- npm

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
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

GOOGLE_OAUTH_CLIENT_ID=your-google-web-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
GOOGLE_CALENDAR_REDIRECT_URI=http://localhost:5173/calendar/google-callback
```

Як отримати значення:

- `DJANGO_SECRET_KEY`: згенеруй командою

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

- `DJANGO_DEBUG`: `True` для локальної розробки, `False` для продакшну.
- `DJANGO_ALLOWED_HOSTS`: список хостів через кому (локально: `localhost,127.0.0.1`).
- `CORS_ALLOWED_ORIGINS`: адреса фронтенду (локально: `http://localhost:5173`).
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`: для Gmail залиш як у прикладі.
- `EMAIL_HOST_USER`: твоя Gmail-адреса.
- `EMAIL_HOST_PASSWORD`: App Password у Google Account:
  1. Увімкни 2FA у Google Account.
  2. Відкрий `Security -> App passwords`.
  3. Створи пароль застосунку та встав у `.env`.
- `GOOGLE_OAUTH_CLIENT_ID`: у Google Cloud Console:
  1. `APIs & Services -> Credentials`.
  2. `Create Credentials -> OAuth client ID -> Web application`.
  3. Додай `http://localhost:5173` у `Authorized JavaScript origins`.
  4. Скопіюй `Client ID`.
- `GOOGLE_OAUTH_CLIENT_SECRET`: секрет OAuth-клієнта, доступний у тих же Credentials.
- `GOOGLE_CALENDAR_REDIRECT_URI`: URI для OAuth callback (за замовчуванням `http://localhost:5173/calendar/google-callback`). Додай цю адресу як **Authorized redirect URI** у Google Cloud Console.

### Google Calendar Integration

Для роботи інтеграції з Google Calendar додатково потрібно:

1. Увімкнути **Google Calendar API** у Google Cloud Console (`APIs & Services -> Library`).
2. Додати `http://localhost:5173/calendar/google-callback` до **Authorized redirect URIs** в OAuth client.
3. Заповнити `GOOGLE_OAUTH_CLIENT_SECRET` та `GOOGLE_CALENDAR_REDIRECT_URI` у `backend/.env`.

**Можливості:**
- Підключення Google Calendar з профілю у розділі Calendar.
- Автоматична синхронізація всіх існуючих подій при підключенні.
- Автоматичне додавання нових подій та раундів у Google Calendar (`post_save` сигнали).
- Ручний експорт окремих подій через кнопку "Add to GCal".

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

`VITE_GOOGLE_CLIENT_ID` має збігатися зі значенням `GOOGLE_OAUTH_CLIENT_ID` на backend.

## 3. Запуск проєкту

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
```

#### Варіант A: з WebSocket (ASGI, рекомендовано для realtime notifications)

```powershell
daphne -b 0.0.0.0 -p 8000 backend.asgi:application
```

Використовуй цей режим, якщо потрібні realtime події через `/ws/notifications/`.

#### Варіант B: без WebSocket (класичний Django runserver)

```powershell
python manage.py runserver
```

Використовуй цей режим для REST/OpenAPI. WebSocket-нотифікації в цьому режимі недоступні.

Backend буде доступний на `http://localhost:8000`.

### Frontend (в новому терміналі)

```powershell
cd frontend
nvm use
npm install
npm run dev
```

Frontend буде доступний на `http://localhost:5173`.

## 4. Тести

### Backend

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py test
```

### Frontend

Окремі unit/integration тести наразі не налаштовані. Для перевірки коду використовуй:

```powershell
cd frontend
npm run lint
```



## 5. Генерація API (OpenAPI & Orval)

Якщо ви змінили або додали нові ендпоінти в бекенді (views/serializers), потрібно оновити згенерований API-клієнт на фронтенді.
Оскільки Orval налаштований на отримання схеми з працюючого бекенду, переконайтеся, що Django сервер запущений (`python manage.py runserver`).

### Оновити хуки на фронтенді
```powershell
cd frontend
nvm use
npm run generate-api
```

Після цього оновлені хуки (наприклад, `useGetUserPoints`) з'являться в `frontend/src/api/`.

## 6. Правила розробки

- Не генерувати описи комітів за допомогою ШІ.
- Генерувати код за допомогою ШІ можна, але перед комітом код має бути обов'язково прочитаний і перевірений розробником.
- Під час розробки дотримуватися наявної структури та архітектури проєкту.
- Змінювати структуру або архітектуру можна, але притримуватися цілісності проекту, щоб код не виглядав різнобійним.

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

- Створити PR: `feature/*` -> `dev`.
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

- Merge `dev` -> `main` через Pull Request.
