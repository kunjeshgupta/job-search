# 🎓 Job Search Radar & Daily Intelligence Briefing

[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automated-blue?logo=github-actions)](../../.github/workflows/daily_job_search.yml)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen?logo=python)](https://python.org)
[![Zero-Spam Guard](https://img.shields.io/badge/Spam_Guard-Zero--Noise-orange)](#-dual-daily-cadence)
[![Work Authorization Gatekeeper](https://img.shields.io/badge/Visa_Gatekeeper-CPT%20%2F%20STEM%20OPT-purple)](#-4-stage-gatekeeper-engine)

An automated, hyper-targeted career intelligence system that monitors company ATS feeds (Greenhouse, Lever, Ashby), filters out noise, and delivers high-relevance **Internships** and **Early Career / University (0–2 yrs)** job alerts with ready-to-send LinkedIn networking drafts directly to your inbox.

---

## ⚡ Quickstart (Get Running in 2 Minutes)

### 1. Clone & Run the Onboarding Wizard
```bash
# Clone the repository
git clone https://github.com/kunjeshgupta/job-search.git
cd job-search

# Run the interactive onboarding wizard
python3 setup.py
```

The interactive wizard will ask you 7 simple questions:
1. **Your Name & Delivery Email**: Where to send your alerts.
2. **University & Alma Mater**: Your school name, short acronym (e.g. `Stanford`, `NYU`, `MIT`), and optional motto.
3. **Degree & Major**: Your current program (e.g., `MS in Data Science`, `BS in Computer Science`, `MBA`).
4. **Work Authorization**: F-1 (CPT/STEM OPT eligible) vs. US Citizen / Green Card.
5. **Target Career Track**: Product Management (APM), Data Science & Analytics, BizOps, or Custom.
6. **Pitch Hook (1-Sentence)**: A brief summary of your strongest past experience or flagship project.
7. **Email Delivery (Resend API Key)**: Free key from [resend.com](https://resend.com/api-keys) (press Enter to skip and view local HTML digests).

### 2. Manual Commands
```bash
# Preview briefing in terminal + save local HTML
python3 projects/job-search/run.py --dry-run

# Run live email dispatch
python3 projects/job-search/run.py --send

# Run evening flash alert (only sends if fresh roles exist, skips news)
python3 projects/job-search/run.py --send --only-if-jobs --no-news
```

---

## 🛡️ 4-Stage Gatekeeper Engine

Unlike standard job boards that bombard you with stale postings and senior roles, this system applies strict gatekeepers:

1. **Strict 30-Day Freshness Gatekeeper**: Postings older than 30 days are automatically discarded. Postings under 7 days receive a `📅 Fresh 🔥` badge.
2. **US Location Enforcement**: Eliminates international or EMEA/APAC roles, strictly keeping US-based positions.
3. **Automated Experience (YOE) Parser**: Discards roles requiring >3 years of experience. Flags student/CPT eligibility for all internships.
4. **Visa & Work Authorization Sieve**: Screens job descriptions for strict exclusionary phrases (e.g. *"requires citizenship"*, *"no CPT/OPT"*, *"security clearance"*).
5. **1-Click Alumni Networking**: Automatically generates direct LinkedIn alumni search links and tailored coffee-chat outreach drafts connecting your background to the posting company.

---

## ⏰ Dual Daily Cadence

| Cadence | Schedule | Mode | Description |
| :--- | :--- | :--- | :--- |
| **Morning Briefing** | `8:00 AM PT` (`15:00 UTC`) | Full Briefing | Top fresh jobs + 3-minute curated market intelligence briefing (Fintech, AI, Automotive). |
| **Evening Flash** | `6:00 PM PT` (`01:00 UTC`) | Flash Alert | **Zero-Spam Guard**: Runs jobs-only. Exits silently with 0 emails if no new jobs were posted during the day. |

---

## ☁️ Automated Cloud Deployment (GitHub Actions)

To let the system run automatically in the cloud for free:

1. Fork or clone this repository to your GitHub account.
2. In your GitHub repository, go to **Settings** > **Secrets and variables** > **Actions**.
3. Add the following repository secrets:
   - `RESEND_API_KEY`: Your API key from [resend.com](https://resend.com/api-keys).
   - *(Optional)* `RECIPIENT_EMAIL`: Your destination email (defaults to the one configured in `setup.py`).
4. The workflow in [`.github/workflows/daily_job_search.yml`](../../.github/workflows/daily_job_search.yml) will automatically run twice daily.

---

## 🔒 Privacy & Open-Source Architecture

This repository is designed so that anyone can use or fork it publicly while keeping personal details private:

- **Gitignored Files**:
  - `projects/job-search/.env` (Contains API keys — never committed).
  - `projects/job-search/config/profile.json` (Contains your personal identity & pitch hook — never committed).
  - `projects/job-search/data/jobs.db` (Local SQLite database tracking seen jobs).
- **Public Templates**:
  - `projects/job-search/config/profile.example.json` (Clean reference template).
  - `projects/job-search/config/roles.json` (Customizable role and keyword taxonomy).
  - `projects/job-search/config/targets.json` (Curated registry of top tech & fintech companies).
