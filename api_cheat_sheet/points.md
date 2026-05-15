# Points API Cheat Sheet

---

### 1. Endpoints

| Action | Method | Path | Access |
| :--- | :--- | :--- | :--- |
| Get my points balance | GET | `/api/points/balance/` | Auth |
| Get my transaction history | GET | `/api/points/transactions/` | Auth |
| Get any user's balance | GET | `/api/points/admin/users/{user_id}/balance/` | Admin |
| Get any user's transaction history | GET | `/api/points/admin/users/{user_id}/transactions/` | Admin |
| Modify any user's balance | POST | `/api/points/admin/users/{user_id}/modify/` | Admin |

---

### 2. My Balance

**GET `/api/points/balance/`**

Returns current balance for authenticated user.

**Response example**
```json
{
  "user_id": 42,
  "balance": 120,
  "updated_at": "2026-05-13T15:42:10.182347Z"
}
```

---

### 3. My Transaction History

**GET `/api/points/transactions/`**

**Query params**
- `page` (optional)
- `page_size` (optional, max `100`)
- `ordering` (optional): `-created_at` (default), `created_at`, `amount`, `-amount`

**Response example**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 11,
      "user_id": 42,
      "amount": 50,
      "reason": "Tournament bonus",
      "created_at": "2026-05-13T15:40:00.000000Z"
    },
    {
      "id": 10,
      "user_id": 42,
      "amount": -20,
      "reason": "Penalty",
      "created_at": "2026-05-13T14:10:00.000000Z"
    }
  ]
}
```

---

### 4. Admin: View User Balance

**GET `/api/points/admin/users/{user_id}/balance/`**

Returns the selected user's current balance.

---

### 5. Admin: View User Transactions

**GET `/api/points/admin/users/{user_id}/transactions/`**

Supports same pagination and sorting params as user history endpoint:
- `page`
- `page_size`
- `ordering` = `-created_at`, `created_at`, `amount`, `-amount`

---

### 6. Admin: Modify User Balance

**POST `/api/points/admin/users/{user_id}/modify/`**

Every modification creates a `PointsTransaction` record.

**Operations**
- `add`: increase by `amount`
- `subtract`: decrease by `amount`
- `set`: set exact final balance to `amount`
- `reset`: set final balance to `0`

**Request examples**

Add points:
```json
{
  "operation": "add",
  "amount": 30,
  "reason": "Hackathon prize"
}
```

Subtract points:
```json
{
  "operation": "subtract",
  "amount": 15,
  "reason": "Rule violation"
}
```

Set absolute value:
```json
{
  "operation": "set",
  "amount": 100,
  "reason": "Manual correction"
}
```

Reset to zero:
```json
{
  "operation": "reset",
  "reason": "Season reset"
}
```

**Response example**
```json
{
  "user": {
    "id": 42,
    "username": "player1",
    "email": "player1@example.com"
  },
  "balance": {
    "user_id": 42,
    "balance": 100,
    "updated_at": "2026-05-13T15:44:02.220000Z"
  },
  "transaction": {
    "id": 12,
    "user_id": 42,
    "amount": 20,
    "reason": "Manual correction",
    "created_at": "2026-05-13T15:44:02.220000Z"
  }
}
```

---

### 7. Notes

- All `/api/points/` endpoints require Bearer token authentication.
- Admin endpoints require platform admin role (or superuser).
- Invalid `ordering` returns `400 validation_error`.
- If user does not exist, admin user-specific endpoints return `404 not_found`.
