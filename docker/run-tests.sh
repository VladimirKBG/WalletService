#!/bin/sh
set -e

WEB_URL="${WEB_URL:-http://localhost:8000/}"
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${POSTGRES_USER:-wallet_user}"
DB_NAME="${POSTGRES_DB:-test_db}"

echo "Waiting for Postgres..."
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
  sleep 1
done
echo "Postgres is ready."

echo "Waiting for web at $WEB_URL ..."
i=0
while true; do
  if curl -fs "$WEB_URL" >/dev/null 2>&1; then
    echo "Web is ready."
    break
  fi
  i=$((i+1))
  if [ "$i" -gt 60 ]; then
    echo "Timeout waiting for web"
    exit 1
  fi
  sleep 1
done

exec "$@"