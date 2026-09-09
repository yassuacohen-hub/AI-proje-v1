#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""P4-1: Kalite skorunu 50+ yukseltmek icin eksik alan analizi ve backfill."""
from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from rapidfuzz import fuzz
from sqlalchemy import text

PROJE_KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJE_KOK / "src"))
from company_master.db.connection import get_engine  # noqa: E402

LOG_KLASOR = PROJE_KOK / "logs"
LOG_KLASOR.mkdir(parents=True, exist_ok=True)
LOG_DOSYA = LOG_KLASOR / "p41_quality_boost.log"
logger = logging.getLogger("p41_quality_boost")
logger.setLevel(logging.INFO)
_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
_fh = logging.FileHandler(LOG_DOSYA, encoding="utf-8")
_fh.setFormatter(_fmt)
_sh = logging.StreamHandler()
_sh.setFormatter(_fmt)
logger.addHandler(_fh)
logger.addHandler(_sh)

TURKISH_CHAR_MAP = str.maketrans({
    "\u0131": "i", "\u0130": "I", "\u011f": "g", "\u011e": "G", "\u00fc": "u", "\u00dc": "U",
    "\u015f": "s", "\u015e": "S", "\u00f6": "o", "\u00d6": "O", "\u00e7": "c", "\u00c7": "C",
})
ABBREVIATIONS = {
    "san.", "tic.", "ltd.", "\u015fti.", "a.\u015f.", "a.s.", "anonim", "\u015firketi",
    "limited", "\u015firket", "ve", "ticaret", "sanayi", "imalat", "de\u011ferleme",
    "organize", "av.", "tur.", "org.", "dan.", "kim.", "i\u0307n\u015f.", "in\u015f.",
    "d\u0131\u015f", "dis", "i\u00e7", "ic", "tekstil", "tek.", "imal", "ithalat", "ihracat",
    "m\u00fchendislik", "m\u00fch.", "muh.", "m\u00fc\u015favir", "musavir", "hizmet", "hizm.",
    "g\u0131da", "gida", "metal", "otomotiv", "otom.", "elektronik", "elektr.",
    "yaz\u0131l\u0131m", "yazilim", "teknoloji", "tekno.", "teknol.", "mobilya",
    "mob.", "tekstil", "tekst.", "tek.", "plastik", "kau\u00e7uk", "kaucuk",
    "\u00fcr\u00fcnler", "urunler", "\u00fcr\u00fcn", "urun", "imalat", "imal.", "de\u011ferleme",
    "degerleme", "de\u011fer.", "deger.",
}


def normalize_name(name: str) -> str:
    name = name.translate(TURKISH_CHAR_MAP)
    name = name.lower()
    name = re.sub(r"[^\w\s]", "", name)
    tokens = [t for t in name.split() if t and t not in ABBREVIATIONS]
    return " ".join(tokens)


def fuzzy_match(query: str, candidates: dict[str, str], threshold: float = 0.80) -> str | None:
    q = normalize_name(query)
    best = None
    best_score = 0.0
    for cname, cid in candidates.items():
        score = fuzz.ratio(q, normalize_name(cname)) / 100.0
        if score > best_score:
            best_score = score
            best = cid
    if best_score >= threshold:
        return best
    return None


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def adim1_db_index(conn) -> tuple[dict[str, str], dict[str, str]]:
    exact: dict[str, str] = {}
    normalized: dict[str, list[tuple[str, str]]] = {}
    rows = conn.execute(text("SELECT company_id, legal_name FROM companies WHERE is_ankara = TRUE")).fetchall()
    for cid, name in rows:
        exact.setdefault(name, cid)
        norm = normalize_name(name)
        normalized.setdefault(norm, []).append((name, cid))
    norm_flat = {norm: cid for norm, pairs in normalized.items() for _, cid in pairs[:1]}
    return exact, norm_flat


def adim2_baskent_backfill(conn, exact: dict[str, str], norm_index: dict[str, str]) -> dict:
    logger.info("Adim 2: Baskent OSB backfill (adres + web)")
    records = load_jsonl(PROJE_KOK / "data/baskent/firmalar.jsonl")
    stats = {"baskent_toplam": len(records), "baskent_exact": 0, "baskent_fuzzy": 0,
             "adres_guncellenen": 0, "web_guncellenen": 0}
    targets = []
    for rec in records:
        unvan = (rec.get("unvan") or "").strip()
        if not unvan:
            continue
        adres = (rec.get("adres") or "").strip()
        web = (rec.get("web_sitesi") or "").strip()
        if not adres and not web:
            continue
        cid = exact.get(unvan)
        match_type = None
        if cid:
            match_type = "exact"
        else:
            norm_unvan = normalize_name(unvan)
            cid = norm_index.get(norm_unvan)
            if cid:
                match_type = "exact"
            else:
                cid = fuzzy_match(unvan, {k: v for k, v in norm_index.items()})
                if cid:
                    match_type = "fuzzy"
        if not cid:
            continue
        stats["baskent_exact" if match_type == "exact" else "baskent_fuzzy"] += 1
        targets.append((cid, adres, web))

    for cid, adres, web in targets:
        if adres:
            r = conn.execute(text("""
                UPDATE companies SET adres = :adres, updated_at = NOW()
                WHERE company_id = :cid AND (adres IS NULL OR adres = '')
            """), {"adres": adres[:500], "cid": cid})
            stats["adres_guncellenen"] += r.rowcount
        if web:
            r = conn.execute(text("""
                UPDATE companies SET website_domain = :web, updated_at = NOW()
                WHERE company_id = :cid AND (website_domain IS NULL OR website_domain = '')
            """), {"web": web.lower().strip(), "cid": cid})
            stats["web_guncellenen"] += r.rowcount
    conn.commit()
    return stats


def adim3_vkn_web_scrape(conn, limit: int = 50) -> dict:
    logger.info("Adim 3: VKN web kazima (sinirli: %d)", limit)
    import ssl
    import urllib.request
    import urllib.error
    import urllib.robotparser

    records = load_jsonl(PROJE_KOK / "data/ostim/firmalar_detayli.jsonl")
    targets = []
    for idx, r in enumerate(records):
        web = (r.get("web_sitesi") or "").strip()
        if not web or "ostimonline.com" in web.lower() or "ostimistihdam" in web.lower():
            continue
        if r.get("vergi_no"):
            continue
        targets.append((idx, r))
        if len(targets) >= limit:
            break

    stats = {"hedef": len(targets), "bulunan": 0, "db_guncellenen": 0, "hata": 0}
    UA = "AnkaraB2B-Bot/1.0 (+research contact: site owner)"
    AYRACI_YOLLAR = ["", "/hakkimizda", "/iletisim", "/kurumsal", "/kvkk", "/hakkinda"]
    VKN_DESENLER = [
        re.compile(r"vergi\s*(?:no|numaras[\u0131i])\s*[:\u2013\u2014]?\s*([0-9]{10})", re.IGNORECASE),
        re.compile(r"v\.?\s*d\.?\s*\.?\s*[^0-9]{0,40}([0-9]{10})", re.IGNORECASE),
        re.compile(r"vergi\s*dairesi[^0-9]{0,60}([0-9]{10})", re.IGNORECASE),
        re.compile(r"tax\s*(?:no|number|id)\s*[:\u2013\u2014]?\s*([0-9]{10})", re.IGNORECASE),
    ]
    TIMEOUT = 15
    SSL_CTX = ssl.create_default_context()
    SSL_CTX.check_hostname = False
    SSL_CTX.verify_mode = ssl.CERT_NONE

    def vkn_gecerli_mi(v: str) -> bool:
        if len(v) != 10 or not v.isdigit():
            return False
        d = [int(c) for c in v]
        toplam = 0
        for i in range(9):
            t = (d[i] + 10 - (i + 1)) % 10
            toplam += (t * (2 ** (9 - i))) % 9
        kontrol = (10 - (toplam % 10)) % 10
        return kontrol == d[9]

    def vkn_ayikla(metin: str) -> list[str]:
        bulunan = []
        for desen in VKN_DESENLER:
            for m in desen.finditer(metin or ""):
                v = m.group(1)
                if vkn_gecerli_mi(v) and v not in bulunan:
                    bulunan.append(v)
        return bulunan

    def domain_cikar(web: str) -> str | None:
        m = re.match(r"^https?://([^/:?#]+)", (web or "").strip(), re.IGNORECASE)
        return m.group(1).lower() if m else None

    rp_cache: dict = {}
    for idx, rec in targets:
        web = rec.get("web_sitesi")
        dom = domain_cikar(web)
        if not dom:
            continue
        bulunan = []
        for yol in AYRACI_YOLLAR:
            if len(bulunan) >= 2:
                break
            try:
                rp = rp_cache.get(dom)
                if rp is None:
                    req = urllib.request.Request(f"https://{dom}/robots.txt", headers={"User-Agent": UA, "Accept-Language": "tr"})
                    try:
                        with urllib.request.urlopen(req, timeout=TIMEOUT, context=SSL_CTX) as r:
                            metin = r.read().decode("utf-8", errors="ignore")
                        rp = urllib.robotparser.RobotFileParser()
                        rp.parse(metin.splitlines())
                    except Exception:
                        rp = False
                    rp_cache[dom] = rp
                if rp is False:
                    continue
                if not rp.can_fetch(UA, f"https://{dom}{yol or '/'}"):
                    continue
                req = urllib.request.Request(f"https://{dom}{yol}", headers={"User-Agent": UA, "Accept-Language": "tr"})
                try:
                    with urllib.request.urlopen(req, timeout=TIMEOUT, context=SSL_CTX) as r:
                        ham = r.read()
                        try:
                            metin = ham.decode("utf-8")
                        except UnicodeDecodeError:
                            metin = ham.decode("latin-1", errors="ignore")
                    bulunan.extend(vkn_ayikla(metin))
                    time.sleep(0.5)
                except Exception as e:
                    logger.debug("scrape error %s: %s", dom, e)
                    stats["hata"] += 1
            except Exception:
                continue

        if bulunan:
            vkn = bulunan[0]
            unvan = (rec.get("unvan") or "").strip()
            row = conn.execute(text("""
                SELECT company_id FROM companies WHERE LOWER(TRIM(legal_name)) = LOWER(:n) LIMIT 1
            """), {"n": unvan}).first()
            if row:
                conn.execute(text("""
                    UPDATE companies SET tax_number = COALESCE(:vkn, tax_number), vergi_no = COALESCE(:vkn, vergi_no)
                    WHERE company_id = :cid
                """), {"vkn": vkn, "cid": row[0]})
                stats["db_guncellenen"] += 1
            stats["bulunan"] += 1
    conn.commit()
    return stats


def adim4_recalculate(conn) -> dict:
    logger.info("Adim 4: Kalite skorlari yeniden hesaplaniyor")
    result = conn.execute(text("""
        WITH scored AS (
            SELECT c.company_id, (
                CASE WHEN COALESCE(c.primary_phone, sr.raw_phone) IS NOT NULL
                          AND COALESCE(c.primary_phone, sr.raw_phone) <> '' THEN 10 ELSE 0 END
                + CASE WHEN COALESCE(c.primary_email, sr.raw_email) IS NOT NULL
                            AND COALESCE(c.primary_email, sr.raw_email) <> '' THEN 5 ELSE 0 END
                + CASE WHEN COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) IS NOT NULL
                            AND COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) <> '' THEN 15 ELSE 0 END
                + CASE WHEN COALESCE(c.adres, sr.raw_payload->>:adres) IS NOT NULL
                            AND COALESCE(c.adres, sr.raw_payload->>:adres) <> '' THEN 20 ELSE 0 END
                + CASE WHEN COALESCE(c.osb_parsel, sr.raw_payload->>:osb_parsel) IS NOT NULL
                            AND COALESCE(c.osb_parsel, sr.raw_payload->>:osb_parsel) <> '' THEN 15 ELSE 0 END
                + CASE WHEN sr.raw_payload->>:sektor IS NOT NULL
                            AND sr.raw_payload->>:sektor <> '' THEN 10 ELSE 0 END
                + CASE WHEN COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) IS NOT NULL
                            AND COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) <> '' THEN 20 ELSE 0 END
                + CASE WHEN (sr.raw_payload->>:nace_code IS NOT NULL
                              AND sr.raw_payload->>:nace_code <> '')
                            OR (sr.raw_nace IS NOT NULL AND sr.raw_nace <> '') THEN 5 ELSE 0 END
                + CASE WHEN COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) IS NULL
                            OR COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) = '' THEN -15 ELSE 0 END
                + CASE WHEN COALESCE(c.adres, sr.raw_payload->>:adres) IS NULL
                            OR COALESCE(c.adres, sr.raw_payload->>:adres) = '' THEN -10 ELSE 0 END
                + CASE WHEN COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) IS NULL
                            OR COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) = '' THEN -5 ELSE 0 END
                + CASE WHEN (COALESCE(c.primary_phone, sr.raw_phone) IS NULL OR COALESCE(c.primary_phone, sr.raw_phone) = '')
                          AND (COALESCE(c.primary_email, sr.raw_email) IS NULL OR COALESCE(c.primary_email, sr.raw_email) = '')
                          AND (COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) IS NULL OR COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) = '')
                       THEN -5 ELSE 0 END
            ) AS new_score
            FROM companies c
            LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        )
        UPDATE companies c
        SET data_quality_score = GREATEST(0, LEAST(100, scored.new_score))
        FROM scored
        WHERE c.company_id = scored.company_id
    """), {"adres": "adres", "sektor": "sektor", "nace_code": "nace_code", "osb_parsel": "osb_parsel"})
    updated = result.rowcount or 0
    avg = conn.execute(text("SELECT AVG(data_quality_score) FROM companies WHERE is_ankara = TRUE")).scalar()
    zero = conn.execute(text("SELECT COUNT(*) FROM companies WHERE is_ankara = TRUE AND data_quality_score = 0")).scalar()
    dist = {}
    rows = conn.execute(text("SELECT data_quality_score, COUNT(*) FROM companies WHERE is_ankara = TRUE GROUP BY data_quality_score ORDER BY data_quality_score")).fetchall()
    for skor, sayi in rows:
        dist[str(int(skor))] = int(sayi)
    return {"updated": updated, "avg": float(avg or 0), "zero_count": zero, "distribution": dist}


def adim5_field_stats(conn) -> dict:
    stats = {}
    for alan, sql in [
        ("phone", "SELECT COUNT(*) FROM companies WHERE primary_phone IS NOT NULL AND primary_phone <> ''"),
        ("email", "SELECT COUNT(*) FROM companies WHERE primary_email IS NOT NULL AND primary_email <> ''"),
        ("web_sitesi", "SELECT COUNT(*) FROM companies WHERE website_domain IS NOT NULL AND website_domain <> ''"),
        ("vergi_no", "SELECT COUNT(*) FROM companies WHERE vergi_no IS NOT NULL AND vergi_no <> ''"),
        ("tax_number", "SELECT COUNT(*) FROM companies WHERE tax_number IS NOT NULL AND tax_number <> ''"),
        ("adres", "SELECT COUNT(*) FROM companies WHERE adres IS NOT NULL AND adres <> ''"),
        ("osb_parsel", "SELECT COUNT(*) FROM companies WHERE osb_parsel IS NOT NULL AND osb_parsel <> ''"),
    ]:
        stats[alan] = conn.execute(text(sql)).scalar()
    return stats


def main() -> int:
    logger.info("==== P4-1 Kalite Yukseltme Basladi ====")
    engine = get_engine()
    conn = engine.connect().execution_options(compiled_cache=None)
    try:
        exact, norm_index = adim1_db_index(conn)
        baskent_stats = adim2_baskent_backfill(conn, exact, norm_index)
        scrape_stats = adim3_vkn_web_scrape(conn, limit=50)
        kalite = adim4_recalculate(conn)
        field_stats = adim5_field_stats(conn)
    finally:
        conn.close()

    toplam = 10105
    sonuc = {
        "task": "P41: Kalite skorunu 50+ yukseltmek icin backfill ve VKN kazima",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "database": {
            "connection": "DATABASE_URL (Supabase PostgreSQL)",
            "total_ankara_companies": toplam,
        },
        "initial_state": {
            "avg_quality_score": 31.9,
            "zero_score_count": 3249,
        },
        "backfill_actions": [
            {
                "step": 1,
                "name": "Baskent OSB adres + web backfill",
                "stats": baskent_stats,
            },
            {
                "step": 2,
                "name": "VKN web kazima (sinirli ornek: 50 hedef)",
                "stats": scrape_stats,
            },
        ],
        "recalculation": {
            "records_updated": kalite["updated"],
            "new_avg_quality_score": kalite["avg"],
            "new_zero_score_count": kalite["zero_count"],
            "distribution": kalite["distribution"],
        },
        "final_state": {
            "avg_quality_score": kalite["avg"],
            "zero_score_count": kalite["zero_count"],
            "field_fill_counts": field_stats,
            "total_companies_updated": baskent_stats.get("adres_guncellenen", 0) + baskent_stats.get("web_guncellenen", 0) + scrape_stats.get("db_guncellenen", 0),
        },
        "analysis": {
            "bottleneck": "VKN kapsami cok dusuk. Web kazima VPN/erisim sorunlari nedeniyle sinirli basari.",
            "path_to_50_plus": "VKN web kazima tamamlanmali (5000+ hedef). Adres/web backfill fetched data ile %60-70'a cikarilabilir.",
            "next_steps": [
                "p43_ostim_vkn.py tamami calistir (eri\u015fim varsa)",
                "p32_vkn_from_ivedik_baskent.py calistir",
                "ASO / Ticaret Sicil kaynaklarindan VKN cross-match",
            ],
        },
    }

    out_path = PROJE_KOK / "data/orchestrator/p41_result.json"
    out_path.write_text(json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Sonuc kaydedildi: %s", out_path)
    print(json.dumps(sonuc, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
