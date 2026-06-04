"""
API tests using the AAA (Arrange-Act-Assert) pattern.
- Arrange: Set up test data and preconditions
- Act: Execute the code being tested
- Assert: Verify the results
"""

import pytest


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, test_client, test_activities):
        """
        Arrange: Test client with 3 activities ready
        Act: Send GET request to /activities
        Assert: Response contains all activities with correct structure
        """
        # Act
        response = test_client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert "Test Activity 1" in data
        assert "Test Activity 2" in data
        assert "Test Activity 3" in data

    def test_get_activities_contains_correct_fields(self, test_client):
        """
        Arrange: Test client ready
        Act: Send GET request to /activities
        Assert: Each activity has required fields
        """
        # Act
        response = test_client.get("/activities")
        data = response.json()

        # Assert
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_shows_existing_participants(self, test_client, test_activities):
        """
        Arrange: Test Activity 1 has 2 participants
        Act: Send GET request to /activities
        Assert: Participants list matches expected data
        """
        # Act
        response = test_client.get("/activities")
        data = response.json()

        # Assert
        assert len(data["Test Activity 1"]["participants"]) == 2
        assert "student1@test.edu" in data["Test Activity 1"]["participants"]
        assert "student2@test.edu" in data["Test Activity 1"]["participants"]


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static(self, test_client):
        """
        Arrange: Test client ready
        Act: Send GET request to /
        Assert: Responds with redirect to static page
        """
        # Act
        response = test_client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_student_success(self, test_client, test_activities):
        """
        Arrange: Test Activity 2 has no participants, new student email ready
        Act: Send POST signup request for new student
        Assert: Response is successful, student added to participants
        """
        # Arrange
        activity_name = "Test Activity 2"
        email = "newstudent@test.edu"

        # Act
        response = test_client.post(
            f"/activities/{activity_name}/signup?email={email}",
            json={}
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in test_activities[activity_name]["participants"]

    def test_signup_multiple_students_same_activity(self, test_client, test_activities):
        """
        Arrange: Test Activity 2 is empty
        Act: Sign up 3 different students for same activity
        Assert: All students are in participants list
        """
        # Arrange
        activity_name = "Test Activity 2"
        emails = ["alice@test.edu", "bob@test.edu", "charlie@test.edu"]

        # Act & Assert
        for email in emails:
            response = test_client.post(
                f"/activities/{activity_name}/signup?email={email}",
                json={}
            )
            assert response.status_code == 200

        # Final assertion: all students registered
        assert len(test_activities[activity_name]["participants"]) == 3
        for email in emails:
            assert email in test_activities[activity_name]["participants"]

    def test_signup_same_student_different_activities(self, test_client, test_activities):
        """
        Arrange: Test Activity 2 and 3 are available, same student ready
        Act: Sign up same student to multiple activities
        Assert: Student appears in all activities' participant lists
        """
        # Arrange
        email = "versatile@test.edu"
        activities = ["Test Activity 2", "Test Activity 3"]

        # Act & Assert for each activity
        for activity_name in activities:
            response = test_client.post(
                f"/activities/{activity_name}/signup?email={email}",
                json={}
            )
            assert response.status_code == 200

        # Final assertion: student in all activities
        for activity_name in activities:
            assert email in test_activities[activity_name]["participants"]

    def test_signup_duplicate_student_fails(self, test_client, test_activities):
        """
        Arrange: student1@test.edu already in Test Activity 1
        Act: Try to signup the same student again
        Assert: Request fails with 400 status
        """
        # Arrange
        activity_name = "Test Activity 1"
        email = "student1@test.edu"

        # Act
        response = test_client.post(
            f"/activities/{activity_name}/signup?email={email}",
            json={}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_fails(self, test_client):
        """
        Arrange: Activity "Nonexistent Activity" doesn't exist
        Act: Try to signup for nonexistent activity
        Assert: Request fails with 404 status
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@test.edu"

        # Act
        response = test_client.post(
            f"/activities/{activity_name}/signup?email={email}",
            json={}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_response_message_format(self, test_client):
        """
        Arrange: Valid activity and new student ready
        Act: Send signup request
        Assert: Response message has correct format
        """
        # Arrange
        activity_name = "Test Activity 2"
        email = "format@test.edu"

        # Act
        response = test_client.post(
            f"/activities/{activity_name}/signup?email={email}",
            json={}
        )

        # Assert
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]


class TestUnregisterEndpoint:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_student_success(self, test_client, test_activities):
        """
        Arrange: student1@test.edu is in Test Activity 1
        Act: Send POST unregister request
        Assert: Response is successful, student removed from participants
        """
        # Arrange
        activity_name = "Test Activity 1"
        email = "student1@test.edu"
        initial_count = len(test_activities[activity_name]["participants"])

        # Act
        response = test_client.post(
            f"/activities/{activity_name}/unregister?email={email}",
            json={}
        )

        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert email not in test_activities[activity_name]["participants"]
        assert len(test_activities[activity_name]["participants"]) == initial_count - 1

    def test_unregister_nonexistent_student_fails(self, test_client):
        """
        Arrange: notregistered@test.edu is not in Test Activity 2
        Act: Try to unregister student not in activity
        Assert: Request fails with 400 status
        """
        # Arrange
        activity_name = "Test Activity 2"
        email = "notregistered@test.edu"

        # Act
        response = test_client.post(
            f"/activities/{activity_name}/unregister?email={email}",
            json={}
        )

        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_nonexistent_activity_fails(self, test_client):
        """
        Arrange: "Fake Activity" doesn't exist
        Act: Try to unregister from nonexistent activity
        Assert: Request fails with 404 status
        """
        # Arrange
        activity_name = "Fake Activity"
        email = "student@test.edu"

        # Act
        response = test_client.post(
            f"/activities/{activity_name}/unregister?email={email}",
            json={}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_response_message_format(self, test_client, test_activities):
        """
        Arrange: student1@test.edu in Test Activity 1
        Act: Send unregister request
        Assert: Response message has correct format
        """
        # Arrange
        activity_name = "Test Activity 1"
        email = "student1@test.edu"

        # Act
        response = test_client.post(
            f"/activities/{activity_name}/unregister?email={email}",
            json={}
        )

        # Assert
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]


class TestIntegrationFlows:
    """Integration tests combining multiple operations"""

    def test_signup_then_unregister_flow(self, test_client, test_activities):
        """
        Arrange: Activity and email ready
        Act: Sign up student, then unregister
        Assert: Student appears then disappears from participants
        """
        # Arrange
        activity_name = "Test Activity 2"
        email = "flow@test.edu"

        # Act: Sign up
        signup_response = test_client.post(
            f"/activities/{activity_name}/signup?email={email}",
            json={}
        )

        # Assert: Signup successful
        assert signup_response.status_code == 200
        assert email in test_activities[activity_name]["participants"]

        # Act: Unregister
        unregister_response = test_client.post(
            f"/activities/{activity_name}/unregister?email={email}",
            json={}
        )

        # Assert: Unregister successful
        assert unregister_response.status_code == 200
        assert email not in test_activities[activity_name]["participants"]

    def test_signup_reregister_after_unregister(self, test_client, test_activities):
        """
        Arrange: Activity and email ready
        Act: Sign up, unregister, sign up again
        Assert: Each operation succeeds
        """
        # Arrange
        activity_name = "Test Activity 2"
        email = "resurge@test.edu"

        # Act & Assert: First signup
        response1 = test_client.post(
            f"/activities/{activity_name}/signup?email={email}",
            json={}
        )
        assert response1.status_code == 200
        assert email in test_activities[activity_name]["participants"]

        # Act & Assert: Unregister
        response2 = test_client.post(
            f"/activities/{activity_name}/unregister?email={email}",
            json={}
        )
        assert response2.status_code == 200
        assert email not in test_activities[activity_name]["participants"]

        # Act & Assert: Signup again
        response3 = test_client.post(
            f"/activities/{activity_name}/signup?email={email}",
            json={}
        )
        assert response3.status_code == 200
        assert email in test_activities[activity_name]["participants"]

    def test_multiple_students_signup_consistency(self, test_client, test_activities):
        """
        Arrange: Activity with 0 participants
        Act: 5 students sign up, check total in GET
        Assert: GET /activities shows all 5 students
        """
        # Arrange
        activity_name = "Test Activity 2"
        emails = ["user1@test.edu", "user2@test.edu", "user3@test.edu", 
                  "user4@test.edu", "user5@test.edu"]

        # Act: All signup
        for email in emails:
            test_client.post(
                f"/activities/{activity_name}/signup?email={email}",
                json={}
            )

        # Assert: GET shows all participants
        response = test_client.get("/activities")
        data = response.json()
        activity_participants = data[activity_name]["participants"]
        
        assert len(activity_participants) == 5
        for email in emails:
            assert email in activity_participants
