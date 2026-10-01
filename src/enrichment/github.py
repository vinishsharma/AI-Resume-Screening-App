"""
GitHub profile enrichment module with caching, rate-limit resilience, and detailed logging.
"""
import os
import json
import logging
import urllib.request
import urllib.error
from typing import Tuple, Dict, Any, Optional
from ..config import config

logger = logging.getLogger("ResumeScreener.GitHub")

# In-memory cache for GitHub API responses across the batch
_GITHUB_CACHE: Dict[str, Tuple[float, str]] = {}

def get_github_headers() -> Dict[str, str]:
    """Build GitHub API headers with optional token."""
    headers = {
        "User-Agent": "Resume-Screening-System/1.0",
        "Accept": "application/vnd.github.v3+json"
    }
    token = config.github_token or os.getenv("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = f"token {token}"
    return headers

def fetch_github_json(url: str) -> Optional[Any]:
    """Execute GET request to GitHub API safely with logging."""
    req = urllib.request.Request(url, headers=get_github_headers())
    try:
        with urllib.request.urlopen(req, timeout=config.github_timeout_seconds) as response:
            if response.status == 200:
                data = response.read().decode('utf-8')
                return json.loads(data)
    except urllib.error.HTTPError as e:
        logger.warning(f"[GitHub API] HTTP {e.code} for URL: {url} (Rate limit or user not found)")
        return None
    except Exception as e:
        logger.warning(f"[GitHub API] Network/Connection error for URL {url}: {e}")
        return None
    return None

def analyze_github_profile(username: str) -> Tuple[float, str]:
    """
    Score GitHub activity (Max 10 points):
    - 0-5 points for recent activity / public events.
    - 0-5 points for maintained/relevant repositories in Python/AI.
    Returns: (score, summary)
    """
    if not username:
        return 0.0, "No GitHub profile provided."

    username_clean = username.strip().lstrip('@')
    cache_key = username_clean.lower()
    
    if config.cache_enabled and cache_key in _GITHUB_CACHE:
        logger.info(f"[GitHub Cache] Reusing cached evaluation for @{username_clean}")
        return _GITHUB_CACHE[cache_key]

    token_status = "Authenticated with GITHUB_TOKEN" if config.github_token else "Unauthenticated (60 req/hr limit)"
    logger.info(f"[GitHub] Querying profile for @{username_clean} ({token_status})...")

    base_url = config.github_api_base
    user_url = f"{base_url}/users/{username_clean}"
    repos_url = f"{base_url}/users/{username_clean}/repos?sort=updated&per_page=15"
    events_url = f"{base_url}/users/{username_clean}/events/public?per_page=20"

    user_data = fetch_github_json(user_url)
    if not user_data:
        res = (0.0, "GitHub profile not reachable, private, or rate limit reached.")
        logger.warning(f"[GitHub] Unable to retrieve data for @{username_clean}. Assigned 0.0 bonus points.")
        if config.cache_enabled:
            _GITHUB_CACHE[cache_key] = res
        return res

    public_repos = user_data.get("public_repos", 0)
    followers = user_data.get("followers", 0)
    logger.info(f"[GitHub] Found @{username_clean}: {public_repos} public repos, {followers} followers.")

    # 1. Activity Score (0-5 pts)
    activity_score = 0.0
    events = fetch_github_json(events_url) or []
    if len(events) >= 10:
        activity_score = 5.0
    elif len(events) >= 3:
        activity_score = 3.5
    elif len(events) > 0:
        activity_score = 2.0
    elif public_repos > 5:
        activity_score = 1.5

    # 2. Maintained & Relevant Repositories (0-5 pts)
    repos_score = 0.0
    repos = fetch_github_json(repos_url) or []
    python_ai_repos = 0
    stars_count = 0

    ai_keywords = {"llm", "agent", "rag", "langchain", "langgraph", "fastapi", "ai", "machine-learning", "pytorch"}

    for r in repos:
        lang = (r.get("language") or "").lower()
        desc = (r.get("description") or "").lower()
        name = (r.get("name") or "").lower()
        stargazers = r.get("stargazers_count", 0)
        stars_count += stargazers

        is_relevant = (lang == "python") or any(kw in desc or kw in name for kw in ai_keywords)
        if is_relevant:
            python_ai_repos += 1

    if python_ai_repos >= 4:
        repos_score = 5.0
    elif python_ai_repos >= 2:
        repos_score = 3.5
    elif python_ai_repos >= 1 or public_repos >= 3:
        repos_score = 2.0
    elif public_repos > 0:
        repos_score = 1.0

    total_github_score = min(10.0, activity_score + repos_score)

    summary_parts = []
    if activity_score >= 3.5:
        summary_parts.append("High recent public commit and event activity")
    elif activity_score > 0:
        summary_parts.append("Moderate public activity")
    else:
        summary_parts.append("Low recent public events")

    if python_ai_repos > 0:
        summary_parts.append(f"{python_ai_repos} active Python/AI repositories identified")
    elif public_repos > 0:
        summary_parts.append(f"{public_repos} public repositories")

    summary = "; ".join(summary_parts) + "."
    result = (round(total_github_score, 1), summary)
    logger.info(f"[GitHub] @{username_clean} Scored: {result[0]}/10 points ({summary})")

    if config.cache_enabled:
        _GITHUB_CACHE[cache_key] = result
        
    return result
