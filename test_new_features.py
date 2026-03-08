"""Quick test script for newly implemented features."""
import sys
from utils.validators import InputValidator

def test_validators():
    """Test input validators."""
    print("Testing Input Validators...")
    
    # Test email validation
    assert InputValidator.validate_email("test@example.com") == True
    assert InputValidator.validate_email("invalid-email") == False
    print("✓ Email validation works")
    
    # Test phone validation
    assert InputValidator.validate_phone("+1234567890") == True
    assert InputValidator.validate_phone("123") == False
    print("✓ Phone validation works")
    
    # Test URL validation
    assert InputValidator.validate_url("https://example.com") == True
    assert InputValidator.validate_url("not-a-url") == False
    print("✓ URL validation works")
    
    # Test search query sanitization
    sanitized = InputValidator.sanitize_search_query("test<script>alert('xss')</script>")
    assert "<script>" not in sanitized
    print("✓ Search query sanitization works")
    
    # Test education level validation
    assert InputValidator.validate_education_level("bachelor") == True
    assert InputValidator.validate_education_level("invalid") == False
    print("✓ Education level validation works")
    
    print("\nAll validator tests passed! ✅\n")


def test_cache_service():
    """Test cache service."""
    print("Testing Cache Service...")
    
    from services.cache_service import CacheService, CacheKeys, CacheTTL
    
    cache = CacheService()
    
    if cache.enabled:
        print("✓ Redis connection established")
        
        # Test set and get
        cache.set("test_key", {"data": "test_value"}, ttl=60)
        value = cache.get("test_key")
        assert value == {"data": "test_value"}
        print("✓ Cache set/get works")
        
        # Test delete
        cache.delete("test_key")
        value = cache.get("test_key")
        assert value is None
        print("✓ Cache delete works")
        
        # Test cache key generators
        profile_key = CacheKeys.user_profile("user123")
        assert profile_key == "profile:user123"
        print("✓ Cache key generators work")
        
        print("\nAll cache tests passed! ✅\n")
    else:
        print("⚠ Redis not available, cache tests skipped\n")


def test_educational_content():
    """Test educational content service."""
    print("Testing Educational Content Service...")
    
    from services.educational_content_service import EducationalContentService
    from database import SessionLocal
    
    db = SessionLocal()
    try:
        service = EducationalContentService(db)
        
        # Test glossary
        term = service.get_glossary_term("hackathon")
        assert term is not None
        assert "definition" in term
        print("✓ Glossary retrieval works")
        
        # Test guides
        guide = service.get_application_guide("scholarship")
        assert guide is not None
        assert "steps" in guide
        print("✓ Application guide retrieval works")
        
        print("\nAll educational content tests passed! ✅\n")
    finally:
        db.close()


def test_scheduler_service():
    """Test scheduler service."""
    print("Testing Scheduler Service...")
    
    from services.scheduler_service import SchedulerService
    
    # Just verify the methods exist and are callable
    assert hasattr(SchedulerService, 'process_deadline_reminders')
    assert hasattr(SchedulerService, 'archive_expired_opportunities')
    assert hasattr(SchedulerService, 'update_recommendations')
    assert hasattr(SchedulerService, 'cleanup_old_reminders')
    print("✓ All scheduler methods exist")
    
    print("\nScheduler service structure verified! ✅\n")


if __name__ == "__main__":
    try:
        print("=" * 60)
        print("Testing Newly Implemented Features (Tasks 14.4-17)")
        print("=" * 60 + "\n")
        
        test_validators()
        test_cache_service()
        test_educational_content()
        test_scheduler_service()
        
        print("=" * 60)
        print("All tests completed successfully! 🎉")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
