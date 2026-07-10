# Appointment Booker SaaS

A multi-tenant appointment-booking backend (Calendly/Cal.com style) built with **FastAPI**. Business owners create organizations, define services and weekly availability, and customers book open time-slots through a public page — with database-enforced protection against double-booking.

Built backend-first and testable end-to-end through the auto-generated Swagger UI at `/docs`, plus two lightweight web frontends served by the app itself.

---

## Features

**Implemented**
- **Authentication** — register / login with hashed passwords (bcrypt) and JWT access tokens; protected routes via a reusable dependency.
- **Organizations** — owner-scoped CRUD with unique slugs. Full multi-tenancy: users only ever see and edit their own data.
- **Services** — per-organization offerings (title, duration, price, ONLINE/OFFLINE), scoped to the owning org.
- **Availability rules** — weekly opening hours per organization (day-of-week + start/end time) with cross-field validation.
- **Slot generation** — computes open time-slots for a service on a given date from availability rules minus already-booked times, honoring each org's timezone.
- **Public booking** — unauthenticated endpoints for customers to browse services, view open slots, and book. Double-booking prevented by a database unique constraint.
- **Owner dashboard** (`/`) — manage organizations and services in the browser.
- **Customer booking page** (`/book`) — a service → day → time → details booking flow.

**Planned** (see [Roadmap](#roadmap))
- Async confirmation emails (Celery + Redis + Resend)
- Payments (Razorpay), Google Calendar/Meet, payouts, subscriptions

---

## Tech stack

| Concern | Technology |
|---|---|
| Web framework / API | **FastAPI** |
| ASGI server | **Uvicorn** |
| ORM | **SQLAlchemy 2.0** |
| Migrations | **Alembic** |
| Database | **PostgreSQL** (via Docker) |
| Validation / settings | **Pydantic v2** / **pydantic-settings** |
| Auth | **PyJWT** + **passlib[bcrypt]** |
| Background jobs *(planned)* | **Celery** + **Redis** |
| Email *(planned)* | **Resend** |
| Frontend | Static HTML + vanilla JS, styled with **Pico.css** |

---

## Project structure

```
app/
  main.py                 # FastAPI app entry + router wiring + static serving
  config.py               # env-backed settings (pydantic-settings)
  database.py             # SQLAlchemy engine, SessionLocal, Base
  deps.py                 # shared dependencies (get_db, get_current_user)
  core/
    security.py           # password hashing + JWT helpers
  models/                 # SQLAlchemy models (one table per file)
  modules/                # feature modules, each: schemas / service / router
    auth/  organization/  service/  availability/  slot/  booking/  public/
  static/                 # owner dashboard + customer booking page
alembic/                  # database migrations
docker-compose.yml        # Postgres + Redis
requirements.txt
```

Each feature module follows the same split: **`schemas.py`** (Pydantic request/response), **`service.py`** (business logic + DB access), **`router.py`** (HTTP endpoints).

---

## Getting started

### Prerequisites
- Python 3.11+
- Docker Desktop (runs Postgres + Redis)
- Git

### Setup

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd AppointmentBookerSaaS

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env (see below), then start Postgres + Redis
docker compose up -d

# 5. Apply database migrations
alembic upgrade head

# 6. Run the app
uvicorn app.main:app --reload
```

### Environment (`.env`)
Create a `.env` file in the project root (never commit it):

```
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/appointments
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=change-me-dev-secret
JWT_REFRESH_SECRET=change-me-refresh-secret
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=60
RESEND_API_KEY=your_resend_key
EMAIL_FROM=onboarding@resend.dev
```

Generate real JWT secrets with:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Where things live
| URL | What |
|---|---|
| `http://localhost:8000/docs` | Swagger UI — interactive API testing |
| `http://localhost:8000/` | Owner dashboard (login → manage orgs & services) |
| `http://localhost:8000/book?org=<slug>` | Customer booking page |
| `http://localhost:8000/health-check` | Health check |

---

## API overview

**Owner (authenticated — `Authorization: Bearer <token>`)**
- `POST /auth/register`, `POST /auth/login`, `GET /auth/me`
- `GET/POST/PATCH/DELETE /organizations`
- `GET/POST/PATCH/DELETE /services`
- `GET/POST/DELETE /availability`

**Public (no auth)**
- `GET /orgs/{slug}` and `GET /orgs/{slug}/services`
- `GET /slots?service_id=&date=`
- `POST /bookings`

---

## Roadmap

- [x] Phase 0–1 — Project setup, database, first model + migrations
- [x] Phase 2 — Auth (register / login / protected routes)
- [x] Phase 3 — Organizations (multi-tenancy)
- [x] Phase 4 — Services
- [x] Phase 5 — Availability rules
- [x] Phase 6 — Slots + Bookings (public booking, double-booking guard)
- [x] Web frontends — owner dashboard + customer booking page
- [ ] Phase 7 — Async confirmation email (Celery + Redis + Resend)
- [ ] Phase 8 — Payments (Razorpay)
- [ ] Phase 9 — Google Calendar / Meet integration
- [ ] Phase 10 — Bank details + payouts (encrypted)
- [ ] Phase 11 — Subscriptions (FREE/PRO plans)
- [ ] Deferred auth extras — refresh tokens, password reset

---

## Development notes
- **Migrations:** after changing a model, run `alembic revision --autogenerate -m "..."` then `alembic upgrade head`. Inspect the generated migration before applying.
- **Money** is stored as `Numeric` (exact decimal), never float.
- **Ownership** is enforced by scoping every query to the authenticated user; cross-tenant access returns `404`, not `403`.
