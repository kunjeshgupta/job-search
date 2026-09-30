# 🎯 Job Search Radar & Autonomous Career Intelligence

[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automated-blue?logo=github-actions)](.github/workflows/daily_job_search.yml)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen?logo=python)](https://python.org)
[![Zero-Spam Guard](https://img.shields.io/badge/Spam_Guard-Zero--Noise-orange)](#-dual-daily-cadence)
[![Work Authorization](https://img.shields.io/badge/Visa_Gatekeeper-CPT%20%2F%20STEM%20OPT-purple)](#-features)

An automated, hyper-targeted career discovery radar and student market briefing engine. It queries ATS feeds (Greenhouse, Lever, Ashby) directly across premier tech and fintech companies, filters out noise using a strict 4-stage gatekeeper, and delivers daily email digests with 1-click alumni networking links.

---

## 🚀 Quickstart (Setup in 2 Minutes)

Anyone can clone and run their own personalized radar with our interactive setup wizard:

```bash
# 1. Clone the repository
git clone https://github.com/kunjeshgupta/job-search.git
cd job-search

# 2. Run the interactive onboarding wizard
python3 setup.py
```

The wizard will guide you through:
1. **Candidate Identity**: Your name and alert delivery email.
2. **University & Alma Mater**: School name, short acronym (e.g. `Stanford`, `NYU`, `MIT`), and optional motto.
3. **Degree & Major**: Program name (e.g. `MS in Data Science`, `BS in Computer Science`, `MBA`).
4. **Work Authorization**: F-1 (CPT/STEM OPT eligible) vs. US Citizen / Permanent Resident.
5. **Target Career Track**: Product Management (APM), Data Science & Analytics, BizOps, or Custom.
6. **Pitch Hook**: 1-sentence summary of your past achievements (dynamically embedded into match notes).
7. **Email Delivery**: Optional Resend API key for inbox delivery (free at [resend.com](https://resend.com)).

### Manual Commands
```bash
# Preview briefing in terminal + save local HTML
python3 run.py --dry-run

# Run live email dispatch
python3 run.py --send

# Run evening flash alert (only sends if fresh roles exist, skips news)
python3 run.py --send --only-if-jobs --no-news
```

---

## ⚡ Daily Automation (GitHub Actions)

This repo includes a dual-cadence GitHub Actions workflow in [`.github/workflows/daily_job_search.yml`](.github/workflows/daily_job_search.yml):

- **8:00 AM PT (`15:00 UTC`)**: **Morning Full Briefing** (Fresh Roles + 3-minute market intelligence briefing).
- **6:00 PM PT (`01:00 UTC`)**: **Evening Flash Alert** (**Zero-Spam Guard**: exits silently if no new jobs were posted today).

### Deploying to Your GitHub Account
1. Fork or push this repository to GitHub.
2. Go to **Settings** > **Secrets and variables** > **Actions**.
3. Add `RESEND_API_KEY` (and optionally `RECIPIENT_EMAIL`).
4. GitHub Actions will handle daily execution automatically with zero maintenance.

---

## 🛡️ Key Features

- **Strict 30-Day Freshness**: Postings older than 30 days are automatically filtered out.
- **US Location Filter**: Excludes non-US and overseas positions.
- **Experience (YOE) Parser**: Discards senior positions (>3 years required) while flagging graduate student/CPT eligibility.
- **Visa Compliance**: Auto-checks JDs for sponsorship restrictions.
- **1-Click Alumni Networking**: Generates direct LinkedIn alumni search links and tailored coffee-chat templates for every matched company.
- **Zero-Spam Guard**: Silent evening runs when no new jobs are posted.

---

## 🔒 Privacy & Open-Source Architecture

This repository is built for public sharing while keeping private credentials safe:
- **Private Files (`.gitignore`)**: Local `.env` credentials, `config/profile.json`, and SQLite seen-jobs cache are strictly gitignored and never published.
- **Public Reference Templates**: `projects/job-search/config/profile.example.json` and `projects/job-search/config/roles.json`.
