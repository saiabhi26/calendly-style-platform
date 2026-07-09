from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Database / infra ---
    DATABASE_URL: str
    REDIS_URL: str

    # --- Auth / JWT (used from Phase 2) ---
    JWT_SECRET: str
    JWT_REFRESH_SECRET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 60

    # --- Email (used from Phase 7) ---
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "onboarding@resend.dev"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()