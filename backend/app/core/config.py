from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool = False

    SECRET_KEY: str

    GROQ_API_KEY: str  

    DATABASE_URL: str
    REDIS_URL: str

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()