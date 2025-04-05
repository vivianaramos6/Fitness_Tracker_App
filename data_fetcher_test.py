#############################################################################
# data_fetcher_test.py
#
# This file contains tests for data_fetcher.py.
#
# You will write these tests in Unit 3.
#############################################################################
import unittest
from unittest.mock import patch, MagicMock, PropertyMock
from google.cloud.bigquery import QueryJob, Row, Client
from data_fetcher import get_user_profile, get_user_posts

class TestGetUserProfile(unittest.TestCase):

    @patch('google.cloud.bigquery.Client')
    def test_get_user_profile_success(self, mock_client):
        """Test successful retrieval of user profile with friends"""
        # Setup mock client and query results
        mock_client.return_value = MagicMock()
        
        mock_profile_job = MagicMock(spec=QueryJob)
        mock_profile_job.result.return_value = [
            MagicMock(
                full_name='Alice Johnson',
                username='alicej',
                date_of_birth='1990-01-15',
                profile_image='http://example.com/alice.jpg'
            )
        ]
        
        mock_friends_job = MagicMock(spec=QueryJob)
        mock_friends_job.result.return_value = [
            MagicMock(friend_id='user2'),
            MagicMock(friend_id='user3')
        ]
        
        # Configure mock client to return different jobs for different queries
        mock_client.return_value.query.side_effect = [
            mock_profile_job,
            mock_friends_job
        ]
        
        # Execute
        result = get_user_profile('user1')
        
        # Assertions
        self.assertEqual(result['full_name'], 'Alice Johnson')
        self.assertEqual(result['username'], 'alicej')
        self.assertEqual(result['date_of_birth'], '1990-01-15')
        self.assertEqual(result['profile_image'], 'http://example.com/alice.jpg')
        self.assertCountEqual(result['friends'], ['user2', 'user3'])
    
    @patch('google.cloud.bigquery.Client')
    def test_get_user_profile_not_found(self, mock_client):
        """Test when user doesn't exist in database"""
        # Setup mock empty result
        mock_profile_job = MagicMock(spec=QueryJob)
        mock_profile_job.result.return_value = []
        
        # Configure mock client with project attribute
        mock_client_instance = MagicMock(spec=Client)
        type(mock_client_instance).project = PropertyMock(return_value='vivianaramos6techx25')
        mock_client_instance.query.return_value = mock_profile_job
        mock_client.return_value = mock_client_instance
        
        # Execute
        result = get_user_profile('nonexistent_user')
        
        # Assertions
        self.assertIsNone(result)
        self.assertEqual(mock_client_instance.query.call_count, 1)

class TestGetUserPosts(unittest.TestCase):
    @patch('google.cloud.bigquery.Client')
    def test_get_user_posts_success(self, mock_client):
        """Test successful retrieval of user posts"""
        # Setup mock post rows
        mock_post_row1 = MagicMock()
        mock_post_row1.post_id = 'post1'
        mock_post_row1.user_id = 'user1'
        mock_post_row1.timestamp = '2023-01-01 12:00:00'
        mock_post_row1.content = 'First post'
        mock_post_row1.image = 'http://example.com/image1.jpg'
        mock_post_row1.username = 'alice'
        mock_post_row1.user_image = 'http://example.com/profile1.jpg'

        mock_post_row2 = MagicMock()
        mock_post_row2.post_id = 'post2'
        mock_post_row2.user_id = 'user1'
        mock_post_row2.timestamp = '2023-01-02 12:00:00'
        mock_post_row2.content = 'Second post'
        mock_post_row2.image = None
        mock_post_row2.username = 'alice'
        mock_post_row2.user_image = 'http://example.com/profile1.jpg'

        # Setup mock query job
        mock_query_job = MagicMock(spec=QueryJob)
        mock_query_job.result.return_value = [mock_post_row1, mock_post_row2]

        # Configure mock client
        mock_client_instance = MagicMock(spec=Client)
        type(mock_client_instance).project = PropertyMock(return_value='vivianaramos6techx25')
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
        self.assertEqual(mock_client_instance.query.call_count, 1)

    @patch('google.cloud.bigquery.Client')
    def test_get_user_posts_empty(self, mock_client):
        """Test when user has no posts"""
        # Setup mock empty result
        mock_query_job = MagicMock(spec=QueryJob)
        mock_query_job.result.return_value = []

        # Configure mock client
        mock_client_instance = MagicMock(spec=Client)
        type(mock_client_instance).project = PropertyMock(return_value='vivianaramos6techx25')
        mock_client_instance.query.return_value = mock_query_job
        mock_client.return_value = mock_client_instance

        # Execute
        result = get_user_posts('user_with_no_posts')

        # Assertions
        self.assertEqual(len(result), 0)
        self.assertEqual(mock_client_instance.query.call_count, 1)


if __name__ == "__main__":
    unittest.main()