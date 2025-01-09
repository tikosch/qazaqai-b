import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://userdb:1k18MnsC6iV4ApTjE7hJfGus97MIzaHf@dpg-ctvv89popnds73duv4rg-a/elearndb_75qa"
    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24

    class Config:
        env_file = ".env"

settings = Settings()
