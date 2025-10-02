#!/bin/sh
set -e

echo "Waiting for database..."
until pg_isready -h "${DB_HOST:-db}" -p "${DB_PORT:-5432}" -U "${POSTGRES_USER:-wallet_user}"; do
  sleep 1
done
echo "Database ready"

if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
    echo "Running Alembic migrations..."
    alembic upgrade head
    echo "Migrations complete."
fi

exec "$@"
