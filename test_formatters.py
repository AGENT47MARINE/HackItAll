"""Test script for response formatters."""
import sys
from datetime import datetime
from utils.formatters import ResponseFormatter


class MockUser:
    """Mock User model for testing."""
    def __init__(self):
        self.id = "user123"
        self.email = "test@example.com"
        self.phone = "+1234567890"
        self.created_at = datetime(2024, 1, 1, 12, 0, 0)
        self.updated_at = datetime(2024, 3, 1, 12, 0, 0)


class MockProfile:
    """Mock Profile model for testing."""
    def __init__(self):
        self.interests = '["AI", "Web Development"]'
        self.skills = '["Python", "JavaScript"]'
        self.education_level = "bachelor"
        self.notification_email = True
        self.notification_sms = False
        self.low_bandwidth_mode = False
        self.updated_at = datetime(2024, 3, 1, 12, 0, 0)


class MockOpportunity:
    """Mock Opportunity model for testing."""
    def __init__(self):
        self.id = "opp123"
        self.title = "Test Hackathon"
        self.description = "A test hackathon"
        self.type = "hackathon"
        self.deadline = datetime(2024, 12, 31, 23, 59, 59)
        self.application_link = "https://example.com/apply"
        self.image_url = "https://example.com/image.jpg"
        self.tags = '["AI", "ML"]'
        self.required_skills = '["Python"]'
        self.eligibility = "Open to all"
        self.status = "active"
        self.created_at = datetime(2024, 1, 1, 12, 0, 0)
        self.updated_at = datetime(2024, 3, 1, 12, 0, 0)


class MockTrackedOpportunity:
    """Mock TrackedOpportunity model for testing."""
    def __init__(self):
        self.user_id = "user123"
        self.opportunity_id = "opp123"
        self.saved_at = datetime(2024, 2, 1, 12, 0, 0)
        self.is_expired = False


class MockParticipationHistory:
    """Mock ParticipationHistory model for testing."""
    def __init__(self):
        self.id = "part123"
        self.user_id = "user123"
        self.opportunity_id = "opp123"
        self.status = "applied"
        self.notes = "Test notes"
        self.timestamp = datetime(2024, 2, 15, 12, 0, 0)


def test_profile_formatter():
    """Test profile response formatter."""
    print("Testing Profile Formatter...")
    
    user = MockUser()
    profile = MockProfile()
    participation_history = [
        {
            "id": "part1",
            "opportunity_id": "opp1",
            "status": "applied",
            "notes": "Test",
            "created_at": "2024-02-01T12:00:00"
        }
    ]
    
    result = ResponseFormatter.format_profile_response(user, profile, participation_history)
    
    assert result["id"] == "user123"
    assert result["email"] == "test@example.com"
    assert result["interests"] == ["AI", "Web Development"]
    assert result["skills"] == ["Python", "JavaScript"]
    assert result["education_level"] == "bachelor"
    assert result["notification_email"] == True
    assert result["low_bandwidth_mode"] == False
    assert "created_at" in result
    assert "updated_at" in result
    assert len(result["participation_history"]) == 1
    
    print("✓ Profile formatter works correctly")


def test_opportunity_formatter():
    """Test opportunity response formatter."""
    print("Testing Opportunity Formatter...")
    
    opportunity = MockOpportunity()
    
    result = ResponseFormatter.format_opportunity_response(opportunity, tracked_count=5)
    
    assert result["id"] == "opp123"
    assert result["title"] == "Test Hackathon"
    assert result["type"] == "hackathon"
    assert result["tags"] == ["AI", "ML"]
    assert result["required_skills"] == ["Python"]
    assert result["tracked_count"] == 5
    assert result["status"] == "active"
    
    print("✓ Opportunity formatter works correctly")


def test_tracked_opportunities_formatter():
    """Test tracked opportunities list formatter."""
    print("Testing Tracked Opportunities Formatter...")
    
    tracked = MockTrackedOpportunity()
    opportunity = MockOpportunity()
    
    tracked_list = [(tracked, opportunity)]
    
    result = ResponseFormatter.format_tracked_opportunities_response(tracked_list)
    
    assert len(result) == 1
    assert result[0]["user_id"] == "user123"
    assert result[0]["opportunity_id"] == "opp123"
    assert result[0]["is_expired"] == False
    assert "opportunity" in result[0]
    assert result[0]["opportunity"]["title"] == "Test Hackathon"
    
    print("✓ Tracked opportunities formatter works correctly")


def test_participation_history_formatter():
    """Test participation history formatter."""
    print("Testing Participation History Formatter...")
    
    participation = MockParticipationHistory()
    
    result = ResponseFormatter.format_participation_history_response(participation)
    
    assert result["id"] == "part123"
    assert result["user_id"] == "user123"
    assert result["opportunity_id"] == "opp123"
    assert result["status"] == "applied"
    assert result["notes"] == "Test notes"
    
    print("✓ Participation history formatter works correctly")


def test_error_formatter():
    """Test error response formatter."""
    print("Testing Error Formatter...")
    
    result = ResponseFormatter.format_error_response(
        "Validation Error",
        "Invalid input data",
        [{"field": "email", "message": "Invalid email format"}]
    )
    
    assert result["error"] == "Validation Error"
    assert result["message"] == "Invalid input data"
    assert len(result["details"]) == 1
    assert result["details"][0]["field"] == "email"
    
    print("✓ Error formatter works correctly")


if __name__ == "__main__":
    try:
        print("=" * 60)
        print("Testing Response Formatters (Task 18)")
        print("=" * 60 + "\n")
        
        test_profile_formatter()
        test_opportunity_formatter()
        test_tracked_opportunities_formatter()
        test_participation_history_formatter()
        test_error_formatter()
        
        print("\n" + "=" * 60)
        print("All formatter tests passed! 🎉")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
