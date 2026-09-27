"""
Configuration settings for KYRON Admin Panel.
Production-ready configuration with environment variable support.
"""

import os
from typing import List

class Settings:
    """Application settings and configuration"""
    
    # Application
    APP_NAME: str = "KYRON Admin Panel"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # MongoDB Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "kyron_db")
    
    # PostgreSQL Configuration (Optional)
    POSTGRES_URL: str = os.getenv(
        "POSTGRES_URL",
        "postgresql://postgres:postgres@localhost:5432/kyron_db"
    )
    
    # JWT Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-min-32-chars")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3002",  # Frontend port
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3002",  # Frontend port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*",  # Allow all origins in development (remove in production)
    ]
    
    # Security
    BCRYPT_ROUNDS: int = 12
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    
    # Role Hierarchy (strict order - higher number = higher privilege)
    ROLES = {
        "MASTER_ADMIN": 5,
        "SUPER_ADMIN": 4,
        "ADMIN": 3,
        "OPERATOR": 2,
        "VIEWER": 1
    }
    
    # Default permissions per role
    ROLE_PERMISSIONS = {
        "MASTER_ADMIN": [
            "admin.create",
            "admin.delete",
            "admin.block",
            "admin.view_all",
            "admin.assign_roles",
            "user.view_all",
            "user.manage",
            "logs.view_all",
            "logs.view_sensitive",
            "system.agent_toggle",
            "system.settings",
            "system.view_all"
        ],
        "SUPER_ADMIN": [
            "admin.view_all",
            "user.view_all",
            "user.manage",
            "logs.view_all",
            "system.view_all"
        ],
        "ADMIN": [
            "user.view_all",
            "user.manage",
            "logs.view_agent",
            "logs.view_error"
        ],
        "OPERATOR": [
            "user.view",
            "logs.view_agent"
        ],
        "VIEWER": [
            "user.view",
            "logs.view_agent"
        ]
    }

# Global settings instance
settings = Settings()

