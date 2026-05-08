#  API Cheat Sheet

## Access Updates (2026-05-07)

- `POST /api/teams/` -> `Auth`, but `admin` and `superuser` are denied (`403`).
- `PUT/PATCH/DELETE /api/teams/{id}/` -> `Auth + captain rules`, but `admin` and `superuser` are denied (`403`).
- `POST /api/tournaments/{id}/register-team/` -> `Auth + tournament registration rules`, but `admin` and `superuser` are denied (`403`).

---

### 1. Турніри

| Дія | Метод | Шлях | Доступ |
| :--- | :--- | :--- | :--- |
| **Список турнірів** | GET | `/api/tournaments/` | Всі |
| **Деталі турніру** | GET | `/api/tournaments/{id}/` | Всі (+ `registered_team` для Auth) |
| **Створити турнір** | POST | `/api/tournaments/manage/` | Admin |
| **Редагувати турнір** | PATCH/DEL| `/api/tournaments/manage/{id}/` | Admin |
| **Відкрити реєстрацію**| POST | `/api/tournaments/{id}/start-registration/` | Admin |
| **Доступні команди капітана** | GET | `/api/tournaments/{id}/eligible-teams/` | Auth |
| **Зареєстровані команди турніру** | GET | `/api/tournaments/{id}/teams/` | Auth |
| **Активний турнір команди** | GET | `/api/tournaments/active/?team_id={id}` | Auth |
| **Реєстрація команди** | POST | `/api/tournaments/{id}/register-team/` | Капітан |
| **Деталі/Зміна реєстрації**| GET/PATCH | `/api/tournaments/{id}/registrations/{reg_id}/` | Admin |
| **Список раундів** | GET | `/api/tournaments/{id}/rounds/` | Auth |
| **Створити раунд** | POST | `/api/tournaments/{id}/rounds/` | Admin |
| **Деталі/Зміна/Видалення раунду**| GET/PATCH/DEL | `/api/tournaments/rounds/{id}/` | GET: Auth, PATCH/DEL: Admin |
| **Почати раунд** | POST | `/api/tournaments/rounds/{id}/start/` | Admin |
| **Закрити прийом робіт**| POST | `/api/tournaments/rounds/{id}/close-submissions/` | Admin |
| **Фіналізація оцінок** | POST | `/api/tournaments/rounds/{id}/mark-evaluated/` | Admin |
| **Всі роботи турніру** | GET | `/api/tournaments/{id}/submissions/` | Auth (журі/адмін) |
| **Всі роботи раунду** | GET | `/api/tournaments/rounds/{id}/submissions/` | Auth (журі/адмін) |
| **Мої роботи** | GET | `/api/tournaments/submissions/` | Команда |
| **Подати роботу** | POST | `/api/tournaments/submissions/` | Команда |
| **Деталі/Зміна роботи** | GET/PATCH | `/api/tournaments/submissions/{id}/` | Команда |
| **Поточне завдання** | GET | `/api/tournaments/current-task/?tournament_id={id}` *(опц.)* | Учасники |
| **Список подій** | GET | `/api/tournaments/events/?tournament={id}` *(опц.)* | Всі |
| **Деталі події** | GET | `/api/tournaments/events/{id}/` | Всі |
| **Створити подію** | POST | `/api/tournaments/events/` | Admin |
| **Редагувати подію** | PATCH | `/api/tournaments/events/{id}/` | Admin |
| **Видалити подію** | DELETE | `/api/tournaments/events/{id}/` | Admin |
| **Список іконок** | GET | `/api/tournaments/icons/` | Всі |

> **`GET /api/tournaments/current-task/`**
> - Повертає перший активний раунд (`status=active`) серед турнірів зі статусом `running`, відсортований за `end_date`, `id`.
> - Опційний фільтр: `tournament_id` (query param).
> - Доступ: лише авторизовані користувачі, які є `admin` або учасниками/капітанами команди.
> - Якщо активного раунду немає — `404` (`No active round is available right now.`).
> - Поля відповіді: `id`, `tournament_id`, `tournament_name`, `name`, `task`, `deadline`, `must_have_requirements`, `tech_requirements`.

### 2. Раунди 

| Дія | Метод | Шлях | Доступ |
| :--- | :--- | :--- | :--- |
| **Розподіл робіт (журі)**| POST | `/api/evaluation/rounds/{id}/assign-jury/` | Admin |
| **Доступне журі для раунду**| GET | `/api/evaluation/rounds/{id}/available-jury/?include_assigned=true|false` | Admin |
| **Призначені роботи** | GET | `/api/evaluation/assignments/` | Jury |
| **Відправити оцінку** | POST | `/api/evaluation/evaluate/` | Jury |
| **Перегл/Зміна/Вид. оцінки**| GET/PATCH/DEL| `/api/evaluation/evaluate/{id}/` | Jury |



---

### 1. Турніри (Admin)

**Деталі турніру — GET `/api/tournaments/{id}/`**
```json
{
  "id": 5,
  "name": "Hackathon 2026",
  "description": "...",
  "start_date": "2026-05-01T10:00:00Z",
  "end_date": "2026-05-10T10:00:00Z",
  "max_teams": 20,
  "min_team_members": 2,
  "status": "registration",
  "rounds": [...],
  "registered_team": {
    "id": 3,
    "name": "Team Rocket"
  }
}
```
> Поле `registered_team` — команда, якою авторизований користувач зареєстрований у цьому турнірі (капітан або учасник, `is_active=true`).
> Якщо не авторизований або команди немає — `registered_team: null`.
> Використовується для визначення `team` при поданні submission.

**Створення турніру — POST `/api/tournaments/manage/`**
```json
{
  "name": "Hack 2026",
  "description": "Build a scalable backend",
  "start_date": "2026-05-01T10:00:00Z",
  "end_date": "2026-05-10T10:00:00Z",
  "max_teams": 20,
  "min_team_members": 2
}
```

**Редагування турніру — PATCH `/api/tournaments/manage/{id}/`**
```json
{
  "max_teams": 25,
  "description": "Updated hackathon description"
}
```

**Реєстрація команди — POST `/api/tournaments/{id}/register-team/`**
```json
{ "team_id": 10 }
```
> **Перевірки колізій (Phase 7):**
> - Команда не може бути зареєстрована в іншому активному турнірі (`registration` або `running`).
> - Жоден учасник команди (включно з капітаном) не може одночасно брати участь в іншому активному турнірі у складі іншої команди.
> - При конфлікті учасників API повертає email-и учасників, що вже беруть участь в іншому активному турнірі.

**Доступні команди капітана — GET `/api/tournaments/{id}/eligible-teams/`**
```json
[
  { "id": 10, "name": "Team Alpha", "members_count": 3 },
  { "id": 14, "name": "Team Beta", "members_count": 2 }
]
```
> Повертає тільки команди, де `team.captain_id == request.user.id`.
> Додаткових перевірок eligibility тут немає (перевірки колізій виконуються на етапі реєстрації).

**Зареєстровані команди турніру — GET `/api/tournaments/{id}/teams/`**
```json
[
  {
    "id": 10,
    "name": "Team Alpha",
    "members_count": 3,
    "is_public": true,
    "is_active": true
  },
  {
    "id": 11,
    "name": "Team Beta",
    "is_public": false,
    "is_active": false
  }
]
```
> Повертає всі реєстрації команд у конкретному турнірі з ознакою активності `is_active`.
> Доступний query-параметр `?only_active=true`, щоб повернути тільки активні команди (`is_active=true`).
> Якщо турнір не існує — `404`.

**Активний турнір команди — GET `/api/tournaments/active/?team_id={id}`**
```json
{
  "id": 3,
  "name": "Hack 2026",
  "status": "registration",
  "start_date": "2026-05-01T10:00:00Z"
}
```
> Повертає активний турнір команди (статус `registration` або `running`).
> Якщо активної участі для `team_id` немає — повертає `404`.

**Дисквалификація/Активація команди (Admin) — PATCH `/api/tournaments/{id}/registrations/{reg_id}/`**
```json
{ "is_active": false }
```
> Деактивовані команди (`is_active: false`) не можуть подавати роботи. Запис не видаляється.

> **Обмеження під час активного турніру (`registration` або `running`):**
> - Заборонені: інвайти в команду, join-request, прийняття інвайту/заявки, зміна `name`, зміна `is_public`.
> - Дозволено: видалення учасника капітаном, але тільки коли поточний розмір команди **строго більший** за `tournament.min_team_members`.
> - Для фронтенду в `GET /api/teams/{id}/` доступне поле `is_in_active_tournament` (`true/false`) для умовного приховування заборонених дій.

### 2. Раунди

**Список раундів — GET `/api/tournaments/{id}/rounds/`**
- Доступні фільтри: `?status=active,submission_closed`
- Звичайні користувачі бачать тільки раунди, які не мають статусу `draft`. Адміни бачать всі.

**Створення раунду (Admin) — POST `/api/tournaments/{id}/rounds/`**
```json
{
  "name": "Final Stage",
  "start_date": "2026-05-05T10:00:00Z",
  "end_date": "2026-05-07T18:00:00Z",
  "passing_count": 5,
  "tech_requirements": {},
  "must_have_requirements": {},
  "description": {},
  "criteria": [
    {
      "id": "backend",
      "name": "Backend Quality",
      "description": "Code quality",
      "max_score": 10
    }
  ]
}
```

**Видалення раунду (Admin) — DELETE `/api/tournaments/rounds/{id}/`**
- Неможливо видалити останній раунд турніру.

**Редагування раунду — PATCH `/api/tournaments/rounds/{id}/`**
```json
{
  "passing_count": 8,
  "tech_requirements": {
    "db": "PostgreSQL"
  },
  "description": {
    "text": "Updated description"
  }
}
```

> **Валідація раунду (актуальна бізнес-логіка):**
> - `start_date < end_date` (інакше 400).
> - Дати раунду мають бути в межах дат турніру (включно): дозволено `start_date == tournament.start_date` і `end_date == tournament.end_date`.
> - Раунди одного турніру не можуть перетинатися в часі. Перевірка виконується в бізнес-логіці моделі (`Round.clean()`), тому працює однаково для create/update.
> - Кейс на кшталт `round1(21.04-24.04)` і `round2(23.04-27.04)` заборонений (перетин періодів).
>
> **Валідація `passing_count`:**
> Якщо вказано `passing_count` і в турнірі вже є зареєстровані команди, значення не може перевищувати кількість зареєстрованих команд. Якщо команд ще немає (реєстрація не відкрита), перевірка пропускається.

### 3. Роботи (Команда)

**Всі роботи турніру (Jury/Admin) — GET `/api/tournaments/{id}/submissions/`**
```json
[
  {
    "id": 1,
    "team_details": {
      "id": 3,
      "name": "Team Rocket"
    },
    "round_details": {
      "id": 2,
      "name": "Round 1",
      "start_date": "...",
      "end_date": "...",
      "status": "submission_closed"
    },
    "github_url": "https://github.com/...",
    "demo_video_url": "https://youtube.com/...",
    "live_demo_url": "",
    "description": "...",
    "created_at": "...",
    "updated_at": "..."
  }
]
```
> Повертає всі submissions усіх раундів вказаного турніру, відсортовані за `updated_at` (спадання).
> Якщо турнір не існує — `404`.

**Всі роботи раунду (Jury/Admin) — GET `/api/tournaments/rounds/{id}/submissions/`**
> Аналогічна структура відповіді, але фільтрує submissions тільки для конкретного раунду.
> Якщо раунд не існує — `404`.

**Подача роботи — POST `/api/tournaments/submissions/`**
```json
{
  "team": 1,
  "round": 1,
  "github_url": "https://github.com/user/repo",
  "demo_video_url": "https://youtube.com/...",
  "description": "Ready for review"
}
```

**Редагування роботи — PATCH `/api/tournaments/submissions/{id}/`**
```json
{
  "github_url": "https://github.com/user/new-repo-link",
  "description": "Updated submission notes"
}
```

### 4. Розклад / Події (Admin)

**Список подій — GET `/api/tournaments/events/`**
> Опційний query-параметр: `?tournament={id}` для фільтрації за турніром.
> Сортування: за `start_datetime` (зростання).

**Створення події — POST `/api/tournaments/events/`**
```json
{
  "tournament": 1,
  "type": "meet",
  "title": "Online Consultation",
  "description": "Discuss project",
  "link": "https://meet.google.com/abc",
  "start_datetime": "2026-05-01T10:00:00Z",
  "icon": 2
}
```

**Створення без іконки (авто-призначення) — POST `/api/tournaments/events/`**
```json
{
  "tournament": 1,
  "type": "event",
  "title": "Deadline",
  "start_datetime": "2026-05-02T18:00:00Z"
}
```
> Якщо `icon` не передано або `null`:
> - `type == "meet"` → автоматично призначається іконка з `name="meet_default"` (camera)
> - `type == "event"` → автоматично призначається іконка з `name="event_default"` (calendar)

**Редагування події — PATCH `/api/tournaments/events/{id}/`**
```json
{
  "title": "Updated Title",
  "start_datetime": "2026-05-01T12:00:00Z"
}
```

**Видалення події — DELETE `/api/tournaments/events/{id}/`**
> Повертає `204 No Content`.

> **Валідація подій:**
> - `start_datetime` є обов'язковим.
> - Якщо `type == "event"` — поле `link` ігнорується (встановлюється порожнім).
> - Якщо `type == "meet"` — поле `link` дозволено.
> - `tournament` має існувати.

**Список іконок — GET `/api/tournaments/icons/`**
```json
[
  { "id": 1, "name": "meet_default", "path": "icons/camera.svg" },
  { "id": 2, "name": "event_default", "path": "icons/calendar.svg" }
]
```
> Повертає всі іконки з бази. Доступ публічний.

### 5. Оцінювання (Jury/Admin)

**Розподіл робіт (Admin) — POST `/api/evaluation/rounds/{id}/assign-jury/`**
```json
[
  { "submission": 101, "jury": [12, 13] },
  { "submission": 102, "jury": [12, 13] }
]
```
> **Логіка призначення (manual replace-all):**
> - endpoint доступний тільки у `round.status = submission_closed`;
> - потрібно покрити **всі** submission цього раунду;
> - для кожного submission має бути щонайменше 1 jury;
> - для всіх submission кількість jury має бути однакова;
> - дозволені тільки користувачі з роллю `jury`;
> - дублікати submission у payload і дублікати jury в межах submission заборонені;
> - при успіху попередні призначення раунду видаляються, створюються рівно ті, що передані в payload.

**Доступне журі (Admin) — GET `/api/evaluation/rounds/{id}/available-jury/`**
> Query param: `include_assigned` (`true` за замовчуванням).
> - `true`: повертає всіх користувачів з роллю `jury`.
> - `false`: виключає журі, яке вже має призначення в цьому раунді.

**Створення оцінки (Jury) — POST `/api/evaluation/evaluate/`**
```json
{
  "tournament_id": 123,
  "assignment": 1,
  "scores": [
    { "criterion_id": "backend", "score": 10 },
    { "criterion_id": "db", "score": 8 }
  ],
  "comment": "Excellent work!"
}
```
*Response Example:*
```json
{
  "id": 12,
  "assignment": 1,
  "scores": [
    { "criterion_id": "backend", "score": 10 },
    { "criterion_id": "db", "score": 8 }
  ],
  "comment": "Excellent work!",
  "total_score": 18,
  "final_score": 9.0,
  "created_at": "2026-04-26T10:00:00Z"
}
```

**Оновлення оцінки (Jury) — PATCH `/api/evaluation/evaluate/{id}/`**
```json
{
  "scores": [
    { "criterion_id": "backend", "score": 9 },
    { "criterion_id": "db", "score": 8 }
  ],
  "comment": "Revised score after check"
}
```

> **Важливо для оцінювання:**
> - `tournament_id` є **обов'язковим** для створення оцінки.
> - `assignment` має належати саме до переданого `tournament_id`, інакше повернеться помилка валідації.
> - `tournament_id` використовується лише для валідації (write-only) і не повертається у відповіді.
> - Кожен `criterion_id` має точно збігатися з id критерію з раунду.
> - Оцінка `score` має бути $\ge 0$ та $\le$ `max_score` критерію.
> - Дублікати `criterion_id` не допускаються.
> - Необхідно передати оцінки для **всіх** критеріїв раунду. Якщо потрібен 0, його потрібно передати явно (`"score": 0`).
> - **Авто-фіналізація:** Коли всі `JuryAssignment` для раунду мають оцінки, раунд автоматично переходить у статус `evaluated`. Якщо це останній раунд — турнір завершується автоматично.
