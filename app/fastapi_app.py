from fastapi import FastAPI

from .schemas import NotificationSchema
from .tasks import notify_user

app = FastAPI()


@app.get("/hello")
async def hello_world():
    return {"message": "hello world"}


@app.post("/notification")
async def create_notification(notification: NotificationSchema):
    notify_user.delay(notification.model_dump())
    return notification
