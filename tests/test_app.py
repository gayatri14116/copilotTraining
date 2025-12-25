"""
Tests for the High School Management System API
"""

import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store a deep copy of the current state to restore after each test
    original_activities = copy.deepcopy(activities)
    
    yield
    
    # Restore to original state after test
    activities.clear()
    activities.update(original_activities)


def test_root_redirects(client):
    """Test that root path redirects to static index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    # Check that we have all three default activities
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    
    # Check structure of an activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_for_activity_success(client):
    """Test successfully signing up for an activity"""
    initial_count = len(activities["Chess Club"]["participants"])
    
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "newstudent@mergington.edu" in data["message"]
    assert "Chess Club" in data["message"]
    
    # Verify participant was added
    assert len(activities["Chess Club"]["participants"]) == initial_count + 1
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_for_nonexistent_activity(client):
    """Test signing up for an activity that doesn't exist"""
    response = client.post(
        "/activities/Nonexistent Activity/signup",
        params={"email": "student@mergington.edu"}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Activity not found"


def test_signup_with_url_encoded_activity_name(client):
    """Test signing up with URL-encoded activity name"""
    response = client.post(
        "/activities/Programming%20Class/signup",
        params={"email": "coder@mergington.edu"}
    )
    
    assert response.status_code == 200
    assert "coder@mergington.edu" in activities["Programming Class"]["participants"]


def test_multiple_students_can_signup(client):
    """Test that multiple different students can sign up for the same activity"""
    emails = [
        "student1@mergington.edu",
        "student2@mergington.edu",
        "student3@mergington.edu"
    ]
    
    for email in emails:
        response = client.post(
            "/activities/Gym Class/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify all students were added
    for email in emails:
        assert email in activities["Gym Class"]["participants"]


def test_activities_persist_in_memory(client):
    """Test that activity data persists across requests within the same session"""
    # Sign up a student
    client.post(
        "/activities/Chess Club/signup",
        params={"email": "persistent@mergington.edu"}
    )
    
    # Fetch activities again
    response = client.get("/activities")
    data = response.json()
    
    # Verify the signup persisted
    assert "persistent@mergington.edu" in data["Chess Club"]["participants"]


def test_all_activities_have_required_fields(client):
    """Test that all activities have the required fields"""
    response = client.get("/activities")
    data = response.json()
    
    required_fields = ["description", "schedule", "max_participants", "participants"]
    
    for activity_name, activity_data in data.items():
        for field in required_fields:
            assert field in activity_data, f"{activity_name} missing {field}"


def test_participants_list_is_list_type(client):
    """Test that participants field is always a list"""
    response = client.get("/activities")
    data = response.json()
    
    for activity_name, activity_data in data.items():
        assert isinstance(activity_data["participants"], list), \
            f"{activity_name} participants is not a list"


def test_duplicate_signup_prevention(client):
    """Test that a student cannot sign up twice for the same activity"""
    email = "duplicate@mergington.edu"
    
    # First signup should succeed
    response1 = client.post(
        "/activities/Chess Club/signup",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Second signup should fail
    response2 = client.post(
        "/activities/Chess Club/signup",
        params={"email": email}
    )
    assert response2.status_code == 400
    data = response2.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()
