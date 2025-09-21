import logging
import smtplib
import ssl
from email.message import EmailMessage

from . import NotificationMethodInterface


class EmailNotificationMethod(NotificationMethodInterface):
    server = None
    email = None
    email_password = None
    use_tsl = None
    use_ssl = None
    port = None

    def __init__(
        self,
    ):

        if None in (self.email, self.email_password, self.server, self.port):
            raise AttributeError("Email service configuration is missing or incomplete")

    def notify(self, body: str, title: str | None, user_email: str = "") -> bool:
        """
        Отправляет уведомление пользователю.

        Args:
            body: Текст сообщения (обязательный)
            title: Заголовок сообщения (опциональный)
            user_email: Email пользователя (обязательный)

        Returns:
            bool: True если отправлено успешно, False в случае ошибки

        Raises:
            AttributeError: Если переданы некорректные параметры
        """
        if user_email == "":
            raise AttributeError("User email is required")
        try:
            return self.send_message(body, title, user_email)
        except Exception as e:
            logging.error(f"Error {self.__class__.__name__}: {e}")
            return False

    def send_message(self, body, title, user_email):
        if self.use_ssl:
            return self.send_message_by_ssl(body, title, user_email)
        if self.use_tsl:
            return self.send_message_by_tsl(body, title, user_email)
        return False

    def send_message_by_ssl(self, body, title, user_email):

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.server, self.port, context=context) as server:
            try:
                server.login(self.email, self.email_password)
                new_mail = self.create_message(body, title, user_email)
                server.send_message(new_mail)
                server.quit()
                logging.info(f"{self.send_message_by_ssl.__name__}:send message to email: {body}")
                return True
            except Exception as err:
                logging.error(f"{self.send_message_by_ssl.__name__} is failed: {err}")
                return False

    def send_message_by_tsl(self, body, title, user_email):
        try:
            smtpObj = smtplib.SMTP(self.server, self.port)
            smtpObj.starttls()
            smtpObj.login(user=self.email, password=self.email_password)
            new_mail = self.create_message(body, title, user_email)
            smtpObj.send_message(new_mail)
            smtpObj.quit()
            logging.info(f"{self.send_message_by_tsl.__name__}:send message to email: {body}")
            return True
        except Exception as err:
            logging.error(f"{self.send_message_by_tsl.__name__} is failed: {err}")
            return False

    def create_message(self, body, title, user_email):
        new_mail = EmailMessage()
        new_mail.set_content(body)
        new_mail["To"] = user_email
        new_mail["From"] = self.email
        new_mail["Subject"] = title or "New notification"
        return new_mail

    def __str__(self):
        return self.__class__.__name__
