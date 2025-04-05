import unittest
from unittest.mock import patch, MagicMock
from data_fetcher import get_user_sensor_data, get_user_workouts

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



if __name__ == '__main__':
    unittest.main()
