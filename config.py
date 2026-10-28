"""
config.py
=========
Configuration settings for the Flask Electric Vehicle Market Analysis application.
Supports Development, Testing, and Production environments.
"""

import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    """Base configuration with safe production defaults."""
    SECRET_KEY = os.getenv("SECRET_KEY", "ev-market-dev-secret-key-39281982736412")
    DEBUG = False
    TESTING = False

    # MySQL Configuration
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB = os.getenv("MYSQL_DB", "ev_market_db")

    # SQLAlchemy Database URI (MySQL with PyMySQL driver)
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
        "pool_timeout": 5
    }

    # Tableau Integration URLs
    TABLEAU_DASHBOARD_URL = os.getenv(
        "TABLEAU_DASHBOARD_URL",
        "https://public.tableau.com/views/ElectricVehicleMarketAnalysis/EVMarketOverview"
    )
    TABLEAU_STORY_URL = os.getenv(
        "TABLEAU_STORY_URL",
        "https://public.tableau.com/views/ElectricVehicleMarketAnalysis/EVMarketStory"
    )

    # Pagination
    ITEMS_PER_PAGE = 20


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    DEBUG = False
    SECRET_KEY = "test-secret-key"


class ProductionConfig(Config):
    """Production environment configuration with hardened security."""
    DEBUG = False
    TESTING = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
