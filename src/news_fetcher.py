"""News fetcher parsing curated fintech, AI, and automotive RSS feeds."""

import json
import os
import ssl
import urllib.request
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
NEWS_CONFIG = os.path.join(CONFIG_DIR, "news_sources.json")


def load_news_sources() -> List[Dict[str, Any]]:
    if os.path.exists(NEWS_CONFIG):
        with open(NEWS_CONFIG, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def clean_xml_text(text: str) -> str:
    if not text:
        return ""
    # Strip HTML tags simply
    import re
    clean = re.sub(r"<[^>]+>", "", text)
    return " ".join(clean.split()).strip()


def fetch_rss_feed(source_name: str, feed_url: str, category: str, max_items: int = 2) -> List[Dict[str, Any]]:
    req = urllib.request.Request(
        feed_url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) OpportunityRadar/1.0"},
    )
    articles = []
    try:
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
            content = resp.read()
            root = ET.fromstring(content)

            # Look for RSS items or Atom entries
            items = root.findall(".//item")
            if not items:
                items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

            for item in items[:max_items]:
                # Title
                title_elem = item.find("title")
                if title_elem is None:
                    title_elem = item.find("{http://www.w3.org/2005/Atom}title")
                title = title_elem.text if title_elem is not None and title_elem.text else "Untitled"

                # Link
                link_elem = item.find("link")
                link = ""
                if link_elem is not None:
                    link = link_elem.text or link_elem.attrib.get("href", "")
                if not link:
                    link_atom = item.find("{http://www.w3.org/2005/Atom}link")
                    if link_atom is not None:
                        link = link_atom.attrib.get("href", "") or link_atom.text or ""

                # Summary / Description
                desc_elem = item.find("description")
                if desc_elem is None:
                    desc_elem = item.find("{http://www.w3.org/2005/Atom}summary")
                summary = desc_elem.text if desc_elem is not None and desc_elem.text else ""
                summary = clean_xml_text(summary)[:200]

                if title and link:
                    articles.append({
                        "source": source_name,
                        "category": category,
                        "title": clean_xml_text(title),
                        "link": link.strip(),
                        "summary": summary,
                    })
    except Exception:
        pass

    return articles


def fetch_curated_market_intelligence() -> List[Dict[str, Any]]:
    sources = load_news_sources()
    all_articles = []
    for s in sources:
        articles = fetch_rss_feed(s["name"], s["url"], s.get("category", "Tech"), s.get("max_items", 2))
        all_articles.extend(articles)
    return all_articles[:6]  # Return top 5-6 curated stories
