# Challenges & Solutions

A running log of notable problems hit while building and deploying this project, and how they were resolved. Newest first.

Each entry: **Symptom** (what we saw) → **Cause** (why) → **Fix** (what solved it) → **Lesson** (the takeaway).

---

## 2026-07-11 — Production 500 on register: "SSL connection has been closed unexpectedly"

**Symptom:** Register/login worked locally but returned `500 Internal Server Error` on the deployed (Render) app. Render logs showed:
`psycopg2.OperationalError: SSL connection has been closed unexpectedly` on the first DB query (`SELECT ... FROM users`). Migrations on deploy had succeeded, and read-only routes worked.

**Cause:** Neon is *serverless* Postgres — it drops idle connections (and auto-suspends compute). SQLAlchemy keeps a pool of connections and tried to **reuse a connection Neon had already closed**, so the SSL socket was dead. Migrations worked because they opened fresh connections.

**Fix:** Enable liveness checking on the engine in `app/database.py`:
```python
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_recycle=300, ...)
```
`pool_pre_ping` sends a lightweight check before using a pooled connection and transparently reconnects if it's dead; `pool_recycle=300` retires connections older than 5 minutes.

**Lesson:** With any serverless/cloud Postgres (Neon, Supabase, RDS proxy, etc.), always set `pool_pre_ping=True`. "Works locally, 500s in prod on the first query after idle" is the signature of a stale pooled connection.

---

## 2026-07-08 — Register 500 locally: bcrypt "password cannot be longer than 72 bytes"

**Symptom:** `POST /auth/register` returned 500 even with a short password; error mentioned a 72-byte limit.

**Cause:** `passlib` 1.7.4 (last released 2020, unmaintained) is incompatible with `bcrypt` 5.0, which it mis-drives.

**Fix:** Pin `bcrypt==4.0.1` in `requirements.txt` (the last release before `bcrypt` removed the internals passlib relies on).

**Lesson:** passlib is effectively abandoned; pin `bcrypt<4.1`, or call the `bcrypt` library directly. bcrypt also has a real 72-byte input limit regardless.
