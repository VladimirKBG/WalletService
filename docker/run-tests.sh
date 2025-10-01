#!/bin/sh
set -e

WEB_URL="http://web:8000/"
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${POSTGRES_USER:-wallet_user}"
DB_NAME="${POSTGRES_DB:-test_db}"

echo "Waiting for Postgres..."
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
  sleep 1
done
echo "Postgres is ready."

exec "$@"