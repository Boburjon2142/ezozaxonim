from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LifePause API"
    env: str = "dev"
    secret_key: str = "change-me-in-prod"
    algorithm: str = "HS256"
    access_token_exp_minutes: int = 30
    refresh_token_exp_minutes: int = 60 * 24 * 7
    database_url: str = "sqlite:///./lifepause.db"
    redis_url: str = "redis://redis:6379/0"
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
