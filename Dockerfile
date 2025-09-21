# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости
RUN pip install uv

COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock

RUN uv sync --locked --no-dev --no-install-project --no-editable --no-managed-python --compile-bytecode

# Копируем остальные файлы приложения
COPY . .
