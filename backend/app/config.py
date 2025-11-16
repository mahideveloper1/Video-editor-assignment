"""
Configuration management for the AI Video Editor backend.
Uses pydantic-settings to load environment variables.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Settings
    app_name: str = "AI Video Editor API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS Settings
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # LLM Settings
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    llm_provider: str = "openai"  # "openai", "anthropic", or "google"/"gemini"
    llm_model: str = "gpt-4o-mini"  # or "claude-3-5-sonnet-20241022" or "gemini-pro"
    llm_temperature: float = 0.7

    # File Upload Settings
    max_upload_size: int = 500 * 1024 * 1024  # 500MB in bytes
    allowed_video_formats: list[str] = [".mp4", ".mov", ".avi", ".webm"]

    # Directory Settings
    base_dir: Path = Path(__file__).parent.parent
    upload_dir: Path = base_dir / "uploads"
    output_dir: Path = base_dir / "outputs"
    temp_dir: Path = base_dir / "temp"

    # Session Settings
    session_ttl: int = 3600  # 1 hour in seconds

    # Subtitle Default Settings
    default_font_family: str = "Arial"
    default_font_size: int = 32
    default_font_color: str = "white"
    default_subtitle_position: str = "bottom"

    # FFmpeg Settings
    ffmpeg_threads: int = 4
    video_quality: str = "high"  # "high", "medium", "low"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()


# Create necessary directories on startup
def create_directories():
    """Create upload, output, and temp directories if they don't exist."""
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    settings.temp_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created directories:")
    print(f"  - Upload: {settings.upload_dir}")
    print(f"  - Output: {settings.output_dir}")
    print(f"  - Temp: {settings.temp_dir}")
