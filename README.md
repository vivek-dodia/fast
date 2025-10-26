# Fast - Workout Analyzer CLI Tool

A Python CLI tool that fetches workout data from intervals.icu and provides intelligent analysis using AI through OpenRouter.

## Features

- Fetches training data directly from intervals.icu API
- AI-powered analysis using OpenRouter (supports multiple models)
- Analyzes fitness metrics, training load, and performance trends
- Natural language queries - just ask questions in plain English
- Fast and lightweight - no local database needed

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure credentials

Copy the example environment file and add your credentials:

```bash
cp .env.example .env
```

Then edit `.env` with your credentials:

```
INTERVALS_API=your_intervals_api_key
ATHLETE_ID=your_athlete_id
OPENROUTER=your_openrouter_api_key
OPENROUTER_MODEL=google/gemini-2.5-flash
```

**Where to get credentials:**
- **intervals.icu**: Log in → Settings → API Key
- **OpenRouter**: https://openrouter.ai (sign up for API access)

### 3. Run setup check

```bash
python fast.py --setup
```

## Usage

### Basic Usage

```bash
python fast.py "your question here"
```

### Examples

```bash
# General training analysis
python fast.py "How's my training this month?"

# Specific activity analysis
python fast.py "Analyze my last 5 runs"

# Fitness metrics
python fast.py "What's my current fitness level?"

# Performance trends
python fast.py "Compare my interval sessions this week"

# Training advice
python fast.py "What should I focus on to improve my 10K time?"

# Recovery check
python fast.py "Am I overtraining?"
```

### Advanced Options

```bash
# Look back more days (default is 30)
python fast.py --days 60 "Compare my fitness over the last 2 months"

# Look back 90 days
python fast.py --days 90 "Show my training volume trends"
```

## How It Works

1. **Fetches Data**: Retrieves your training data from intervals.icu (today + last 30 days by default)
2. **Formats Context**: Structures the data including:
   - Athlete profile (fitness, fatigue, form)
   - Recent activities with metrics
   - Wellness data (if available)
3. **AI Analysis**: Sends the data + your question to OpenRouter's AI
4. **Smart Insights**: Returns actionable analysis and recommendations

## Data Fetched

The tool fetches:
- **Athlete Profile**: CTL, ATL, TSB, FTP, threshold pace
- **Activities**: Distance, duration, heart rate, power, training load
- **Activity Types**: Runs, rides, swims, etc.
- **Wellness Data**: Optional recovery metrics

## Understanding Metrics

- **CTL (Chronic Training Load / Fitness)**: 42-day weighted average of training load - your fitness level
- **ATL (Acute Training Load / Fatigue)**: 7-day weighted average - recent training stress
- **TSB (Training Stress Balance / Form)**: CTL - ATL
  - Positive TSB = Fresh/recovered
  - Negative TSB = Fatigued
- **Training Load**: Workout stress score (similar to TSS)
- **FTP**: Functional Threshold Power (cycling)
- **Threshold Pace**: Running pace at lactate threshold

## Project Structure

```
fast/
├── fast.py                  # Main CLI script
├── config.py                # Configuration loader
├── intervals_client.py      # intervals.icu API client
├── llm_analyzer.py          # OpenRouter/LLM integration
├── requirements.txt         # Python dependencies
├── .env                     # Your credentials (not in git)
└── README.md               # This file
```

## Tips

- **Be specific**: "Analyze my last 3 interval workouts" works better than "analyze my training"
- **Ask for advice**: "What should I focus on?" gets recommendations
- **Compare periods**: Use `--days` to look at longer trends
- **Check recovery**: Ask about overtraining, fatigue, or form

## Cost

- intervals.icu: Free API access for premium members
- OpenRouter: Pay-per-use (~$0.01-0.03 per query with Gemini Flash)

## Troubleshooting

### Configuration errors
```bash
python fast.py --setup
```

### Missing credentials
Check your `.env` file has all required fields

### API errors
- Verify your intervals.icu API key is valid
- Check your athlete ID is correct
- Ensure OpenRouter API key is active

### Debug mode
```bash
python fast.py "query" --debug
```

## Future Enhancements

- Activity type filtering (runs only, rides only)
- Date range parsing ("last week", "January")
- Export analysis to file
- Interactive REPL mode
- Wellness data integration
- Power curve analysis

## License

MIT

## Repository

https://github.com/vivek-dodia/fast
