# Pulse - Daily Summary Bot
# Fetches: weather (wttr.in) + a quote (zenquotes.io)
# Runs:    every day at 8 AM IST via GitHub Actions
# APIs:    both free, no API keys needed

import requests
from datetime import date

# -- FUNCTION 1: Weather --------------------------------------------
def get_weather(city="Bengaluru"):
    """Fetch today's weather as a one-line text summary."""
    url = f"https://wttr.in/{city}?format=3"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text.strip()  # remove trailing whitespace/newlines
    except Exception as e:
        return f"Weather unavailable ({e})"

# -- FUNCTION 2: Quote ----------------------------------------------
def get_quote():
    """Fetch a random motivational quote from ZenQuotes."""
    url = "https://zenquotes.io/api/random"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()        # converts JSON text to a Python list
        quote = data[0]["q"]          # the quote text
        author = data[0]["a"]         # the author name
        return f'"{quote}" - {author}'
    except Exception as e:
        return f"Quote unavailable ({e})"

# -- FUNCTION 3: Build the summary ----------------------------------
def build_summary():
    """Assemble the full daily summary from all data sources."""
    today = date.today().strftime("%A, %d %B %Y")  # e.g. Saturday, 13 June 2026
    weather = get_weather()
    quote = get_quote()

   
    summary = f"""
================================
  PULSE - Daily Summary
  {today}
================================

WEATHER
  {weather}

TODAY'S QUOTE
  {quote}

================================
"""
    return summary

# -- FUNCTION 4: Run everything -------------------------------------
def run():
    """Main entry point. Called by GitHub Actions."""
    summary = build_summary()

    
    print(summary)

   
    with open("daily_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)

    print("Pulse ran successfully.")


if __name__ == "__main__":
    run()