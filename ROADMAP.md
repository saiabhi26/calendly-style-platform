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
- **Web frontends** — owner dashboard (`/`) and customer booking page (`/book`), served by FastAPI.
- **Booking-page day picker** filtered to the org's available weekdays.

---

## Stage 1 — Deploy (free: Render + Neon) 🚀

Goal: a live public URL, running the containerized app against a persistent free Postgres.

**Prep (files added to the repo):**
- [ ] `Dockerfile` — package the web app into a container image.
- [ ] `.dockerignore` — keep `.venv`, `.git`, `.env` out of the image.
- [ ] `render.yaml` — Blueprint describing the web service (reproducible setup).
- [x] `config.py` — normalize `DATABASE_URL` (`postgres://` → `postgresql+psycopg2://`).

**Deploy flow:**
- [ ] Push repo to GitHub (public, so it's visible to recruiters).
- [ ] Create a **Neon** Postgres project → copy its connection string. (Free & persistent — no 90-day expiry.)
- [ ] Create a **Render** Web Service from the repo (Docker build).
- [ ] Set env vars on Render: `DATABASE_URL` (Neon), a strong `JWT_SECRET`, `JWT_REFRESH_SECRET`, etc.
- [ ] Deploy → container runs `alembic upgrade head` then starts the server → live URL.
- [ ] Verify `/docs`, `/`, `/book` on the live URL.

**Free-tier notes:** Render's free web service sleeps after ~15 min idle (wakes on first request). Neon auto-suspends when idle and resumes on connect. Both fine for a portfolio.

---

## Stage 2 — CI/CD (GitHub Actions) ⚙️

Goal: automated tests + lint on every PR, auto-deploy on merge.

- [ ] Add a **pytest** suite under `tests/` (test DB): auth, ownership scoping, booking + double-booking.
- [ ] Add `ruff` for linting.
- [ ] `.github/workflows/ci.yml` — on push/PR: start a Postgres service → `alembic upgrade head` → `pytest` → `ruff`.
- [ ] Enable Render auto-deploy on push to `main` (**CD** — built in).
- [ ] Add a CI status badge to the README.

---

## Stage 3 — UI polish 🎨

- [ ] Nicer styling on the owner dashboard and booking page (once live and CI-protected).

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
