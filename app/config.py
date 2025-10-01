from pydantic import BaseModel, Field, ValidationError
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        assistant_id (str): VAPI assistant ID (UUID format expected).
        public_key (str): VAPI public key (UUID format expected).
        vapi_private_key (str): VAPI private key for server-side API calls (optional).
    """

    assistant_id: str = Field(
        default="",
        description="VAPI Assistant ID - REQUIRED: Set via ASSISTANT_ID env var"
    )
    public_key: str = Field(
        default="",
        description="VAPI Public Key - REQUIRED: Set via PUBLIC_KEY env var"
    )
    vapi_private_key: str = Field(
        default="",
        description="VAPI Private Key - OPTIONAL: Set via VAPI_PRIVATE_KEY env var for chat functionality"
    )
    facebook_business_whatsapp: str = Field(
        default="",
        description="Facebook Business WhatsApp - OPTIONAL: Set via FACEBOOK_BUSINESS_WHATSAPP env var"
    )
    calendly_link: str = Field(
        default="",
        description="Calendly Link - OPTIONAL: Set via CALENDLY_LINK env var"
    )
    
    # Domain Analysis Results
    analyzed_domain: str = Field(
        default="",
        description="Analyzed Domain - OPTIONAL: Set via ANALYZED_DOMAIN env var"
    )
    company_name: str = Field(
        default="",
        description="Company Name - OPTIONAL: Set via COMPANY_NAME env var"
    )

    primary_color: str = Field(
        default="",
        description="Primary Brand Color - OPTIONAL: Set via PRIMARY_COLOR env var"
    )
    secondary_color: str = Field(
        default="",
        description="Secondary Brand Color - OPTIONAL: Set via SECONDARY_COLOR env var"
    )
    accent_color: str = Field(
        default="",
        description="Accent Brand Color - OPTIONAL: Set via ACCENT_COLOR env var"
    )
    logo_url: str = Field(
        default="",
        description="Logo URL - OPTIONAL: Set via LOGO_URL env var"
    )
    support_email: str = Field(
        default="",
        description="Support Email - OPTIONAL: Set via SUPPORT_EMAIL env var"
    )
    website_url: str = Field(
        default="",
        description="Website URL - OPTIONAL: Set via WEBSITE_URL env var"
    )
    impressum_url: str = Field(
        default="",
        description="Impressum URL - OPTIONAL: Set via IMPRESSUM_URL env var"
    )
    privacy_policy_url: str = Field(
        default="",
        description="Privacy Policy URL - OPTIONAL: Set via PRIVACY_POLICY_URL env var"
    )
    terms_url: str = Field(
        default="",
        description="Terms URL - OPTIONAL: Set via TERMS_URL env var"
    )
    hero_title: str = Field(
        default="",
        description="Hero Title - OPTIONAL: Set via HERO_TITLE env var"
    )
    hero_text: str = Field(
        default="",
        description="Hero Text - OPTIONAL: Set via HERO_TEXT env var"
    )
    config_password: str = Field(
        default="",
        description="Config Password - OPTIONAL: Set via CONFIG_PASSWORD env var for admin access"
    )
    
    # Redis Configuration
    redis_url: str = Field(
        default="",
        description="Redis URL - OPTIONAL: Set via REDIS_URL env var for Upstash Redis"
    )
    redis_username: str = Field(
        default="",
        description="Redis Username - OPTIONAL: Set via REDIS_USERNAME env var for Upstash Redis"
    )
    redis_password: str = Field(
        default="",
        description="Redis Password - OPTIONAL: Set via REDIS_PASSWORD env var for Upstash Redis"
    )
    
    # Shlink Configuration
    shlink_api_key: str = Field(
        default="",
        description="Shlink API Key - OPTIONAL: Set via SHLINK_API_KEY env var for URL shortening"
    )
    shlink_base_url: str = Field(
        default="https://demo.bifrotek.com/rest/v3",
        description="Shlink Base URL - OPTIONAL: Set via SHLINK_BASE_URL env var"
    )

    model_config = {
        "env_prefix": "",
        "env_file": ".env",
        "env_ignore_empty": True,
        "extra": "ignore",  # Ignore extra fields instead of raising error
    }


_cached_settings: AppSettings | None = None


def get_settings() -> AppSettings:
    """Get cached settings instance.

    Returns:
        AppSettings: The application settings.
    """

    global _cached_settings
    if _cached_settings is None:
        _cached_settings = AppSettings()
    return _cached_settings


def reset_settings_cache() -> None:
    """Reset the cached settings instance (used in tests)."""

    global _cached_settings
    _cached_settings = None



