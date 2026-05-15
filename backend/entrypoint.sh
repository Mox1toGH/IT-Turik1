#!/bin/sh
set -e

if [ "${DB_ENGINE:-django.db.backends.sqlite3}" != "django.db.backends.sqlite3" ]; then
  python - <<'PY'
import os
import socket
import sys
import time

host = os.getenv("DB_HOST", "db")
port = int(os.getenv("DB_PORT", "5432"))

for attempt in range(60):
    try:
        with socket.create_connection((host, port), timeout=2):
            break
    except OSError:
        print(f"Waiting for database {host}:{port} ({attempt + 1}/60)")
        time.sleep(2)
else:
    print("Database is unreachable.")
    sys.exit(1)
PY
fi

python manage.py migrate --noinput
exec daphne -b 0.0.0.0 -p 8000 backend.asgi:application
