import os


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost:5432/lifescience")


settings = Settings()
