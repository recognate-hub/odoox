from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import HttpUrl, SecretStr, Field
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables or .env file.
    Pydantic strictly validates these variables to ensure all required
    values are present and properly typed.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # MCP / Server Configuration
    SERVER_HOST: str = Field(default="0.0.0.0", description="Server host address")
    SERVER_PORT: int = Field(default=8000, description="Server port")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # Supabase (Multi-Tenant)
    SUPABASE_URL: Optional[str] = Field(default=None, description="Supabase project URL")
    SUPABASE_KEY: Optional[str] = Field(default=None, description="Supabase API key")
    
    # CORS Configuration
    CORS_ORIGINS: list[str] = Field(default=["*"], description="List of allowed CORS origins")

    # Security
    ENCRYPTION_KEY: str = Field(min_length=32, description="Master key for encrypting tenant secrets")

    # Client/Tenant Identification
    COMPANY_NAME: str = Field(min_length=1, description="Company name")
    COMPANY_EMAIL: str = Field(min_length=1, description="Company contact email")
    COMPANY_PHONE: str = Field(default="", description="Company contact phone")

    def validate_config(self) -> None:
        """
        Since Pydantic automatically validates upon instantiation,
        this method serves as a simple explicit check.
        It will raise a ValidationError if configuration is invalid.
        """
        pass


def get_settings() -> Settings:
    """
    Factory to retrieve settings. In a real DI setup, this could be cached.
    """
    return Settings()
