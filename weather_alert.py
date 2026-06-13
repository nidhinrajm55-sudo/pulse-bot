# Weather Alert Bot
# Checks temp > 35°C or rain predicted → sends Gmail alert
# Runs daily via GitHub Actions

import requests
import smtplib
from email.mime.text import MIMEText
import os

CITY = "Bengaluru"
API_KEY = os.environ.get("OPENWEATHER_API_KEY")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")   # Gmail App Password
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")

def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]
        return temp, description
    except Exception as e:
        print(f"Weather fetch failed: {e}")
        return None, None

def should_alert(temp, description):
    if temp is None:
        return False, ""
    reasons = []
    if temp > 35:
        reasons.append(f"Temperature is {temp}°C (above 35°C)")
    rain_keywords = ["rain", "drizzle", "thunderstorm", "shower"]
    if any(word in description.lower() for word in rain_keywords):
        reasons.append(f"Rain predicted: {description}")
    return bool(reasons), reasons

def send_alert(temp, description, reasons):
    body = f"""Weather Alert for {CITY}!

Current conditions:
  Temperature : {temp}°C
  Weather     : {description}

Alert reasons:
"""
    for r in reasons:
        body += f"  - {r}\n"

    msg = MIMEText(body)
    msg["Subject"] = f"Weather Alert: {CITY} needs your attention"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
    print("Alert email sent!")

def run():
    print(f"Checking weather for {CITY}...")
    temp, description = get_weather()
    alert, reasons = should_alert(temp, description)

    if alert:
        send_alert(temp, description, reasons)
    else:
        print(f"No alert needed. Temp: {temp}°C, Conditions: {description}")

if __name__ == "__main__":
    run()