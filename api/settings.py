from pydantic import BaseSettings


class Settings(BaseSettings):
    user_token: str
    database_url: str = "sqlite:///data.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

__all__ = ["Settings", "settings"]
