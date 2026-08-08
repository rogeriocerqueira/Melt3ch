from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://melt3ch:melt3ch_secret@db:5432/melt3ch_db"
    SECRET_KEY: str = "melt3ch_jwt_secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()
