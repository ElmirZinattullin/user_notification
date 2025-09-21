import logging

from requests.sessions import session

from . import NotificationMethodInterface


class TelegramNotificationMethod(NotificationMethodInterface):
    """
    Уведомления через сервис sms.ru
    """

    telegram_url = "https://api.telegram.org"
    _send_endpoint = "/bot{bot_token}/sendMessage"
    token = None

    def __init__(self):
        if self.token is None:
            raise AttributeError("Telegram service configuration is missing or incomplete")

    def notify(self, body: str, title: str | None, user_telegram_id=None) -> bool:
        if user_telegram_id is None:
            raise AttributeError("user_phone is required")
        else:
            try:
                return self.send_notification(body, title, user_telegram_id)
            except Exception as e:
                logging.error(f"Error while notify via {self.__class__.__name__}: {e}")
                return False

    def send_notification(self, body, title, user_telegram_id):
        url = self.telegram_url + self._send_endpoint.format(bot_token=self.token)
        params = {
            "chat_id": user_telegram_id,
            "text": f"{title}\n\n{body}",
        }
        logging.info(f"{params=}")
        try:
            with session() as s:
                response = s.request("get", url, params=params, timeout=2)
                logging.info(f"{response.json()=}")
            if response.status_code == 200:
                payload = response.json()
                if payload.get("ok") is True:
                    return True
            return False
        except Exception as e:
            logging.error(f"Error while notify via {self.__class__.__name__}: {e}")
            return False

    def __str__(self):
        return self.__class__.__name__
