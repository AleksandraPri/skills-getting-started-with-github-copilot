from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def client():
    # Arrange: reset activities dict before each test by copying the original
    # (we'll store a snapshot and restore it after)
    original = {k: {**v, "participants": list(v["participants"])} for k, v in activities.items()}
    with TestClient(app) as c:
        yield c
    # restore state
    activities.clear()
    activities.update(original)


def test_get_activities_returns_all(client):
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_adds_participant(client):
    # Act
    response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")

    # Assert
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    assert "test@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400(client):
    # Arrange: sign the user up once
    client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")

    # Act
    response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_nonexistent_404(client):
    # Act
    response = client.post("/activities/NoSuchActivity/signup?email=test@mergington.edu")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_success(client):
    # Act
    response = client.delete("/activities/Chess%20Club/participants?email=michael@mergington.edu")

    # Assert
    assert response.status_code == 200
    assert "Removed" in response.json()["message"]
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_remove_same_twice_400(client):
    # Arrange: remove once
    client.delete("/activities/Chess%20Club/participants?email=michael@mergington.edu")

    # Act
    response = client.delete("/activities/Chess%20Club/participants?email=michael@mergington.edu")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not registered for this activity"


def test_remove_nonexistent_404(client):
    # Act
    response = client.delete("/activities/NoSuchActivity/participants?email=foo@bar.com")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
