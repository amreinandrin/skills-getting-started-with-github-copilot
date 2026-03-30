"""
Tests for Mergington High School API endpoints
Using AAA (Arrange-Act-Assert) testing pattern
"""

import pytest


class TestGetActivities:
    """Test suite for GET /activities endpoint"""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns status code 200"""
        # Arrange
        # (no setup needed)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_valid_structure(self, client):
        """Test that GET /activities returns activities with required fields"""
        # Arrange
        required_keys = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert isinstance(activities, dict)
        assert len(activities) > 0
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data, dict)
            assert required_keys.issubset(activity_data.keys())

    def test_get_activities_participants_is_list(self, client):
        """Test that participants field is always a list"""
        # Arrange
        # (no setup needed)

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list)
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)

    def test_get_activities_returns_all_nine_activities(self, client):
        """Test that all nine activities are returned"""
        # Arrange
        expected_activity_count = 9

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert len(activities) == expected_activity_count


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success_adds_participant(self, client):
        """Test successful signup adds student to participants list"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]

    def test_signup_success_returns_success_message(self, client):
        """Test successful signup returns proper message"""
        # Arrange
        activity_name = "Programming Class"
        email = "alice@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_missing_email_parameter(self, client):
        """Test signup without email parameter returns 422"""
        # Arrange
        activity_name = "Basketball Team"

        # Act
        response = client.post(f"/activities/{activity_name}/signup")

        # Assert
        assert response.status_code == 422

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test signup for nonexistent activity returns 404"""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_student_returns_400(self, client):
        """Test duplicate signup returns 400 Bad Request"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"

    def test_signup_same_student_cant_register_twice(self, client):
        """Test that a student cannot sign up twice for same activity"""
        # Arrange
        activity_name = "Drama Club"
        email = "newdramatech@mergington.edu"

        # Act - First signup
        response1 = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Act - Second signup attempt
        response2 = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 400
        assert response2.json()["detail"] == "Student already signed up"

    def test_signup_url_encoded_activity_name(self, client):
        """Test signup with URL-encoded activity name"""
        # Arrange
        activity_name = "Basketball Team"
        email = "bball@mergington.edu"
        encoded_name = "Basketball%20Team"

        # Act
        response = client.post(
            f"/activities/{encoded_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200

    def test_signup_multiple_students_same_activity(self, client):
        """Test multiple different students can sign up for same activity"""
        # Arrange
        activity_name = "Science Club"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"

        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup?email={email1}"
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup?email={email2}"
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both are in participants
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        participants = activities_data[activity_name]["participants"]
        assert email1 in participants
        assert email2 in participants
