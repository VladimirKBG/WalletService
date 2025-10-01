#!/bin/sh

DB_HOST="db"
DB_PORT=5432
DB_USER="wallet_user"
DB_NAME="wallet_db"

until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
  echo "Waiting for Postgres..."
  sleep 1
done

echo "Postgres ready. Reset DB and apply seed."

psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -f /docker-entrypoint-initdb.d/seed.sql

