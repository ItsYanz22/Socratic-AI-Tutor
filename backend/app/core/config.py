from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_JWT_SECRET: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    GEMINI_API_KEY: str

    # NEW: Add this line to load the token from .env
    HUGGINGFACEHUB_API_TOKEN: str

    class Config:
        env_file = ".env"


settings = Settings()