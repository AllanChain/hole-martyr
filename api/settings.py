from pydantic import BaseSettings


class Settings(BaseSettings):
    user_token: str
    database_url: str = "sqlite:///data.db"
    scan_page: int = 4
    initial_delay: int = 10
    initial_interval: int = 30
    max_interval: int = 120
    min_interval: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

__all__ = ["Settings", "settings"]
