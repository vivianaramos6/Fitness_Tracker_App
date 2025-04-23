#############################################################################
# data_fetcher_test.py
#
# This file contains tests for data_fetcher.py.
#
# You will write these tests in Unit 3.
#############################################################################
import unittest
import streamlit as st
from unittest.mock import patch, MagicMock, PropertyMock
import sys
from data_fetcher import get_user_achievements


import unittest
from unittest.mock import patch, MagicMock
import pandas as pd


# # sys.modules['google'] = MagicMock()
# sys.modules['google.cloud'] = MagicMock()
# sys.modules['google.cloud.bigquery'] = MagicMock()
# sys.modules['google.cloud.aiplatform'] = MagicMock()
# sys.modules['vertexai'] = MagicMock()
# sys.modules['vertexai.generative_models'] = MagicMock()

from data_fetcher import get_user_profile, get_user_posts, get_user_sensor_data, get_user_workouts, get_genai_advice

class TestGetUserProfile(unittest.TestCase):

    def test_get_user_profile_success(self):
        with patch('data_fetcher.bigquery.Client') as mock_client:
            # Mock profile query
            mock_profile_job = MagicMock()
            mock_profile_row = MagicMock()
            mock_profile_row.full_name = 'Alice Johnson'
            mock_profile_row.username = 'alicej'
            mock_profile_row.date_of_birth = '1990-01-15'
            mock_profile_row.profile_image = 'http://example.com/alice.jpg'
            mock_profile_job.result.return_value = [mock_profile_row]

            # Mock friends query
            mock_friends_job = MagicMock()
            mock_friend1 = MagicMock()
            mock_friend1.friend_id = 'user2'
            mock_friend2 = MagicMock()
            mock_friend2.friend_id = 'user3'
            mock_friends_job.result.return_value = [mock_friend1, mock_friend2]

            # Configure side effect for different queries
            mock_client.return_value.query.side_effect = [
                mock_profile_job,
                mock_friends_job
            ]

            result = get_user_profile('user1')

            # Verify results
            self.assertEqual(result['full_name'], 'Alice Johnson')
            self.assertEqual(result['username'], 'alicej')
            self.assertEqual(result['date_of_birth'], '1990-01-15')
            self.assertEqual(result['profile_image'], 'http://example.com/alice.jpg')
            self.assertCountEqual(result['friends'], ['user2', 'user3'])

            # Verify query calls
            self.assertEqual(mock_client.return_value.query.call_count, 2)
    
    @patch('data_fetcher.bigquery.Client')
    def test_get_user_profile_not_found(self, mock_client):
        """Test when user doesn't exist in database"""
        # Setup mock client instance with project property
        mock_client_instance = MagicMock()
        type(mock_client_instance).project = PropertyMock(return_value='vivianaramos6techx25')
        
        # Setup mock empty result
        mock_profile_job = MagicMock()
        mock_profile_job.result.return_value = []
        
        # Configure mock client
        mock_client_instance.query.return_value = mock_profile_job
        mock_client.return_value = mock_client_instance
        
        # Execute
        result = get_user_profile('nonexistent_user')
        
        # Assertions
        self.assertIsNone(result)
        mock_client_instance.query.assert_called_once()

class TestGetUserPosts(unittest.TestCase):
    @patch('data_fetcher.bigquery.Client')
    def test_get_user_posts_success(self, mock_client):
        """Test successful retrieval of user posts"""
        # Setup mock client instance with project property
        mock_client_instance = MagicMock()
        type(mock_client_instance).project = PropertyMock(return_value='vivianaramos6techx25')
        
        # Setup mock post data
        mock_post1 = {
            'post_id': 'post1',
            'user_id': 'user1',
            'timestamp': '2023-01-01 12:00:00',
            'content': 'First post',
            'image': 'http://example.com/image1.jpg',
            'username': 'alice',
            'user_image': 'http://example.com/profile1.jpg'
        }
        
        mock_post2 = {
            'post_id': 'post2',
            'user_id': 'user1',
            'timestamp': '2023-01-02 12:00:00',
            'content': 'Second post',
            'image': None,
            'username': 'alice',
            'user_image': 'http://example.com/profile1.jpg'
        }
        
        # Create mock row objects
        def create_mock_row(data):
            mock_row = MagicMock()
            for key, value in data.items():
                setattr(mock_row, key, value)
            return mock_row
        
        # Setup mock query job
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = [
            create_mock_row(mock_post1),
            create_mock_row(mock_post2)
        ]
        
        # Configure mock client
        mock_client_instance.query.return_value = mock_query_job
        mock_client.return_value = mock_client_instance
        
        # Execute
        result = get_user_posts('user1')
        
        # Assertions
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['post_id'], 'post1')
        self.assertEqual(result[0]['content'], 'First post')
        self.assertEqual(result[0]['image'], 'http://example.com/image1.jpg')
        self.assertEqual(result[1]['post_id'], 'post2')
        self.assertEqual(result[1]['content'], 'Second post')
        self.assertIsNone(result[1]['image'])
        mock_client_instance.query.assert_called_once()

    @patch('data_fetcher.bigquery.Client')
    def test_get_user_posts_empty(self, mock_client):
        """Test when user has no posts"""
        # Setup mock client instance with project property
        mock_client_instance = MagicMock()
        type(mock_client_instance).project = PropertyMock(return_value='vivianaramos6techx25')
        
        # Setup mock empty result
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = []
        
        # Configure mock client
        mock_client_instance.query.return_value = mock_query_job
        mock_client.return_value = mock_client_instance
        
        # Execute
        result = get_user_posts('user_with_no_posts')
        
        # Assertions
        self.assertEqual(len(result), 0)
        mock_client_instance.query.assert_called_once()


class TestGetUserSensorData(unittest.TestCase):
    def test_get_user_sensor_data(self):
        with patch('data_fetcher.bigquery.Client') as mock_client:
            mock_query_job = MagicMock()

            # ✅ Mock row with expected attributes
            mock_row = MagicMock()
            mock_row.sensor_type = 'Heart Rate'
            mock_row.timestamp.strftime.return_value = '2024-01-01 00:00:00'
            mock_row.data = 70
            mock_row.units = 'bpm'

            mock_query_job.result.return_value = [mock_row]
            mock_client.return_value.query.return_value = mock_query_job

            result = get_user_sensor_data('user_123', 'workout_456')

            self.assertIsInstance(result, list)
            self.assertEqual(result[0]['sensor_type'], 'Heart Rate')
            self.assertEqual(result[0]['timestamp'], '2024-01-01 00:00:00')
            self.assertEqual(result[0]['data'], 70)
            self.assertEqual(result[0]['units'], 'bpm')


class TestGetUserWorkouts(unittest.TestCase):
    def test_get_user_workouts(self):
        with patch('data_fetcher.bigquery.Client') as mock_client:
            mock_query_job = MagicMock()

            mock_row = MagicMock()
            mock_row.workout_id = 'workout_1'
            mock_row.start_timestamp = '2024-01-01 10:00:00'
            mock_row.end_timestamp = '2024-01-01 10:30:00'
            mock_row.start_lat_lng = [37.7749, -122.4194]
            mock_row.end_lat_lng = [37.7750, -122.4195]
            mock_row.distance = 5000
            mock_row.steps = 6000
            mock_row.calories_burned = 300

            mock_query_job.result.return_value = [mock_row]
            mock_client.return_value.query.return_value = mock_query_job

            result = get_user_workouts('user_123')

            self.assertIsInstance(result, list)
            self.assertEqual(result[0]['workout_id'], 'workout_1')
            self.assertEqual(result[0]['start_timestamp'], '2024-01-01 10:00:00')
            self.assertEqual(result[0]['end_timestamp'], '2024-01-01 10:30:00')
            self.assertEqual(result[0]['start_lat_lng'], [37.7749, -122.4194])
            self.assertEqual(result[0]['end_lat_lng'], [37.7750, -122.4195])
            self.assertEqual(result[0]['distance'], 5000)
            self.assertEqual(result[0]['steps'], 6000)
            self.assertEqual(result[0]['calories_burned'], 300)

#tests if the gen ai advice is personalized and says the corresponding name to the user id in the response
class TestGetGenAIAdvice(unittest.TestCase):
    @patch('data_fetcher.bigquery.Client')
    @patch('data_fetcher.vertexai.init')
    @patch('data_fetcher.GenerativeModel')
    def test_get_genai_advice(self, mock_gen_model, mock_vertex_init, mock_bigquery):
        # Setup test cases
        test_cases = [
            ("user123", "Alice"),
            ("user456", "Bob"),
            ("user789", None)  # Test missing user
        ]

        # Setup mock Vertex AI response
        mock_response = MagicMock()
        mock_response.text = "some generated fitness advice"
        mock_gen_model.return_value.generate_content.return_value = mock_response

        for user_id, expected_name in test_cases:
            # Setup BigQuery mock
            mock_row = MagicMock()
            mock_row.__getitem__.return_value = expected_name
            mock_query_job = MagicMock()
            mock_query_job.result.return_value = [mock_row] if expected_name else []
            mock_bigquery.return_value.query.return_value = mock_query_job

            # Call the function
            result = get_genai_advice(user_id, "Give me fitness advice")

            # Verify the response format
            if expected_name:
                expected_content = f"{expected_name}, some generated fitness advice"
                self.assertEqual(
                    result['content'],
                    expected_content,
                    f"Failed for {user_id}: Response should be '{expected_content}'"
                )
            else:
                self.assertEqual(
                    result['content'],
                    "User, some generated fitness advice",
                    "Failed for missing user: Should use 'User' as default"
                )

            # Verify the advice_id format
            self.assertTrue(result['advice_id'].startswith(f"adv_{user_id}"))

class TestGetUserAchievements(unittest.TestCase):
        @patch("data_fetcher.bigquery.Client")

        def test_get_user_achievements(self, mock_client_class):
            # Arrange
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            # Sample data to return
            sample_data = pd.DataFrame({
                "Name": ["Marathon Finisher", "Early Riser"],
                "Description": ["Completed a marathon", "Woke up early 5 days in a row"],
                "EarnedDate": ["2025-03-01", "2025-04-01"]
            })

            # Mock query().to_dataframe()
            mock_client.query.return_value.to_dataframe.return_value = sample_data.copy()

            # Act
            user_id = "user_123"
            result = get_user_achievements(user_id)

            # Assert
            self.assertEqual(len(result), 2)
            self.assertIn("🏆 Marathon Finisher", result["Name"].values)
            self.assertIn("🏆 Early Riser", result["Name"].values)
            self.assertListEqual(
                result["Description"].tolist(),
                ["Completed a marathon", "Woke up early 5 days in a row"]
            )            

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

# Mock data
sample_achievements = pd.DataFrame([
    {"Name": "Milestone Reached", "Description": "Did something awesome", "EarnedDate": "2025-01-01"}
])
sample_empty = pd.DataFrame()

class TestShowGoalsPage(unittest.TestCase):
    @patch("goals_page.st")  # Patch st where it's used (in goals_page)
    @patch("goals_page.get_completed_goals")
    @patch("goals_page.get_weekly_goals")
    @patch("goals_page.get_group_goals")
    @patch("goals_page.get_suggested_goals")
    @patch("goals_page.get_user_achievements")
    @patch("goals_page.check_and_award_goal_achievements")
    def test_show_goals_page(
        self,
        mock_check_and_award,
        mock_get_user_achievements,
        mock_get_suggested_goals,
        mock_get_group_goals,
        mock_get_weekly_goals,
        mock_get_completed_goals,
        mock_st,  # This is now the Streamlit mock used inside the module
    ):
        from goals_page import show_goals_page

        # Return values
        mock_get_user_achievements.return_value = sample_achievements
        mock_get_suggested_goals.return_value = sample_empty
        mock_get_group_goals.return_value = sample_empty
        mock_get_weekly_goals.return_value = sample_empty
        mock_get_completed_goals.return_value = sample_empty

        # Use dict-like MagicMock for session_state
        mock_st.session_state = {}

        # Run the function
        show_goals_page("user_123")

        # Check it ran as expected
        mock_check_and_award.assert_called_once_with("user_123")
        mock_get_user_achievements.assert_called_once_with("user_123")
        self.assertTrue(mock_st.session_state["achievements_checked"])

if __name__ == "__main__":
    unittest.main()
