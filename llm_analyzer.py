"""LLM integration for workout analysis using OpenRouter."""
from openai import OpenAI
from typing import Dict
from config import Config


class LLMAnalyzer:
    """Analyzes workout data using LLM via OpenRouter."""

    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.model = model

    def format_training_data(self, data: Dict) -> str:
        """
        Format training data into a clear, structured prompt for the LLM.

        Args:
            data: Dictionary containing profile, activities, wellness data

        Returns:
            Formatted string for LLM analysis
        """
        profile = data['profile']
        activities = data['activities']
        wellness = data['wellness']
        date_range = data['date_range']

        # Build the context string
        context = f"""# Training Data Analysis Context

## Date Range
Analyzing data from {date_range['start']} to {date_range['end']} ({date_range['days']} days)

## Athlete Profile
"""

        # Add athlete fitness metrics if available
        if 'ctl' in profile:
            context += f"- Fitness (CTL): {profile.get('ctl', 'N/A')}\n"
        if 'atl' in profile:
            context += f"- Fatigue (ATL): {profile.get('atl', 'N/A')}\n"
        if 'rampRate' in profile:
            context += f"- Form (TSB): {profile.get('rampRate', 'N/A')}\n"

        # Add sport-specific thresholds
        if 'ftp' in profile:
            context += f"- Cycling FTP: {profile.get('ftp', 'N/A')} watts\n"
        if 'ftpWattsPerKg' in profile:
            context += f"- FTP per kg: {profile.get('ftpWattsPerKg', 'N/A')} w/kg\n"
        if 'pace' in profile:
            context += f"- Running Threshold Pace: {profile.get('pace', 'N/A')}\n"

        # Add activity summary
        context += f"\n## Activities Summary\n"
        context += f"Total activities in period: {len(activities)}\n\n"

        if activities:
            # Group by type
            activity_types = {}
            for activity in activities:
                act_type = activity.get('type', 'Unknown')
                if act_type not in activity_types:
                    activity_types[act_type] = []
                activity_types[act_type].append(activity)

            context += "### Activities by Type:\n"
            for act_type, acts in activity_types.items():
                context += f"- {act_type}: {len(acts)} activities\n"

            # Detailed activity list
            context += "\n### Recent Activities:\n"
            for i, activity in enumerate(activities[:15], 1):  # Limit to 15 most recent
                name = activity.get('name', 'Unnamed')
                act_type = activity.get('type', 'Unknown')
                date = activity.get('start_date_local', 'Unknown date')[:10]

                # Extract key metrics
                distance = activity.get('distance', 0)
                distance_km = distance / 1000 if distance else 0

                moving_time = activity.get('moving_time', 0)
                moving_hours = moving_time / 3600 if moving_time else 0

                avg_hr = activity.get('average_hr')
                max_hr = activity.get('max_hr')
                avg_watts = activity.get('average_watts')
                training_load = activity.get('icu_training_load')

                context += f"\n{i}. **{name}** ({act_type}) - {date}\n"

                if distance_km > 0:
                    context += f"   - Distance: {distance_km:.2f} km\n"
                if moving_hours > 0:
                    context += f"   - Duration: {moving_hours:.2f} hours\n"
                if avg_hr:
                    context += f"   - Avg HR: {avg_hr} bpm"
                    if max_hr:
                        context += f" (Max: {max_hr} bpm)"
                    context += "\n"
                if avg_watts:
                    context += f"   - Avg Power: {avg_watts} watts\n"
                if training_load:
                    context += f"   - Training Load: {training_load}\n"

        # Add wellness data if available
        if wellness and len(wellness) > 0:
            context += f"\n## Wellness Data\n"
            context += f"Records available: {len(wellness)}\n"
            # You can add more wellness details here if needed

        return context

    def analyze(self, training_data: Dict, user_query: str) -> str:
        """
        Analyze training data based on user's question.

        Args:
            training_data: Dictionary with profile, activities, wellness
            user_query: User's natural language question

        Returns:
            LLM's analysis response
        """
        # Format the training data
        context = self.format_training_data(training_data)

        # Build the full prompt
        system_prompt = """You are an expert sports scientist and coach analyzing an athlete's training data from intervals.icu.

Provide clear, actionable insights based on the data. When analyzing:
- Look for trends and patterns
- Consider training load, intensity distribution, and recovery
- Reference specific workouts when relevant
- Provide practical recommendations
- Be concise but thorough

Key metrics explained:
- CTL (Chronic Training Load / Fitness): 42-day weighted average of training load
- ATL (Acute Training Load / Fatigue): 7-day weighted average of training load
- TSB (Training Stress Balance / Form): CTL - ATL (positive = fresh, negative = fatigued)
- Training Load: Measure of workout stress (similar to TSS)
- Decoupling: HR drift relative to power/pace (>5% suggests aerobic deficiency)
- eFTP: Estimated functional threshold power
"""

        user_prompt = f"""{context}

## User Question
{user_query}

Please analyze the data and provide insights."""

        # Call OpenRouter API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        return response.choices[0].message.content
