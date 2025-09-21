import logging

from requests.sessions import session

from . import JSONType, ProcessingNotificationMethodInterface


class SMSNotificationMethod(ProcessingNotificationMethodInterface):
    """
    Уведомления через сервис sms.ru
    """

    sms_service_url = "https://sms.ru"
    send_endpoint = "/sms/send"
    sms_status_endpoint = "/sms/status"
    max_processing_attempts = 5
    processing_pause = 30
    token = None

    def __init__(self):
        self.sms_id = None
        if self.token is None:
            raise AttributeError("SMS service configuration is missing or incomplete")

    def notify(self, body: str, title: str | None, user_phone=None) -> bool | dict[str, JSONType]:
        if user_phone is None:
            raise AttributeError("user_phone is required")
        else:
            try:
                return self.send_notification(body, title, user_phone)
            except Exception as e:
                logging.error(f"Error while notify via {self.__class__.__name__}: {e}")
                return False

    def send_notification(self, body, title, user_phone):
        url = self.sms_service_url + self.send_endpoint
        params = {
            "api_id": self.token,
            "to": user_phone,
            "msg": f"{title}\n\n{body}",
            "json": 1,
        }
        try:
            with session() as s:
                response = s.request("get", url, params=params, timeout=2)
            if response.status_code == 200:
                payload = response.json()
                server_status = payload.get("status_code")
                if server_status == 100:
                    sms_list = payload.get("sms") or {}
                    sms = sms_list.get(str(user_phone)) or {}
                    sms_id = sms.get("sms_id")
                    if sms_id:
                        self.sms_id = sms_id
                    sms_status = sms.get("status_code")
                    if sms_status in [100, 101, 102]:
                        return {
                            "sms_id": sms_id,
                        }
                    elif sms_status == 103:
                        return True
                    else:
                        return False
            return False
        except Exception as e:
            logging.error(f"Error while notify via {self.__class__.__name__}: {e}")
            return False

    def check_sms_status(self, sms_id):
        return self.check_sms_status_task(sms_id, 1, 20)

    @classmethod
    def check_sms_status_task(cls, sms_id) -> bool | int:
        url = cls.sms_service_url + cls.sms_status_endpoint
        params = {"api_id": cls.token, "json": 1, "sms_id": sms_id}
        with session() as s:
            try:
                response = s.request("get", url, params=params, timeout=2)
            except Exception as e:
                logging.error(f"Error while check sms status: {e}")
            else:
                if response.status_code == 200:
                    payload = response.json()
                    server_status = payload.get("status_code")
                    if server_status == 100:
                        sms_list = payload.get("sms") or {}
                        sms = sms_list.get(sms_id) or {}
                        sms_status = sms.get("status_code")
                        if sms_status == 103:
                            return True
                        elif sms_status not in [100, 101, 102]:
                            return -1
        return False

    def __str__(self):
        return self.__class__.__name__

    @classmethod
    def processing(
        cls, body: str, title: str | None, current_processing_attempt=0, **kwargs
    ) -> bool | dict[str, JSONType]:
        sms_id = kwargs["sms_id"]
        result = cls.check_sms_status_task(
            sms_id,
        )
        if result is True:
            return True
        if result == -1 or current_processing_attempt + 1 >= cls.max_processing_attempts:
            return False
        return {
            "sms_id": sms_id,
        }

    @classmethod
    def get_processing_pause(cls) -> int:
        """Метод для получения временной паузы между проверками в секундах"""
        return cls.processing_pause
