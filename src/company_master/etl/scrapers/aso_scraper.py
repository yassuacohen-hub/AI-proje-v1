# -*- coding: utf-8 -*-
import json
import time
import requests
import re
from typing import Optional

BASE_URL = "https://www.aso.org.tr/firmarehberi/"
API_URL = BASE_URL + "api.php"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
TIMEOUT = 30
_CSRF_RE = re.compile(r"csrfToken = '([0-9a-f]+)'")

def get_csrf_token(session: requests.Session) -> Optional[str]:
    resp = session.get(BASE_URL, timeout=TIMEOUT)
    match = _CSRF_RE.search(resp.text)
    return match.group(1) if match else None

def search_page(session: requests.Session, csrf: str, page: int) -> list[dict]:
    payload = {"firma_unvan": "A", "page": page, "csrf_token": csrf}
    resp = session.post(API_URL + "?action=ara", json=payload, timeout=60)
    data = resp.json()
    return data.get("data", []) if data.get("status") == "success" else []

def get_detail(session: requests.Session, csrf: str, detail_token: str) -> dict:
    resp = session.post(API_URL + "?action=get_uye_detay",
                        json={"detailToken": detail_token, "csrf_token": csrf}, timeout=30)
    data = resp.json()
    return data.get("data", {}) if data.get("status") == "success" else {}

def run_full_scrape(max_sayfa: int = 30):
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    csrf = get_csrf_token(session)
    
    count_detail = 0
    with open("data/aso/aso_full.jsonl", "a", encoding="utf-8") as f:
        for page in range(1, max_sayfa + 1):
            if page % 50 == 0: csrf = get_csrf_token(session)
            
            items = search_page(session, csrf, page)
            if not items: break
            
            for item in items:
                detail = get_detail(session, csrf, item.get("detailToken", ""))
                if detail:
                    item.update(detail)
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
                    count_detail += 1
                    if count_detail % 10 == 0: time.sleep(1)
    print(f"[BILGI] {count_detail} firma kaydedildi.")
