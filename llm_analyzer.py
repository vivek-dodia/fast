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

        # Detect if this is a reasoning model
        self.is_reasoning_model = any(keyword in model.lower() for keyword in [
            'o1', 'o3', 'deepseek-r1', 'qwq', 'gemini-2.0-flash-thinking',
            'gemini-2.5-pro', 'reasoning'
        ])

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
        fitness_trends = data.get('fitness_trends', [])
        date_range = data['date_range']
        query_scope = data.get('query_scope', 'all activities')

        # Build the context string
        context = f"""# Training Data Analysis Context

## Analysis Scope
FOCUS: User is asking about **{query_scope}**
Data available: {date_range['start']} to {date_range['end']} ({date_range['days']} days)
Activities in focus: {len(activities)}

## Athlete Profile
"""

        # Athlete basic info
        context += f"- Athlete ID: {profile.get('id')}\n"
        context += f"- Name: {profile.get('name', 'N/A')}\n"
        context += f"- Sex: {profile.get('sex', 'N/A')}\n"

        # Physical metrics
        context += f"\n### Physical Metrics\n"
        context += f"- Weight: {self.format_value(profile.get('icu_weight'))} kg\n"
        context += f"- Resting HR: {self.format_value(profile.get('icu_resting_hr'))} bpm\n"
        if profile.get('icu_date_of_birth'):
            context += f"- DOB: {profile.get('icu_date_of_birth')}\n"

        # Current fitness metrics
        context += f"\n### Current Fitness Metrics (Latest)\n"
        if 'icu_ctl' in profile:
            context += f"- Fitness (CTL): {self.format_value(profile.get('icu_ctl'))}\n"
        elif 'ctl' in profile:
            context += f"- Fitness (CTL): {self.format_value(profile.get('ctl'))}\n"

        if 'icu_atl' in profile:
            context += f"- Fatigue (ATL): {self.format_value(profile.get('icu_atl'))}\n"
        elif 'atl' in profile:
            context += f"- Fatigue (ATL): {self.format_value(profile.get('atl'))}\n"

        # Calculate TSB from CTL/ATL
        ctl = profile.get('icu_ctl') or profile.get('ctl')
        atl = profile.get('icu_atl') or profile.get('atl')
        if ctl and atl:
            tsb = ctl - atl
            context += f"- Form (TSB): {tsb:+.1f}\n"

        # Sport-specific thresholds
        context += f"\n### Performance Thresholds\n"
        if 'icu_ftp' in profile and profile.get('icu_ftp'):
            context += f"- Cycling FTP: {self.format_value(profile.get('icu_ftp'))} watts\n"
        elif 'ftp' in profile and profile.get('ftp'):
            context += f"- Cycling FTP: {self.format_value(profile.get('ftp'))} watts\n"

        if 'icu_ftp_watts_per_kg' in profile and profile.get('icu_ftp_watts_per_kg'):
            context += f"- FTP per kg: {self.format_value(profile.get('icu_ftp_watts_per_kg'))} w/kg\n"

        if 'icu_pace' in profile and profile.get('icu_pace'):
            context += f"- Running Threshold Pace: {self.format_value(profile.get('icu_pace'))}\n"
        elif 'pace' in profile and profile.get('pace'):
            context += f"- Running Threshold Pace: {self.format_value(profile.get('pace'))}\n"

        if 'icu_lthr' in profile and profile.get('icu_lthr'):
            context += f"- Lactate Threshold HR: {self.format_value(profile.get('icu_lthr'))} bpm\n"
        elif 'lthr' in profile and profile.get('lthr'):
            context += f"- Lactate Threshold HR: {self.format_value(profile.get('lthr'))} bpm\n"

        # Fitness trends over time (if available)
        if fitness_trends and len(fitness_trends) > 0:
            context += f"\n### Fitness Trend (CTL/ATL/TSB over period)\n"
            # Show weekly snapshots
            weekly = [fitness_trends[i] for i in range(0, len(fitness_trends), 7)][-8:]  # Last 8 weeks
            for entry in weekly:
                date = entry.get('id', '')
                ctl_val = entry.get('ctl', 0)
                atl_val = entry.get('atl', 0)
                tsb_val = ctl_val - atl_val if ctl_val and atl_val else 0
                context += f"- {date}: CTL={ctl_val:.1f}, ATL={atl_val:.1f}, TSB={tsb_val:+.1f}\n"

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

            # Detailed activity list - limit to 10 most recent with key metrics only
            context += "\n### Recent Activities (Last 10):\n"
            for i, activity in enumerate(activities[:10], 1):  # Limit to 10 most recent
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

                # CTL/ATL/TSB at this point in time
                ctl = activity.get('icu_ctl')
                atl = activity.get('icu_atl')
                if ctl and atl:
                    tsb = ctl - atl
                    ramp = activity.get('icu_ramp_rate', 0)
                    context += f"   - Fitness/Fatigue after: CTL={ctl:.1f}, ATL={atl:.1f}, TSB={tsb:+.1f}"
                    if ramp:
                        context += f", Ramp={ramp:+.1f}"
                    context += "\n"

                # Polarization index (training intensity distribution)
                polarization = activity.get('polarization_index')
                if polarization:
                    context += f"   - Polarization Index: {polarization:.2f}\n"

                # Variability index (for power-based activities)
                vi = activity.get('icu_variability_index')
                if vi:
                    context += f"   - Variability Index: {vi:.2f}\n"

                # W' metrics for cycling
                w_prime_used = activity.get('icu_w_prime')
                w_prime_max = activity.get('icu_pm_w_prime') or activity.get('icu_rolling_w_prime')
                if w_prime_used and w_prime_max:
                    w_prime_pct = (w_prime_used / w_prime_max) * 100
                    context += f"   - W' Used: {w_prime_used:.0f}J / {w_prime_max:.0f}J ({w_prime_pct:.1f}%)\n"

                # Joules/Work
                joules = activity.get('icu_joules')
                if joules:
                    context += f"   - Total Work: {joules:.0f} kJ\n"

                joules_above_ftp = activity.get('icu_joules_above_ftp')
                if joules_above_ftp:
                    context += f"   - Work Above FTP: {joules_above_ftp:.0f} kJ\n"

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

    def filter_activities_by_query(self, activities: list, query: str) -> tuple:
        """
        Filter activities based on user query to focus analysis.

        Returns:
            (filtered_activities, focus_scope, scope_description)
        """
        from datetime import datetime, timedelta

        query_lower = query.lower()
        today = datetime.now().date()

        # Single activity queries with type filtering
        if any(word in query_lower for word in ['today', 'todays', "today's"]):
            today_activities = [a for a in activities if a.get('start_date_local', '')[:10] == today.isoformat()]

            # Check if specific activity type is mentioned
            if 'run' in query_lower:
                filtered = [a for a in today_activities if 'run' in a.get('type', '').lower()]
                return filtered, 'today_run', "today's run"
            elif 'ride' in query_lower or 'bike' in query_lower or 'cycle' in query_lower:
                filtered = [a for a in today_activities if 'ride' in a.get('type', '').lower()]
                return filtered, 'today_ride', "today's ride"
            elif 'workout' in query_lower:
                filtered = [a for a in today_activities if 'workout' in a.get('type', '').lower()]
                return filtered, 'today_workout', "today's workout"
            elif 'swim' in query_lower:
                filtered = [a for a in today_activities if 'swim' in a.get('type', '').lower()]
                return filtered, 'today_swim', "today's swim"
            else:
                return today_activities, 'today', "today's activities"

        if 'yesterday' in query_lower:
            yesterday = (today - timedelta(days=1)).isoformat()
            yesterday_activities = [a for a in activities if a.get('start_date_local', '')[:10] == yesterday]

            # Check if specific activity type is mentioned
            if 'run' in query_lower:
                filtered = [a for a in yesterday_activities if 'run' in a.get('type', '').lower()]
                return filtered, 'yesterday_run', "yesterday's run"
            elif 'ride' in query_lower or 'bike' in query_lower or 'cycle' in query_lower:
                filtered = [a for a in yesterday_activities if 'ride' in a.get('type', '').lower()]
                return filtered, 'yesterday_ride', "yesterday's ride"
            else:
                return yesterday_activities, 'yesterday', "yesterday's activities"

        if any(word in query_lower for word in ['latest', 'most recent', 'last workout', 'last run', 'last ride']):
            # Get the most recent activity of the mentioned type
            if 'run' in query_lower:
                filtered = [a for a in activities if 'run' in a.get('type', '').lower()][:1]
                return filtered, 'latest', "latest run"
            elif 'ride' in query_lower:
                filtered = [a for a in activities if 'ride' in a.get('type', '').lower()][:1]
                return filtered, 'latest', "latest ride"
            else:
                return activities[:1], 'latest', "latest activity"

        # Time range queries
        if 'this week' in query_lower:
            week_start = (today - timedelta(days=today.weekday())).isoformat()
            filtered = [a for a in activities if a.get('start_date_local', '')[:10] >= week_start]
            return filtered, 'week', "this week's activities"

        if 'last week' in query_lower:
            week_start = (today - timedelta(days=today.weekday() + 7)).isoformat()
            week_end = (today - timedelta(days=today.weekday() + 1)).isoformat()
            filtered = [a for a in activities
                       if week_start <= a.get('start_date_local', '')[:10] <= week_end]
            return filtered, 'last_week', "last week's activities"

        # Count-based queries
        import re
        match = re.search(r'last (\d+)', query_lower)
        if match and not any(word in query_lower for word in ['days', 'weeks', 'months']):
            count = int(match.group(1))
            if 'run' in query_lower:
                filtered = [a for a in activities if 'run' in a.get('type', '').lower()][:count]
                return filtered, 'count', f"last {count} runs"
            elif 'ride' in query_lower:
                filtered = [a for a in activities if 'ride' in a.get('type', '').lower()][:count]
                return filtered, 'count', f"last {count} rides"
            else:
                return activities[:count], 'count', f"last {count} activities"

        # Default: return all activities for general analysis
        return activities, 'all', "all activities"

    def analyze(self, training_data: Dict, user_query: str) -> str:
        """
        Analyze training data based on user's question.

        Args:
            training_data: Dictionary with profile, activities, wellness
            user_query: User's natural language question

        Returns:
            LLM's analysis response
        """
        # Filter activities based on query
        filtered_activities, scope, scope_desc = self.filter_activities_by_query(
            training_data['activities'],
            user_query
        )

        # Create a filtered copy of training data for focused analysis
        focused_data = training_data.copy()
        focused_data['activities'] = filtered_activities
        focused_data['query_scope'] = scope_desc

        # Format the training data
        context = self.format_training_data(focused_data)

        # Build the full prompt
        system_prompt = """You are an expert sports scientist and endurance coach providing detailed, specific training analysis.

CRITICAL: Be concise but complete. Use short, direct sentences. Avoid repetition and filler words.

IMPORTANT: Check "Analysis Scope" - if user asks about specific workout (e.g., "today's run"), focus ONLY on that. Use broader data for context only.

REQUIRED SECTIONS:

1. **Current Fitness State** (2-3 sentences max)
   - CTL/ATL/TSB interpretation + training trend

2. **Workout Analysis** (Focus workouts only - be concise)
   For each workout:
   - Stats: duration, distance, type
   - HR zones: "Z2: 32min, Z4: 8min" (time in each zone)
   - Purpose: endurance/tempo/intervals?
   - Key insight: what the data reveals (e.g., "HR drift = poor aerobic base")
   - 1-2 improvements

3. **Intensity Distribution**
   - Zone breakdown (% or time)
   - Polarization: 80/20 rule compliance?
   - Missing zones?

4. **Next Workouts** (Be VERY specific)
   - Type: "90min easy run"
   - HR targets: "60min Z2 (130-145bpm), 20min Z3 (145-155bpm)"
   - Focus: "Nasal breathing in Z2"
   - Avoid: "No Z4+ for 3 days"
   - WHY: Brief rationale (e.g., "builds mitochondrial density")

5. **7-Day Plan** (if general query)
   - Day-by-day: Recovery/Hard/Specific session
   - Brief (e.g., "Mon: 60min Z2 run, Tue: Rest, Wed: 4x5min Z4")

WRITING RULES:
- Short sentences. No fluff.
- Use numbers and data
- Reference dates/workouts specifically
- Give exact HR/pace targets
- Explain WHY concisely
- No verbose introductions/summaries

METRICS:
CTL=fitness(42d), ATL=fatigue(7d), TSB=form, Z2=base, Z4=threshold, Ramp>8=risky
"""

        user_prompt = f"""{context}

## User Question
{user_query}

Provide detailed, specific coaching analysis. Be concise but complete. Use short sentences and bullet points."""

        # Adjust parameters based on model type
        if self.is_reasoning_model:
            # Reasoning models need higher limits and different temperature
            max_completion_tokens = 6000  # Reduced from 8000 for more concise responses
            temperature = 1.0  # Reasoning models often work better at 1.0
            extra_params = {}
        else:
            max_completion_tokens = 2000  # Reduced from 2500 for conciseness
            temperature = 0.7
            extra_params = {}

        # Call OpenRouter API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_completion_tokens=max_completion_tokens,  # Use max_completion_tokens instead of max_tokens
                **extra_params
            )

            # Extract content from response
            content = response.choices[0].message.content

            # Check if response was cut off
            finish_reason = response.choices[0].finish_reason
            if finish_reason == 'length':
                content += "\n\n*[Response was truncated due to length. Try asking a more specific question.]*"

            return content

        except Exception as e:
            # Fallback with max_tokens if max_completion_tokens fails
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_completion_tokens
                )
                return response.choices[0].message.content
            except Exception as fallback_e:
                raise Exception(f"API Error: {str(e)}, Fallback Error: {str(fallback_e)}")
