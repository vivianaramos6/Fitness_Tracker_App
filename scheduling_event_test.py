import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import pandas as pd

# Mock the client import at the top-level of the fitness_groups module
with patch('fitness_groups.client', new_callable=MagicMock()) as mock_global_client:
    from fitness_groups import schedule_group_workout, get_group_events



class TestGetGroupEvents(unittest.TestCase):

    @patch('fitness_groups.client')
    def test_get_group_events_success(self, mock_client):
        """Test fetching of group events with mocked BigQuery results"""
        mock_query = MagicMock()

        test_data = [
            MagicMock(EventId="event1", Title="Run Club", EventDate=datetime(2025, 4, 25, 7, 0)),
            MagicMock(EventId="event2", Title="Yoga Flow", EventDate=datetime(2025, 4, 26, 8, 30))
        ]

        mock_query.result.return_value = test_data
        mock_client.query.return_value = mock_query

        df = get_group_events()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertListEqual(list(df.columns), ['EventId', 'Title', 'EventDate'])
        self.assertEqual(df.iloc[0]['Title'], "Run Club")

    @patch('fitness_groups.client')
    def test_get_group_events_error(self, mock_client):
        """Simulate failure while retrieving group events"""
        mock_client.query.side_effect = Exception("Query failed")

        df = get_group_events()
        self.assertTrue(df.empty)
        self.assertListEqual(list(df.columns), ['EventId', 'Title', 'EventDate'])


if __name__ == '__main__':
    unittest.main()
