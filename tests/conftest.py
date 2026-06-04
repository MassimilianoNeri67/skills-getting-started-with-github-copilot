"""
Pytest configuration and fixtures for FastAPI tests.
Provides test client and isolated test data.
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, get_activities_db


@pytest.fixture
def test_activities():
    """
    Arrange: Provide fresh copy of test activities for each test.
    This ensures test isolation - modifications don't affect other tests.
    """
    return {
        "Test Activity 1": {
            "description": "A test activity for learning",
            "schedule": "Monday 3:00 PM",
            "max_participants": 5,
            "participants": ["student1@test.edu", "student2@test.edu"]
        },
        "Test Activity 2": {
            "description": "Another test activity",
            "schedule": "Wednesday 4:00 PM",
            "max_participants": 10,
            "participants": []
        },
        "Test Activity 3": {
            "description": "Fully booked activity",
            "schedule": "Friday 5:00 PM",
            "max_participants": 2,
            "participants": ["student3@test.edu", "student4@test.edu"]
        }
    }


@pytest.fixture
def test_client(test_activities):
    """
    Arrange: Create test client with isolated activities database.
    Uses dependency overrides to inject test data instead of production data.
    """
    # Override the dependency to use test activities
    app.dependency_overrides[get_activities_db] = lambda: test_activities
    
    client = TestClient(app)
    yield client
    
    # Cleanup: Remove dependency override after test
    app.dependency_overrides.clear()
