"""SQLite persistence module to track seen jobs and prevent duplicate alerts."""

import sqlite3
import os
from typing import Set

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "jobs.db")


def get_connection() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS seen_jobs (
                job_id TEXT PRIMARY KEY,
                company TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                location TEXT,
                first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS seen_articles (
                article_url TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                source TEXT NOT NULL,
                first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    conn.close()


def get_seen_job_ids() -> Set[str]:
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT job_id FROM seen_jobs")
    rows = cursor.fetchall()
    conn.close()
    return {r["job_id"] for r in rows}


def mark_jobs_as_seen(jobs: list):
    init_db()
    conn = get_connection()
    with conn:
        for job in jobs:
            conn.execute(
                """
                INSERT OR IGNORE INTO seen_jobs (job_id, company, title, url, location)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    job["id"],
                    job["company"],
                    job["title"],
                    job["url"],
                    job.get("location", ""),
                ),
            )
    conn.close()
