import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime
from fitness_groups import display_fitness_groups, display_group_page


class TestFitnessGroups(unittest.TestCase):

    @patch('google.cloud.bigquery.Client')
    def setUp(self, mock_client):
        self.mock_client = mock_client.return_value
        self.user_id = "test_user_123"

        # Mocks for all groups
        self.mock_all_groups = pd.DataFrame({
            'GroupId': ['group1', 'group2'],
            'Name': ['Cycling Club', 'Yoga Warriors'],
            'Description': ['Road cycling group', 'Morning yoga'],
            'Category': ['Cycling', 'Yoga']
        })
        self.mock_all_groups['member_count'] = [15, 8]

        # Mocks for joined groups
        self.mock_joined_groups = pd.DataFrame({
            'GroupId': ['group1'],
            'Name': ['Cycling Club'],
            'Description': ['Road cycling group'],
            'Category': ['Cycling'],
            'JoinedDate': [datetime(2023, 1, 1)],
            'IsAdmin': [False]
        })
        self.mock_joined_groups['member_count'] = [15]

        # Mocks for group members
        self.mock_members = pd.DataFrame({
            'UserId': ['user1', 'user2'],
            'Name': ['Alice', 'Bob'],
            'ImageUrl': ['url1', 'url2'],
            'JoinedDate': [datetime(2023, 1, 1), datetime(2023, 2, 1)],
            'IsAdmin': [True, False],
            'member_count': [2, 2]
        })

        # Mocks for workouts
        self.mock_workouts = pd.DataFrame({
            'EventId': ['event1'],
            'Title': ['Morning Ride'],
            'Description': ['Group cycling session'],
            'EventDate': [datetime(2025, 6, 15, 8, 0)],
            'Location': ['Central Park'],
            'MaxParticipants': [10]
        })

    @patch('google.cloud.bigquery.Client')
    def test_display_fitness_groups_no_groups(self, mock_client):
        mock_client.return_value.query.return_value.to_dataframe.return_value = pd.DataFrame()
        result = display_fitness_groups(self.user_id)
        self.assertEqual(mock_client.return_value.query.call_count, 2)

    @patch('google.cloud.bigquery.Client')
    def test_display_fitness_groups_with_groups(self, mock_client):
        mock_client.return_value.query.side_effect = [
            MagicMock(to_dataframe=MagicMock(return_value=self.mock_all_groups)),
            MagicMock(to_dataframe=MagicMock(return_value=self.mock_joined_groups))
        ]

        with patch('fitness_groups.get_member_count', return_value=15):
            result = display_fitness_groups(self.user_id)
            self.assertEqual(mock_client.return_value.query.call_count, 2)

    @patch('google.cloud.bigquery.Client')
    def test_display_fitness_groups_error_handling(self, mock_client):
        mock_client.return_value.query.side_effect = Exception("BigQuery error")
        result = display_fitness_groups(self.user_id)
        self.assertIsNone(result)

    @patch('streamlit.image')
    @patch('streamlit.success')
    @patch('streamlit.warning')
    @patch('streamlit.button', return_value=False)
    @patch('google.cloud.bigquery.Client')
    def test_display_group_page_success(self, mock_client, mock_button, mock_warning, mock_success, mock_image):
        group_df = pd.DataFrame([{
            'GroupId': 'group1',
            'Name': 'Cycling Club',
            'Description': 'Road cycling',
            'Category': 'Cycling',
            'JoinedDate': datetime(2023, 1, 1),
            'IsAdmin': False
        }])

        mock_client.return_value.query.side_effect = [
            MagicMock(to_dataframe=MagicMock(return_value=group_df)),
            MagicMock(to_dataframe=MagicMock(return_value=self.mock_members)),
            MagicMock(to_dataframe=MagicMock(return_value=self.mock_workouts)),
            MagicMock(to_dataframe=MagicMock(return_value=pd.DataFrame({'is_creator': [True]}))),
            MagicMock(to_dataframe=MagicMock(return_value=pd.DataFrame({'has_rsvp': [False]}))),
        ]

        result = display_group_page('group1', self.user_id)
        self.assertEqual(mock_client.return_value.query.call_count, 5)

    @patch('streamlit.image')
    @patch('streamlit.button', return_value=False)
    @patch('google.cloud.bigquery.Client')
    def test_display_group_page_not_found(self, mock_client, mock_button, mock_image):
        mock_client.return_value.query.return_value.to_dataframe.return_value = pd.DataFrame()
        result = display_group_page('nonexistent', self.user_id)
        self.assertIsNone(result)

    @patch('streamlit.image')
    @patch('streamlit.success')
    @patch('streamlit.button', return_value=False)
    @patch('google.cloud.bigquery.Client')
    def test_display_group_page_admin_features(self, mock_client, mock_button, mock_success, mock_image):
        group_df = pd.DataFrame([{
            'GroupId': 'group1',
            'Name': 'Cycling Club',
            'Description': 'Road cycling',
            'Category': 'Cycling',
            'JoinedDate': datetime(2023, 1, 1),
            'IsAdmin': True
        }])

        mock_client.return_value.query.side_effect = [
            MagicMock(to_dataframe=MagicMock(return_value=group_df)),
            MagicMock(to_dataframe=MagicMock(return_value=self.mock_members)),
            MagicMock(to_dataframe=MagicMock(return_value=self.mock_workouts)),
            MagicMock(to_dataframe=MagicMock(return_value=pd.DataFrame({'is_creator': [False]}))),
            MagicMock(to_dataframe=MagicMock(return_value=pd.DataFrame({'has_rsvp': [True]}))),
        ]

        result = display_group_page('group1', self.user_id)
        self.assertEqual(mock_client.return_value.query.call_count, 5)

    @patch('streamlit.image')
    @patch('streamlit.button', return_value=True)
    @patch('fitness_groups.leave_group')
    @patch('google.cloud.bigquery.Client')
    def test_display_group_page_leave_group(self, mock_client, mock_leave, mock_button, mock_image):
        mock_leave.return_value = True

        group_df = pd.DataFrame([{
            'GroupId': 'group1',
            'Name': 'Cycling Club',
            'Description': 'Road cycling',
            'Category': 'Cycling',
            'JoinedDate': datetime(2023, 1, 1),
            'IsAdmin': False
        }])

        mock_client.return_value.query.side_effect = [
            MagicMock(to_dataframe=MagicMock(return_value=group_df)),
            MagicMock(to_dataframe=MagicMock(return_value=self.mock_members)),
            MagicMock(to_dataframe=MagicMock(return_value=self.mock_workouts)),
            MagicMock(to_dataframe=MagicMock(return_value=pd.DataFrame({'is_creator': [False]}))),
            MagicMock(to_dataframe=MagicMock(return_value=pd.DataFrame({'has_rsvp': [True]}))),
        ]

        result = display_group_page('group1', self.user_id)
        self.assertTrue(mock_leave.called)


if __name__ == '__main__':
    unittest.main()
