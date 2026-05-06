# Calendar API


---

### 1. Події / Розклад

| Дія | Метод | Шлях | Доступ |
| :--- | :--- | :--- | :--- |
| **Список подій** | GET | `/api/tournaments/events/` | Всі |
| **Деталі події** | GET | `/api/tournaments/events/{id}/` | Всі |
| **Створити подію** | POST | `/api/tournaments/events/` | Admin |
| **Редагувати подію** | PATCH | `/api/tournaments/events/{id}/` | Admin |
| **Видалити подію** | DELETE | `/api/tournaments/events/{id}/` | Admin |
| **Список іконок** | GET | `/api/tournaments/icons/` | Всі |

> **`GET /api/tournaments/events/`** — Query-параметри:
> - `tournament` — фільтр за ID турніру (опц.)
> - `type` — фільтр за типом, підтримує кілька через кому: `?type=meet,event`
> - `start_datetime__gte` — події, що починаються ≥ вказаної дати
> - `start_datetime__lte` — події, що починаються ≤ вказаної дати
> - `end_datetime__gte` — події, що закінчуються ≥ вказаної дати
> - `end_datetime__lte` — події, що закінчуються ≤ вказаної дати
>
> Сортування: за `start_datetime` (зростання).
> Доступ: читання — всі; створення/редагування/видалення — Admin.

---

### 2. Події (Admin)

**Створення події — POST `/api/tournaments/events/`**
```json
{
  "tournament": 1,
  "type": "meet",
  "title": "Online Consultation",
  "description": "Discuss project",
  "link": "https://meet.google.com/abc",
  "start_datetime": "2026-05-01T10:00:00Z",
  "end_datetime": "2026-05-01T11:00:00Z",
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
  "end_datetime": "2026-05-01T12:00:00Z"
}
```

**Видалення події — DELETE `/api/tournaments/events/{id}/`**
> Повертає `204 No Content`.

> **Валідація подій:**
> - `start_datetime` є обов'язковим.
> - Якщо вказано `end_datetime`, він має бути ≥ `start_datetime`.
> - Якщо `type == "event"` — поле `link` ігнорується (встановлюється порожнім).
> - Якщо `type == "meet"` — поле `link` дозволено.
> - `tournament` має існувати.

---

### 3. Фільтри календаря — приклади

**Події за тиждень:**
```
GET /api/tournaments/events/?tournament=1&start_datetime__gte=2026-05-01T00:00:00Z&start_datetime__lte=2026-05-07T23:59:59Z
```

**Тільки онлайн‑консультації:**
```
GET /api/tournaments/events/?type=meet
```

**Події кількох типів:**
```
GET /api/tournaments/events/?type=meet,event
```

**Події, що закінчуються після певної дати:**
```
GET /api/tournaments/events/?end_datetime__gte=2026-05-05T00:00:00Z
```

**Комбінований фільтр (консультації в межах тижня для турніру):**
```
GET /api/tournaments/events/?tournament=1&type=meet&start_datetime__gte=2026-05-01T00:00:00Z&start_datetime__lte=2026-05-07T23:59:59Z
```

---

### 4. Іконки

**Список іконок — GET `/api/tournaments/icons/`**
```json
[
  { "id": 1, "name": "meet_default", "path": "icons/camera.svg" },
  { "id": 2, "name": "event_default", "path": "icons/calendar.svg" }
]
```
> Повертає всі іконки з бази. Доступ публічний.
