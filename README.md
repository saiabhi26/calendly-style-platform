# Appointment Booker SaaS

A multi-tenant appointment-booking backend (Calendly-style) built with **FastAPI** and **PostgreSQL**. Business owners manage organizations, services, and weekly availability; customers book open time-slots through a public page — with database-enforced protection against double-booking.

**🔗 Live demo:** https://appointment-booker-nmkz.onrender.com
| | |
|---|---|
| Owner dashboard | [`/`](https://appointment-booker-nmkz.onrender.com/) |
| Customer booking page | [`/book?org=<slug>`](https://appointment-booker-nmkz.onrender.com/book) |
| Interactive API docs (Swagger) | [`/docs`](https://appointment-booker-nmkz.onrender.com/docs) |

> ⏳ **Free-tier note:** the app sleeps after ~15 min of inactivity. The **first request may take ~30 seconds** to wake it up — then it's fast. (Give it a moment and refresh.)
>
> This is a **backend-focused** project; the two web frontends are intentionally minimal (simple and legible).

---

## What it demonstrates

- **Multi-tenant REST API** with JWT authentication and strict per-owner data isolation.
- **Non-trivial domain logic** — timezone-aware slot generation and concurrency-safe booking.
- **Production deployment** — containerized with Docker, deployed to the cloud with a managed database and auto-deploy on every push.
- **Engineering practices** — versioned database migrations, a layered/modular architecture, and a documented problem→solution log.

---

## Tech stack

| Area | Technology |
|---|---|
| API | FastAPI (Python 3.13), Uvicorn |
| Data | PostgreSQL, SQLAlchemy 2.0, Alembic (migrations) |
| Auth | JWT (PyJWT) + bcrypt password hashing |
| Validation | Pydantic v2 |
| Container / deploy | Docker · **Render** (web) + **Neon** (Postgres) |
| Frontend | Static HTML + vanilla JS (Pico.css) |
| Planned | Celery + Redis (async email) · GitHub Actions (CI/CD) |

---

## Architecture highlights

- **Multi-tenancy / ownership scoping** — every query is scoped to the authenticated owner; cross-tenant access returns `404` (never leaks that a resource exists). Backed by database foreign keys.
- **Slot generation** — for a service + date, computes open slots from the org's weekly availability minus existing bookings, honoring the org's timezone (`zoneinfo`).
- **Double-booking prevention** — a `UNIQUE(service_id, slot_start)` constraint is the source of truth, backed by an app-level availability check. Concurrent requests for the same slot get a clean `409` — never a duplicate row.
- **Migrations** — schema changes are versioned with Alembic and auto-applied on deploy.
- **Modular layout** — each feature is split into `schemas` (request/response), `service` (business logic + DB), and `router` (HTTP).

---

## API overview

**Owner (JWT auth)** — `/auth/*`, `/organizations`, `/services`, `/availability`
**Public (no auth)** — `/orgs/{slug}`, `/orgs/{slug}/services`, `/orgs/{slug}/available-days`, `/slots`, `/bookings`

Full interactive documentation is auto-generated at [`/docs`](https://appointment-booker-nmkz.onrender.com/docs).

---

## Project structure

```
app/
  main.py            # app entry, router wiring, static serving
  config.py          # env-backed settings
  database.py        # SQLAlchemy engine / session / Base
  deps.py            # shared deps (get_db, get_current_user)
  core/security.py   # password hashing + JWT
  models/            # SQLAlchemy models
  modules/           # feature modules (schemas / service / router)
  static/            # owner dashboard + customer booking page
alembic/             # migrations
Dockerfile           # container image
render.yaml          # Render blueprint (infra-as-code)
```

---

## Project docs

- **[ROADMAP.md](./ROADMAP.md)** — what's built and what's next (CI/CD, per-service availability, async email, payments, Google Calendar, subscriptions).
- **[CHALLENGES.md](./CHALLENGES.md)** — notable problems hit while building/deploying, and how they were solved.
