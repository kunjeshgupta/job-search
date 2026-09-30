"""ATS Scraper module fetching active jobs from Greenhouse, Lever, and Ashby endpoints with full job descriptions and timestamps."""

import json
import os
import ssl
import urllib.request
from typing import List, Dict, Any

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
TARGETS_FILE = os.path.join(CONFIG_DIR, "targets.json")


EXAMPLE_TARGETS_FILE = os.path.join(CONFIG_DIR, "targets.example.json")


def get_ssl_context():
    return ssl._create_unverified_context()


def load_targets() -> List[Dict[str, Any]]:
    """Loads target companies from environment JSON (GitHub Actions Secret), targets.json, or targets.example.json."""
    # 1. Check if TARGET_COMPANIES is passed via environment (GitHub Actions Secret)
    env_targets = os.environ.get("TARGET_COMPANIES")
    if env_targets:
        try:
            return json.loads(env_targets)
        except Exception:
            pass

    # 2. Check local config/targets.json (on local Mac)
    if os.path.exists(TARGETS_FILE):
        try:
            with open(TARGETS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # 3. Fallback to targets.example.json
    if os.path.exists(EXAMPLE_TARGETS_FILE):
        try:
            with open(EXAMPLE_TARGETS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    return []


def fetch_greenhouse_jobs(company_name: str, slug: str, h1b_status: str = "H-1B Sponsor") -> List[Dict[str, Any]]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"},
    )
    jobs = []
    try:
        with urllib.request.urlopen(req, context=get_ssl_context(), timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for j in data.get("jobs", []):
                loc = j.get("location", {}).get("name", "Unspecified")
                jobs.append({
                    "id": f"gh_{slug}_{j['id']}",
                    "company": company_name,
                    "title": j.get("title", "").strip(),
                    "location": loc,
                    "url": j.get("absolute_url", ""),
                    "content": j.get("content", ""),
                    "h1b_status": h1b_status,
                    "posted_at": j.get("updated_at", ""),
                })
    except Exception:
        pass
    return jobs


def fetch_lever_jobs(company_name: str, slug: str, h1b_status: str = "H-1B Sponsor") -> List[Dict[str, Any]]:
    url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"},
    )
    jobs = []
    try:
        with urllib.request.urlopen(req, context=get_ssl_context(), timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for j in data:
                loc = j.get("categories", {}).get("location", "Unspecified")
                content = j.get("descriptionPlain", "") + "\n" + j.get("additionalPlain", "")
                jobs.append({
                    "id": f"lever_{slug}_{j['id']}",
                    "company": company_name,
                    "title": j.get("text", "").strip(),
                    "location": loc,
                    "url": j.get("hostedUrl", ""),
                    "content": content,
                    "h1b_status": h1b_status,
                    "posted_at": j.get("createdAt", ""),
                })
    except Exception:
        pass
    return jobs


def fetch_ashby_jobs(company_name: str, slug: str, h1b_status: str = "H-1B Sponsor") -> List[Dict[str, Any]]:
    url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"},
    )
    jobs = []
    try:
        with urllib.request.urlopen(req, context=get_ssl_context(), timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for j in data.get("jobs", []):
                loc = j.get("location", "Unspecified")
                content = j.get("descriptionPlain", "") or j.get("descriptionHtml", "")
                jobs.append({
                    "id": f"ashby_{slug}_{j['id']}",
                    "company": company_name,
                    "title": j.get("title", "").strip(),
                    "location": loc,
                    "url": j.get("jobUrl", ""),
                    "content": content,
                    "h1b_status": h1b_status,
                    "posted_at": j.get("publishedAt", ""),
                })
    except Exception:
        pass
    return jobs


def fetch_all_jobs() -> List[Dict[str, Any]]:
    targets = load_targets()
    all_jobs = []

    for t in targets:
        ats = t.get("ats", "").lower()
        slug = t.get("slug", "")
        name = t.get("name", "")
        h1b_status = t.get("h1b_status", "H-1B Sponsor")

        if ats == "greenhouse":
            all_jobs.extend(fetch_greenhouse_jobs(name, slug, h1b_status))
        elif ats == "lever":
            all_jobs.extend(fetch_lever_jobs(name, slug, h1b_status))
        elif ats == "ashby":
            all_jobs.extend(fetch_ashby_jobs(name, slug, h1b_status))

    return all_jobs
