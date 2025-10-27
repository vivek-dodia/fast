# intervals.icu API - Raw Data Fields

This document describes all the raw data fields we receive from the intervals.icu API.

## Athlete Profile Data

### Basic Info
- `id` - Athlete ID
- `name`, `firstname`, `lastname` - Athlete name
- `email` - Email address
- `sex` - Gender (M/F)
- `city`, `state`, `country` - Location
- `timezone` - Timezone
- `locale` - Language preference

### Physical Metrics
- `icu_weight` - Current weight (kg)
- `weight` - Manual weight entry
- `icu_resting_hr` - Resting heart rate
- `icu_date_of_birth` - Date of birth

### Fitness Metrics
- `icu_atl` - Acute Training Load (7-day fatigue)
- `icu_ctl` - Chronic Training Load (42-day fitness)
- `icu_form_as_percent` - Form/TSB display preference
- `icu_mmp_days` - Mean maximal power calculation days (default 90)

### Preferences
- `measurement_preference` - feet/meters
- `weight_pref_lb` - Use pounds for weight
- `fahrenheit` - Temperature preference
- `wind_speed` - Wind speed units (MPH/KMH)
- `rain` - Rainfall units (INCHES/MM)

### Equipment
- `bikes` - List of bikes
- `shoes` - List of running shoes
- `gear` - Current gear

### Settings
- `visibility` - Profile visibility (PRIVATE/PUBLIC)
- `icu_type_settings` - Activity type specific settings
- `icu_wellness_prompt` - Wellness data prompts enabled
- `icu_track_menstrual_cycle` - Menstrual cycle tracking
- `icu_garmin_*` - Garmin integration settings
- `polar_*` - Polar integration settings

### API
- `icu_api_key` - Your API key
- `icu_permission` - API permission level (WRITE/READ)

---

## Activity Data (Per Activity)

### Basic Activity Info
- `id` - Activity ID (e.g., "i103914809")
- `name` - Activity name
- `description` - Activity description
- `type` - Activity type (Run, Ride, Swim, Workout, WeightTraining, etc.)
- `sub_type` - Sub-type if applicable
- `start_date` - Start date/time UTC
- `start_date_local` - Start date/time in local timezone
- `created` - When activity was created
- `analyzed` - When activity was analyzed

### Time Metrics
- `elapsed_time` - Total elapsed time (seconds)
- `moving_time` - Moving time (seconds)
- `icu_recording_time` - Recording time (seconds)
- `coasting_time` - Coasting time (seconds)
- `icu_warmup_time` - Warmup time (seconds)
- `icu_cooldown_time` - Cooldown time (seconds)

### Distance & Speed
- `distance` - Distance (meters)
- `icu_distance` - ICU calculated distance
- `max_speed` - Maximum speed
- `average_speed` - Average speed
- `pace` - Pace
- `threshold_pace` - Threshold pace
- `gap` - Grade adjusted pace
- `gap_model` - GAP calculation model

### Heart Rate
- `has_heartrate` - Has HR data (boolean)
- `max_heartrate` - Maximum HR
- `average_heartrate` - Average HR
- `lthr` - Lactate threshold heart rate
- `icu_resting_hr` - Resting HR at time of activity
- `athlete_max_hr` - Athlete's max HR
- `icu_hr_zones` - HR zones array [Z1, Z2, Z3, Z4, Z5, Z6, Z7]
- `icu_hr_zone_times` - Time in each HR zone (seconds)
- `icu_hrr` - Heart rate reserve

### Power (Cycling)
- `device_watts` - Device reported watts
- `icu_average_watts` - ICU calculated average watts
- `icu_weighted_avg_watts` - Normalized power
- `icu_ftp` - FTP at time of activity
- `icu_pm_ftp` - Power meter FTP
- `icu_rolling_ftp` - Rolling FTP estimate
- `p_max` - Max power
- `icu_pm_p_max` - Power meter max power
- `icu_power_zones` - Power zones
- `icu_sweet_spot_min/max` - Sweet spot range
- `icu_power_spike_threshold` - Power spike threshold
- `icu_joules` - Total work (joules)
- `icu_joules_above_ftp` - Work above FTP
- `icu_variability_index` - Variability index (VI)
- `power_field` - Power field used
- `power_meter` - Power meter name
- `power_meter_serial` - Power meter serial
- `power_meter_battery` - Power meter battery level

### Critical Power Model
- `icu_pm_cp` - Critical Power
- `icu_pm_w_prime` - W' (work capacity above CP)
- `icu_rolling_cp` - Rolling CP estimate
- `icu_rolling_w_prime` - Rolling W' estimate
- `icu_w_prime` - W' used
- `icu_max_wbal_depletion` - Max W' depletion
- `ss_cp`, `ss_w_prime`, `ss_p_max` - Session CP model values

### Training Load
- `icu_training_load` - Training load/stress score
- `icu_atl` - Acute Training Load (at this point)
- `icu_ctl` - Chronic Training Load (at this point)
- `trimp` - TRIMP score
- `icu_intensity` - Intensity factor
- `session_rpe` - Session RPE
- `power_load`, `hr_load`, `pace_load` - Load by metric
- `strain_score` - Strain score

### Cadence & Stride
- `average_cadence` - Average cadence (RPM or steps/min)
- `average_stride` - Average stride length
- `icu_cadence_z2` - Cadence in zone 2

### Elevation
- `total_elevation_gain` - Total elevation gain
- `total_elevation_loss` - Total elevation loss
- `average_altitude` - Average altitude
- `min_altitude` - Minimum altitude
- `max_altitude` - Maximum altitude
- `use_elevation_correction` - Use elevation correction

### Other Metrics
- `calories` - Calories burned
- `carbs_used` - Carbs used (calculated)
- `carbs_ingested` - Carbs ingested
- `average_temp` - Average temperature
- `min_temp`, `max_temp` - Temperature range
- `kg_lifted` - Weight lifted (strength training)
- `lengths` - Pool lengths (swimming)
- `pool_length` - Pool length

### Zones & Time in Zone
- `icu_zone_times` - Power zone times
- `icu_hr_zone_times` - HR zone times (array)
- `pace_zone_times` - Pace zone times
- `gap_zone_times` - GAP zone times
- `pace_zones` - Pace zones definition
- `tiz_order` - Time in zone order
- `polarization_index` - Polarization index

### Analysis Metrics
- `icu_power_hr_z2` - Power/HR decoupling in Z2
- `icu_power_hr_z2_mins` - Minutes in Z2 for decoupling
- `icu_power_hr` - Power/HR ratio
- `decoupling` - Aerobic decoupling percentage
- `icu_efficiency_factor` - Efficiency factor
- `icu_median_time_delta` - Median time between recordings
- `p30s_exponent` - 30s power exponent

### Intervals
- `interval_summary` - Summary of intervals (e.g., "1x 36m2s 108bpm")
- `icu_intervals_edited` - Intervals manually edited
- `lock_intervals` - Intervals locked
- `icu_lap_count` - Lap count

### Device & Source
- `device_name` - Device name (e.g., "Amazfit Helio Strap")
- `file_type` - File type (fit, tcx, gpx)
- `file_sport_index` - Sport index in file
- `external_id` - External ID
- `source` - Data source
- `oauth_client_id` - OAuth client
- `oauth_client_name` - OAuth client name
- `strava_id` - Strava ID if synced

### Flags & Settings
- `trainer` - Indoor trainer (boolean)
- `commute` - Commute activity
- `race` - Race activity
- `icu_ignore_time` - Ignore time in calculations
- `icu_ignore_power` - Ignore power data
- `icu_ignore_hr` - Ignore HR data
- `ignore_velocity` - Ignore velocity
- `ignore_pace` - Ignore pace
- `ignore_parts` - Parts to ignore

### Weather
- `has_weather` - Has weather data
- `average_weather_temp` - Average weather temp
- `min_weather_temp`, `max_weather_temp` - Weather temp range
- `average_feels_like` - Feels like temperature
- `min_feels_like`, `max_feels_like` - Feels like range
- `average_wind_speed` - Average wind speed
- `average_wind_gust` - Average wind gust
- `prevailing_wind_deg` - Prevailing wind direction
- `headwind_percent` - Headwind percentage
- `tailwind_percent` - Tailwind percentage
- `average_clouds` - Cloud cover
- `max_rain` - Max rainfall
- `max_snow` - Max snowfall

### Stream Data (Time-Series)
- `stream_types` - Available stream types (e.g., ["time", "heartrate"])
  - Possible streams: time, heartrate, watts, cadence, altitude, latlng, velocity_smooth, distance, etc.
- `skyline_chart_bytes` - Compressed chart data
- `has_segments` - Has Strava segments

### Miscellaneous
- `perceived_exertion` - Perceived exertion (RPE)
- `icu_rpe` - ICU RPE
- `feel` - How did you feel
- `compliance` - Workout compliance
- `coach_tick` - Coach tick/approval
- `tags` - Activity tags
- `attachments` - File attachments
- `group` - Activity group
- `route_id` - Route ID
- `paired_event_id` - Paired event ID
- `icu_chat_id` - Chat ID
- `icu_color` - Activity color
- `icu_achievements` - Achievements unlocked
- `icu_sync_date` - Last sync date
- `icu_sync_error` - Sync error if any
- `recording_stops` - Recording stops count
- `workout_shift_secs` - Workout time shift

---

## What We're Currently Using

In our current implementation (`llm_analyzer.py`), we use:

### From Profile:
- `ctl` - Fitness
- `atl` - Fatigue
- `rampRate` - Form (Note: This might be TSB, need to verify)
- `ftp` - Cycling FTP
- `ftpWattsPerKg` - FTP per kg
- `pace` - Running threshold pace

### From Activities:
- `type` - Activity type
- `name` - Activity name
- `start_date_local` - Date
- `distance` - Distance
- `moving_time` - Duration
- `average_hr`, `max_hr` - Heart rate
- `average_watts` - Power
- `icu_training_load` - Training load

## Additional Useful Fields We Could Add

### High Value:
- `icu_power_hr_z2` - Decoupling (aerobic efficiency indicator)
- `decoupling` - Aerobic decoupling percentage
- `icu_efficiency_factor` - Efficiency factor
- `icu_hr_zone_times` - Time in HR zones (training distribution)
- `interval_summary` - Auto-detected intervals
- `perceived_exertion` / `feel` - RPE and subjective feel
- `icu_intensity` - Intensity factor
- `average_cadence` - Cadence

### Moderate Value:
- `total_elevation_gain` - Elevation gain
- `weather_*` - Weather conditions
- `trimp` - TRIMP score
- `icu_variability_index` - Variability index
- `session_rpe` - Session RPE

### Advanced Analysis:
- `icu_w_prime` - W' depletion
- `polarization_index` - Training polarization
- `icu_joules_above_ftp` - Work above FTP
- Complete stream data for detailed analysis
