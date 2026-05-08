# Access Updates

## 2026-05-08

- `GET /api/evaluation/assignments/?round_id={id}` -> `Auth + jury/set_results`, повертає тільки призначення поточного журі; `round_id` фільтрує по раунду.
- `GET /api/evaluation/assignments/{id}/` -> `Auth + jury/set_results`, деталі одного призначення тільки для поточного журі.
- `GET/PATCH/DELETE /api/evaluation/evaluate/{id}/` -> lookup по `pk` (URL: `evaluate/{id}`), доступ тільки до власних evaluation (`assignment__jury=request.user`).
- `GET /api/tournaments/rounds/{id}/submissions/` -> `Auth + set_results` (не просто `IsAuthenticated`).
- `RoundShortSerializer` тепер містить: `id`, `name`, `start_date`, `end_date`, `status`, `criteria`, `tournament`.
- `SubmissionSerializer` (submission details) містить необхідні для evaluation поля: `github_url`, `demo_video_url`, `live_demo_url`, `description`, `team_details`, `round_details`.
- `JuryAssignmentSerializer` повертає: `submission_details`, `evaluation`.
- `POST/PATCH /api/evaluation/evaluate/` зберігає `scores` у збагаченому вигляді:
  - `criterion_id`
  - `criterion_name`
  - `score`
  - Приклад: `{ "criterion_id": "backend", "criterion_name": "Backend Quality", "score": 10 }`
- `CanManageAssignments` лишився на `MANAGE_ROUNDS` (без змін).
- Для ролі `jury` набір прав без змін: тільки `VIEW_TOURNAMENT` + `SET_RESULTS` (без `MANAGE_ROUNDS`).

## 2026-05-07

- `POST /api/teams/` -> `Auth`, but `admin` and `superuser` are denied (`403`).
- `PUT/PATCH/DELETE /api/teams/{id}/` -> `Auth + captain rules`, but `admin` and `superuser` are denied (`403`).
- `POST /api/tournaments/{id}/register-team/` -> `Auth + tournament registration rules`, but `admin` and `superuser` are denied (`403`).
- `POST/PATCH /api/tournaments/submissions/` -> only team captain can create/update submission (`400` if not captain).
