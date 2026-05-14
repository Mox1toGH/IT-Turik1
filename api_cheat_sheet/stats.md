# Stats API Cheat Sheet

---

### 1. Endpoints

| Дія | Метод | Шлях | Доступ |
| :--- | :--- | :--- | :--- |
| **Статистика поточного користувача** | GET | `/api/stats/player/` | Auth |
| **Статистика конкретної команди** | GET | `/api/stats/team/{team_id}/` | Учасник/капітан цієї команди або Admin |
| **Статистика конкретного турніру** | GET | `/api/stats/tournament/{tournament_id}/` | Admin або організатор цього турніру |
| **Загальна admin-статистика** | GET | `/api/stats/admin/` | `is_staff=true` (Admin) |

---

### 2. Player Stats

**GET `/api/stats/player/`**

Повертає агреговану статистику для авторизованого користувача:
- кількість турнірів, де користувач брав участь у складі команди;
- перемоги/поразки;
- win rate;
- середній evaluation score;
- назва поточної (першої знайденої) команди.

**Response example**
```json
{
  "total_tournaments": 4,
  "wins": 1,
  "losses": 3,
  "win_rate": 25.0,
  "average_evaluation_score": 7.85,
  "current_team_name": "Code Falcons"
}
```

> Якщо команда не знайдена, `current_team_name` буде `null`.

---

### 3. Team Stats

**GET `/api/stats/team/{team_id}/`**

Повертає статистику команди:
- total tournaments / wins / losses / win rate;
- середній бал команди;
- кількість активних учасників;
- top player за середнім балом.

**Response example**
```json
{
  "team_id": 7,
  "team_name": "Code Falcons",
  "total_tournaments": 5,
  "wins": 2,
  "losses": 3,
  "win_rate": 40.0,
  "average_member_evaluation_score": 8.12,
  "active_members_count": 4,
  "top_player": {
    "id": 21,
    "username": "captain_neo",
    "average_evaluation_score": 8.9
  }
}
```

**Доступ**
- дозволено: капітан цієї команди, учасник цієї команди, Admin;
- інакше: `403 PermissionDenied`.

---

### 4. Tournament Stats

**GET `/api/stats/tournament/{tournament_id}/`**

Повертає статистику турніру:
- кількість зареєстрованих команд/гравців;
- fill rate відносно `max_teams`;
- завершені/всі матчі (submissions);
- середній evaluation score;
- top-3 команди з leaderboard.

**Response example**
```json
{
  "tournament_id": 12,
  "tournament_name": "IT Turik Spring 2026",
  "total_registered_teams": 14,
  "total_registered_players": 57,
  "fill_rate": 70.0,
  "completed_matches": 28,
  "total_matches": 32,
  "average_evaluation_score": 7.54,
  "top_teams": [
    { "team_id": 7, "team_name": "Code Falcons", "rank": 1, "average_score": 8.91 },
    { "team_id": 3, "team_name": "Null Squad", "rank": 2, "average_score": 8.42 },
    { "team_id": 9, "team_name": "Stack Masters", "rank": 3, "average_score": 8.17 }
  ]
}
```

**Доступ**
- Admin;
- або користувач, який створив цей турнір (`tournament.created_by`).

---

### 5. Admin Stats

**GET `/api/stats/admin/`**

Повертає метрики для admin dashboard:
- total users / teams / tournaments;
- нові реєстрації за 7 та 30 днів;
- кількість активних турнірів (`registration` + `running`);
- розбивка користувачів за ролями;
- total evaluation records.

**Response example**
```json
{
  "total_users": 186,
  "total_teams": 52,
  "total_tournaments": 11,
  "new_registrations_last_7_days": 9,
  "new_registrations_last_30_days": 34,
  "active_tournaments": 3,
  "users_by_role": [
    { "role": "admin", "count": 2 },
    { "role": "jury", "count": 18 },
    { "role": "organizer", "count": 7 },
    { "role": "team", "count": 159 }
  ],
  "total_evaluation_records": 412
}
```

---

### 6. Notes

- Усі endpoints секції `/api/stats/` потребують Bearer token.
- Значення `win_rate`, `fill_rate`, `average_*` округляються до 2 знаків після коми.
- Для командних/турнірних endpoint-ів повертається `404`, якщо `team_id` або `tournament_id` не існує.
