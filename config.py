"""Configuration management for Fast workout analyzer."""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration container for API credentials and settings."""

    # Intervals.icu credentials
    INTERVALS_API_KEY = os.getenv("INTERVALS_API")
    ATHLETE_ID = os.getenv("ATHLETE_ID")

    # OpenRouter credentials
    OPENROUTER_API_KEY = os.getenv("OPENROUTER")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")

    # Default settings
    DEFAULT_DAYS_LOOKBACK = 30
    INTERVALS_BASE_URL = "https://intervals.icu/api/v1"

    @classmethod
    def validate(cls):
        """Validate that all required configuration is present."""
        missing = []

        if not cls.INTERVALS_API_KEY:
            missing.append("INTERVALS_API")
        if not cls.ATHLETE_ID:
            missing.append("ATHLETE_ID")
        if not cls.OPENROUTER_API_KEY:
            missing.append("OPENROUTER")

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                f"Please add them to your .env file"
            )

        return True
