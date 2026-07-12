# Roadmap

This project began as a Python/FastAPI reimplementation of a Node appointment-booking SaaS, built backend-first and tested through Swagger UI. It's now an independent project. This file tracks what's done and what's next.

---

## Built so far ✅

- **Phase 0–1** — Project setup, Docker Postgres, SQLAlchemy + Alembic migrations, first model.
- **Phase 2** — Auth: register/login, bcrypt password hashing, JWT, `get_current_user`, protected `/auth/me`.
- **Phase 3** — Organizations with owner-scoped CRUD (multi-tenancy).
- **Phase 4** — Services (per-org, ONLINE/OFFLINE, decimal price).
- **Phase 5** — Availability rules (weekly hours, cross-field validation).
- **Phase 6** — Slot generation + public bookings, with a DB unique-constraint double-booking guard.
- **Web frontends** — owner dashboard (`/`, incl. availability management) and customer booking page (`/book`), served by FastAPI.
- **Per-service availability** — each service has its own weekly hours (availability moved from org-level to per-service; slot generation, public endpoints, and dashboard updated).
- **Booking-page day picker** filtered to the selected service's available weekdays.
- **Deployed** live on Render + Neon with auto-deploy on push (see Stage 1).

---

## Stage 1 — Deploy (Render + Neon) ✅ done

**Live at https://appointment-booker-nmkz.onrender.com** — containerized app on Render's free tier, backed by a free & persistent Neon Postgres. Auto-deploys on push to `main`.

- [x] `Dockerfile`, `.dockerignore`, `render.yaml` (Blueprint)
- [x] `config.py` normalizes `DATABASE_URL`; engine uses `pool_pre_ping` for serverless Postgres
- [x] Public GitHub repo, Neon project, Render web service + env vars
- [x] Container runs `alembic upgrade head` then serves on each deploy

**Free-tier notes:** Render's free web service sleeps after ~15 min idle (first request wakes it, ~30s). Neon auto-suspends when idle and resumes on connect.

---

## Stage 2 — CI/CD (GitHub Actions) ✅ done

Goal: automated tests + lint on every PR, auto-deploy on merge.

- [x] **pytest** suite under `tests/` (real Postgres test DB): auth, ownership scoping, booking + double-booking.
- [x] `ruff` for linting (config in `pyproject.toml`).
- [x] `.github/workflows/ci.yml` — on push/PR: start a Postgres service → `ruff` → `alembic upgrade head` → `pytest`.
- [x] Render auto-deploy on push to `main` (**CD** — built in).
- [x] CI status badge in the README.

---

## Stage 3 — UI (keep it simple) 🎨

Frontend is intentionally minimal — clean and legible, nothing fancy. This is a backend-focused project; effort goes into the API, architecture, and deployment.
- [ ] Light styling pass on the dashboard and booking page for readability (no heavy redesign).

---

## Stage 4 — Later feature phases

- [ ] **Phase 7** — Async confirmation email (Celery + Redis via **Upstash** + Resend). Adds a background-worker service on Render.
- [ ] **Phase 8** — Payments (Razorpay): create order on booking, verify webhook signature.
- [ ] **Phase 9** — Google Calendar / Meet (OAuth2, create event + Meet link in a worker).
- [ ] **Phase 10** — Bank details + payouts (encrypted account numbers).
- [ ] **Phase 11** — Subscriptions (FREE/PRO plans, subscription webhooks).
- [ ] **Deferred auth extras** — refresh tokens, password reset.

---

## Working conventions

- Each feature is a module: `schemas.py` (Pydantic) / `service.py` (logic + DB) / `router.py` (HTTP).
- After changing a model: `alembic revision --autogenerate -m "..."` → inspect → `alembic upgrade head`.
- Ownership is enforced by scoping every query to the authenticated user; cross-tenant access → `404`.
- Commit after each working phase; keep secrets out of git (`.env` is gitignored).
