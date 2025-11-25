#!/bin/bash
set -e

echo "Waiting for database to be ready..."

# Проверка доступности порта PostgreSQL
max_attempts=60
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if nc -z db 5432 2>/dev/null; then
        echo "Database port is open!"
        break
    fi
    attempt=$((attempt + 1))
    echo "Database port is unavailable - attempt $attempt/$max_attempts - sleeping"
    sleep 1
done

if [ $attempt -eq $max_attempts ]; then
    echo "Database connection failed after $max_attempts attempts"
    exit 1
fi

# Дополнительная задержка для полной инициализации БД и создания базы данных
echo "Waiting for database initialization..."
sleep 5

# Запуск миграций
echo "Running migrations..."
uv run alembic upgrade head

if [ $? -eq 0 ]; then
    echo "Migrations completed successfully!"
else
    echo "Migrations failed!"
    exit 1
fi

# Запуск приложения
echo "Starting application..."
exec "$@"