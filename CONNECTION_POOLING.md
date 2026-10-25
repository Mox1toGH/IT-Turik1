# Database Connection Pooling

How connection pooling works in TournamentOS, when to use which pooler, and why
**you must never run both at once**.

> Audience: backend devs and anyone deploying this project.
> If you only remember one line: **pick exactly one pooler, never two.**

---

## 1. The problem pooling solves

Opening a PostgreSQL connection is expensive: TCP handshake, TLS, authentication,
and Postgres forking a backend process (~5–10 MB RAM each). Django's default
behaviour is to open a connection per request and close it afterwards, so a busy
API spends a large slice of every request just reconnecting.

Pooling keeps connections open and reuses them. There are two places to do that,
and they are **alternatives, not layers**.

---

## 2. The two poolers in this project

### A. Django's built-in pool (psycopg3) — `backend/backend/settings.py`

Django 5.1+ can pool connections inside the application process using
`psycopg_pool`. We enable it by adding a `pool` block to `DATABASES`:

```python
DATABASES["default"]["pool"] = {
    "min_size": 2,
    "max_size": 10,   # per gunicorn worker!
    "timeout": 30,
    "max_lifetime": 3600,
    "max_idle": 600,
}
```

Tuned with `DB_POOL_MIN_SIZE` / `DB_POOL_MAX_SIZE` / `DB_POOL_TIMEOUT` /
`DB_POOL_MAX_LIFETIME` / `DB_POOL_MAX_IDLE`.

> ⚠️ **The numbers are per worker process.** With 6 gunicorn workers and
> `max_size=10`, the app can open **60** connections on its own. Add Celery and
> any `sync_to_async` threads and you approach Postgres' default
> `max_connections = 100` fast. This is not theoretical — see §5.

### B. PgBouncer — `docker-compose.yml`

A separate process that sits between the app and Postgres. Many app connections
share a small, fixed number of real server connections:

```yaml
pgbouncer:
  image: edoburu/pgbouncer:latest
  environment:
    DB_HOST: db
    POOL_MODE: transaction      # connection returned to pool after each transaction
    DEFAULT_POOL_SIZE: "25"     # real Postgres connections PgBouncer keeps open
    MAX_CLIENT_CONN: "1000"     # app-side connections it accepts
    MAX_DB_CONNECTIONS: "60"
```

With PgBouncer, the app's connection count stops mattering: 1,000 client
connections can share 25 server connections.

---

## 3. Why not both? (the core rule)

```
PgBouncer alone:     app (many cheap conns) ──► PgBouncer ──(25 shared)──► Postgres
Django pool alone:   app (pool of N held)    ───────────────────────────► Postgres
Both:                app holds N conns ──► PgBouncer ──(still N)──► Postgres
                                              ↑ nothing left to multiplex
```

PgBouncer exists to **share** a small number of connections among many clients.
If every client is already holding dedicated connections from its own pool,
there is nothing to share — you only pay for the extra network hop and an extra
process to operate.

There is also a **correctness** reason. PgBouncer's default `transaction` pooling
mode breaks session-scoped features: server-side prepared statements,
`LISTEN`/`NOTIFY`, advisory locks held across transactions, and temp tables.
psycopg3's pool uses prepared statements, so running it behind transaction-mode
PgBouncer can produce real bugs — not merely wasted resources.

**Nested pools are a misconfiguration.** That is why the pool is switchable:

```env
DB_POOL_ENABLED=false   # turn Django's pool OFF when using PgBouncer
```

`docker-compose.loadtest.yml` already does exactly this — it routes the app
through PgBouncer **and** sets `DB_POOL_ENABLED=false`.

---

## 4. Which one should I use?

| Deployment | Django pool | PgBouncer | Notes |
|---|:---:|:---:|---|
| **Managed DB with its own pooler** (Neon, Supabase, RDS Proxy, Cloud SQL) | ❌ | ❌ | Point `DB_HOST` at the provider's **pooled** endpoint. Their pooler *is* your pooler. |
| **Remote Postgres, no provider pooler** | ❌ | ✅ | PgBouncer lives next to the DB, not in the app. Server connections stay low and stable. |
| **Local / co-located Postgres** (Docker Compose, same host) | ✅ | ❌ | Zero extra hops; the app process can pool directly. Best for dev. |

### Rule of thumb

- The further away the database, the more you want a pooler **on the DB side**.
- The closer the database, the more you want the pool **in the app**.
- If the provider already gives you a pooler, use it and configure neither.

> For this project's planned setup (remote database), the target is
> **PgBouncer only, `DB_POOL_ENABLED=false`** — or drop PgBouncer entirely and
> use the provider's pooled endpoint if it has one.

---

## 5. What we actually measured

Numbers from the 500-user k6 load test (`perf/RESULTS.md`), 12-core machine:

| Configuration | Throughput | p95 | Errors |
|---|---:|---:|---:|
| 2 workers, no PgBouncer | 67 req/s | 18.75 s | 29% |
| 6 workers, no PgBouncer | 137 req/s | 4.18 s | **50%** |
| 6 workers + PgBouncer (app pool off) | 92 req/s | 6.76 s | **0%** |

Three lessons:

1. **Connection exhaustion is real.** 6 workers × 15 pooled connections + Celery
   exceeded `max_connections=100`, producing `FATAL: sorry, too many clients
   already` on half the requests — a *capacity* failure, not a code bug.
2. **PgBouncer fixed the errors but cost throughput locally** (137 → 92 req/s).
   A local pooler adds a hop while the local Postgres was never the bottleneck.
   That is expected; PgBouncer pays off against **remote** databases.
3. **Adding connections cannot fix a CPU-bound app.** Throughput plateaued at
   ~135 req/s regardless of user count while Postgres idled at 60–80% CPU.
   Pool tuning changes *reliability*, not raw throughput.

---

## 6. Configuration reference

### Environment variables

| Variable | Default | Meaning |
|---|---|---|
| `DB_POOL_ENABLED` | `true` | Enable Django's native psycopg pool. **Set `false` when using PgBouncer.** |
| `DB_POOL_MIN_SIZE` | `2` | Connections kept open per worker |
| `DB_POOL_MAX_SIZE` | `10` | Max connections **per worker** (`workers × this ≤ Postgres limit`) |
| `DB_POOL_TIMEOUT` | `30` | Seconds to wait for a free connection |
| `DB_POOL_MAX_LIFETIME` | `3600` | Recycle a connection after N seconds |
| `DB_POOL_MAX_IDLE` | `600` | Close connections idle longer than N seconds |
| `DB_DISABLE_SERVER_SIDE_CURSORS` | — | Set `true` when using transaction-mode PgBouncer |

### Required with transaction-mode PgBouncer

```env
DB_HOST=pgbouncer
DB_PORT=5432                    # PgBouncer's port inside the compose network
DB_POOL_ENABLED=false
DB_DISABLE_SERVER_SIDE_CURSORS=true
```

`DB_DISABLE_SERVER_SIDE_CURSORS=true` is mandatory: transaction pooling can hand
a cursor's connection to another client mid-iteration.

### Sizing math

```
app connections  = gunicorn workers × DB_POOL_MAX_SIZE    (pool mode)
app connections  = MAX_CLIENT_CONN                         (PgBouncer mode)
server conns     = DEFAULT_POOL_SIZE / MAX_DB_CONNECTIONS  (PgBouncer mode)

Keep server connections well under Postgres' max_connections (default 100).
```

Example, 6 workers:

- Pool mode: `6 × 10 = 60` app connections → fine only on a direct connection.
- PgBouncer mode: 1,000 clients → but only `25` real server connections. ✅

---

## 7. Local development cheat sheet

```powershell
# Direct to Postgres, no PgBouncer (default; uses Django's pool)
#   backend/.env:  DB_HOST=pgbouncer -> db, DB_POOL_ENABLED=true
docker compose up -d db redis backend

# Through PgBouncer, app pool off
#   backend/.env:  DB_HOST=pgbouncer, DB_POOL_ENABLED=false
docker compose up -d db redis pgbouncer backend
```

`docker-compose.loadtest.yml` is the ready-made example of the second shape:

```powershell
docker compose -f docker-compose.yml -f docker-compose.loadtest.yml up -d db redis pgbouncer backend celery
```

### Verifying which mode you are in

```powershell
# App pool disabled + PgBouncer in the path?
docker compose exec backend python -c "import os; print('DB_HOST=', os.getenv('DB_HOST'), 'pool=', os.getenv('DB_POOL_ENABLED'))"

# How many connections has Postgres actually accepted?
docker compose exec db psql -U itturik -d itturik -c "SELECT count(*), state FROM pg_stat_activity GROUP BY state;"
```

If that count climbs with worker count, you are in pool mode. If it stays flat
around `DEFAULT_POOL_SIZE` no matter how many workers you run, PgBouncer is doing
its job.

---

## 8. Related reading

- [`perf/RESULTS.md`](./perf/RESULTS.md) — full load-test report and the
  saturation analysis behind §5.
- [`SETUP.md`](./SETUP.md) — install and run instructions.
- [`docker-compose.loadtest.yml`](./docker-compose.loadtest.yml) — PgBouncer +
  pool-disabled example.

## 9. TL;DR for reviewers

- Pooling is either **in the app** (Django/psycopg) or **beside the DB**
  (PgBouncer). Choose one.
- Running both is not "more optimized" — it is a **misconfiguration** that spends
  a network hop to multiplex connections that are already reserved.
- `DB_POOL_ENABLED=false` whenever a pooler already sits in front of Postgres.
- For a remote DB: PgBouncer (or the provider's pooler), app pool **off**.
