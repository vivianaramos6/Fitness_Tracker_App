import unittest
from unittest.mock import patch, MagicMock
import streamlit as st
from google.cloud import bigquery
from datetime import datetime
import uuid
from fitness_groups import get_user_name, get_group_users, get_group_events, create_event, show_calendar


class TestUserFunctions(unittest.TestCase):

    @patch.object(bigquery.Client, 'query')
    def test_get_user_name(self, mock_query):
        # Simulate a mock BigQuery result for get_user_name function
        mock_query.return_value.result.return_value = iter([MagicMock(Name="Alice Johnson")])

        # Test for a valid user ID
        user_id = "user1"
        result = get_user_name(user_id)
        self.assertEqual(result, "Alice Johnson")

        # Test for an invalid user ID
        user_id = "user99"
        result = get_user_name(user_id)
        self.assertEqual(result, "Unknown User")

    @patch.object(bigquery.Client, 'query')
    def test_get_group_users(self, mock_query):
        # Simulate a mock BigQuery result for get_group_users function
        mock_query.return_value.result.return_value = iter([
            MagicMock(UserId="user2", Name="Bob Smith"),
            MagicMock(UserId="user3", Name="Charlie Brown")
        ])

        # Test getting users for a given group
        user_id = "user1"
        result = get_group_users(user_id)
        self.assertEqual(result, [("user2", "Bob Smith"), ("user3", "Charlie Brown")])

        # Test for a user with no group members
        user_id = "user99"
        result = get_group_users(user_id)
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()
