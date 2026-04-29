#  API Cheat Sheet


---





| Дія | Метод | Шлях | Доступ |
| :--- | :--- | :--- | :--- |
| **Список турнірів** | GET | `/api/tournaments/` | Всі |
| **Деталі турніру** | GET | `/api/tournaments/{id}/` | Всі |
| **Створити турнір** | POST | `/api/tournaments/manage/` | Admin, Organizer |
| **Редагувати турнір** | PATCH/DEL| `/api/tournaments/manage/{id}/` | Admin |
| **Відкрити реєстрацію**| POST | `/api/tournaments/{id}/start-registration/` | Admin |
| **Реєстрація команди** | POST | `/api/tournaments/{id}/register-team/` | Капітан |
| **Список раундів** | GET | `/api/tournaments/rounds/` | Admin |
| **Створити раунд** | POST | `/api/tournaments/rounds/` | Admin |
| **Деталі/Зміна раунду**| GET/PATCH | `/api/tournaments/rounds/{id}/` | Admin |
| **Почати раунд** | POST | `/api/tournaments/rounds/{id}/start/` | Admin |
| **Закрити прийом робіт**| POST | `/api/tournaments/rounds/{id}/close-submissions/` | Admin |
| **Фіналізація оцінок** | POST | `/api/tournaments/rounds/{id}/mark-evaluated/` | Admin |
| **Мої роботи** | GET | `/api/tournaments/submissions/` | Команда |
| **Подати роботу** | POST | `/api/tournaments/submissions/` | Команда |
| **Деталі/Зміна роботи** | GET/PATCH | `/api/tournaments/submissions/{id}/` | Команда |
| **Поточне завдання** | GET | `/api/tournaments/current-task/` | Учасники |
| **Розподіл робіт (журі)**| POST | `/api/evaluation/rounds/{id}/assign-jury/` | Admin |
| **Призначені роботи** | GET | `/api/evaluation/assignments/` | Jury |
| **Відправити оцінку** | POST | `/api/evaluation/evaluate/` | Jury |
| **Перегл/Зміна/Вид. оцінки**| GET/PATCH/DEL| `/api/evaluation/evaluate/{id}/` | Jury |

---

---

### 1. Турніри (Admin)

**Створення турніру — POST `/api/tournaments/manage/`**
```json
{
  "name": "Hack 2026",
  "description": "Build a scalable backend",
  "start_date": "2026-05-01T10:00:00Z",
  "end_date": "2026-05-10T10:00:00Z",
  "rounds_count": 2,
  "max_teams": 20,
  "min_team_members": 2,
  "tech_requirements": "Django + PostgreSQL",
  "must_have_requirements": ["Requirement 1"]
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

### 2. Раунди (Admin)

**Створення раунду — POST `/api/tournaments/rounds/`**
```json
{
  "tournament": 1,
  "position": 2,
  "name": "Final Stage",
  "start_date": "2026-05-05T10:00:00Z",
  "end_date": "2026-05-07T18:00:00Z",
  "passing_count": 5
}
```

**Редагування раунду — PATCH `/api/tournaments/rounds/{id}/`**
```json
{
  "tech_requirements": "FastAPI + MongoDB",
  "passing_count": 8
}
```

### 3. Роботи (Команда)

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

### 4. Оцінювання (Jury/Admin)

**Розподіл робіт (Admin) — POST `/api/evaluation/rounds/{id}/assign-jury/`**
```json
{ "k": 2 } 
```

**Створення оцінки (Jury) — POST `/api/evaluation/evaluate/`**
```json
{
  "assignment": 1,
  "score_backend": 10,
  "score_db": 8,
  "score_frontend": 9,
  "score_completeness": 10,
  "score_stability": 9,
  "score_usability": 10,
  "comment": "Excellent work!"
}
```

**Оновлення оцінки (Jury) — PATCH `/api/evaluation/evaluate/{id}/`**
```json
{
  "score_backend": 9,
  "comment": "Revised score after check"
}
```
