# API Leaderboard

---

## 1. Ендпоінти

| Дія | Метод | Шлях | Доступ |
| :--- | :--- | :--- | :--- |
| **Лідерборд раунду** | GET | `/api/evaluation/tournaments/rounds/{round_id}/leaderboard/` | Auth |
| **Лідерборд турніру (агрегований по раундах)** | GET | `/api/evaluation/tournaments/{tournament_id}/leaderboard/` | Auth |

---

## 2. Режими

### Round leaderboard

- `is_snapshot = true`
  - коли `tournament.status == finished`
  - дані читаються з `LeaderboardEntry` для конкретного `round_id`
- `is_snapshot = false`
  - коли `round.status == evaluated` і турнір ще не `finished`
  - дані обчислюються live з `SubmissionEvaluation`

### Tournament leaderboard

- `is_snapshot = true`
  - коли `tournament.status == finished`
  - дані читаються зі snapshot-записів `LeaderboardEntry` з `round = null`
- `is_snapshot = false`
  - коли є хоча б один раунд зі статусом `evaluated`
  - дані обчислюються live як сума результатів команди по всіх раундах участі

---

## 3. Доступ і видимість

- Обидва ендпоінти вимагають авторизацію (`IsAuthenticated`).
- Якщо дані ще не доступні для публічного перегляду:
  - роль `team` отримує `403 Forbidden`
  - ролі `admin`, `organizer`, `jury` можуть переглядати live-дані
- Поле `jury_breakdown`:
  - для ролі `team` завжди `null`
  - для `admin` / `organizer` / `jury` повертається повне значення

---

## 4. GET `/api/evaluation/tournaments/rounds/{round_id}/leaderboard/`

### Успіх (`200`)

```json
{
  "round_id": 1,
  "is_snapshot": true,
  "rankings": [
    {
      "rank": 1,
      "team_id": 3,
      "team_name": "Team Alpha",
      "total_score": 87.5,
      "average_score": 29.2,
      "criteria_breakdown": {
        "Innovation": 30,
        "Design": 28,
        "Presentation": 29.5
      },
      "jury_breakdown": null
    }
  ]
}
```

### Помилки

- `404 Not Found` — раунд не існує
- `403 Forbidden` — роль `team`, а раунд ще не `evaluated`

---

## 5. GET `/api/evaluation/tournaments/{tournament_id}/leaderboard/`

Повертає **агрегований лідерборд турніру**:
- у `rankings[]` кожна команда має загальний `total_score`
- `total_score` = сума `total_score` по всіх раундах, де команда мала submission
- `rounds[]` містить тільки ті раунди, де команда фактично брала участь
- ранжування йде за спаданням top-level `total_score`

### Успіх (`200`)

```json
{
  "tournament_id": 1,
  "is_snapshot": true,
  "rankings": [
    {
      "rank": 1,
      "team_id": 3,
      "team_name": "Team Alpha",
      "total_score": 210.5,
      "rounds": [
        {
          "round_id": 1,
          "round_name": "Qualifying",
          "total_score": 87.5,
          "average_score": 29.2,
          "criteria_breakdown": {
            "Innovation": 30,
            "Design": 28,
            "Presentation": 29.5
          },
          "jury_breakdown": null
        },
        {
          "round_id": 2,
          "round_name": "Final",
          "total_score": 123.0,
          "average_score": 41.0,
          "criteria_breakdown": {
            "Innovation": 42,
            "Design": 40,
            "Presentation": 41
          },
          "jury_breakdown": null
        }
      ]
    }
  ]
}
```

### Помилки

- `404 Not Found` — турнір не існує
- `404 Not Found` — у турніру немає раундів
- `403 Forbidden` — роль `team`, а в турнірі ще немає раундів зі статусом `evaluated`

---

## 6. Життєвий цикл snapshot

- Snapshot створюється автоматично при переході турніру у `finished`.
- Використовується сервіс `save_leaderboard_snapshot(tournament_id, round_id)`.
- Зберігаються:
  - per-round snapshot записи (`round = конкретний round_id`)
  - tournament-level snapshot записи (`round = null`) з `rounds_breakdown`
- Функція idempotent: повторний виклик не створює дублікати.
