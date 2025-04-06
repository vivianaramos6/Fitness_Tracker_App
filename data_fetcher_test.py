#############################################################################
# data_fetcher_test.py
#
# This file contains tests for data_fetcher.py.
#
# You will write these tests in Unit 3.
#############################################################################
import unittest
from unittest.mock import patch, MagicMock, PropertyMock
import streamlit as st
import sys

# sys.modules['google'] = MagicMock()
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.bigquery'] = MagicMock()
sys.modules['google.cloud.aiplatform'] = MagicMock()
sys.modules['vertexai'] = MagicMock()
sys.modules['vertexai.generative_models'] = MagicMock()

from data_fetcher import get_user_profile, get_user_posts, get_user_sensor_data, get_user_workouts

class TestGetUserProfile(unittest.TestCase):

    def test_get_user_profile_success(self):
        # Patch all Google imports at the test level
        with patch('data_fetcher.bigquery.Client') as mock_client, \
            patch('google.api_core.exceptions.NotFound', create=True):
            
            # Rest of your test remains exactly the same
            mock_profile_job = MagicMock()
            mock_profile_row = MagicMock()
            mock_profile_row.full_name = 'Alice Johnson'
            mock_profile_row.username = 'alicej'
            mock_profile_row.date_of_birth = '1990-01-15'
            mock_profile_row.profile_image = 'http://example.com/alice.jpg'
            mock_profile_job.result.return_value = [mock_profile_row]

            mock_friends_job = MagicMock()
            mock_friend1 = MagicMock(friend_id='user2')
            mock_friend2 = MagicMock(friend_id='user3')
            mock_friends_job.result.return_value = [mock_friend1, mock_friend2]

            mock_client.return_value.query.side_effect = [
                mock_profile_job,
                mock_friends_job
            ]

            result = get_user_profile('user1')

            self.assertEqual(result['full_name'], 'Alice Johnson')
            self.assertEqual(result['username'], 'alicej')
            self.assertEqual(result['date_of_birth'], '1990-01-15')
            self.assertEqual(result['profile_image'], 'http://example.com/alice.jpg')
            self.assertCountEqual(result['friends'], ['user2', 'user3'])
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



if __name__ == "__main__":
    unittest.main()