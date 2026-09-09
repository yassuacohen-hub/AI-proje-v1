# -*- coding: utf-8 -*-
import json, re, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Optional
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[4]
INPUT_FILE = ROOT / "data" / "ostim" / "firmalar_full.jsonl"
OUTPUT_FILE = ROOT / "data" / "ostim" / "firmalar_detailed.jsonl"

BASE_URL = "https://www.ostim.org.tr/firmalar"
USER_AGENT = "AnkaraB2B-Bot/1.0"
TIMEOUT = 15
MAX_WORKERS = 4

WEB_BLOCKLIST = (
    "ostim.org.tr", "ostimonline.com", "ostimradyo.com",
    "isim.org.tr", "osp.com.tr",
    "facebook.com", "twitter.com", "x.com",
    "linkedin.com", "instagram.com", "youtube.com",
)


def _is_company_website(href: str) -> bool:
    if not href or not href.startswith("http"):
        return False
    low = href.lower()
    if any(b in low for b in WEB_BLOCKLIST):
        return False
    if low.endswith(("/", "/index.html", "/home")):
        return False
    return True


def extract_detail(slug: str) -> dict:
    if not slug: return {}
    url = f"{BASE_URL}/{slug}"
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        if resp.status_code == 404: return {}
        resp.raise_for_status()
    except Exception: return {}
    soup = BeautifulSoup(resp.text, "html.parser")
    data = {"web_sitesi": None, "adres": None, "sosyal_medya": {}, "vergi_no": None, "osb_parsel": None}
    for a in soup.select("a[href^='http']"):
        href = a.get("href", "")
        if _is_company_website(href):
            data["web_sitesi"] = href
            break
    for a in soup.select("a[href*='linkedin.com'], a[href*='twitter.com'], a[href*='x.com'], a[href*='facebook.com'], a[href*='instagram.com']"):
        href = a.get("href", "")
        if "linkedin.com" in href: data["sosyal_medya"]["linkedin"] = href
        elif "twitter.com" in href or "x.com" in href: data["sosyal_medya"]["twitter"] = href
        elif "facebook.com" in href: data["sosyal_medya"]["facebook"] = href
        elif "instagram.com" in href: data["sosyal_medya"]["instagram"] = href
    for label in ["Adres", "Adresi"]:
        el = soup.find(string=re.compile(label, re.IGNORECASE))
        if el and el.parent:
            parent_text = el.parent.get_text(strip=True)
            next_sib = el.parent.find_next_sibling()
            data["adres"] = next_sib.get_text(strip=True) if next_sib else parent_text.replace(label, "").strip(" :")
            if data["adres"]: break
    for label in ["Vergi No", "Vergi"]:
        el = soup.find(string=re.compile(label, re.IGNORECASE))
        if el and el.parent:
            next_sib = el.parent.find_next_sibling()
            if next_sib: data["vergi_no"] = next_sib.get_text(strip=True); break
    for label in ["Ada / Parsel", "Ada", "Parsel"]:
        el = soup.find(string=re.compile(label, re.IGNORECASE))
        if el and el.parent:
            next_sib = el.parent.find_next_sibling()
            if next_sib: data["osb_parsel"] = next_sib.get_text(strip=True); break
    return data

def process_firm(firm: dict) -> dict:
    slug = firm.get("slug")
    if slug:
        details = extract_detail(slug)
        firm.update(details)
    firm["detail_scraped_at"] = datetime.now().isoformat()
    return firm

def run_scraper(limit: Optional[int] = None):
    completed_slugs = set()
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        r = json.loads(line)
                        if r.get("slug"): completed_slugs.add(r["slug"])
                    except: pass
    firms_to_scrape = []
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                firm = json.loads(line)
                if firm.get("slug") not in completed_slugs: firms_to_scrape.append(firm)
    if limit: firms_to_scrape = firms_to_scrape[:limit]
    total = len(firms_to_scrape)
    if total == 0: print("Yeni firma kalmadı."); return
    print(f"Çekilecek: {total}")
    with open(OUTPUT_FILE, "a", encoding="utf-8") as out_f:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_firm = {executor.submit(process_firm, firm): firm for firm in firms_to_scrape}
            count = 0
            for future in as_completed(future_to_firm):
                count += 1
                try:
                    result = future.result()
                    out_f.write(json.dumps(result, ensure_ascii=False) + "\n")
                    out_f.flush()
                except Exception as e: print(f"Hata: {e}")
                if count % 25 == 0 or count == total: print(f"{count}/{total} tamamlandı.")
                time.sleep(0.5)

if __name__ == "__main__":
    import sys
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run_scraper(limit)