import logging
import os

from conf import settings

from .notification_service import EmailNotificationMethod, Postman, SMSNotificationMethod, TelegramNotificationMethod


def config_email_notification_method():
    EmailNotificationMethod.email = settings.EMAIL
    EmailNotificationMethod.server = settings.EMAIL_HOST
    EmailNotificationMethod.email_password = settings.EMAIL_PASSWORD.get_secret_value()
    EmailNotificationMethod.port = settings.EMAIL_PORT
    EmailNotificationMethod.use_ssl = settings.EMAIL_USE_SSL
    EmailNotificationMethod.use_tsl = settings.EMAIL_USE_TSL
    return EmailNotificationMethod


def config_sms_notification_method():
    SMSNotificationMethod.token = settings.SMS_SERVICE_TOKEN.get_secret_value()
    return SMSNotificationMethod


def config_telegram_notification_method():
    TelegramNotificationMethod.token = settings.TG_BOT_TOKEN.get_secret_value()
    return TelegramNotificationMethod


def get_notification_service() -> Postman:
    notification_service = Postman()
    email_method = config_email_notification_method()
    sms_method = config_sms_notification_method()
    telegram_method = config_telegram_notification_method()

    notification_service.add_notification_method(email_method, ("user_email",))
    notification_service.add_notification_method(telegram_method, ("user_telegram_id",))
    notification_service.add_notification_method(sms_method, ("user_phone",))
    return notification_service


def setup_logger(log_file="notification.log"):
    # Создаем директорию для логов если ее нет
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # Настраиваем логгер
    logger = logging.getLogger("Notification_loger")

    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(logging.StreamHandler())

    return logger


notification_logger = setup_logger("app/notification_logger/my_app.log")
service: Postman = get_notification_service()
