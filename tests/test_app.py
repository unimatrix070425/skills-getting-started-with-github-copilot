"""
Comprehensive test suite for Mergington High School Activities API.

All tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the action being tested
- Assert: Verify the expected outcome
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a TestClient instance for making requests to the app."""
    return TestClient(app)


# ============================================================================
# GET /activities Tests
# ============================================================================

def test_get_activities_returns_200(client):
    """Test that GET /activities returns a 200 status code."""
    # Arrange
    # No setup needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200


def test_get_activities_returns_all_activities(client):
    """Test that GET /activities returns all 10 activities."""
    # Arrange
    expected_activities = {
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Tennis Club",
        "Drama Club",
        "Visual Arts Studio",
        "Debate Club",
        "Science Club",
    }

    # Act
    response = client.get("/activities")
    activities = response.json()

    # Assert
    assert len(activities) == 9  # 9 activities defined in app.py
    assert set(activities.keys()) == expected_activities


def test_get_activities_contain_required_fields(client):
    """Test that each activity contains required fields."""
    # Arrange
    required_fields = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")
    activities = response.json()

    # Assert
    for activity_name, activity_data in activities.items():
        assert set(activity_data.keys()) == required_fields, \
            f"Activity '{activity_name}' missing required fields"


def test_get_activities_participants_is_list(client):
    """Test that participants field is a list for all activities."""
    # Arrange
    # No setup needed

    # Act
    response = client.get("/activities")
    activities = response.json()

    # Assert
    for activity_name, activity_data in activities.items():
        assert isinstance(activity_data["participants"], list), \
            f"Activity '{activity_name}' participants should be a list"


# ============================================================================
# POST /activities/{activity_name}/signup Tests
# ============================================================================

def test_signup_successful_returns_200(client):
    """Test that successfully signing up returns a 200 status code."""
    # Arrange
    test_email = "newstudent@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={test_email}"
    )

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert "Signed up" in result["message"]


def test_signup_increases_participant_count(client):
    """Test that signing up a student increases the participant count."""
    # Arrange
    test_email = "uniquestudent123@mergington.edu"
    activity_name = "Programming Class"
    
    # Get initial count
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()[activity_name]["participants"])

    # Act
    signup_response = client.post(
        f"/activities/{activity_name}/signup?email={test_email}"
    )
    
    # Get updated count
    updated_response = client.get("/activities")
    updated_count = len(updated_response.json()[activity_name]["participants"])

    # Assert
    assert signup_response.status_code == 200
    assert updated_count == initial_count + 1
    assert test_email in updated_response.json()[activity_name]["participants"]


def test_signup_duplicate_rejected(client):
    """Test that signing up with a duplicate email is rejected."""
    # Arrange
    # Use an existing participant from app.py
    duplicate_email = "michael@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={duplicate_email}"
    )

    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "detail" in result
    assert "already signed up" in result["detail"].lower()


def test_signup_nonexistent_activity_rejected(client):
    """Test that signing up for a nonexistent activity is rejected."""
    # Arrange
    test_email = "student@mergington.edu"
    fake_activity = "Fake Activity That Does Not Exist"

    # Act
    response = client.post(
        f"/activities/{fake_activity}/signup?email={test_email}"
    )

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "detail" in result
    assert "Activity not found" in result["detail"]


def test_signup_with_url_encoded_activity_name(client):
    """Test that signing up works with URL-encoded activity names (spaces)."""
    # Arrange
    test_email = "basketball_student@mergington.edu"
    activity_name = "Basketball Team"  # Activity with spaces

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={test_email}"
    )

    # Assert
    assert response.status_code == 200
    
    # Verify participant was added
    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert test_email in participants


# ============================================================================
# DELETE /activities/{activity_name}/unregister Tests
# ============================================================================

def test_unregister_successful_returns_200(client):
    """Test that successfully unregistering returns a 200 status code."""
    # Arrange
    # First, sign up a student
    test_email = "unregister_test1@mergington.edu"
    activity_name = "Gym Class"
    client.post(f"/activities/{activity_name}/signup?email={test_email}")

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={test_email}"
    )

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert "Unregistered" in result["message"]


def test_unregister_decreases_participant_count(client):
    """Test that unregistering a student decreases the participant count."""
    # Arrange
    # Use an existing participant
    test_email = "sarah@mergington.edu"
    activity_name = "Tennis Club"
    
    # Get initial count
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()[activity_name]["participants"])

    # Act
    unregister_response = client.delete(
        f"/activities/{activity_name}/unregister?email={test_email}"
    )
    
    # Get updated count
    updated_response = client.get("/activities")
    updated_count = len(updated_response.json()[activity_name]["participants"])

    # Assert
    assert unregister_response.status_code == 200
    assert updated_count == initial_count - 1
    assert test_email not in updated_response.json()[activity_name]["participants"]


def test_unregister_not_signed_up_rejected(client):
    """Test that unregistering a student not signed up is rejected."""
    # Arrange
    not_signed_up_email = "notparticipant@mergington.edu"
    activity_name = "Drama Club"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={not_signed_up_email}"
    )

    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "detail" in result
    assert "not signed up" in result["detail"].lower()


def test_unregister_nonexistent_activity_rejected(client):
    """Test that unregistering from a nonexistent activity is rejected."""
    # Arrange
    test_email = "student@mergington.edu"
    fake_activity = "Fake Activity That Does Not Exist"

    # Act
    response = client.delete(
        f"/activities/{fake_activity}/unregister?email={test_email}"
    )

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "detail" in result
    assert "Activity not found" in result["detail"]


def test_unregister_with_url_encoded_activity_name(client):
    """Test that unregistering works with URL-encoded activity names (spaces)."""
    # Arrange
    # First, sign up a student
    test_email = "drama_student@mergington.edu"
    activity_name = "Drama Club"  # Activity with spaces
    
    client.post(f"/activities/{activity_name}/signup?email={test_email}")

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={test_email}"
    )

    # Assert
    assert response.status_code == 200
    
    # Verify participant was removed
    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert test_email not in participants
