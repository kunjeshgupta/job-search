"""Formatting engine generating both Terminal Markdown and responsive HTML emails with transparent freshness, experience, and visa badges."""

from datetime import datetime
from typing import List, Dict, Any

from src.profile_loader import load_user_profile


def format_terminal_markdown(jobs: List[Dict[str, Any]], news: List[Dict[str, Any]]) -> str:
    now_str = datetime.now().strftime("%B %d, %Y")
    lines = [
        "═" * 70,
        f" 🎯 OPPORTUNITY RADAR & MORNING INTEL — {now_str}",
        "═" * 70,
        "",
        f"⚡ SECTION 1: FRESH TARGET OPPORTUNITIES ({len(jobs)} ROLES < 30 DAYS OLD)",
        "─" * 70,
    ]

    if not jobs:
        lines.append("No fresh internship/early career matches (< 30 days) found in this run.")
    else:
        for idx, j in enumerate(jobs, 1):
            role_type = j.get("role_type", "🎓 Internship")
            lines.append(f"[{idx}] {role_type} | {j['company']} — {j['title']}")
            lines.append(f"    📅 Posted: {j.get('age_badge', 'Recently Posted')}")
            lines.append(f"    📍 Location: {j.get('location', 'Unspecified')}")
            lines.append(f"    🎯 Target Experience: {j.get('exp_badge', 'Currently Enrolled / Early Career')}")
            lines.append(f"    🛂 Work Auth: {j.get('visa_badge', 'CPT / STEM OPT Eligible')}")
            lines.append(f"    🔗 Apply: {j['url']}")
            lines.append(f"    💡 Why it fits: {j.get('fit_reason', '')}")
            lines.append(f"    🎓 Alumni Search: {j.get('trojan_url', '')}")
            lines.append("    ✉️ Coffee-Chat Draft:")
            lines.append(f"       \"{j.get('coffee_chat_draft', '')}\"")
            lines.append("")

    lines.append("")
    lines.append(f"📰 SECTION 2: 3-MINUTE MARKET INTEL ({len(news)} STORIES)")
    lines.append("─" * 70)

    if not news:
        lines.append("No news items retrieved in this cycle.")
    else:
        for n in news:
            lines.append(f"• [{n['category']}] {n['title']} ({n['source']})")
            if n.get("summary"):
                lines.append(f"  Summary: {n['summary']}...")
            lines.append(f"  Source: {n['link']}")
            lines.append("")

    lines.append("═" * 70)
    return "\n".join(lines)


def format_html_email(jobs: List[Dict[str, Any]], news: List[Dict[str, Any]]) -> str:
    now_str = datetime.now().strftime("%B %d, %Y")
    profile = load_user_profile()
    candidate_name = profile.get("name", "Candidate")
    school = profile.get("university", "University")
    degree = profile.get("degree_program", "Student")
    motto = profile.get("school_motto", "")
    motto_suffix = f" &bull; {motto}" if motto else ""
    sub_header = f"{school} • {degree} Career Radar"

    jobs_html = ""
    if not jobs:
        jobs_html = "<p style='color: #666;'>No fresh internship or early-career roles (< 30 days) found in this check. The radar is actively monitoring target feeds.</p>"
    else:
        for j in jobs:
            role_type = j.get("role_type", "🎓 Internship")
            is_intern = "Internship" in role_type
            badge_bg = "#eff6ff" if is_intern else "#f0fdf4"
            badge_color = "#1d4ed8" if is_intern else "#15803d"
            badge_border = "#bfdbfe" if is_intern else "#bbf7d0"
            age_badge = j.get("age_badge", "Recently Posted")
            is_fresh = "Today" in age_badge or "Yesterday" in age_badge
            fresh_bg = "#fef2f2" if is_fresh else "#f8fafc"
            fresh_color = "#b91c1c" if is_fresh else "#475569"
            fresh_border = "#fecaca" if is_fresh else "#e2e8f0"

            jobs_html += f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px; margin-bottom: 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                
                <!-- Header Badges -->
                <div style="margin-bottom: 8px; display: flex; flex-wrap: wrap; gap: 6px;">
                    <span style="display: inline-block; background: {badge_bg}; color: {badge_color}; border: 1px solid {badge_border}; font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 12px; text-transform: uppercase;">
                        {role_type}
                    </span>
                    <span style="display: inline-block; background: {fresh_bg}; color: {fresh_color}; border: 1px solid {fresh_border}; font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 12px;">
                        📅 {age_badge}
                    </span>
                    <span style="display: inline-block; background: #fdf2f8; color: #be185d; border: 1px solid #fbcfe8; font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 12px;">
                        🎯 {j.get('exp_badge', 'Enrolled / Early Career')}
                    </span>
                </div>

                <h3 style="margin: 0 0 6px 0; color: #0f172a; font-size: 17px; font-weight: 700; line-height: 1.3;">{j['title']}</h3>
                
                <div style="margin: 0 0 12px 0; color: #475569; font-size: 14px;">
                    <strong style="color: #990000; font-weight: 700;">{j['company']}</strong> &bull; 📍 {j.get('location', 'Unspecified')}
                </div>

                <!-- Visa Status Badge -->
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 8px 12px; margin-bottom: 12px; font-size: 12px; color: #334155;">
                    <strong>🛂 Work Authorization:</strong> {j.get('visa_badge', '🏆 Top H-1B Sponsor • CPT/STEM OPT Eligible')}
                </div>

                <!-- Why It Fits -->
                <div style="background: #fffdf5; border-left: 3px solid #990000; padding: 10px 14px; margin-bottom: 14px; font-size: 13px; color: #334155; line-height: 1.5;">
                    <strong>💡 Why It Fits You:</strong> {j.get('fit_reason', '')}
                </div>

                <!-- Action Buttons -->
                <div style="margin-bottom: 14px;">
                    <a href="{j['url']}" style="display: inline-block; background: #0284c7; color: #ffffff; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: 600;">Apply to Role &rarr;</a>
                    <a href="{j.get('trojan_url', '#')}" style="display: inline-block; background: #f1f5f9; color: #0f172a; padding: 8px 14px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: 600; margin-left: 8px;">🎓 Search Alumni on LinkedIn</a>
                </div>

                <!-- Coffee-Chat Draft -->
                <div style="background: #fffbeb; border: 1px dashed #f59e0b; border-radius: 6px; padding: 12px; font-size: 12px; color: #78350f; line-height: 1.5;">
                    <strong style="display: block; margin-bottom: 4px; color: #b45309;">✉️ Coffee-Chat Draft (Ready to Copy & Send):</strong>
                    <em>"{j.get('coffee_chat_draft', '')}"</em>
                </div>
            </div>
            """

    news_html = ""
    if not news:
        news_html = "<p style='color: #666;'>Market intelligence feed is loading...</p>"
    else:
        for n in news:
            news_html += f"""
            <div style="border-bottom: 1px solid #f1f5f9; padding: 12px 0;">
                <span style="display: inline-block; background: #e0f2fe; color: #0369a1; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 4px; margin-bottom: 4px;">{n['category']}</span>
                <h4 style="margin: 4px 0; font-size: 15px; color: #0f172a;">
                    <a href="{n['link']}" style="color: #0f172a; text-decoration: none;">{n['title']} &rarr;</a>
                </h4>
                <p style="margin: 4px 0 0 0; color: #64748b; font-size: 13px; line-height: 1.4;">
                    {n.get('summary', '')}
                </p>
                <span style="font-size: 11px; color: #94a3b8;">Source: {n['source']}</span>
            </div>
            """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Opportunity Radar & Student Intelligence</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px;">
        <div style="max-width: 680px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.04); border: 1px solid #e2e8f0;">
            
            <!-- Header with Clean Dark Gradient -->
            <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 28px 24px; color: #ffffff;">
                <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 1px; color: #38bdf8; font-weight: 700;">{sub_header}</div>
                <h1 style="margin: 6px 0 0 0; font-size: 22px; font-weight: 800;">Target Internships & Early Career Briefing</h1>
                <p style="margin: 6px 0 0 0; font-size: 13px; color: #cbd5e1;">{now_str} &bull; Prepared for {candidate_name}{motto_suffix}</p>
            </div>

            <!-- Student CPT / STEM OPT Notice Banner -->
            <div style="background: #eff6ff; border-bottom: 1px solid #dbeafe; padding: 12px 24px; font-size: 12px; color: #1e40af; line-height: 1.4;">
                <strong>🎓 Work Authorization Notice:</strong> All listed internships are eligible under <strong>CPT (Curricular Practical Training)</strong> with \$0 employer visa cost. New Grad roles qualify for up to <strong>3 years of STEM OPT</strong>. Only jobs posted/updated within the <strong>last 30 days</strong> are included.
            </div>

            <div style="padding: 24px;">
                <!-- Section 1: Jobs -->
                <div style="margin-bottom: 28px;">
                    <h2 style="font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px; color: #0f172a; margin-top: 0; margin-bottom: 16px; border-bottom: 2px solid #0284c7; padding-bottom: 6px;">
                        ⚡ Verified Target Opportunities ({len(jobs)} Roles &lt; 30 Days Old)
                    </h2>
                    {jobs_html}
                </div>

                <!-- Section 2: News -->
                <div>
                    <h2 style="font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px; color: #0f172a; margin-top: 0; margin-bottom: 16px; border-bottom: 2px solid #0369a1; padding-bottom: 6px;">
                        📰 3-Minute Market Intelligence (Fintech, AI & Auto)
                    </h2>
                    {news_html}
                </div>
            </div>

            <!-- Footer -->
            <div style="background: #f1f5f9; padding: 16px 24px; text-align: center; font-size: 12px; color: #64748b;">
                Job Search Radar &bull; Automated Career Intelligence Briefing
            </div>
        </div>
    </body>
    </html>
    """
