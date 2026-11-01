# TournamentOS

Web platform for organizing and running programming tournaments. Decoupled architecture with Django Ninja + Vue.js SPA. 

## Features

- Role-based access control (Admin, Organizer, Jury, Team)
- Real-time updates via WebSockets (Django Channels)
- Task submission and evaluation workflow
- Google OAuth and JWT authentication
- Google Calendar sync for tournament events/rounds
- Google Sheets export for results
- Points system with built-in shop (merch and digital items)
- Auto-generated typed API client (OpenAPI + Orval)

## Tech Stack

- **Backend:** Python 3.11, Django 5.x, Django Ninja, Django Channels, Daphne, djangorestframework-simplejwt
- **Frontend:** Vue.js 3, Vite, TypeScript
- **Database:** PostgreSQL 16
- **Cache/Queue:** Redis (django-redis, channels-redis), Celery
- **Integrations:** Google OAuth, Google Calendar API, Google Sheets API
- **DevOps:** Docker Compose
- **API:** OpenAPI schema with Orval codegen
- **Perf/Debug:** django-debug-toolbar, django-silk

## Architecture

```
frontend/          # Vue.js SPA (Vite)
backend/
├── accounts/      # Auth, roles, Google OAuth
├── teams/         # Team management
├── tournaments/   # Tournaments and rounds
├── evaluation/    # Submissions and jury scoring
├── notifications/ # WebSocket notifications
├── news/          # News posts
├── stats/         # Statistics
└── corrupted_archive_api.py # Corrupted archive auth endpoint
```

- API via Django Ninja
- Real-time via WebSockets (Django Channels + Daphne)
- OpenAPI schema consumed by Orval for typed Vue composables/hooks

## Getting Started

See [SETUP.md](./SETUP.md) for setup instructions (manual or Docker), tests, and superuser creation.

See [CONNECTION_POOLING.md](./CONNECTION_POOLING.md) for database/PgBouncer configuration.
