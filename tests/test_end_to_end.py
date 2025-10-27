"""End-to-end integration tests."""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from query_parser import QueryParser
from intervals_client import IntervalsClient
from llm_analyzer import LLMAnalyzer


class TestEndToEnd(unittest.TestCase):
    """End-to-end integration tests."""

    @patch('intervals_client.requests.Session')
    @patch('llm_analyzer.OpenAI')
    def test_full_analysis_workflow(self, mock_openai, mock_session):
        """Test complete workflow from query to analysis."""
        # 1. Parse query
        parser = QueryParser()
        context = parser.parse("How's my training this month?")

        self.assertEqual(context.scope, 'range')
        self.assertEqual(context.timeframe, 'month')

        # 2. Mock intervals.icu data fetch
        mock_get = MagicMock()
        mock_session.return_value.get = mock_get

        # Mock profile response
        profile_response = Mock()
        profile_response.json.return_value = {
            'id': 'athlete1',
            'icu_weight': 70.0,
            'icu_resting_hr': 60,
            'ctl': 25.0,
            'atl': 20.0
        }

        # Mock activities response
        activities_response = Mock()
        activities_response.json.return_value = [
            {
                'id': 'act1',
                'type': 'Run',
                'start_date_local': '2025-10-26T08:00:00',
                'distance': 5000,
                'moving_time': 1800,
                'average_heartrate': 150,
                'icu_training_load': 45
            },
            {
                'id': 'act2',
                'type': 'Ride',
                'start_date_local': '2025-10-25T09:00:00',
                'distance': 20000,
                'moving_time': 3600,
                'average_heartrate': 140,
                'icu_training_load': 60
            }
        ]

        # Mock wellness response
        wellness_response = Mock()
        wellness_response.json.return_value = []

        mock_get.side_effect = [profile_response, activities_response, wellness_response]

        # Fetch data
        client = IntervalsClient('api_key', 'athlete_id')
        training_data = client.fetch_training_data(days_back=context.days_back)

        # Verify fetched data
        self.assertEqual(training_data['profile']['id'], 'athlete1')
        self.assertEqual(len(training_data['activities']), 2)

        # 3. Mock LLM analysis
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_completion = Mock()
        mock_message = Mock()
        mock_message.content = "Your training this month shows good consistency..."
        mock_completion.choices = [Mock(message=mock_message)]

        mock_client.chat.completions.create.return_value = mock_completion

        # Analyze with LLM
        analyzer = LLMAnalyzer('openrouter_key', 'gemini-2.5-flash')
        analysis = analyzer.analyze(training_data, "How's my training this month?")

        # Verify analysis
        self.assertIn("training", analysis.lower())
        mock_client.chat.completions.create.assert_called_once()

    @patch('intervals_client.requests.Session')
    def test_activity_filtering_workflow(self, mock_session):
        """Test workflow with activity type filtering."""
        # Parse query with activity type
        parser = QueryParser()
        context = parser.parse("Analyze my last 5 runs")

        self.assertEqual(context.scope, 'comparison')
        self.assertEqual(context.activity_type, 'run')
        self.assertEqual(context.activity_count, 5)

        # Mock data fetch
        mock_get = MagicMock()
        mock_session.return_value.get = mock_get

        profile_response = Mock()
        profile_response.json.return_value = {'id': 'athlete1'}

        # Mix of activities
        activities_response = Mock()
        activities_response.json.return_value = [
            {'id': 'act1', 'type': 'Run', 'distance': 5000},
            {'id': 'act2', 'type': 'Ride', 'distance': 20000},
            {'id': 'act3', 'type': 'Run', 'distance': 6000},
            {'id': 'act4', 'type': 'Run', 'distance': 5500},
            {'id': 'act5', 'type': 'Workout', 'distance': 0},
            {'id': 'act6', 'type': 'Run', 'distance': 7000},
        ]

        wellness_response = Mock()
        wellness_response.json.return_value = []

        mock_get.side_effect = [profile_response, activities_response, wellness_response]

        # Fetch and filter
        client = IntervalsClient('api_key', 'athlete_id')
        training_data = client.fetch_training_data(days_back=30)

        # Filter by activity type
        filtered_activities = [
            a for a in training_data['activities']
            if context.activity_type in a.get('type', '').lower()
        ]

        # Limit to activity count
        filtered_activities = filtered_activities[:context.activity_count]

        # Verify filtering
        self.assertLessEqual(len(filtered_activities), context.activity_count)
        for activity in filtered_activities:
            self.assertEqual(activity['type'], 'Run')

    def test_query_parsing_variations(self):
        """Test various query formats."""
        parser = QueryParser()

        test_cases = [
            ("How's my training this month?", 'range', 'month'),
            ("Analyze today's run", 'single_activity', 'today'),
            ("Compare my last 3 interval sessions", 'comparison', 'default'),
            ("What about my running this week?", 'range', 'week'),
            ("Show me my workouts from last month", 'range', 'month'),
        ]

        for query, expected_scope, expected_timeframe in test_cases:
            with self.subTest(query=query):
                context = parser.parse(query)
                self.assertEqual(context.scope, expected_scope)
                self.assertEqual(context.timeframe, expected_timeframe)


if __name__ == '__main__':
    unittest.main()
