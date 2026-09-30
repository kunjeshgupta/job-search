"""Profile loader module providing unified user configuration across the application."""

import json
import os
from typing import Dict, Any

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
PROFILE_FILE = os.path.join(CONFIG_DIR, "profile.json")
EXAMPLE_FILE = os.path.join(CONFIG_DIR, "profile.example.json")

DEFAULT_PROFILE = {
    "name": "Candidate",
    "recipient_email": "candidate@example.com",
    "university": "State University",
    "university_short": "Alumni",
    "school_motto": "",
    "degree_program": "Master of Science",
    "work_auth_status": "F-1 Student (CPT / STEM OPT)",
    "experience_hook": "Prior to graduate school, I built analytics dashboards and automated workflow tools.",
    "primary_track": "Internship",
}


def load_user_profile() -> Dict[str, Any]:
    """Loads user profile from environment JSON (GitHub Actions Secret), profile.json, or profile.example.json."""
    # 1. Check if USER_PROFILE JSON is passed in environment (from GitHub Actions secret)
    env_profile = os.environ.get("USER_PROFILE")
    if env_profile:
        try:
            data = json.loads(env_profile)
            merged = DEFAULT_PROFILE.copy()
            merged.update(data)
            return merged
        except Exception:
            pass

    # 2. Check local config/profile.json (on local Mac)
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                merged = DEFAULT_PROFILE.copy()
                merged.update(data)
                return merged
        except Exception:
            pass

    # 3. Fallback to profile.example.json
    if os.path.exists(EXAMPLE_FILE):
        try:
            with open(EXAMPLE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                merged = DEFAULT_PROFILE.copy()
                merged.update(data)
                return merged
        except Exception:
            pass

    return DEFAULT_PROFILE.copy()
