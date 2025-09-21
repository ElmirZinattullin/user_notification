from .celery import app
from .notification import notification_logger, service


@app.task
def notify_user(
    notification: dict,
    method_id: int = 0,
    processing=False,
    current_processing_attempt=0,
    **kwargs,
):
    user_data = {
        "user_email": notification.get("user_email"),
        "user_telegram_id": notification.get("user_telegram_id"),
        "user_phone": notification.get("user_phone"),
    }
    message_title = notification.get("title")
    message_body = notification.get("body")
    method = service.get_notify_method_by_id_or_none(method_id)
    if not method:
        raise Exception(f"Error in notification method: {method_id}")
    result = service.notify_by_method_id(
        user_data,
        message_body,
        message_title,
        method_id,
        processing,
        current_processing_attempt,
        **kwargs,
    )
    if isinstance(result, bool):
        # Получен результат от метода уведомления
        if result:
            notification_logger.info(f"OK__:via={str(method)}:{message_title=}:{message_body=}:{user_data=}")
            return
        else:
            notification_logger.info(f"FAIL:via={str(method)}:{message_title=}:{message_body=}:{user_data=}")
            next_method_id = service.get_next_method_id_by_id_or_none(method_id)
            if next_method_id is None:
                notification_logger.error(f"FAILED:via=ALL:{message_title=}:{message_body=}:{user_data=}")
                return
            else:
                notify_user.delay(notification, method_id + 1)
                return
    else:
        # запускаем проверку результата метода
        attempt = current_processing_attempt
        notification_logger.info(
            f"PROCESSING:via={str(method)}:{message_title=}:{message_body=}:{user_data=}:{attempt=}"
        )
        pause = method.get_processing_pause()
        notify_user.apply_async(
            args=[notification, method_id, True, current_processing_attempt + 1],
            kwargs=result,
            countdown=pause,
        )
