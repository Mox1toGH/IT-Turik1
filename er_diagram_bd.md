# ER-діаграма бази даних проєкту

Документ містить ER-діаграми (Entity-Relationship), згруповані за модулями Django (apps), щоб кожна діаграма залишалась компактною та читабельною. "Зовнішні" сутності (з інших модулів) показані скорочено — лише `id` та назва — щоб було видно зв'язок без дублювання всіх полів.

---

## Загальна карта зв'язків (огляд)

```mermaid
erDiagram
    USER ||--o{ TEAM : "captain"
    USER ||--o{ TEAM_MEMBER : "членство"
    TEAM ||--o{ TEAM_MEMBER : "учасники"
    USER ||--o{ TOURNAMENT : "створив"
    TOURNAMENT ||--o{ ROUND : "раунди"
    TEAM ||--o{ SUBMISSION : "подання"
    ROUND ||--o{ SUBMISSION : "подання"
    SUBMISSION ||--o{ JURY_ASSIGNMENT : "оцінювання"
    USER ||--o{ JURY_ASSIGNMENT : "член жюрі"
    USER ||--o{ CERTIFICATE : "сертифікати"
    TEAM ||--o{ CERTIFICATE : "сертифікати"
    TOURNAMENT ||--o{ CERTIFICATE : "сертифікати"
    USER ||--o{ ORDER : "замовлення"
    PRODUCT ||--o{ ORDER : "замовлення"
    USER ||--|| USER_POINTS_BALANCE : "баланс балів"
    USER ||--o{ USER_INVENTORY : "інвентар"
    USER ||--o{ NOTIFICATION : "сповіщення"
    USER ||--o{ NEWS_ARTICLE : "новини"
```

---

## 1. Акаунти (accounts)

```mermaid
erDiagram
    USER {
        int id PK
        string username
        string email
        string password
        string first_name
        string last_name
        string role
        boolean is_staff
        boolean is_superuser
        boolean is_active
        boolean needs_onboarding
        string full_name
        string phone
        string city
        string avatar
        json google_calendar_token
        boolean google_calendar_connected
        datetime date_joined
        datetime last_login
    }

    ROLE_ACTIVATION_CODE {
        int id PK
        string code
        string role
        boolean is_used
        int created_by_id FK
        int used_by_id FK
        datetime created_at
        datetime used_at
    }

    USER ||--o{ ROLE_ACTIVATION_CODE : "created_by"
    USER ||--o{ ROLE_ACTIVATION_CODE : "used_by"
```

**Примітки:**
- `role` — одне з: `admin`, `team`, `jury`, `organizer`.
- `email` — унікальне поле.
- `ROLE_ACTIVATION_CODE.code` — унікальний, є індекс `(role, is_used)`.
- `created_by_id` / `used_by_id` — обидва nullable (`SET_NULL`).

---

## 2. Команди (teams)

```mermaid
erDiagram
    USER {
        int id PK
        string username
    }

    TEAM {
        int id PK
        string name
        string email
        int captain_id FK
        boolean is_public
        string organization
        string contact_telegram
        string contact_discord
        string banner
    }

    TEAM_MEMBER {
        int id PK
        int user_id FK
        int team_id FK
    }

    TEAM_INVITATION {
        int id PK
        int team_id FK
        int user_id FK
        int invited_by_id FK
        string status
        datetime responded_at
        datetime created_at
        datetime updated_at
    }

    TEAM_JOIN_REQUEST {
        int id PK
        int team_id FK
        int user_id FK
        string status
        int reviewed_by_id FK
        datetime reviewed_at
        datetime created_at
        datetime updated_at
    }

    USER ||--o{ TEAM : "captain"
    TEAM ||--o{ TEAM_MEMBER : "учасники"
    USER ||--o{ TEAM_MEMBER : "членства"
    TEAM ||--o{ TEAM_INVITATION : "запрошення"
    USER ||--o{ TEAM_INVITATION : "кого запрошено"
    USER ||--o{ TEAM_INVITATION : "хто запросив"
    TEAM ||--o{ TEAM_JOIN_REQUEST : "заявки на вступ"
    USER ||--o{ TEAM_JOIN_REQUEST : "хто подав заявку"
    USER ||--o{ TEAM_JOIN_REQUEST : "хто розглянув"
```

**Примітки:**
- `TEAM.name` — унікальне.
- `TEAM.members` (M2M User ↔ Team) реалізовано через таблицю `TEAM_MEMBER` — `unique(user, team)`.
- `TEAM_INVITATION` — `unique(team, user)`, індекси за `(team, status)` та `(user, status)`.
- `TEAM_JOIN_REQUEST` — `unique(team, user)`, аналогічні індекси.
- `reviewed_by_id` у `TEAM_JOIN_REQUEST` — nullable.

---

## 3. Турніри та подання (tournaments)

```mermaid
erDiagram
    USER {
        int id PK
        string username
    }

    TEAM {
        int id PK
        string name
    }

    TOURNAMENT {
        int id PK
        string name
        string description
        datetime start_date
        datetime end_date
        int max_teams
        int min_team_members
        string banner
        string status
        int created_by_id FK
        datetime created_at
        datetime updated_at
    }

    ROUND {
        int id PK
        int tournament_id FK
        string name
        json description
        json tech_requirements
        json must_have_requirements
        json criteria
        datetime start_date
        datetime end_date
        int passing_count
        string evaluation_criteria
        json materials
        string status
        datetime created_at
        datetime updated_at
    }

    SUBMISSION {
        int id PK
        int team_id FK
        int round_id FK
        string github_url
        string demo_video_url
        string demo_video_file
        string live_demo_url
        string description
        int created_by_id FK
        datetime created_at
        datetime updated_at
    }

    TOURNAMENT_TEAM_REGISTRATION {
        int id PK
        int tournament_id FK
        int team_id FK
        int created_by_id FK
        datetime created_at
        boolean is_active
        boolean is_disqualified
        string disqualification_reason
    }

    ICON {
        int id PK
        string name
        string path
    }

    EVENT {
        int id PK
        int tournament_id FK
        string type
        string title
        string description
        string link
        datetime start_datetime
        int icon_id FK
        datetime created_at
        datetime updated_at
    }

    USER ||--o{ TOURNAMENT : "created_by"
    TOURNAMENT ||--o{ ROUND : "раунди"
    TEAM ||--o{ SUBMISSION : "подання"
    ROUND ||--o{ SUBMISSION : "подання"
    USER ||--o{ SUBMISSION : "created_by"
    TOURNAMENT ||--o{ TOURNAMENT_TEAM_REGISTRATION : "реєстрації команд"
    TEAM ||--o{ TOURNAMENT_TEAM_REGISTRATION : "реєстрації"
    USER ||--o{ TOURNAMENT_TEAM_REGISTRATION : "created_by"
    TOURNAMENT ||--o{ EVENT : "події"
    ICON ||--o{ EVENT : "іконка"
```

**Примітки:**
- `ROUND` — `unique(tournament, start_date)`; також лише один `active`-раунд на турнір (умовний унікальний індекс по `status='active'`).
- `SUBMISSION` — `unique(team, round)`.
- `TOURNAMENT_TEAM_REGISTRATION` — `unique(tournament, team)`.
- `created_by_id` у `TOURNAMENT`, `SUBMISSION`, `TOURNAMENT_TEAM_REGISTRATION` — nullable (`SET_NULL`).
- `EVENT.icon_id` — nullable.

---

## 4. Оцінювання (evaluation)

```mermaid
erDiagram
    USER {
        int id PK
        string username
    }

    TEAM {
        int id PK
        string name
    }

    TOURNAMENT {
        int id PK
        string name
    }

    ROUND {
        int id PK
        string name
    }

    SUBMISSION {
        int id PK
        int team_id FK
        int round_id FK
    }

    JURY_ASSIGNMENT {
        int id PK
        int submission_id FK
        int jury_id FK
        datetime created_at
    }

    SUBMISSION_EVALUATION {
        int id PK
        int assignment_id FK
        json scores
        int total_score
        decimal final_score
        string comment
        datetime created_at
    }

    LEADERBOARD_ENTRY {
        int id PK
        int tournament_id FK
        int round_id FK
        int team_id FK
        int rank
        decimal total_score
        decimal average_score
        json criteria_breakdown
        json jury_breakdown
        json rounds_breakdown
        datetime snapshot_at
    }

    SUBMISSION ||--o{ JURY_ASSIGNMENT : "призначення жюрі"
    USER ||--o{ JURY_ASSIGNMENT : "член жюрі"
    JURY_ASSIGNMENT ||--|| SUBMISSION_EVALUATION : "оцінка"
    TOURNAMENT ||--o{ LEADERBOARD_ENTRY : "записи рейтингу"
    ROUND ||--o{ LEADERBOARD_ENTRY : "записи рейтингу"
    TEAM ||--o{ LEADERBOARD_ENTRY : "записи рейтингу"
```

**Примітки:**
- `JURY_ASSIGNMENT` — `unique(submission, jury)`.
- `SUBMISSION_EVALUATION.assignment_id` — `OneToOne` до `JURY_ASSIGNMENT` (одна оцінка на одне призначення).
- `total_score` та `final_score` обчислюються автоматично з `scores` при збереженні.
- `LEADERBOARD_ENTRY` — `unique(tournament, round, team)`; `round_id` та `jury_breakdown`/`rounds_breakdown` — nullable.

---

## 5. Сертифікати (certificates)

```mermaid
erDiagram
    USER {
        int id PK
        string username
        string full_name
    }

    TEAM {
        int id PK
        string name
    }

    TOURNAMENT {
        int id PK
        string name
    }

    CERTIFICATE_TEMPLATE {
        int id PK
        string name
        string image
        boolean is_default
        datetime created_at
    }

    CERTIFICATE {
        int id PK
        string unique_code
        int user_id FK
        int team_id FK
        int tournament_id FK
        string participant_name_snapshot
        string team_name_snapshot
        string tournament_name_snapshot
        string placement
        string certificate_number
        int template_id FK
        datetime created_at
    }

    USER ||--o{ CERTIFICATE : "сертифікати"
    TEAM ||--o{ CERTIFICATE : "сертифікати"
    TOURNAMENT ||--o{ CERTIFICATE : "сертифікати"
    CERTIFICATE_TEMPLATE ||--o{ CERTIFICATE : "шаблон"
```

**Примітки:**
- `CERTIFICATE.unique_code` — унікальний UUID.
- `user_id`, `team_id`, `tournament_id`, `template_id` — усі nullable (`SET_NULL`); назви/учасники "заморожуються" у полях `*_name_snapshot` на момент створення.
- `CERTIFICATE_TEMPLATE` — лише один шаблон може мати `is_default = true` (забезпечується при збереженні).

---

## 6. Магазин та інвентар (shop, inventory)

```mermaid
erDiagram
    USER {
        int id PK
        string username
    }

    CATEGORY {
        int id PK
        string name
    }

    AVATAR_FRAME {
        int id PK
        string name
        string svg_file
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    PRODUCT {
        int id PK
        string name
        string description
        int price
        int stock_quantity
        int category_id FK
        string product_type
        int avatar_frame_id FK
        string digital_asset_url
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    PRODUCT_IMAGE {
        int id PK
        int product_id FK
        string image
        datetime created_at
    }

    ORDER {
        int id PK
        int user_id FK
        int product_id FK
        int quantity
        int total_cost
        string status
        datetime created_at
        datetime updated_at
    }

    USER_INVENTORY {
        int id PK
        int user_id FK
        int product_id FK
        boolean is_equipped
        datetime acquired_at
        datetime updated_at
    }

    CATEGORY ||--o{ PRODUCT : "товари"
    AVATAR_FRAME ||--o{ PRODUCT : "товари"
    PRODUCT ||--o{ PRODUCT_IMAGE : "зображення"
    USER ||--o{ ORDER : "замовлення"
    PRODUCT ||--o{ ORDER : "замовлення"
    USER ||--o{ USER_INVENTORY : "інвентар"
    PRODUCT ||--o{ USER_INVENTORY : "власники"
```

**Примітки:**
- `CATEGORY.name` — унікальне; видалення категорії захищене (`PROTECT`), якщо є товари.
- `PRODUCT.product_type` — `physical` або `digital`; `avatar_frame_id` — nullable, лише для активних рамок.
- `digital_asset_url` — застаріле поле (deprecated), залишене для сумісності; реальний URL обчислюється через `effective_digital_asset_url`.
- `USER_INVENTORY` — `unique(user, product)`, товар має бути `digital`.
- Індекси `ORDER`: `(user, -created_at)`, `(status, -created_at)`.

---

## 7. Бали (points)

```mermaid
erDiagram
    USER {
        int id PK
        string username
    }

    TEAM {
        int id PK
        string name
    }

    TOURNAMENT {
        int id PK
        string name
    }

    ORDER {
        int id PK
        int user_id FK
    }

    USER_POINTS_BALANCE {
        int id PK
        int user_id FK
        int balance
        datetime updated_at
    }

    POINTS_TRANSACTION {
        int id PK
        int user_id FK
        int order_id FK
        int amount
        string reason
        datetime created_at
    }

    TOURNAMENT_POINTS_AWARD {
        int id PK
        int user_id FK
        int tournament_id FK
        int team_id FK
        string award_type
        int rank
        int amount
        datetime created_at
    }

    USER ||--|| USER_POINTS_BALANCE : "баланс балів"
    USER ||--o{ POINTS_TRANSACTION : "транзакції"
    ORDER ||--o{ POINTS_TRANSACTION : "транзакції"
    USER ||--o{ TOURNAMENT_POINTS_AWARD : "нагороди"
    TOURNAMENT ||--o{ TOURNAMENT_POINTS_AWARD : "нагороди"
    TEAM ||--o{ TOURNAMENT_POINTS_AWARD : "нагороди"
```

**Примітки:**
- `USER_POINTS_BALANCE.user_id` — `OneToOne`, по одному балансу на користувача.
- `POINTS_TRANSACTION.order_id` — nullable (`SET_NULL`); індекси `(user, -created_at)` та `(user, amount)`.
- `TOURNAMENT_POINTS_AWARD` — `award_type` ∈ {`participation`, `placement`}; `unique(user, tournament, award_type)`; `team_id` — nullable.

---

## 8. Сповіщення та новини (notifications, news)

```mermaid
erDiagram
    USER {
        int id PK
        string username
    }

    NOTIFICATION {
        int id PK
        int recipient_id FK
        string event_type
        string title
        string message
        boolean is_read
        datetime created_at
    }

    USER_NOTIFICATION_SETTINGS {
        int id PK
        int user_id FK
        boolean emails_disabled_globally
    }

    NOTIFICATION_CONFIG {
        int id PK
        int user_id FK
        string event_type
        boolean is_system_enabled
        boolean is_email_enabled
    }

    NOTIFICATION_DELIVERY_TASK {
        int id PK
        int recipient_id FK
        string channel
        string event_type
        string title
        string message
        string email_subject
        string status
        int attempts
        string last_error
        datetime next_attempt_at
        datetime created_at
        datetime updated_at
    }

    NEWS_ARTICLE {
        int id PK
        string title
        json content
        int created_by_id FK
        datetime created_at
        datetime updated_at
    }

    USER ||--o{ NOTIFICATION : "сповіщення"
    USER ||--|| USER_NOTIFICATION_SETTINGS : "налаштування"
    USER ||--o{ NOTIFICATION_CONFIG : "налаштування подій"
    USER ||--o{ NOTIFICATION_DELIVERY_TASK : "завдання доставки"
    USER ||--o{ NEWS_ARTICLE : "новини"
```

**Примітки:**
- `NOTIFICATION` — індекси `(recipient, is_read)`, `(recipient, created_at)`.
- `USER_NOTIFICATION_SETTINGS.user_id` — `OneToOne` (глобальне вимкнення email).
- `NOTIFICATION_CONFIG` — `unique(user, event_type)` (системні/email-сповіщення для конкретного типу події).
- `NOTIFICATION_DELIVERY_TASK.status` ∈ {`pending`, `processing`, `sent`, `failed`}; індекси `(status, next_attempt_at)`, `(recipient, created_at)`.
- `NEWS_ARTICLE.created_by_id` — nullable (`SET_NULL`); `content` — JSON-об'єкт (валідується, що саме dict).

---

## Підсумок: модулі та кількість сутностей

| Модуль (Django app) | Сутності |
|---|---|
| accounts | User, RoleActivationCode |
| teams | Team, TeamMember, TeamInvitation, TeamJoinRequest |
| tournaments | Tournament, Round, Submission, TournamentTeamRegistration, Icon, Event |
| evaluation | JuryAssignment, SubmissionEvaluation, LeaderboardEntry |
| certificates | CertificateTemplate, Certificate |
| shop | Category, AvatarFrame, Product, ProductImage, Order |
| inventory | UserInventory |
| points | UserPointsBalance, PointsTransaction, TournamentPointsAward |
| notifications | Notification, UserNotificationSettings, NotificationConfig, NotificationDeliveryTask |
| news | NewsArticle |

Усього: **31 сутність** у 10 модулях. `User` — центральна сутність, з якою пов'язана більшість інших таблиць.
