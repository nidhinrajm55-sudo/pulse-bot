# Portfolio Updater Bot
# Fetches all your GitHub repos via API
# Generates projects.json and commits it back to the repo
# Then pings Netlify to trigger a redeploy

import requests
import json
import os
import subprocess
from datetime import datetime

GH_TOKEN        = os.environ.get("GH_TOKEN")
GH_USERNAME     = os.environ.get("GH_USERNAME")
NETLIFY_HOOK    = os.environ.get("NETLIFY_BUILD_HOOK")

def fetch_repos():
    """Fetch all public repos from GitHub API."""
    url = f"https://api.github.com/users/{GH_USERNAME}/repos"
    headers = {
        "Authorization": f"token {GH_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {
        "sort": "updated",
        "per_page": 50,
        "type": "public"
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Failed to fetch repos: {e}")
        return []

def build_projects_json(repos):
    """Convert raw GitHub API data into clean projects.json."""
    projects = []
    for repo in repos:
        # Skip forked repos and the portfolio repo itself
        if repo.get("fork"):
            continue
        projects.append({
            "name":        repo["name"],
            "description": repo["description"] or "No description yet.",
            "language":    repo["language"] or "Unknown",
            "stars":       repo["stargazers_count"],
            "forks":       repo["forks_count"],
            "url":         repo["html_url"],
            "homepage":    repo.get("homepage") or "",
            "topics":      repo.get("topics", []),
            "updated_at":  repo["updated_at"][:10],  # just the date
        })
    return projects

def save_and_commit(projects):
    """Save projects.json and commit it to the repo."""
    output = {
        "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "total":        len(projects),
        "projects":     projects
    }

    with open("projects.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"Saved projects.json with {len(projects)} repos.")

def trigger_netlify():
    """Ping Netlify build hook to trigger a redeploy."""
    if not NETLIFY_HOOK:
        print("No Netlify hook set — skipping redeploy trigger.")
        return
    try:
        response = requests.post(NETLIFY_HOOK, timeout=10)
        response.raise_for_status()
        print("Netlify redeploy triggered!")
    except Exception as e:
        print(f"Netlify trigger failed: {e}")

def run():
    print(f"Fetching repos for {GH_USERNAME}...")
    repos    = fetch_repos()
    projects = build_projects_json(repos)
    print(f"Found {len(projects)} public non-fork repos.")
    save_and_commit(projects)
    trigger_netlify()
    print("Portfolio updater done.")

if __name__ == "__main__":
    run()