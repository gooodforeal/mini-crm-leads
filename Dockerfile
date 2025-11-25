FROM python:3.12-slim as builder

# Установка uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Установка зависимостей системы для сборки
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml uv.lock ./

# Установка зависимостей через uv
RUN uv sync --frozen --no-dev

# Финальный образ
FROM python:3.12-slim

# Установка uv в финальный образ
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Установка зависимостей для runtime (libpq для PostgreSQL и netcat для проверки порта)
RUN apt-get update && apt-get install -y \
    libpq5 \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копирование виртуального окружения из builder
COPY --from=builder /app/.venv /app/.venv

# Копирование кода приложения
COPY . .

# Копирование и настройка entrypoint скрипта
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Установка переменных окружения для uv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]