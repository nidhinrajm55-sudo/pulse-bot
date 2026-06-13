# News Digest Bot
# Scrapes BBC, The Hindu, Hacker News via RSS
# Compiles a formatted HTML email and sends at 7 AM IST

import smtplib
import os
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

EMAIL_SENDER   = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")

SOURCES = [
    {
        "name": "BBC News",
        "url": "http://feeds.bbci.co.uk/news/rss.xml",
        "limit": 5,
    },
    {
        "name": "The Hindu",
        "url": "https://www.thehindu.com/news/national/feeder/default.rss",
        "limit": 5,
    },
    {
        "name": "Hacker News",
        "url": "https://hnrss.org/frontpage",
        "limit": 5,
    },
]

def fetch_headlines(source):
    """Fetch top headlines from an RSS feed."""
    try:
        response = requests.get(source["url"], timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        items = root.findall(".//item")
        headlines = []
        for item in items[:source["limit"]]:
            title = item.findtext("title", "No title").strip()
            link  = item.findtext("link",  "#").strip()
            pub   = item.findtext("pubDate", "")
            # Parse and reformat the date nicely
            try:
                dt = datetime.strptime(pub, "%a, %d %b %Y %H:%M:%S %z")
                pub = dt.strftime("%d %b %Y, %I:%M %p")
            except Exception:
                pub = pub[:25] if pub else "Unknown time"
            headlines.append({"title": title, "link": link, "pub": pub})
        return headlines
    except Exception as e:
        return [{"title": f"Could not fetch {source['name']}: {e}",
                 "link": "#", "pub": ""}]

def build_html(all_headlines):
    """Build a clean HTML email body."""
    today = datetime.now().strftime("%A, %d %B %Y")

    sections = ""
    for source_name, headlines in all_headlines.items():
        items_html = ""
        for h in headlines:
            items_html += f"""
            <tr>
              <td style="padding:10px 0;border-bottom:1px solid #eee;">
                <a href="{h['link']}" style="color:#1a1a2e;font-size:15px;
                   font-weight:500;text-decoration:none;">{h['title']}</a>
                <br>
                <span style="color:#888;font-size:12px;">{h['pub']}</span>
              </td>
            </tr>"""
        sections += f"""
        <div style="margin-bottom:32px;">
          <h2 style="color:#4a4a8a;font-size:18px;margin:0 0 12px;
              border-left:4px solid #4a4a8a;padding-left:10px;">{source_name}</h2>
          <table width="100%" cellpadding="0" cellspacing="0">{items_html}</table>
        </div>"""

    return f"""
    <html><body style="font-family:Arial,sans-serif;max-width:640px;
      margin:auto;padding:24px;color:#1a1a2e;">
      <div style="background:#4a4a8a;color:white;padding:20px 24px;border-radius:8px;margin-bottom:28px;">
        <h1 style="margin:0;font-size:22px;">Your Morning News Digest</h1>
        <p style="margin:6px 0 0;opacity:0.85;font-size:14px;">{today}</p>
      </div>
      {sections}
      <p style="color:#aaa;font-size:12px;text-align:center;margin-top:32px;">
        Sent by Pulse Bot · GitHub Actions
      </p>
    </body></html>"""

def send_email(html_body):
    """Send the HTML digest email."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Morning News Digest — {datetime.now().strftime('%d %b %Y')}"
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = EMAIL_RECEIVER
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
    print("News digest email sent!")

def run():
    print("Fetching headlines...")
    all_headlines = {}
    for source in SOURCES:
        print(f"  - {source['name']}...")
        all_headlines[source["name"]] = fetch_headlines(source)

    html = build_html(all_headlines)
    send_email(html)
    print("Done.")

if __name__ == "__main__":
    run()