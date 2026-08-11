
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    SUPABASE_URL: str | None = Field(default=None, description="Supabase project URL")
    SUPABASE_KEY: str | None = Field(default=None, description="Supabase API key")
    # Redis Configuration
    REDIS_URL: str | None = Field(default=None, description="Redis connection URL for caching and rate limiting")
    
    # CORS Configuration
    CORS_ORIGINS: list[str] = Field(default=[], description="List of allowed CORS origins")
    FRONTEND_URL: str = Field(default="http://localhost:3000", description="Base URL of the frontend application for redirects")

    # Security
    ENCRYPTION_KEY: str = Field(min_length=32, description="Master key for encrypting tenant secrets")
    OLD_ENCRYPTION_KEYS: str = Field(default="", description="Comma-separated old encryption keys for rotation")
    
    # mTLS configurations
    ODOO_CLIENT_CERT_PATH: str | None = Field(default=None, description="Path to mTLS client cert")
    ODOO_CLIENT_KEY_PATH: str | None = Field(default=None, description="Path to mTLS client key")

    # Client/Tenant Identification
    COMPANY_NAME: str = Field(default="ODOOX", min_length=1, description="Company name")
    COMPANY_EMAIL: str = Field(default="admin@odoox.com", min_length=1, description="Company contact email")
    COMPANY_PHONE: str = Field(default="", description="Company contact phone")

    def validate_config(self) -> None:
        """
        Since Pydantic automatically validates upon instantiation,
        this method serves as a simple explicit check.
        It will raise a ValidationError if configuration is invalid.
        """


def get_settings() -> Settings:
    """
    Factory to retrieve settings. In a real DI setup, this could be cached.
    """
    return Settings()
