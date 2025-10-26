"""LLM integration for workout analysis using OpenRouter."""
from openai import OpenAI
from typing import Dict, Any, Optional
from config import Config


class LLMAnalyzer:
    """Analyzes workout data using LLM via OpenRouter."""

    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.model = model

    def format_value(self, value: Any) -> str:
        """Format a value for display, handling None values."""
        if value is None:
            return "N/A"
        if isinstance(value, float):
            return f"{value:.2f}"
        if isinstance(value, list):
            return ", ".join(str(v) for v in value)
        return str(value)

    def format_duration(self, seconds: Optional[int]) -> str:
        """Format seconds into human readable duration."""
        if seconds is None:
            return "N/A"
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

    def format_distance(self, meters: Optional[float]) -> str:
        """Format meters into km."""
        if meters is None or meters == 0:
            return "N/A"
        return f"{meters / 1000:.2f} km"

    def format_hr_zones(self, zone_times: Optional[list]) -> str:
        """Format time in HR zones."""
        if not zone_times:
            return "N/A"
        zones = []
        zone_names = ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6", "Z7"]
        for i, time_secs in enumerate(zone_times):
            if time_secs and time_secs > 0:
                zones.append(f"{zone_names[i]}: {self.format_duration(time_secs)}")
        return " | ".join(zones) if zones else "N/A"

    def format_training_data(self, data: Dict) -> str:
        """
        Format ALL training data into a comprehensive prompt for the LLM.

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

        # Athlete basic info
        context += f"- Athlete ID: {profile.get('id')}\n"
        context += f"- Name: {profile.get('name', 'N/A')}\n"
        context += f"- Location: {profile.get('city', 'N/A')}, {profile.get('state', 'N/A')}, {profile.get('country', 'N/A')}\n"
        context += f"- Sex: {profile.get('sex', 'N/A')}\n"

        # Physical metrics
        context += f"\n### Physical Metrics\n"
        context += f"- Weight: {self.format_value(profile.get('icu_weight'))} kg\n"
        context += f"- Resting HR: {self.format_value(profile.get('icu_resting_hr'))} bpm\n"

        # Fitness metrics (if available)
        context += f"\n### Fitness Metrics\n"
        if 'ctl' in profile:
            context += f"- Fitness (CTL): {self.format_value(profile.get('ctl'))}\n"
        if 'atl' in profile:
            context += f"- Fatigue (ATL): {self.format_value(profile.get('atl'))}\n"
        if 'tsb' in profile or 'rampRate' in profile:
            tsb = profile.get('tsb') or profile.get('rampRate')
            context += f"- Form (TSB): {self.format_value(tsb)}\n"

        # Sport-specific thresholds
        context += f"\n### Performance Thresholds\n"
        if 'ftp' in profile and profile.get('ftp'):
            context += f"- Cycling FTP: {self.format_value(profile.get('ftp'))} watts\n"
        if 'ftpWattsPerKg' in profile and profile.get('ftpWattsPerKg'):
            context += f"- FTP per kg: {self.format_value(profile.get('ftpWattsPerKg'))} w/kg\n"
        if 'pace' in profile and profile.get('pace'):
            context += f"- Running Threshold Pace: {self.format_value(profile.get('pace'))}\n"
        if 'lthr' in profile and profile.get('lthr'):
            context += f"- Lactate Threshold HR: {self.format_value(profile.get('lthr'))} bpm\n"

        # Activity summary
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
                total_distance = sum(a.get('distance', 0) or 0 for a in acts) / 1000
                total_time = sum(a.get('moving_time', 0) or 0 for a in acts) / 3600
                total_load = sum(a.get('icu_training_load', 0) or 0 for a in acts)
                context += f"- {act_type}: {len(acts)} activities | "
                if total_distance > 0:
                    context += f"{total_distance:.1f} km | "
                context += f"{total_time:.1f} hrs | Load: {total_load:.0f}\n"

            # Detailed activity list with ALL available metrics
            context += "\n### Detailed Activity Data:\n"
            for i, activity in enumerate(activities[:20], 1):  # Limit to 20 most recent
                name = activity.get('name', 'Unnamed')
                act_type = activity.get('type', 'Unknown')
                date = activity.get('start_date_local', 'Unknown date')[:10]

                context += f"\n**{i}. {name}** ({act_type}) - {date}\n"

                # Basic metrics
                distance = activity.get('distance') or activity.get('icu_distance')
                if distance:
                    context += f"   - Distance: {self.format_distance(distance)}\n"

                moving_time = activity.get('moving_time')
                if moving_time:
                    context += f"   - Duration: {self.format_duration(moving_time)}\n"

                elapsed_time = activity.get('elapsed_time')
                if elapsed_time and moving_time and elapsed_time > moving_time:
                    context += f"   - Elapsed Time: {self.format_duration(elapsed_time)}\n"

                # Heart rate metrics
                avg_hr = activity.get('average_heartrate')
                max_hr = activity.get('max_heartrate')
                if avg_hr:
                    context += f"   - Avg HR: {avg_hr:.0f} bpm"
                    if max_hr:
                        context += f" (Max: {max_hr:.0f} bpm)"
                    context += "\n"

                # HR zones
                hr_zone_times = activity.get('icu_hr_zone_times')
                if hr_zone_times:
                    context += f"   - HR Zones: {self.format_hr_zones(hr_zone_times)}\n"

                # Power metrics
                avg_watts = activity.get('average_watts') or activity.get('icu_average_watts')
                weighted_watts = activity.get('icu_weighted_avg_watts')
                if avg_watts:
                    context += f"   - Avg Power: {avg_watts:.0f} watts"
                    if weighted_watts:
                        context += f" (Normalized: {weighted_watts:.0f} watts)"
                    context += "\n"

                # FTP and intensity
                activity_ftp = activity.get('icu_ftp')
                if activity_ftp:
                    context += f"   - FTP at time: {activity_ftp:.0f} watts\n"

                intensity = activity.get('icu_intensity')
                if intensity:
                    context += f"   - Intensity Factor: {intensity:.2f}\n"

                # Pace metrics
                pace = activity.get('pace')
                if pace:
                    context += f"   - Pace: {self.format_value(pace)}\n"

                avg_speed = activity.get('average_speed')
                if avg_speed:
                    context += f"   - Avg Speed: {avg_speed:.2f} m/s\n"

                # Cadence
                avg_cadence = activity.get('average_cadence')
                if avg_cadence and avg_cadence > 0:
                    context += f"   - Avg Cadence: {avg_cadence:.0f}\n"

                # Elevation
                elevation_gain = activity.get('total_elevation_gain')
                if elevation_gain:
                    context += f"   - Elevation Gain: {elevation_gain:.0f} m\n"

                # Training load
                training_load = activity.get('icu_training_load')
                if training_load:
                    context += f"   - Training Load: {training_load:.0f}\n"

                trimp = activity.get('trimp')
                if trimp:
                    context += f"   - TRIMP: {trimp:.0f}\n"

                # Efficiency metrics
                efficiency_factor = activity.get('icu_efficiency_factor')
                if efficiency_factor:
                    context += f"   - Efficiency Factor: {efficiency_factor:.2f}\n"

                decoupling = activity.get('decoupling')
                if decoupling:
                    context += f"   - Aerobic Decoupling: {decoupling:.1f}%\n"

                power_hr_z2 = activity.get('icu_power_hr_z2')
                if power_hr_z2:
                    context += f"   - Power/HR Z2: {power_hr_z2:.2f}\n"

                # Intervals
                interval_summary = activity.get('interval_summary')
                if interval_summary:
                    context += f"   - Intervals: {', '.join(interval_summary)}\n"

                # Feel/RPE
                feel = activity.get('feel')
                if feel:
                    context += f"   - Feel: {feel}\n"

                perceived_exertion = activity.get('perceived_exertion')
                if perceived_exertion:
                    context += f"   - RPE: {perceived_exertion}\n"

                session_rpe = activity.get('session_rpe')
                if session_rpe:
                    context += f"   - Session RPE: {session_rpe}\n"

                # Calories
                calories = activity.get('calories')
                if calories:
                    context += f"   - Calories: {calories:.0f}\n"

                # Weather (if available)
                if activity.get('has_weather'):
                    weather_temp = activity.get('average_weather_temp')
                    wind_speed = activity.get('average_wind_speed')
                    if weather_temp or wind_speed:
                        context += f"   - Weather: "
                        if weather_temp:
                            context += f"Temp: {weather_temp:.1f}°C"
                        if wind_speed:
                            context += f" Wind: {wind_speed:.1f} m/s"
                        context += "\n"

                # Device
                device = activity.get('device_name')
                if device:
                    context += f"   - Device: {device}\n"

                # Power meter
                power_meter = activity.get('power_meter')
                if power_meter:
                    context += f"   - Power Meter: {power_meter}\n"

                # CTL/ATL at this point
                ctl = activity.get('icu_ctl')
                atl = activity.get('icu_atl')
                if ctl or atl:
                    context += f"   - Fitness/Fatigue after: "
                    if ctl:
                        context += f"CTL: {ctl:.1f}"
                    if atl:
                        context += f" ATL: {atl:.1f}"
                    context += "\n"

        # Add wellness data if available
        if wellness and len(wellness) > 0:
            context += f"\n## Wellness Data\n"
            context += f"Records available: {len(wellness)}\n"
            context += "\nRecent wellness entries:\n"
            for i, entry in enumerate(wellness[:7], 1):  # Last 7 days
                date = entry.get('id', 'Unknown')
                context += f"{i}. {date}: "
                metrics = []
                for key, value in entry.items():
                    if key != 'id' and value is not None:
                        metrics.append(f"{key}: {value}")
                context += ", ".join(metrics) if metrics else "No data"
                context += "\n"

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
- Look for trends and patterns across all available metrics
- Consider training load, intensity distribution, and recovery
- Analyze heart rate zones and time distribution
- Evaluate power metrics, normalized power, and intensity factor
- Check for aerobic decoupling and efficiency factors
- Review intervals and workout structure
- Consider subjective metrics like RPE and feel
- Reference specific workouts when relevant
- Provide practical recommendations
- Be concise but thorough

Key metrics explained:
- CTL (Chronic Training Load / Fitness): 42-day weighted average of training load
- ATL (Acute Training Load / Fatigue): 7-day weighted average of training load
- TSB (Training Stress Balance / Form): CTL - ATL (positive = fresh, negative = fatigued)
- Training Load: Measure of workout stress (similar to TSS)
- TRIMP: Heart rate based training impulse
- Intensity Factor: Ratio of normalized power to FTP (or similar for HR/pace)
- Decoupling: HR drift relative to power/pace (>5% suggests aerobic deficiency or fatigue)
- Efficiency Factor: Power or pace divided by heart rate (higher = better aerobic fitness)
- Normalized Power: Weighted average power accounting for variability
- eFTP: Estimated functional threshold power
- HR Zones: Z1 (recovery), Z2 (aerobic base), Z3 (tempo), Z4 (threshold), Z5+ (VO2max/anaerobic)
- RPE: Rate of Perceived Exertion (1-10 scale)
- Session RPE: Overall session difficulty rating
"""

        user_prompt = f"""{context}

## User Question
{user_query}

Please analyze the data thoroughly and provide insights."""

        # Call OpenRouter API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=4000  # Increased for more detailed responses
        )

        return response.choices[0].message.content
