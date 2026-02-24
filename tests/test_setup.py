"""Test basic project setup."""
import pytest
from sqlalchemy import inspect

from database import Base, engine


def test_database_connection():
    """Test that database connection can be established."""
    inspector = inspect(engine)
    # Should not raise an exception
    assert inspector is not None


def test_base_metadata():
    """Test that Base metadata is properly configured."""
    assert Base.metadata is not None
    assert hasattr(Base, 'metadata')


def test_config_import():
    """Test that configuration can be imported."""
    from config import config
    assert config is not None
    assert hasattr(config, 'DATABASE_URL')
    assert hasattr(config, 'SECRET_KEY')


def test_main_app_import():
    """Test that main application can be imported."""
    from main import app
    assert app is not None
    assert app.title == "Opportunity Access Platform"
