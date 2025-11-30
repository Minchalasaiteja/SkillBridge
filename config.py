"""
Configuration management for SkillBridge Capstone Project
Handles environment variables and application settings
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Flask Configuration
    flask_env: str = Field(default="development", alias="FLASK_ENV")
    flask_debug: bool = Field(default=True, alias="FLASK_DEBUG")
    flask_host: str = Field(default="0.0.0.0", alias="FLASK_HOST")
    flask_port: int = Field(default=5000, alias="FLASK_PORT")
    
    # Google Gemini Configuration
    gemini_api_key: str = Field(..., alias="GEMINI_API_KEY")
    
    # MongoDB Configuration
    mongodb_uri: str = Field(..., alias="MONGODB_URI")
    mongodb_db_name: str = Field(default="skillbridge", alias="MONGODB_DB_NAME")
    
    # Frontend Configuration
    react_app_api_url: str = Field(default="http://localhost:5000", alias="REACT_APP_API_URL")
    react_app_environment: str = Field(default="development", alias="REACT_APP_ENVIRONMENT")
    
    # Observability Configuration
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    enable_tracing: bool = Field(default=True, alias="ENABLE_TRACING")
    enable_metrics: bool = Field(default=True, alias="ENABLE_METRICS")
    # OpenTelemetry / Exporters
    jaeger_host: Optional[str] = Field(default="localhost", alias="JAEGER_HOST")
    jaeger_port: Optional[int] = Field(default=6831, alias="JAEGER_PORT")
    prometheus_port: Optional[int] = Field(default=8000, alias="PROMETHEUS_PORT")
    
    # Session Configuration
    session_timeout: int = Field(default=3600, alias="SESSION_TIMEOUT")
    session_type: str = Field(default="filesystem", alias="SESSION_TYPE")

    # Authentication
    jwt_secret_key: str = Field(default="please-change-this-secret", alias="JWT_SECRET_KEY")
    jwt_access_token_expires: int = Field(default=3600, alias="JWT_ACCESS_EXPIRES")
    
    # CORS Configuration
    # Stored as a comma-separated string in the env for compatibility with dotenv.
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5000",
        alias="CORS_ORIGINS"
    )
    
    # Feature Flags
    enable_parallel_agents: bool = Field(default=True, alias="ENABLE_PARALLEL_AGENTS")
    enable_long_running_operations: bool = Field(default=True, alias="ENABLE_LONG_RUNNING_OPERATIONS")
    enable_memory_persistence: bool = Field(default=True, alias="ENABLE_MEMORY_PERSISTENCE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        model_config = {"extra": "ignore"}

    # Seeder options (read from env if present)
    seeder_count: int = Field(default=500, alias="SEEDER_COUNT")
    seeder_mode: str = Field(default="dry-run", alias="SEEDER_MODE")
    
    def cors_origins_list(self) -> list:
        """Return parsed list of CORS origins from the env string"""
        v = self.cors_origins
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        if isinstance(v, (list, tuple)):
            return list(v)
        return []
    
    def get_mongo_connection_string(self) -> str:
        """Get MongoDB connection string"""
        return self.mongodb_uri
    
    def get_gemini_config(self) -> dict:
        """Get Gemini API configuration"""
        return {
            "api_key": self.gemini_api_key,
            "model": "gemini-pro",
            "temperature": 0.7,
            "max_output_tokens": 2048
        }


def get_settings() -> Settings:
    """Load and cache settings"""
    return Settings()


settings = get_settings()
