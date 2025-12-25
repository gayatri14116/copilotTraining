"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities database before each test"""
    activities.clear()
    activities.update({
        "Basketball Team": {
            "description": "Join the school basketball team and compete in inter-school tournaments",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "lucas@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Learn swimming techniques and participate in swim meets",
            "schedule": "Mondays and Wednesdays, 3:00 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["ava@mergington.edu", "mia@mergington.edu"]
        }
    })


def test_root_redirect(client):
    """Test that root redirects to static HTML"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Basketball Team" in data
    assert "Swimming Club" in data
    assert data["Basketball Team"]["max_participants"] == 15
    assert len(data["Basketball Team"]["participants"]) == 2


def test_signup_for_activity_success(client):
    """Test successful signup for an activity"""
    response = client.post(
        "/activities/Basketball Team/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Signed up newstudent@mergington.edu" in data["message"]
    
    # Verify the participant was added
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "newstudent@mergington.edu" in activities_data["Basketball Team"]["participants"]


def test_signup_for_nonexistent_activity(client):
    """Test signup for an activity that doesn't exist"""
    response = client.post(
        "/activities/Nonexistent Activity/signup",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_duplicate(client):
    """Test signing up a student who is already registered"""
    response = client.post(
        "/activities/Basketball Team/signup",
        params={"email": "james@mergington.edu"}
    )
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_unregister_from_activity_success(client):
    """Test successful unregistration from an activity"""
    response = client.delete(
        "/activities/Basketball Team/unregister",
        params={"email": "james@mergington.edu"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered james@mergington.edu" in data["message"]
    
    # Verify the participant was removed
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "james@mergington.edu" not in activities_data["Basketball Team"]["participants"]


def test_unregister_from_nonexistent_activity(client):
    """Test unregister from an activity that doesn't exist"""
    response = client.delete(
        "/activities/Nonexistent Activity/unregister",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_non_participant(client):
    """Test unregistering a student who is not registered"""
    response = client.delete(
        "/activities/Basketball Team/unregister",
        params={"email": "notregistered@mergington.edu"}
    )
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]


def test_activity_participants_count(client):
    """Test that participants are correctly tracked"""
    # Initial count
    response = client.get("/activities")
    data = response.json()
    initial_count = len(data["Swimming Club"]["participants"])
    
    # Add a participant
    client.post(
        "/activities/Swimming Club/signup",
        params={"email": "newswimmer@mergington.edu"}
    )
    
    # Verify count increased
    response = client.get("/activities")
    data = response.json()
    new_count = len(data["Swimming Club"]["participants"])
    assert new_count == initial_count + 1
    
    # Remove a participant
    client.delete(
        "/activities/Swimming Club/unregister",
        params={"email": "ava@mergington.edu"}
    )
    
    # Verify count decreased
    response = client.get("/activities")
    data = response.json()
    final_count = len(data["Swimming Club"]["participants"])
    assert final_count == initial_count  # Should be back to original count
