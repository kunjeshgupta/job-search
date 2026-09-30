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
    """Loads profile.json if present, otherwise profile.example.json or defaults."""
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                merged = DEFAULT_PROFILE.copy()
                merged.update(data)
                return merged
        except Exception:
            pass

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
