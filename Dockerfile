# --- Appointment Booker web app ---
FROM python:3.13-slim

# Faster, cleaner Python in containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first so this layer is cached unless requirements change
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Hosts (Render) inject the port to listen on via $PORT
ENV PORT=8000
EXPOSE 8000

# Apply migrations, then start the server. `exec` hands OS signals (e.g. SIGTERM on
# redeploy) directly to uvicorn for a graceful shutdown; JSON form silences the warning.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
