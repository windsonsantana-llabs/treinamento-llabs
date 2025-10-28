import pytest
from fastapi.testclient import TestClient
from src.app import app

@pytest.fixture
def client():
    return TestClient(app)

def test_root_redirect(client):
    """Test that root endpoint redirects to static/index.html"""
    response = client.get("/")
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    
    # Test structure of an activity
    first_activity = list(activities.values())[0]
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity
    assert isinstance(first_activity["participants"], list)

def test_signup_success(client):
    """Test successful activity signup"""
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]

    # Verify participant was added
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]

def test_signup_duplicate(client):
    """Test signing up same student twice"""
    activity_name = "Programming Class"
    email = "duplicate@mergington.edu"
    
    # First signup should succeed
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    
    # Second signup should fail
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()

def test_signup_invalid_activity(client):
    """Test signing up for non-existent activity"""
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_unregister_success(client):
    """Test successful unregistration from activity"""
    activity_name = "Chess Club"
    email = "unregistertest@mergington.edu"
    
    # First sign up the student
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Then unregister
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]

    # Verify participant was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]

def test_unregister_not_registered(client):
    """Test unregistering a student who is not registered"""
    response = client.delete("/activities/Chess Club/unregister?email=notregistered@mergington.edu")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"].lower()

def test_unregister_invalid_activity(client):
    """Test unregistering from non-existent activity"""
    response = client.delete("/activities/NonexistentClub/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()