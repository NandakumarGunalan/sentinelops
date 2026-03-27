import os
from typing import List


class Settings:
    """Application configuration loaded from environment variables"""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/sentinelops.db")
    
    # Agent Configuration
    MAX_INVESTIGATION_STEPS: int = int(os.getenv("MAX_INVESTIGATION_STEPS", "15"))
    TOOL_TIMEOUT_SECONDS: int = int(os.getenv("TOOL_TIMEOUT_SECONDS", "10"))
    ENABLE_REAL_ACTIONS: bool = os.getenv("ENABLE_REAL_ACTIONS", "false").lower() == "true"
    
    # Risk Score Thresholds
    RISK_THRESHOLD_LOW: int = int(os.getenv("RISK_THRESHOLD_LOW", "20"))
    RISK_THRESHOLD_MEDIUM: int = int(os.getenv("RISK_THRESHOLD_MEDIUM", "40"))
    RISK_THRESHOLD_HIGH: int = int(os.getenv("RISK_THRESHOLD_HIGH", "60"))
    RISK_THRESHOLD_CRITICAL: int = int(os.getenv("RISK_THRESHOLD_CRITICAL", "80"))
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        """Validate configuration on startup"""
        if cls.MAX_INVESTIGATION_STEPS < 1:
            raise ValueError("MAX_INVESTIGATION_STEPS must be at least 1")
        if cls.TOOL_TIMEOUT_SECONDS < 1:
            raise ValueError("TOOL_TIMEOUT_SECONDS must be at least 1")
        if not (0 <= cls.RISK_THRESHOLD_LOW < cls.RISK_THRESHOLD_MEDIUM < cls.RISK_THRESHOLD_HIGH < cls.RISK_THRESHOLD_CRITICAL <= 100):
            raise ValueError("Risk thresholds must be in ascending order between 0 and 100")


# Global settings instance
settings = Settings()
