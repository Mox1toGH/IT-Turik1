# 🏆 TournamentOS — Programming Tournament Platform

---

## 📖 Project Overview

**TournamentOS** is a comprehensive web platform for organizing and running programming tournaments. The system supports the full lifecycle of a competition — from team registration and task evaluation to real-time leaderboards and prize distribution.

The platform is built with a modern decoupled architecture: a **Django REST Framework** backend with WebSocket support and a **Vue.js** SPA frontend.

### Key Capabilities

- Role-based access control: **Admin**, **Organizer**, **Jury**, **Team**
- Real-time notifications and leaderboard updates via **WebSockets**
- Task submission and evaluation workflow
- **Google Calendar** integration — automatic sync of tournament events and rounds
- **Google OAuth** — one-click sign-in
- Export results to **Google Sheets**
- Built-in **Shop** — physical merch (t-shirts, bottles, bags) and digital items (avatar frames)
- Points system — earn points through competition, spend in the shop
- Auto-generated API client via **OpenAPI & Orval**

---

## 🛠️ Technologies Used

| Technology | Description | Usage in Project |
|------------|-------------|-----------------|
| ![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&style=flat-square) | Main backend language | Server logic, models, business rules |
| ![Django](https://img.shields.io/badge/Django-5.x-green?logo=django&style=flat-square) | Python web framework | ORM, routing, auth, signals |
| ![DRF](https://img.shields.io/badge/DRF-3.x-red?logo=django&style=flat-square) | REST API framework | API endpoints, serializers, permissions |
| ![Daphne](https://img.shields.io/badge/Daphne-ASGI-blueviolet?logo=django&style=flat-square) | ASGI server | WebSocket support, real-time events |
| ![Vue.js](https://img.shields.io/badge/Vue.js-3.x-brightgreen?logo=vue.js&style=flat-square) | Frontend SPA framework | UI, routing, state management |
| ![Vite](https://img.shields.io/badge/Vite-5.x-646CFF?logo=vite&style=flat-square) | Frontend build tool | Dev server, bundling |
| ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql&style=flat-square) | Relational database | Persistent data storage |
| ![WebSockets](https://img.shields.io/badge/WebSockets-Django--Channels-orange?logo=socket.io&style=flat-square) | Real-time protocol | Live notifications, leaderboard updates |
| ![OpenAPI](https://img.shields.io/badge/OpenAPI-Orval-brightgreen?logo=openapiinitiative&style=flat-square) | API schema & codegen | Auto-generated frontend API hooks |
| ![JWT](https://img.shields.io/badge/JWT-SimpleJWT-yellow?logo=jsonwebtokens&style=flat-square) | Authentication | Stateless token-based auth |
| ![Google OAuth](https://img.shields.io/badge/Google-OAuth2-red?logo=google&style=flat-square) | Social login | One-click sign-in via Google |
| ![Google Calendar](https://img.shields.io/badge/Google-Calendar_API-blue?logo=googlecalendar&style=flat-square) | Calendar integration | Auto-sync of events and rounds |
| ![Google Sheets](https://img.shields.io/badge/Google-Sheets_API-green?logo=googlesheets&style=flat-square) | Spreadsheet export | Export tournament results |
| ![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&style=flat-square) | Containerization | One-command local setup |

---

## 🏗️ Architecture

The project follows a **decoupled SPA + REST API** architecture:

```
frontend/          ← Vue.js SPA (Vite)
backend/
├── accounts/      ← user auth, roles, Google OAuth
├── teams/         ← team management
├── tournaments/   ← tournament and round logic
├── evaluation/    ← jury scoring and submission review
├── notifications/ ← WebSocket real-time notifications
└── shop/          ← points system, merch and digital items
```

- **REST API** — all communication via DRF endpoints
- **WebSockets** — real-time updates through Django Channels + Daphne
- **OpenAPI schema** — auto-generated and consumed by Orval to produce typed Vue hooks
- **Role-based permissions** — each role has scoped access across all modules

---

## 🧩 Design Patterns Implemented

- **JWT Authentication** — stateless, secure token-based auth
- **Custom Exception Handler** — unified error response format across all endpoints
- **Signal-driven side effects** — Google Calendar sync on `post_save`
- **Permission classes** — role-scoped access per view
- **Serializer-level validation** — clean separation of input validation from business logic
- **DRY via shared base classes** — reusable serializers, views, and mixins

---

## 👥 Team

| # | GitHub | Role | Main Area |
|---|--------|------|-----------|
| 1 | [@Mykhailo-Tr](https://github.com/Mykhailo-Tr) | Team Lead / Architect | Management + Architecture + Backend |
| 2 | [@Mox1toGH](https://github.com/Mox1toGH) | Tech Lead (DRF) | API + Backend / Frontend |
| 3 | [@lliyussha](https://github.com/lliyussha) | Project Manager / Support Developer | Documentation + Task Management |
| 4 | [@Lastto0](https://github.com/Lastto0) | Frontend Lead (Vue.js) | SPA Architecture |
| 5 | [@janekdev](https://github.com/janekdev) | Full-Stack Developer | Frontend Development + Backend Feature Support + UI Logic |

---

## 🚀 Getting Started

See [SETUP.md](./SETUP.md) for full setup instructions — manual and Docker variants, tests, and superuser creation.