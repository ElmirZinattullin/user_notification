from abc import ABC, abstractmethod
from typing import Dict, List, Union

# Типы, которые можно сериализовать в JSON
JSONType = Union[str, int, float, bool, None, List["JSONType"], Dict[str, "JSONType"]]


class NotificationMethodInterface(ABC):

    @abstractmethod
    def notify(self, body: str, title: str | None, **kwargs) -> bool:
        """Абстрактный метод для отправки уведомления"""
        pass


class ProcessingNotificationMethodInterface(NotificationMethodInterface, ABC):

    @abstractmethod
    def notify(self, body: str, title: str | None, **kwargs) -> bool | dict[str, JSONType]:
        """Абстрактный метод для отправки уведомления возвращает либо результат либо доп. kwargs для processing"""
        pass

    @classmethod
    @abstractmethod
    def processing(
        cls, current_processing_attempt, body: str, title: str | None, **kwargs
    ) -> bool | dict[str, JSONType]:
        """Метод для проверки успешности отправки уведомления возвращает либо результат либо доп. kwargs для
        следующей попытки processing"""
        pass

    @classmethod
    @abstractmethod
    def get_processing_pause(cls) -> int:
        """Метод для получения временной паузы между проверками в секундах"""
        pass
