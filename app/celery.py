from celery import Celery

from conf import settings

app = Celery(
    "myapp",
    broker=settings.CELERY_BROKER_URL,  # или 'amqp://guest:guest@localhost:5672//'
    backend=settings.CELERY_RESULT_BACKEND,  # для хранения результатов
)

# Конфигурация
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
    include=["app.tasks"],
)
