from pydantic import BaseModel, EmailStr


class NotificationSchema(BaseModel):
    title: str | None
    body: str
    user_email: EmailStr | None = None
    user_telegram_id: int | None = None
    user_phone: int | None = None
