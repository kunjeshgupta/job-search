#!/usr/bin/env python3
"""
Job Search CLI Runner
Usage:
  python run.py --dry-run             # Fetches jobs & news, outputs terminal briefing, saves HTML preview
  python run.py --send                # Sends outbound email digest via Resend
  python run.py --send --only-if-jobs # Sends ONLY if new jobs are found (Zero-Spam Guard)
  python run.py --send --no-news      # Flash alert mode (skips market news)
"""

import argparse
import os
import sys
from datetime import datetime

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from src.db import init_db, get_seen_job_ids, mark_jobs_as_seen
from src.matcher import is_job_match, generate_fit_reason, load_roles_config
from src.outreach import build_trojan_linkedin_url, generate_coffee_chat_draft
from src.scraper import fetch_all_jobs
from src.news_fetcher import fetch_curated_market_intelligence
from src.formatter import format_terminal_markdown, format_html_email
from src.notifier import send_email_via_resend


def main():
    parser = argparse.ArgumentParser(description="Job Search & Student Briefing Runner")
    parser.add_argument("--send", action="store_true", help="Send email digest via Resend")
    parser.add_argument("--dry-run", action="store_true", help="Run without sending email (default)", default=True)
    parser.add_argument("--include-seen", action="store_true", help="Include previously seen jobs for testing")
    parser.add_argument("--max-age", type=int, default=30, help="Maximum job age in days (default: 30)")
    parser.add_argument("--only-if-jobs", action="store_true", help="Only dispatch email if at least one new job is found (Zero-Spam Guard)")
    parser.add_argument("--no-news", action="store_true", help="Skip market news (flash alert mode)")
    args = parser.parse_args()

    print("\n🔍 [JOB SEARCH RADAR] Starting discovery run...")

    # 1. Initialize SQLite
    init_db()
    seen_ids = get_seen_job_ids()

    # 2. Fetch raw jobs with full descriptions and timestamps
    print("📡 Querying target ATS feeds (Greenhouse, Lever, Ashby) with full JD scraping...")
    raw_jobs = fetch_all_jobs()
    print(f"   Fetched {len(raw_jobs)} active positions across target companies.")

    # 3. Match against roles config with 4-stage gatekeeper & 30-day freshness
    roles_cfg = load_roles_config()
    matched_jobs = []

    for job in raw_jobs:
        if not args.include_seen and job["id"] in seen_ids:
            continue

        is_match, meta = is_job_match(
            title=job["title"],
            location=job.get("location", ""),
            content=job.get("content", ""),
            posted_at=job.get("posted_at"),
            company_h1b=job.get("h1b_status", "Top H-1B Sponsor"),
            config=roles_cfg,
            max_days_old=args.max_age,
        )

        if is_match:
            job["role_type"] = meta["role_type"]
            job["exp_badge"] = meta["exp_badge"]
            job["age_days"] = meta.get("age_days", 999)
            job["age_badge"] = meta.get("age_badge", "Recently Posted")
            job["visa_badge"] = meta["visa_badge"]
            job["fit_reason"] = generate_fit_reason(job["title"], job["company"], meta["role_type"])
            job["trojan_url"] = build_trojan_linkedin_url(job["company"], "Product")
            job["coffee_chat_draft"] = generate_coffee_chat_draft(job["company"], job["title"], meta["role_type"])
            matched_jobs.append(job)

    # Sort matched jobs: Internships first, then sorted by freshness (newest first)
    matched_jobs.sort(key=lambda j: (
        0 if "Internship" in j.get("role_type", "") else 1,
        j.get("age_days") if j.get("age_days") is not None else 999
    ))

    print(f"🎯 Filtered to {len(matched_jobs)} fresh target roles (< {args.max_age} days old).")

    # 4. Check Zero-Spam Guard
    if args.only_if_jobs and len(matched_jobs) == 0:
        print("🛡️ [ZERO-SPAM GUARD] No new jobs found. Skipping email dispatch.")
        print("🏁 Job Search run finished.\n")
        return

    # 5. Fetch market intelligence (unless --no-news)
    if args.no_news:
        news_items = []
        print("⚡ Flash mode: Skipping market intelligence news.")
    else:
        print("📰 Fetching curated market intelligence (Fintech, AI, Automotive)...")
        news_items = fetch_curated_market_intelligence()
        print(f"   Retrieved {len(news_items)} market news stories.")

    # 6. Build outputs with exact synchronized counts
    display_jobs = matched_jobs[:10]
    terminal_output = format_terminal_markdown(display_jobs, news_items)
    html_output = format_html_email(display_jobs, news_items)

    # 7. Save local HTML preview
    preview_path = os.path.join(BASE_DIR, "data", "latest_briefing.html")
    os.makedirs(os.path.dirname(preview_path), exist_ok=True)
    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(html_output)

    # 8. Print Terminal Briefing
    print("\n" + terminal_output + "\n")
    print(f"💾 Full HTML briefing saved to: {preview_path}")

    # 9. Dispatch email if requested (subject strictly matches display_jobs count)
    if args.send:
        now_str = datetime.now().strftime("%b %d")
        if args.no_news:
            subject = f"⚡ Flash Job Alert ({len(display_jobs)} New Target Roles) — {now_str}"
        else:
            subject = f"🎓 Job Search Radar ({len(display_jobs)} Fresh Roles) & Student Briefing — {now_str}"
        print(f"\n📧 Sending email to recipient...")
        res = send_email_via_resend(subject, html_output)
        print(f"   Result: {res.get('status')} - {res.get('message')}")

    # 10. Mark jobs as seen
    if matched_jobs and not args.include_seen:
        mark_jobs_as_seen(matched_jobs)
        print(f"✅ Marked {len(matched_jobs)} jobs as seen in database.")

    print("🏁 Job Search run finished.\n")


if __name__ == "__main__":
    main()
