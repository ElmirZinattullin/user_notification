from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TG_BOT_TOKEN: SecretStr
    EMAIL: str
    EMAIL_PASSWORD: SecretStr
    EMAIL_HOST: str
    SMS_SERVICE_TOKEN: SecretStr
    EMAIL_USE_TSL: bool = True
    EMAIL_USE_SSL: bool = False
    EMAIL_PORT: int
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    class Config:
        env_file = ".env"


# Использование
settings = Settings()
