from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_JWT_SECRET: str

    class Config:
        # This tells pydantic to read from the .env file
        env_file = ".env"

# Create a single, reusable instance
settings = Settings()