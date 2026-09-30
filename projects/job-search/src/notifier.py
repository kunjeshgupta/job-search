"""Email notification dispatcher supporting Resend API, system environment variables, and local preview."""

import json
import os
import ssl
import urllib.request
from typing import Dict, Any

from src.profile_loader import load_user_profile


def load_env_vars() -> Dict[str, str]:
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    env = {}
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    env[key.strip()] = val.strip().strip("'\"")

    # Merge system environment variables (e.g., from GitHub Actions Secrets)
    for k in ["RESEND_API_KEY", "RECIPIENT_EMAIL", "SENDER_EMAIL"]:
        if k in os.environ and os.environ[k]:
            env[k] = os.environ[k]

    return env


def send_email_via_resend(
    subject: str,
    html_content: str,
    recipient_email: str = "candidate@example.com",
    api_key: str = "",
    from_email: str = "onboarding@resend.dev",
) -> Dict[str, Any]:
    if not api_key:
        env = load_env_vars()
        api_key = env.get("RESEND_API_KEY", "")
        profile = load_user_profile()
        recipient_email = env.get("RECIPIENT_EMAIL") or profile.get("recipient_email") or recipient_email
        from_email = env.get("SENDER_EMAIL", from_email)

    if not api_key or api_key == "re_your_free_key_here":
        return {
            "status": "skipped",
            "message": "RESEND_API_KEY not configured in environment or .env. Skipping outbound email.",
        }

    url = "https://api.resend.com/emails"
    payload = json.dumps({
        "from": from_email,
        "to": [recipient_email],
        "subject": subject,
        "html": html_content,
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "OpportunityRadar/1.0",
        },
        method="POST",
    )

    ctx = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {"status": "success", "id": data.get("id"), "message": "Email sent successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to send email: {str(e)}"}
