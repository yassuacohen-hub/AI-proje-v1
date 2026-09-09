#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Gelişmiş VKN çıkarıcı - footer, sayfa başlığı, meta etiketler ve fallback desenler."""
from __future__ import annotations

import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]

LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "vkn_extractor_v2.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8"), logging.StreamHandler()],
)
log = logging.getLogger("vkn_extractor_v2")

# Placeholder / OSB portal siteleri - bunlarÄ± atla
PLACEHOLDER_DOMAINS = {
    "osp.com.tr", "ostim.org.tr", "ostimonline.com", "isim.org.tr",
    "ostimistihdam.com", "ostimradyo.com", "facebook.com", "twitter.com",
    "x.com", "linkedin.com", "instagram.com", "youtube.com",
}

VKN_PATTERN = re.compile(r"\b(\d{10,11})\b")
VKN_KEYWORDS = [
    "vergi no", "vergi numarasi", "vkn", "vergi dairesi", "tax number",
    "tax id", "tc kimlik", "vergi kimlik", "vergino",
]


def is_placeholder(url: str) -> bool:
    if not url:
        return True
    url_lower = url.lower()
    for domain in PLACEHOLDER_DOMAINS:
        if domain in url_lower:
            return True
    return False


def normalize_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def score_candidate(vkn: str, context: str) -> float:
    if len(vkn) not in (10, 11):
        return 0.0
    if vkn[0] == "0":
        return 0.0
    if not vkn.isdigit():
        return 0.0
    
    ctx_lower = context.lower()
    score = 0.3
    
    for kw in VKN_KEYWORDS:
        if kw in ctx_lower:
            score += 0.4
            break
    
    if len(context) < 500:
        score += 0.1
    
    surrounding = re.sub(r"\d{10,11}", "", context)
    digit_ratio = (len(context) - len(surrounding)) / max(len(context), 1)
    if digit_ratio > 0.5:
        score -= 0.2
    
    return min(max(score, 0.0), 1.0)


def extract_vkn_from_html(html: str, url: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    best_vergi_no = None
    best_kaynak = None
    best_guven = 0.0
    
    # 1. Meta etiketlerinden dene
    for meta in soup.find_all("meta"):
        content = meta.get("content", "")
        if any(kw in content.lower() for kw in VKN_KEYWORDS):
            for m in VKN_PATTERN.finditer(content):
                vkn = m.group(1)
                s = score_candidate(vkn, content)
                if s > best_guven:
                    best_vergi_no = vkn
                    best_kaynak = "meta"
                    best_guven = s
    
    # 2. Sayfa basligi
    title = soup.title.string if soup.title else ""
    if title:
        for m in VKN_PATTERN.finditer(title):
            vkn = m.group(1)
            s = score_candidate(vkn, title)
            if s > best_guven:
                best_vergi_no = vkn
                best_kaynak = "title"
                best_guven = s
    
    # 3. JSON-LD structured data
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            text = json.dumps(data, ensure_ascii=False)
            for m in VKN_PATTERN.finditer(text):
                vkn = m.group(1)
                s = score_candidate(vkn, text)
                if s > best_guven:
                    best_vergi_no = vkn
                    best_kaynak = "jsonld"
                    best_guven = s
        except (json.JSONDecodeError, TypeError):
            continue
    
    # 4. Anahtar kelime baglamli arama
    for element in soup.find_all(text=True):
        text = element.strip()
        if any(kw in text.lower() for kw in VKN_KEYWORDS):
            parent_text = element.parent.get_text(" ", strip=True) if element.parent else text
            for m in VKN_PATTERN.finditer(parent_text):
                vkn = m.group(1)
                ctx_start = max(0, m.start() - 100)
                ctx_end = min(len(parent_text), m.end() + 100)
                ctx = parent_text[ctx_start:ctx_end]
                s = score_candidate(vkn, ctx)
                if s > best_guven:
                    best_vergi_no = vkn
                    best_kaynak = "keyword_context"
                    best_guven = s
    
    # 5. Footer arama
    footer = soup.find("footer") or soup.find("div", class_=re.compile("footer", re.I))
    if footer:
        footer_text = footer.get_text(" ", strip=True)
        for m in VKN_PATTERN.finditer(footer_text):
            vkn = m.group(1)
            ctx_start = max(0, m.start() - 50)
            ctx_end = min(len(footer_text), m.end() + 50)
            ctx = footer_text[ctx_start:ctx_end]
            s = score_candidate(vkn, ctx)
            if s > best_guven:
                best_vergi_no = vkn
                best_kaynak = "footer"
                best_guven = s
    
    return {
        "vergi_no": best_vergi_no,
        "kaynak": best_kaynak,
        "guven": round(best_guven, 2) if best_guven else 0.0,
    }


def fetch_website(url: str, timeout: int = 15) -> str | None:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        resp = requests.get(url, headers=headers, timeout=timeout, verify=False, allow_redirects=True)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as exc:
        log.debug("Fetch failed for %s: %s", url, exc)
        return None


def load_state(state_path: Path) -> dict[str, Any]:
    if not state_path.exists():
        return {"processed": {}, "stats": {"total": 0, "vkn_found": 0, "skipped_placeholder": 0, "fetch_failed": 0}}
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"processed": {}, "stats": {"total": 0, "vkn_found": 0, "skipped_placeholder": 0, "fetch_failed": 0}}


def save_state(state_path: Path, state: dict[str, Any]) -> None:
    tmp = state_path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    try:
        os.replace(tmp, state_path)
    except PermissionError:
        # Windows fallback: try shutil.move, then direct write
        import shutil
        try:
            shutil.move(str(tmp), str(state_path))
        except PermissionError:
            # Last resort: write directly
            with open(state_path, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
                if tmp.exists():
                    tmp.unlink()


def main() -> int:
    input_path = ROOT / "data" / "ostim" / "firmalar_detayli.jsonl"
    output_path = ROOT / "data" / "ostim" / "firmalar_vkn_ekli.jsonl"
    state_path = ROOT / "data" / "ostim" / ".vkn_extractor_state.json"
    
    if not input_path.exists():
        log.error("Input file not found: %s", input_path)
        return 1
    
    records = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    
    total_records = len(records)
    log.info("Toplam %d kayit yuklendi", total_records)
    
    state = load_state(state_path)
    processed_slugs = set(state.get("processed", {}).keys())
    stats = state.get("stats", {"total": 0, "vkn_found": 0, "skipped_placeholder": 0, "fetch_failed": 0})
    
    log.info("Devam ediliyor: %d kayit zaten islendi", len(processed_slugs))
    
    file_mode = "a" if output_path.exists() and len(processed_slugs) > 0 else "w"
    log.info("Cikti dosyasi modu: %s", file_mode)
    
    processed_count = 0
    vkn_found_count = 0
    
    with open(output_path, file_mode, encoding="utf-8") as out:
        for rec in records:
            slug = rec.get("slug", "")
            
            if slug in processed_slugs:
                processed_count += 1
                if rec.get("vergi_no"):
                    vkn_found_count += 1
                continue
            
            web = rec.get("web_sitesi")
            stats["total"] += 1
            
            if is_placeholder(web):
                stats["skipped_placeholder"] += 1
                rec["vergi_no"] = rec.get("vergi_no")
                rec["vergi_no_kaynagi"] = rec.get("vergi_no_kaynagi")
                state["processed"][slug] = {"status": "skipped_placeholder", "web": web}
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                processed_count += 1
                save_state(state_path, state)
                continue
            
            if web:
                url = normalize_url(web)
                html = fetch_website(url)
                if html:
                    result = extract_vkn_from_html(html, url)
                    if result.get("vergi_no") and result.get("guven", 0) >= 0.5:
                        rec["vergi_no"] = result["vergi_no"]
                        rec["vergi_no_kaynagi"] = result["kaynak"]
                        rec["vergi_no_guven"] = result["guven"]
                        vkn_found_count += 1
                        log.info("VKN bulundu: %s -> %s (kaynak: %s, guven: %.2f)", 
                                rec.get("unvan", ""), result["vergi_no"], result["kaynak"], result["guven"])
                else:
                    stats["fetch_failed"] += 1
            
            state["processed"][slug] = {"status": "processed", "web": web, "vkn": rec.get("vergi_no")}
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            processed_count += 1
            
            if processed_count % 100 == 0:
                save_state(state_path, state)
                log.info("Ilerleme: %d/%d (%.1f%%), VKN: %d, Atlamalar: %d, Hatalar: %d",
                        processed_count, total_records,
                        processed_count / total_records * 100,
                        vkn_found_count,
                        stats["skipped_placeholder"],
                        stats["fetch_failed"])
            
            time.sleep(1.5)
    
    save_state(state_path, state)
    log.info("TAMAM! Islenen: %d/%d, VKN bulundu: %d, Atlanan placeholder: %d, Cekim hatasi: %d",
            processed_count, total_records, vkn_found_count,
            stats["skipped_placeholder"], stats["fetch_failed"])
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
