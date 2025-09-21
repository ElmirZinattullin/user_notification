# Сервис уведомлений (Notification Service)

Микросервис для отправки уведомлений пользователям по различным каналам: электронной почте, Telegram и SMS. Решение идеально подходит для интеграции в существующие системы для отправки оповещений, верификационных кодов и важных сообщений.

## 🚀 Возможности

- **📧 Email уведомления:** Отправка писем на указанный email адрес.
- **📱 Telegram сообщения:** Отправка сообщений через Telegram Bot.
- **📞 SMS рассылка:** Отправка SMS через интеграцию с сервисом sms.ru.
- **🔌 RESTful API:** Простой и понятный HTTP API для интеграции.
- **📘 Swagger документация:** Полная интерактивная документация API.
- **⏱️ Асинхронная обработка:** Использование Celery для фоновой обработки задач.

## 📦 Быстрый старт

Для запуска сервиса требуются только Docker и Docker Compose.

1. **Клонируйте репозиторий:**
    ```bash
    git clone <your-repo-url>
    cd <project-directory>
    ```

2. **Настройте окружение:**

    Скопируйте файл с переменными окружения и настройте его:
    ```bash
    cp .env.template .env
    ```

    *Отредактируйте файл `.env`, указав свои учетные данные (см. раздел Конфигурация ниже).*

3. **Запустите сервис:**

    Соберите и запустите контейнеры в фоновом режиме:
    ```bash
    docker compose build
    docker compose up -d
    ```

4. **Проверьте работу сервиса:**

    После запуска откройте в браузере документацию Swagger UI:
    ```
    http://localhost:8000/docs
    ```

## 🛠️ Использование

### Отправка уведомления через API

Для отправки уведомления отправьте `POST`-запрос на эндпоинт `/notification`. Вы можете указать один или несколько каналов для отправки.

**Пример запроса с использованием `curl`:**

```bash
curl -X 'POST' \
  'http://localhost:8000/notification' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "Важное уведомление",
  "body": "Здравствуйте! Это тестовое сообщение для проверки работы сервиса.",
  "user_email": "your@email.ru",
  "user_telegram_id": 123456678,
  "user_phone": 79821234567
}'
```
### 📝 Описание полей запроса:

- `title` (string): Заголовок уведомления.
- `body` (string): Текст уведомления.
- `user_email` (string, опционально): Email адрес получателя.
- `user_telegram_id` (integer, опционально): ID пользователя в Telegram.
- `user_phone` (integer, опционально): Номер телефона получателя (в формате `79XXXXXXXXX`).

> ⚠️ Для работы соответствующего канала необходимо:
> - Заполнить его поле в теле запроса.
> - Убедиться, что переменные окружения для этого канала корректно настроены (см. ниже).

---

## Логирование

логи сервиса уведомлений записываются в файл:

`app.notification_logger.my_app.log`



## ⚙️ Конфигурация

Перед запуском необходимо задать настройки в файле `.env`.

### 📞 Настройки SMS (sms.ru)

```env
SMS_SERVICE_TOKEN=your_sms_api_token
```

### 📧 Настройки Email

Для отправки email-уведомлений необходимо указать настройки SMTP-сервера и учетные данные отправителя в файле `.env`:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL=your_email@gmail.com
EMAIL_PASSWORD=your_email_password_or_app_password
EMAIL_PORT=465
EMAIL_USE_TLS=0
EMAIL_USE_SSL=1
```

### 🤖 Настройки Telegram Bot

Для отправки уведомлений через Telegram необходимо создать бота и получить токен через [@BotFather](https://t.me/BotFather).

Добавьте следующую переменную в файл `.env`:

```env
TG_BOT_TOKEN=your_telegram_bot_token
```

## ⚙️ Расширение функциональности

`Notification Service` разработан с возможностью простой и гибкой интеграции собственных методов отправки уведомлений. Это позволяет подключать любые внешние каналы или логику обработки, не затрагивая основную архитектуру проекта.

---

### ➕ Добавление собственного метода

Чтобы добавить новый способ уведомлений, необходимо реализовать один из базовых интерфейсов.

---

### 📘 Интерфейс `NotificationMethodInterface`

Простой интерфейс для отправки уведомлений, без повторной обработки:

```python
from app.notification_service.methods.base_methods import NotificationMethodInterface
from abc import ABC, abstractmethod

class NotificationMethodInterface(ABC):

    @abstractmethod
    def notify(self, body: str, title: str | None, **kwargs) -> bool:
        """Абстрактный метод для отправки уведомления"""
        pass
```
- Метод notify должен реализовать основную логику отправки.

- Возвращаемое значение: True, если отправка успешна, иначе False.

### 🌀 Интерфейс `ProcessingNotificationMethodInterface`

Если вашему каналу уведомлений требуется **обработка с повторными попытками**, **асинхронная проверка доставки** или отложенная отправка (например, SMS с задержкой, webhooks, сообщения с подтверждением доставки) — используйте интерфейс `ProcessingNotificationMethodInterface`.

#### 📄 Интерфейс:

```python
from abc import ABC, abstractmethod
from typing import Any
from app.notification_service.methods.base_methods import NotificationMethodInterface

class ProcessingNotificationMethodInterface(NotificationMethodInterface, ABC):

    @abstractmethod
    def notify(
        self,
        body: str,
        title: str | None,
        **kwargs
    ) -> bool | dict[str, JSONType]:
        """
        Метод вызывается для первичной попытки отправки уведомления.
        Возвращает:
          - True, если уведомление отправлено успешно.
          - False, если отправка не удалась.
          - dict[str, JSONType] — дополнительные параметры для повторной обработки (если требуется).
        """
        pass

    @classmethod
    @abstractmethod
    def processing(
        cls,
        current_processing_attempt: int,
        body: str,
        title: str | None,
        **kwargs
    ) -> bool | dict[str, JSONType]:
        """
        Метод вызывается фоновым процессом Celery для повторной попытки отправки или проверки состояния.

        Параметры:
          - current_processing_attempt: номер текущей попытки (начиная с 1).
          - body, title: содержимое уведомления.
          - kwargs: дополнительные данные, переданные из предыдущего шага (например, status_id, external_id и т.д.)

        Возвращает:
          - True, если отправка или проверка успешна.
          - False, если необходимо ещё повторить.
          - dict[str, JSONType] — обновлённые kwargs для следующей попытки (например, новое состояние).
        """
        pass

    @classmethod
    @abstractmethod
    def get_processing_pause(cls) -> int:
        """
        Возвращает количество секунд между повторными попытками.
        Например, если метод вернёт 60 — следующая проверка произойдёт через минуту.
        """
        pass
```

### 🔧 Регистрация и настройка метода

Чтобы подключить новый метод уведомлений, его необходимо **зарегистрировать** в системе.

Для этого:

- Отредактируйте файл:  
  ```plaintext
  app/notification.py
  ```
