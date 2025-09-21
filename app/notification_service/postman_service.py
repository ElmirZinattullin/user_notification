from typing import Type

from .methods import JSONType, NotificationMethodInterface, ProcessingNotificationMethodInterface


class Postman:

    notification_methods_list: list[tuple[Type[NotificationMethodInterface], tuple[str, ...]]] = []

    def add_notification_method(
        self,
        method: Type[NotificationMethodInterface | ProcessingNotificationMethodInterface],
        method_kwargs_name: tuple[str, ...],
    ):
        self.notification_methods_list.append((method, method_kwargs_name))

    def get_notify_method_by_id_or_none(
        self, method_id
    ) -> Type[NotificationMethodInterface | ProcessingNotificationMethodInterface] | None:
        try:
            return self.notification_methods_list[method_id][0]
        except IndexError:
            return None

    def get_next_method_id_by_id_or_none(self, method_id):
        try:
            return self.notification_methods_list[method_id + 1]
        except IndexError:
            return None

    @staticmethod
    def notify_via_method_or_processing(
        method_cls,
        method_kwargs_name,
        user_data: dict[str, ...],
        body,
        title,
        processing: bool = False,
        current_processing_attempt=0,
        **kwargs,
    ):
        method = method_cls()
        method_kwargs = {}
        for kwarg in method_kwargs_name:
            method_kwargs[kwarg] = user_data.get(kwarg)
        if not processing:
            result = method.notify(body, title, **method_kwargs)
        else:
            result = method.processing(body, title, current_processing_attempt, **method_kwargs, **kwargs)
        return result

    def notify_by_method_id(
        self,
        user_data: dict[str, ...],
        body,
        title,
        method_id: int,
        processing: bool = False,
        current_processing_attempt=0,
        **kwargs,
    ) -> bool | JSONType:
        method = self.notification_methods_list[method_id]
        method_cls = method[0]
        method_kwargs_name = method[1]
        result = self.notify_via_method_or_processing(
            method_cls,
            method_kwargs_name,
            user_data,
            body,
            title,
            processing,
            current_processing_attempt=current_processing_attempt,
            **kwargs,
        )
        return result
