"""Unit tests for intervals client."""
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from intervals_client import IntervalsClient


class TestIntervalsClient(unittest.TestCase):
    """Test cases for IntervalsClient."""

    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        self.athlete_id = "test_athlete"
        self.client = IntervalsClient(self.api_key, self.athlete_id)

    @patch('intervals_client.requests.Session')
    def test_initialization(self, mock_session):
        """Test client initialization."""
        client = IntervalsClient("key", "athlete_id")
        self.assertEqual(client.api_key, "key")
        self.assertEqual(client.athlete_id, "athlete_id")

    @patch('intervals_client.requests.Session.get')
    def test_get_athlete_profile(self, mock_get):
        """Test fetching athlete profile."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'id': 'test_athlete',
            'name': 'Test Athlete',
            'icu_weight': 70.0,
            'icu_resting_hr': 60
        }
        mock_get.return_value = mock_response

        # Test
        profile = self.client.get_athlete_profile()

        # Assertions
        self.assertEqual(profile['id'], 'test_athlete')
        self.assertEqual(profile['name'], 'Test Athlete')
        self.assertEqual(profile['icu_weight'], 70.0)
        mock_get.assert_called_once()

    @patch('intervals_client.requests.Session.get')
    def test_get_activities(self, mock_get):
        """Test fetching activities."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                'id': 'activity1',
                'type': 'Run',
                'distance': 5000,
                'icu_training_load': 45
            },
            {
                'id': 'activity2',
                'type': 'Ride',
                'distance': 20000,
                'icu_training_load': 60
            }
        ]
        mock_get.return_value = mock_response

        # Test
        activities = self.client.get_activities(
            oldest='2025-10-01',
            newest='2025-10-26'
        )

        # Assertions
        self.assertEqual(len(activities), 2)
        self.assertEqual(activities[0]['type'], 'Run')
        self.assertEqual(activities[1]['type'], 'Ride')
        mock_get.assert_called_once()

    @patch('intervals_client.requests.Session.get')
    def test_get_activity_detail(self, mock_get):
        """Test fetching single activity detail."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'id': 'activity1',
            'type': 'Run',
            'distance': 5000,
            'moving_time': 1800,
            'average_heartrate': 150,
            'icu_training_load': 45
        }
        mock_get.return_value = mock_response

        # Test
        activity = self.client.get_activity_detail('activity1')

        # Assertions
        self.assertEqual(activity['id'], 'activity1')
        self.assertEqual(activity['distance'], 5000)
        self.assertEqual(activity['moving_time'], 1800)
        mock_get.assert_called_once()

    @patch('intervals_client.requests.Session.get')
    def test_fetch_training_data(self, mock_get):
        """Test comprehensive training data fetch."""
        # Mock responses for multiple calls
        profile_response = Mock()
        profile_response.json.return_value = {
            'id': 'test_athlete',
            'icu_weight': 70.0,
            'ctl': 25.0,
            'atl': 20.0
        }

        activities_response = Mock()
        activities_response.json.return_value = [
            {'id': 'act1', 'type': 'Run', 'icu_training_load': 45},
            {'id': 'act2', 'type': 'Ride', 'icu_training_load': 60}
        ]

        wellness_response = Mock()
        wellness_response.json.return_value = [
            {'id': '2025-10-26', 'restingHR': 60, 'hrv': 45}
        ]

        # Configure mock to return different responses
        mock_get.side_effect = [profile_response, activities_response, wellness_response]

        # Test
        data = self.client.fetch_training_data(days_back=30)

        # Assertions
        self.assertIn('profile', data)
        self.assertIn('activities', data)
        self.assertIn('wellness', data)
        self.assertIn('date_range', data)

        self.assertEqual(data['profile']['id'], 'test_athlete')
        self.assertEqual(len(data['activities']), 2)
        self.assertEqual(data['date_range']['days'], 30)

        # Verify date range calculation
        today = datetime.now().date()
        start_date = today - timedelta(days=30)
        self.assertEqual(data['date_range']['start'], start_date.isoformat())
        self.assertEqual(data['date_range']['end'], today.isoformat())

    @patch('intervals_client.requests.Session.get')
    def test_fetch_training_data_wellness_error(self, mock_get):
        """Test training data fetch when wellness data fails."""
        # Mock responses
        profile_response = Mock()
        profile_response.json.return_value = {'id': 'test_athlete'}

        activities_response = Mock()
        activities_response.json.return_value = [{'id': 'act1'}]

        # Wellness request fails
        wellness_response = Mock()
        wellness_response.raise_for_status.side_effect = Exception("Wellness not available")

        mock_get.side_effect = [profile_response, activities_response, wellness_response]

        # Test - should not raise exception
        data = self.client.fetch_training_data(days_back=7)

        # Assertions - wellness should be empty
        self.assertEqual(data['wellness'], [])

    @patch('intervals_client.requests.Session.get')
    def test_api_error_handling(self, mock_get):
        """Test handling of API errors."""
        # Mock error response
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_get.return_value = mock_response

        # Test - should raise exception
        with self.assertRaises(Exception):
            self.client.get_athlete_profile()


if __name__ == '__main__':
    unittest.main()
