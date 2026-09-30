"""Rule-based and JD-content matching engine for job titles, experience requirements, H-1B friendliness, and 30-day freshness."""

import html
import json
import os
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple, List

from src.profile_loader import load_user_profile

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
ROLES_CONFIG = os.path.join(CONFIG_DIR, "roles.json")


def load_roles_config() -> dict:
    if os.path.exists(ROLES_CONFIG):
        with open(ROLES_CONFIG, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


NON_US_LOCATIONS = [
    "london", "uk", "united kingdom", "paris", "france", "sydney", "melbourne",
    "australia", "berlin", "germany", "dublin", "ireland", "tokyo", "japan",
    "singapore", "toronto", "vancouver", "canada", "india", "bengaluru", "bangalore",
    "mumbai", "delhi", "amsterdam", "netherlands", "brazil", "sao paulo", "mexico",
    "poland", "spain", "sweden", "emea", "apac", "latam", "europe", "chile", "colombia",
    "argentina", "israel", "tel aviv", "italy", "switzerland", "zurich", "austria", "vienna"
]

US_KEYWORDS = [
    "us", "united states", "usa", "ca", "ny", "wa", "tx", "il", "co", "dc", "ma", "ga",
    "san francisco", "los angeles", "new york", "seattle", "austin", "chicago",
    "boston", "mountain view", "menlo park", "palo alto", "sunnyvale", "hawthorne",
    "remote - us", "remote - usa", "remote, us", "remote (us)", "remote usa"
]

WORD_TO_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
}


def is_us_location(loc_str: str) -> bool:
    if not loc_str:
        return True
    loc_lower = loc_str.lower()
    
    # 1. Direct match on non-US countries/cities
    for n in NON_US_LOCATIONS:
        if re.search(rf"\b{re.escape(n)}\b", loc_lower):
            return False

    # 2. Check remote strings
    if "remote" in loc_lower:
        for n in NON_US_LOCATIONS:
            if n in loc_lower:
                return False
        return True

    # 3. Must match known US keywords
    return any(re.search(rf"\b{re.escape(u)}\b", loc_lower) for u in US_KEYWORDS)


def parse_job_age(raw_date: Any) -> Tuple[Optional[int], str]:
    """Parses date string or epoch timestamp into (days_ago, human_badge)."""
    if not raw_date:
        return None, "Recently Posted"
    try:
        if isinstance(raw_date, (int, float)):
            dt = datetime.fromtimestamp(raw_date / 1000.0, tz=timezone.utc)
        else:
            s = str(raw_date).replace("Z", "+00:00")
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = now - dt
        days = max(0, delta.days)
        if days == 0:
            badge = "Today (Fresh 🔥)"
        elif days == 1:
            badge = "Yesterday (Fresh 🔥)"
        elif days <= 7:
            badge = f"{days} days ago (This Week)"
        else:
            badge = f"{days} days ago"
        return days, badge
    except Exception:
        return None, "Recently Posted"


def extract_years_experience(text: str) -> Tuple[Optional[int], List[str]]:
    """Extracts minimum years of experience from job description text."""
    if not text:
        return None, []

    # Clean HTML tags
    clean_text = re.sub(r"<[^>]+>", " ", html.unescape(text))
    t_clean = clean_text.lower()
    for w, n in WORD_TO_NUM.items():
        t_clean = re.sub(rf"\b{w}\b", str(n), t_clean)

    pat = re.compile(
        r"(?:minimum\s*(?:of)?\s*|at\s*least\s*|more\s*than\s*)?"
        r"(\d+)\+?\s*(?:to|-)?\s*(\d+)?\s*"
        r"(?:years?|yrs?)\s*"
        r"(?:of|in)?\s*"
        r"(?:[-\w\s]{0,45})?\s*"
        r"(?:experience|role|track record|background)",
        re.IGNORECASE,
    )

    years = []
    matched_phrases = []
    for m in pat.finditer(t_clean):
        try:
            val = int(m.group(1))
            if 0 <= val <= 25:
                years.append(val)
                matched_phrases.append(m.group(0).strip())
        except ValueError:
            pass

    min_yoe = min(years) if years else None
    return min_yoe, matched_phrases


def check_h1b_visa(text: str, company_h1b: str = "Top H-1B Sponsor") -> Tuple[bool, str]:
    """
    Checks if job description contains restrictive work authorization clauses.
    Returns (is_restricted, display_badge).
    """
    if not text:
        return False, f"🏆 {company_h1b} (CPT / STEM OPT Eligible • No Restrictions)"

    t_lower = text.lower()
    neg_patterns = [
        r"no\s+visa\s+sponsorship",
        r"unable\s+to\s+sponsor",
        r"not\s+(?:currently\s+)?offering\s+sponsorship",
        r"does\s+not\s+(?:now\s+or\s+in\s+the\s+future\s+)?sponsor",
        r"must\s+be\s+(?:a\s+)?u\.?s\.?\s+citizen",
        r"u\.?s\.?\s+citizenship\s+required",
        r"security\s+clearance",
        r"itar\s+complian",
        r"permanent\s+work\s+authorization\s+without\s+(?:the\s+need\s+for\s+)?sponsorship",
    ]
    for pat in neg_patterns:
        if re.search(pat, t_lower):
            return True, "⚠️ Sponsorship Restricted (JD specifies no visa support)"

    pos_patterns = [
        r"sponsorship\s+(?:is\s+)?available",
        r"will\s+sponsor",
        r"opt\s+(?:or|and|\/)\s*cpt\s+(?:eligible|accepted|welcome)",
    ]
    for pat in pos_patterns:
        if re.search(pat, t_lower):
            return False, "✅ H-1B Sponsored (Confirmed in JD)"

    return False, f"🏆 {company_h1b} (CPT / STEM OPT Eligible • No Restrictions)"


def classify_role_type(title: str) -> str:
    t_lower = title.lower()
    if re.search(r"\b(?:interns?(?:hip)?|campus|fellow|summer\s*202\d)\b", t_lower):
        return "🎓 Internship"
    return "💼 Early Career / New Grad"


def is_job_match(
    title: str,
    location: str = "",
    content: str = "",
    posted_at: Any = None,
    company_h1b: str = "Top H-1B Sponsor",
    config: Optional[dict] = None,
    max_days_old: int = 30,
) -> Tuple[bool, Dict[str, Any]]:
    """
    4-Stage Deep Relevancy, Freshness & Experience Gatekeeper.
    Returns (is_match, metadata_dict).
    """
    if not config:
        config = load_roles_config()

    title_lower = title.lower()

    # 1. Location filter
    if not is_us_location(location):
        return False, {"reject_reason": f"Non-US location: {location}"}

    # 2. Freshness Gatekeeper (Strict 30-Day Cutoff)
    age_days, age_badge = parse_job_age(posted_at)
    if age_days is not None and age_days > max_days_old:
        return False, {"reject_reason": f"Role is {age_days} days old (exceeds {max_days_old}-day limit)"}

    # 3. Negative Keyword Disqualification (Zero Tolerance)
    negative_keywords = config.get("negative_keywords", [])
    for neg in negative_keywords:
        if re.search(rf"\b{re.escape(neg)}\b", title_lower):
            return False, {"reject_reason": f"Negative keyword in title: {neg}"}

    # 4. Check Target Roles & Positive Keywords with word boundaries
    target_roles = config.get("target_roles", [])
    positive_keywords = config.get("positive_keywords", [])

    matches_target_role = any(re.search(rf"\b{re.escape(r.lower())}\b", title_lower) for r in target_roles)
    matches_positive_kw = any(re.search(rf"\b{re.escape(p.lower())}\b", title_lower) for p in positive_keywords)

    if not (matches_target_role or matches_positive_kw):
        return False, {"reject_reason": "Title does not match target roles or keywords"}

    # 5. JD Content Verification: Visa Restrictions
    is_visa_restricted, visa_badge = check_h1b_visa(content, company_h1b)
    if is_visa_restricted:
        return False, {"reject_reason": "Visa restricted in JD"}

    # 6. JD Content Verification: Degree Exclusions
    clean_text = re.sub(r"<[^>]+>", " ", html.unescape(content or "")).lower()
    if re.search(r"\bphd\s+(?:required|must\s+have|candidates?\s+only)\b", clean_text):
        return False, {"reject_reason": "PhD required in JD"}

    # 7. JD Content Verification: Experience Level
    min_yoe, matched_phrases = extract_years_experience(content)
    role_type = classify_role_type(title)

    # For internships: Students are eligible (CPT)
    if role_type == "🎓 Internship":
        exp_badge = "Currently Enrolled Student (MSBA / Graduate CPT)"
    elif min_yoe is not None:
        if min_yoe > 3:  # Hard ceiling for student / early career
            return False, {"reject_reason": f"Requires {min_yoe}+ years experience"}
        exp_badge = f"{min_yoe}–{min(min_yoe + 2, 4)} Years (JD Verified)"
    else:
        exp_badge = "0–2 Years (Early Career / University Band)"

    metadata = {
        "role_type": role_type,
        "min_yoe": min_yoe,
        "exp_badge": exp_badge,
        "age_days": age_days,
        "age_badge": age_badge,
        "visa_badge": visa_badge,
        "clues": matched_phrases[:2],
    }

    return True, metadata


def generate_fit_reason(
    job_title: str,
    company: str,
    role_type: str = "🎓 Internship",
    profile: Optional[Dict[str, Any]] = None,
) -> str:
    """Generates a concise 1-sentence hook linking the job to candidate's background."""
    if not profile:
        profile = load_user_profile()

    school = profile.get("university_short") or profile.get("university") or "university"
    degree = profile.get("degree_program") or "degree"
    hook = profile.get("experience_hook") or "Prior to grad school, I worked in analytics and product operations."

    title_lower = job_title.lower()
    comp_lower = company.lower()

    if role_type == "🎓 Internship":
        if any(k in title_lower for k in ["product", "apm"]):
            return (
                f"Summer PM internship. Aligns your {degree} studies at {school} "
                f"and past experience: {hook}"
            )
        if any(k in title_lower for k in ["data", "analytics", "business analyst", "bizops", "risk", "operations"]):
            return (
                f"Summer Analytics/Operations internship. Connects your {degree} toolkit at {school} "
                f"and track record: {hook}"
            )

    if any(k in title_lower for k in ["payment", "billing", "pricing", "fintech"]) or any(
        c in comp_lower for c in ["stripe", "robinhood", "coinbase", "plaid", "brex", "ramp"]
    ):
        return (
            f"Focuses on payments and fintech monetization. Directly connects to your track record: {hook}"
        )

    if any(k in title_lower for k in ["product manager", "apm", "rotational", "rpm", "accelerator"]):
        return (
            f"Early career PM / University Accelerator track. Combines your {school} {degree} background "
            f"with your past experience: {hook}"
        )

    return (
        f"Focuses on metrics, SQL analysis, and data-driven decision-making. "
        f"Directly leverages your {school} {degree} toolkit: {hook}"
    )
