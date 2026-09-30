"""Dynamic LinkedIn alumni URL builder and personalized coffee-chat message generator."""

import urllib.parse
from typing import Dict, Any, Optional
from src.profile_loader import load_user_profile


def build_trojan_linkedin_url(
    company_name: str,
    domain_keyword: str = "Product",
    school_name: Optional[str] = None,
) -> str:
    """
    Constructs a precision LinkedIn search URL filtering for:
    - Company Name
    - Domain Keyword (Product, Analytics, Data)
    - School / University alumni network
    """
    if not school_name:
        profile = load_user_profile()
        school_name = profile.get("university_short") or profile.get("university") or ""

    query = f"{company_name} {domain_keyword} {school_name}".strip()
    encoded_query = urllib.parse.quote(query)
    return f"https://www.linkedin.com/search/results/people/?keywords={encoded_query}"


def generate_coffee_chat_draft(
    company: str,
    title: str,
    role_type: str = "🎓 Internship",
    profile: Optional[Dict[str, Any]] = None,
) -> str:
    """Generates a warm, authentic, <80-word coffee chat message tailored to the user's school & background."""
    if not profile:
        profile = load_user_profile()

    motto = profile.get("school_motto", "")
    degree = profile.get("degree_program", "graduate student")
    university = profile.get("university", "university")
    hook = profile.get("experience_hook", "Prior to grad school, I worked in analytics and product operations.")

    greeting_suffix = f" {motto}" if motto else ""
    closing_suffix = f" and {motto}" if motto else ""
    title_lower = title.lower()

    if any(k in title_lower for k in ["payment", "fintech", "pricing", "billing"]) or company.lower() in [
        "stripe", "robinhood", "coinbase", "plaid", "brex", "ramp"
    ]:
        interest = f"how {company} approaches payments and monetization infrastructure"
    elif any(k in title_lower for k in ["product", "apm", "rpm"]):
        interest = f"your product journey and the team culture at {company}"
    elif company.lower() in ["tesla", "rivian"]:
        interest = f"how data drives decision-making on your team at {company}"
    else:
        interest = f"your experience on the data and product team at {company}"

    goal = f"I'm exploring {title} opportunities at {company} and would love to learn more about {interest}."

    return (
        f"Hi [Name],{greeting_suffix}! I'm a {degree} at {university}. "
        f"I came across your profile at {company} and was really inspired by your path. {hook} "
        f"{goal} If you have 10-15 minutes for a brief coffee chat in the coming weeks, "
        f"I'd be deeply grateful for your perspective. Either way, thanks for your time{closing_suffix}!"
    )
