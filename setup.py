#!/usr/bin/env python3
"""
Interactive Onboarding & Configuration Wizard for Job Search Radar.
Prompts the user for identity, school, work authorization, target tracks,
elevator pitch, and API keys to automatically generate config/profile.json.
"""

import argparse
import json
import os
import re
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
PROFILE_FILE = os.path.join(CONFIG_DIR, "profile.json")
ENV_FILE = os.path.join(BASE_DIR, ".env")

PRESET_TRACKS = {
    "1": {
        "name": "Product Management & APM",
        "roles": [
            "Product Management Intern",
            "Product Manager Intern",
            "APM Intern",
            "Associate Product Manager",
            "Product Analyst Intern",
            "Product Analyst",
            "Product Manager: New Grad Accelerator",
        ],
    },
    "2": {
        "name": "Data Science & Analytics",
        "roles": [
            "Data Science Intern",
            "Data Analyst Intern",
            "Business Analyst Intern",
            "Data Scientist",
            "Data Analyst",
            "Business Analyst",
            "People Analytics Intern",
        ],
    },
    "3": {
        "name": "BizOps, Strategy & Finance",
        "roles": [
            "Business Operations Intern",
            "BizOps Intern",
            "Finance and Strategy Intern",
            "Payment Risk Intern",
            "Operations Analyst",
            "Business Operations Associate",
        ],
    },
    "4": {
        "name": "All Tracks (Product, Data, Analytics & BizOps)",
        "roles": [
            "Product Management Intern",
            "Product Manager Intern",
            "APM Intern",
            "Product Analyst Intern",
            "Business Analyst Intern",
            "Data Science Intern",
            "Data Analyst Intern",
            "People Analytics Intern",
            "Payment Risk Intern",
            "Finance and Strategy Intern",
            "Futures & Prediction Market Operations Intern",
            "Product Manager: New Grad Accelerator",
            "Associate Product Manager",
            "Data Scientist",
            "Product Analyst",
            "Business Analyst",
        ],
    },
}


def print_banner():
    print("\n" + "=" * 65)
    print(" 🚀  JOB SEARCH RADAR — Personalized Onboarding Wizard")
    print("=" * 65)
    print("Configure your high-precision career radar in 2 minutes.")
    print("Your answers will personalize your match scoring, LinkedIn")
    print("alumni searches, coffee-chat drafts, and daily email delivery.")
    print("=" * 65 + "\n")


def prompt_input(prompt_text: str, default_val: str = "", required: bool = False) -> str:
    default_hint = f" [{default_val}]" if default_val else ""
    while True:
        try:
            val = input(f"{prompt_text}{default_hint}: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSetup cancelled.")
            sys.exit(0)

        if not val and default_val:
            return default_val
        if not val and required:
            print("  ⚠️  This field is required. Please provide a value.")
            continue
        return val


def prompt_choice(prompt_text: str, choices: dict, default_key: str = "1") -> tuple:
    print(f"\n{prompt_text}")
    for k, v in choices.items():
        marker = " (Default)" if k == default_key else ""
        print(f"  [{k}] {v}{marker}")
    while True:
        try:
            choice = input(f"Select option [{default_key}]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSetup cancelled.")
            sys.exit(0)

        if not choice:
            choice = default_key
        if choice in choices:
            return choice, choices[choice]
        print(f"  ⚠️  Please select a valid option ({', '.join(choices.keys())}).")


def run_wizard(args=None):
    if args and getattr(args, "test", False):
        print("🤖 Running setup wizard in automated test mode...")
        profile = {
            "name": "Test User",
            "recipient_email": "test@example.com",
            "university": "State University",
            "university_short": "Alumni",
            "school_motto": "",
            "degree_program": "Master of Science",
            "work_auth_status": "F-1 Student (CPT / STEM OPT)",
            "experience_hook": "Prior to graduate school, I built analytics dashboards and automated workflow tools.",
            "primary_track": "Internship",
            "target_roles": PRESET_TRACKS["4"]["roles"],
        }
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2)
        print("✅ Automated test configuration written successfully.")
        return profile

    print_banner()

    # Step 1: Candidate Identity
    print("👤 Step 1/7: Candidate Identity")
    name = prompt_input("  Your Full Name", default_val="Alex Taylor", required=True)
    
    email = ""
    while True:
        email = prompt_input("  Delivery Email (where daily briefings will be sent)", required=True)
        if re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            break
        print("  ⚠️  Please enter a valid email address.")

    # Step 2: University & Alma Mater
    print("\n🏛️  Step 2/7: University & Alma Mater")
    print("  Used for generating 1-click LinkedIn alumni searches & tailored outreach.")
    university = prompt_input(
        "  Full University Name (e.g. Stanford University, NYU, State University)",
        default_val="State University",
        required=True,
    )
    uni_short = prompt_input(
        "  Short Code / Acronym (e.g. Stanford, NYU, MIT)",
        default_val="Alumni",
        required=True,
    )
    motto = prompt_input(
        "  School Cheer / Greeting (e.g. Go Cardinal!, Roll Tide! - or press Enter to skip)",
        default_val="",
    )

    # Step 3: Degree & Program
    print("\n📚 Step 3/7: Degree Program")
    degree = prompt_input(
        "  Degree & Field (e.g. MS in Data Science, BS in Computer Science, MBA)",
        default_val="Master of Science",
        required=True,
    )

    # Step 4: Work Authorization
    auth_choices = {
        "1": "F-1 Student (CPT / STEM OPT eligible) [Filters strictly for visa-friendly roles]",
        "2": "US Citizen / Permanent Resident (No sponsorship required)",
        "3": "H-1B / Other Visa (Requires immediate employer sponsorship)",
    }
    _, auth_val = prompt_choice("🛂 Step 4/7: Work Authorization Status", auth_choices, default_key="1")
    # Clean label
    clean_auth = auth_val.split(" [")[0]

    # Step 5: Target Track & Desired Roles
    track_choices = {
        "1": "Product Management & APM (Internships & Early Career)",
        "2": "Data Science & Analytics (DS, DA, Business Analytics)",
        "3": "BizOps, Strategy & Finance",
        "4": "All Tracks (Product, Data, Analytics & BizOps)",
        "5": "Custom (Enter your own comma-separated role titles)",
    }
    track_key, _ = prompt_choice("🎯 Step 5/7: Target Roles & Career Tracks", track_choices, default_key="4")

    if track_key == "5":
        raw_roles = prompt_input(
            "  Enter your target roles separated by commas",
            default_val="Product Manager Intern, Data Science Intern, Business Analyst",
            required=True,
        )
        target_roles = [r.strip() for r in raw_roles.split(",") if r.strip()]
    else:
        target_roles = PRESET_TRACKS[track_key]["roles"]

    cadence_choices = {
        "1": "Internships (Summer, Fall, Spring)",
        "2": "Early Career / University New Grad (0–2 Years YOE)",
        "3": "Both Internships & Early Career",
    }
    _, primary_track = prompt_choice("  Primary Target Band", cadence_choices, default_key="1")

    # Step 6: 1-Sentence Experience Hook
    print("\n💡 Step 6/7: Pitch Hook (1 Sentence)")
    print("  Highlight your strongest past experience or flagship project.")
    print("  This is dynamically embedded into your fit score and LinkedIn coffee-chat drafts.")
    hook_default = "Prior to graduate school, I built automated data pipelines and analytics dashboards."
    hook = prompt_input("  Your Hook", default_val=hook_default, required=True)

    # Step 7: Email Delivery & API Key
    print("\n✉️  Step 7/7: Email Delivery Setup (Resend)")
    print("  We use Resend (free 3,000 emails/month) for clean, high-deliverability emails.")
    print("  Get a free key in 30 seconds at: https://resend.com/api-keys")
    resend_key = prompt_input(
        "  Resend API Key (starts with 're_') [Press Enter to skip & view briefings in terminal/HTML]",
        default_val="",
    )

    # Build Profile Dictionary
    profile_data = {
        "name": name,
        "recipient_email": email,
        "university": university,
        "university_short": uni_short,
        "school_motto": motto,
        "degree_program": degree,
        "work_auth_status": clean_auth,
        "experience_hook": hook,
        "primary_track": primary_track,
        "target_roles": target_roles,
    }

    # Save profile.json
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=2)

    # Update .env if Resend key was provided
    if resend_key:
        env_lines = []
        if os.path.exists(ENV_FILE):
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.startswith("RESEND_API_KEY=") and not line.startswith("RECIPIENT_EMAIL="):
                        env_lines.append(line.rstrip())
        env_lines.append(f"RESEND_API_KEY={resend_key}")
        env_lines.append(f"RECIPIENT_EMAIL={email}")
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(env_lines) + "\n")
        print(f"\n🔐 API credentials saved to {ENV_FILE} (protected by .gitignore).")

    print("\n" + "=" * 65)
    print(" 🎉  CONFIGURATION COMPLETE!")
    print("=" * 65)
    print(f"  • Candidate:      {name} ({email})")
    print(f"  • School:         {university} ({uni_short})")
    print(f"  • Degree:         {degree}")
    print(f"  • Authorization:  {clean_auth}")
    print(f"  • Target Roles:   {len(target_roles)} roles configured")
    print(f"  • Pitch Hook:     {hook}")
    print(f"  • Saved File:     config/profile.json (gitignored for privacy)")
    print("=" * 65)

    # Ask for instant test run
    test_run = prompt_input("\nWould you like to run an instant dry-run scan now? (y/n)", default_val="y")
    if test_run.lower().startswith("y"):
        print("\n🔍 Running instant discovery scan in dry-run mode...\n")
        run_script = os.path.join(BASE_DIR, "run.py")
        subprocess.run([sys.executable, run_script, "--dry-run", "--include-seen"], check=False)

    print("\n✨ You are all set! To run manually at any time:")
    print("   python3 run.py --dry-run             # Preview in terminal + HTML")
    print("   python3 run.py --send                # Dispatch live email digest")
    print("=" * 65 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Interactive Onboarding Wizard for Job Search Radar")
    parser.add_argument("--test", action="store_true", help="Run in automated test mode with dummy data")
    args = parser.parse_args()
    run_wizard(args)


if __name__ == "__main__":
    main()
