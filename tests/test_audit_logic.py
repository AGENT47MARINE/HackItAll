"""Unit tests for logic identified as untested in the audit."""
import pytest
from datetime import datetime
from utils.validators import InputValidator
from services.low_bandwidth_service import LowBandwidthService
from services.educational_content_service import EducationalContentService
from services.profile_service import ProfileService
from database import SessionLocal

def test_phone_validation():
    """Test phone validation regex pattern."""
    assert InputValidator.validate_phone("+1234567890") is True
    assert InputValidator.validate_phone("1234567890") is True
    assert InputValidator.validate_phone("+1 234-567-890") is True
    assert InputValidator.validate_phone("123") is False
    assert InputValidator.validate_phone("not-a-phone") is False
    assert InputValidator.validate_phone("") is False

def test_url_validation():
    """Test URL validation regex patterns."""
    assert InputValidator.validate_url("https://example.com") is True
    # The current implementation uses urlparse, let's verify edge cases
    assert InputValidator.validate_url("http://localhost:8000") is True
    assert InputValidator.validate_url("invalid-url") is False
    assert InputValidator.validate_url("ftp://example.com") is False

def test_date_parsing_error_path():
    """Test error path for date parsing."""
    assert InputValidator.validate_date("2024-01-01") is not None
    assert InputValidator.validate_date("invalid-date") is None
    assert InputValidator.validate_date("") is None

def test_text_compression():
    """Test text compression and decompression."""
    test_text = "This is a test string for compression auditing."
    compressed = LowBandwidthService.compress_text(test_text)
    assert isinstance(compressed, bytes)
    assert len(compressed) > 0
    
    decompressed = LowBandwidthService.decompress_text(compressed)
    assert decompressed == test_text

def test_strip_heavy_content():
    """Test strip_heavy_content logic."""
    data = {
        "title": "Hackathon",
        "description": "A" * 300,
        "image_url": "https://example.com/image.jpg",
        "metadata": {"key": "value"}
    }
    optimized = LowBandwidthService.strip_heavy_content(data)
    
    assert len(optimized["description"]) <= 203 # 200 + "..."
    assert "image_url" not in optimized
    assert "metadata" not in optimized
    assert optimized["title"] == "Hackathon"

def test_optimize_opportunity_list():
    """Test optimize_opportunity_list logic."""
    opportunities = [
        {
            "id": "1",
            "title": "Opp 1",
            "description": "Long " * 50,
            "type": "hackathon",
            "deadline": "2024-12-31",
            "image_url": "http://img.com"
        }
    ]
    
    # Low bandwidth OFF
    normal = LowBandwidthService.optimize_opportunity_list(opportunities, low_bandwidth=False)
    assert normal == opportunities
    
    # Low bandwidth ON
    optimized = LowBandwidthService.optimize_opportunity_list(opportunities, low_bandwidth=True)
    assert len(optimized) == 1
    assert len(optimized[0]["description"]) <= 153
    assert "image_url" not in optimized[0]

def test_glossary_lookup():
    """Test glossary lookup in EducationalContentService."""
    db = SessionLocal()
    try:
        service = EducationalContentService(db)
        # Test existing term
        result = service.get_glossary_term("hackathon")
        assert result is not None
        assert "definition" in result
        
        # Test non-existing term
        assert service.get_glossary_term("nonexistent") is None
    finally:
        db.close()

def test_application_guide_logic():
    """Test application guide retrieval."""
    db = SessionLocal()
    try:
        service = EducationalContentService(db)
        # Test existing guide
        result = service.get_application_guide("hackathon")
        assert result is not None
        assert "steps" in result
        
        # Test non-existing guide
        assert service.get_application_guide("unknown") is None
    finally:
        db.close()

def test_activity_streak_logic():
    """Test activity streak logic in ProfileService."""
    db = SessionLocal()
    try:
        service = ProfileService(db)
        # Test with no activity
        streak = service._calculate_activity_streak("non-existent-user")
        assert streak == 0
        
        # We'd need to mock data for positive streaks, but this covers the zero path.
    finally:
        db.close()
