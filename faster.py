#!/usr/bin/env python3
"""
Faster
Fetches data from intervals.icu and analyzes it using LLM via OpenRouter.
"""
import sys
import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from config import Config
from intervals_client import IntervalsClient
from llm_analyzer import LLMAnalyzer

# Use safe_box=True for Windows compatibility
console = Console(force_terminal=True, legacy_windows=False)


@click.command()
@click.argument('query', required=False)
@click.option('--days', default=30, help='Number of days to look back (default: 30)')
@click.option('--setup', is_flag=True, help='Show setup instructions')
def main(query, days, setup):
    """
    Faster

    Fetches your training data from intervals.icu and analyzes it using AI.

    Examples:
        faster "How's my training this month?"
        faster "Analyze my last 5 runs"
        faster "What should I focus on this week?"
        faster --days 60 "Compare my fitness trends"
    """
    if setup:
        show_setup_instructions()
        return

    if not query:
        console.print("[yellow]No query provided. Usage:[/yellow]")
        console.print("  faster \"your question here\"")
        console.print("\nExamples:")
        console.print("  faster \"How's my training this month?\"")
        console.print("  faster \"Analyze my last 5 runs\"")
        console.print("  faster --days 60 \"Compare my fitness trends\"")
        console.print("\nFor setup help: faster --setup")
        return

    try:
        # Validate configuration
        console.print("[cyan]Validating configuration...[/cyan]")
        Config.validate()

        # Initialize clients
        intervals_client = IntervalsClient(
            api_key=Config.INTERVALS_API_KEY,
            athlete_id=Config.ATHLETE_ID
        )

        analyzer = LLMAnalyzer(
            api_key=Config.OPENROUTER_API_KEY,
            model=Config.OPENROUTER_MODEL
        )

        # Fetch training data
        console.print(f"[cyan]Fetching training data from intervals.icu (last {days} days)...[/cyan]")
        training_data = intervals_client.fetch_training_data(days_back=days)

        activity_count = len(training_data['activities'])
        console.print(f"[green]OK[/green] Fetched {activity_count} activities")

        # Analyze with LLM
        model_name = Config.OPENROUTER_MODEL
        is_reasoning = analyzer.is_reasoning_model
        model_type = "[magenta](reasoning mode)[/magenta]" if is_reasoning else ""
        console.print(f"[cyan]Analyzing with {model_name}[/cyan] {model_type}")

        # Show what we're analyzing
        _, _, scope_desc = analyzer.filter_activities_by_query(training_data['activities'], query)
        console.print(f"[dim]Focus: {scope_desc}[/dim]")

        analysis = analyzer.analyze(training_data, query)

        # Display results
        console.print("\n")
        panel = Panel(
            Markdown(analysis),
            title="[bold cyan]Training Analysis[/bold cyan]",
            border_style="cyan"
        )
        console.print(panel)

    except ValueError as e:
        console.print(f"[red]Configuration Error:[/red] {e}")
        console.print("\nRun [cyan]fast --setup[/cyan] for configuration instructions")
        sys.exit(1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        import traceback
        if '--debug' in sys.argv:
            console.print("\n[yellow]Debug traceback:[/yellow]")
            console.print(traceback.format_exc())
        sys.exit(1)


def show_setup_instructions():
    """Display setup instructions."""
    instructions = """
# Faster Setup Instructions

## 1. Get your intervals.icu API credentials

1. Go to https://intervals.icu
2. Log in to your account
3. Go to Settings → API Key
4. Copy your API key and athlete ID

## 2. Get OpenRouter API key

1. Go to https://openrouter.ai
2. Sign up or log in
3. Generate an API key

## 3. Create .env file

Create a file named `.env` in the same directory as this script:

```
INTERVALS_API=your_intervals_api_key_here
ATHLETE_ID=your_athlete_id_here
OPENROUTER=your_openrouter_api_key_here
OPENROUTER_MODEL=google/gemini-2.5-flash
```

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

## 5. Run the tool

```bash
faster "How's my training this month?"
```

## Example Queries

- "How's my training this month?"
- "Analyze my last 5 runs"
- "What's my current fitness level?"
- "Compare my interval sessions this week"
- "What should I focus on to improve my 10K time?"
- "Am I overtraining?"
"""
    console.print(Markdown(instructions))


if __name__ == '__main__':
    main()
