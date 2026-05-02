"""
Configuration Management for ADK Trip Planner (Optimized)

Centralized configuration following 12-factor app principles.
Environment variables override defaults.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


# Load environment variables from .env file
ENV_FILE = Path(__file__).parent.parent / '.env'
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)


class Config:
    """Base configuration class."""
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    CACHE_DIR = PROJECT_ROOT / '.cache'
    
    # API Configuration
    GOOGLE_API_KEY: Optional[str] = os.getenv('GOOGLE_API_KEY')
    GOOGLE_API_TIMEOUT: int = int(os.getenv('GOOGLE_API_TIMEOUT', '10'))
    
    # Cache Configuration
    CACHE_DB_PATH: str = str(CACHE_DIR / 'trip_cache.db')
    CACHE_DEFAULT_TTL_HOURS: int = int(os.getenv('CACHE_DEFAULT_TTL_HOURS', '48'))
    CACHE_DESTINATION_TTL_HOURS: int = int(os.getenv('CACHE_DESTINATION_TTL_HOURS', '720'))  # 30 days
    CACHE_SEARCH_TTL_HOURS: int = int(os.getenv('CACHE_SEARCH_TTL_HOURS', '48'))
    
    # LLM Configuration
    LLM_MODEL: str = os.getenv('LLM_MODEL', 'gemini-2.5-flash')
    LLM_TIMEOUT: int = int(os.getenv('LLM_TIMEOUT', '30'))
    
    # Tool Configuration
    ENABLE_GOOGLE_SEARCH: bool = os.getenv('ENABLE_GOOGLE_SEARCH', 'true').lower() == 'true'
    ENABLE_CACHING: bool = os.getenv('ENABLE_CACHING', 'true').lower() == 'true'
    ENABLE_DESTINATION_DB: bool = os.getenv('ENABLE_DESTINATION_DB', 'true').lower() == 'true'
    
    # Geolocation Configuration
    GEO_SEARCH_RADIUS_METERS: int = int(os.getenv('GEO_SEARCH_RADIUS_METERS', '3000'))
    GEO_SEARCH_LIMIT: int = int(os.getenv('GEO_SEARCH_LIMIT', '5'))
    NOMINATIM_USER_AGENT: str = os.getenv('NOMINATIM_USER_AGENT', 'adk_trip_planner')
    
    # Agent Configuration
    AGENT_TEMPERATURE: float = float(os.getenv('AGENT_TEMPERATURE', '0.7'))
    MAX_AGENTS_PER_QUERY: int = int(os.getenv('MAX_AGENTS_PER_QUERY', '2'))
    
    # Performance Configuration
    ENABLE_STATS_LOGGING: bool = os.getenv('ENABLE_STATS_LOGGING', 'true').lower() == 'true'
    DEBUG_MODE: bool = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate configuration.
        
        Returns:
            True if valid, False otherwise
        """
        if not cls.GOOGLE_API_KEY and cls.ENABLE_GOOGLE_SEARCH:
            print("⚠️ Warning: GOOGLE_API_KEY not set but ENABLE_GOOGLE_SEARCH is True")
        
        # Ensure cache directory exists
        cls.CACHE_DIR.mkdir(exist_ok=True)
        
        return True
    
    @classmethod
    def to_dict(cls) -> dict:
        """Get configuration as dictionary (exclude sensitive data)."""
        return {
            'LLM_MODEL': cls.LLM_MODEL,
            'CACHE_DEFAULT_TTL_HOURS': cls.CACHE_DEFAULT_TTL_HOURS,
            'CACHE_DESTINATION_TTL_HOURS': cls.CACHE_DESTINATION_TTL_HOURS,
            'ENABLE_GOOGLE_SEARCH': cls.ENABLE_GOOGLE_SEARCH,
            'ENABLE_CACHING': cls.ENABLE_CACHING,
            'ENABLE_DESTINATION_DB': cls.ENABLE_DESTINATION_DB,
            'GEO_SEARCH_RADIUS_METERS': cls.GEO_SEARCH_RADIUS_METERS,
            'DEBUG_MODE': cls.DEBUG_MODE,
        }


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG_MODE = True
    ENABLE_STATS_LOGGING = True
    CACHE_DEFAULT_TTL_HOURS = 1  # Shorter TTL for testing


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG_MODE = False
    CACHE_DEFAULT_TTL_HOURS = 48


class TestingConfig(Config):
    """Testing environment configuration."""
    DEBUG_MODE = True
    CACHE_DB_PATH = str(Path(__file__).parent.parent / '.cache' / 'test_cache.db')
    ENABLE_GOOGLE_SEARCH = False  # Don't use real API in tests


def get_config(env: Optional[str] = None) -> Config:
    """
    Get configuration instance based on environment.
    
    Args:
        env: Environment name ('development', 'production', 'testing')
             Default: os.getenv('ENVIRONMENT', 'development')
    
    Returns:
        Configuration instance
    """
    if env is None:
        env = os.getenv('ENVIRONMENT', 'development').lower()
    
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
    }
    
    config_class = configs.get(env, DevelopmentConfig)
    config = config_class()
    config.validate()
    return config
