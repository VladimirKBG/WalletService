from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    ENABLE_OPENAPI_DOCS: bool
    DATABASE_URL: str
    SQL_ECHO: bool
    DB_POOL_SIZE: int
    DB_MAX_OVERFLOW: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

