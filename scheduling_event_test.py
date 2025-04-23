import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import pandas as pd
from fitness_groups import schedule_group_workout, get_group_events


class TestGroupEventsAndScheduling(unittest.TestCase):
    
    
    def setUp(self):
        self.group_id = "group1"
        self.user_id = "user123"
        self.future_time = datetime.now() + timedelta(days=1)
        self.event_data = [
            MagicMock(EventId="event1", Title="Run Club", EventDate=datetime(2025, 4, 25, 7, 0)),
            MagicMock(EventId="event2", Title="Yoga Flow", EventDate=datetime(2025, 4, 26, 8, 30))
        ]
        

    @patch('fitness_groups.get_client')
    def test_get_group_events_failure(self, mock_client):
        """Test error handling during event fetch"""
        mock_client.query.side_effect = Exception("BigQuery error")

        result = get_group_events()
        self.assertTrue(result.empty)
        self.assertListEqual(list(result.columns), ['EventId', 'Title', 'EventDate'])

    @patch('streamlit.success')
    @patch('streamlit.error')
    @patch('fitness_groups.get_client')
    def test_schedule_group_workout_success(self, mock_client, mock_error, mock_success):
        """Test scheduling a group workout successfully"""
        mock_query = MagicMock()
        mock_query.result.return_value = None
        mock_client.query.return_value = mock_query

        result = schedule_group_workout(
            group_id=self.group_id,
            user_id=self.user_id,
            workout_datetime=self.future_time,
            location="City Park",
            title="Cardio Session",
            description="Morning HIIT training"
        )

        self.assertTrue(result)
        self.assertTrue(mock_success.called)
        self.assertFalse(mock_error.called)



if __name__ == '__main__':
    unittest.main()
