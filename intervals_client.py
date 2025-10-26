"""Client for interacting with intervals.icu API."""
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import Config


class IntervalsClient:
    """Client for fetching data from intervals.icu API."""

    def __init__(self, api_key: str, athlete_id: str):
        self.api_key = api_key
        self.athlete_id = athlete_id
        self.base_url = Config.INTERVALS_BASE_URL
        self.session = requests.Session()
        # intervals.icu uses 'API_KEY' as username and the actual API key as password
        self.session.auth = HTTPBasicAuth('API_KEY', api_key)
        self.session.headers.update({
            'User-Agent': 'Fast-Workout-Analyzer/1.0'
        })

    def get_athlete_profile(self) -> Dict:
        """Fetch athlete profile including current fitness metrics."""
        url = f"{self.base_url}/athlete/{self.athlete_id}"
        response = self.session.get(url)

        if response.status_code == 403:
            raise Exception(
                f"Authentication failed (403 Forbidden). "
                f"Please check your INTERVALS_API key and ATHLETE_ID in .env file. "
                f"Attempted to access: {url}"
            )

        response.raise_for_status()
        return response.json()

    def get_activities(
        self,
        oldest: Optional[str] = None,
        newest: Optional[str] = None
    ) -> List[Dict]:
        """
        Fetch activities for a date range.

        Args:
            oldest: Start date in YYYY-MM-DD format
            newest: End date in YYYY-MM-DD format

        Returns:
            List of activity dictionaries
        """
        url = f"{self.base_url}/athlete/{self.athlete_id}/activities"
        params = {}

        if oldest:
            params['oldest'] = oldest
        if newest:
            params['newest'] = newest

        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_activity_detail(self, activity_id: int) -> Dict:
        """Fetch detailed information for a single activity."""
        url = f"{self.base_url}/activity/{activity_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_wellness_data(
        self,
        oldest: Optional[str] = None,
        newest: Optional[str] = None
    ) -> List[Dict]:
        """Fetch wellness data for a date range."""
        url = f"{self.base_url}/athlete/{self.athlete_id}/wellness.json"
        params = {}

        if oldest:
            params['oldest'] = oldest
        if newest:
            params['newest'] = newest

        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def fetch_training_data(self, days_back: int = 30) -> Dict:
        """
        Fetch comprehensive training data for analysis.

        Args:
            days_back: Number of days to look back from today

        Returns:
            Dictionary containing athlete profile, activities, and wellness data
        """
        # Calculate date range
        today = datetime.now().date()
        start_date = today - timedelta(days=days_back)

        oldest_str = start_date.isoformat()
        newest_str = today.isoformat()

        # Fetch all data
        profile = self.get_athlete_profile()
        activities = self.get_activities(oldest=oldest_str, newest=newest_str)

        # Try to get wellness data (optional, may not be available)
        try:
            wellness = self.get_wellness_data(oldest=oldest_str, newest=newest_str)
        except Exception:
            wellness = []

        return {
            'profile': profile,
            'activities': activities,
            'wellness': wellness,
            'date_range': {
                'start': oldest_str,
                'end': newest_str,
                'days': days_back
            }
        }
