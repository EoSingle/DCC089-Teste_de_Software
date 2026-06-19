from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./ctf_platform.db"

    model_config = {"env_file": ".env"}


settings = Settings()
