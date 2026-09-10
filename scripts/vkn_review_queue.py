#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""VKN review queue olusturucu.

VKN'si eksik firmalar icin inceleme kuyrugu hazirlar.
Gorev P3-2, P4-3, Y10 engellerini asmak icin manuel/toplanti oncesi hazirlik yapar.

Cikti: data/orchestrator/vkn_review_queue.jsonl

Kullanim:
    python scripts/vkn_review_queue.py
    python scripts/vkn_review_queue.py --limit 100
    python scripts/vkn_review_queue.py --source ostim
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

try:
    from sqlalchemy import text
    from company_master.db.connection import get_engine
except ImportError as e:
    print(f"Bagimlilik hatasi: {e}")
    sys.exit(1)

CIKTI = ROOT / "data" / "orchestrator" / "vkn_review_queue.jsonl"


def db_vkn_eksik(limit: int = 0, source_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    engine = get_engine()
    query = """
        SELECT
            c.company_id,
            c.legal_name,
            c.trade_name,
            COALESCE(c.tax_number, c.vergi_no) as mevcut_vkn,
            c.website_domain,
            c.phone,
            c.email,
            c.nace_code,
            c.quality_score,
            sr.source_id,
            sr.raw_payload
        FROM companies c
        LEFT JOIN source_records sr ON c.source_record_id = sr.source_record_id
        WHERE COALESCE(c.tax_number, c.vergi_no) IS NULL
           OR COALESCE(c.tax_number, c.vergi_no) = ''
    """
    params: Dict[str, Any] = {}
    if source_filter:
        query += " AND sr.source_id = :src"
        params["src"] = source_filter
    if limit:
        query += " LIMIT :lim"
        params["lim"] = limit

    with engine.connect() as conn:
        rows = conn.execute(text(query), params).fetchall()

    results = []
    for row in rows:
        results.append({
            "company_id": row[0],
            "legal_name": row[1],
            "trade_name": row[2],
            "mevcut_vkn": row[3],
            "website_domain": row[4],
            "phone": row[5],
            "email": row[6],
            "nace_code": row[7],
            "quality_score": row[8],
            "source_id": row[9],
            "raw_payload": row[10] if len(row) > 10 else None,
        })
    return results


def priority_skor(rec: Dict[str, Any]) -> int:
    skor = 0
    if rec.get("website_domain"):
        skor += 20
    if rec.get("phone"):
        skor += 10
    if rec.get("email"):
        skor += 10
    if rec.get("nace_code"):
        skor += 15
    if rec.get("quality_score") and rec["quality_score"] > 50:
        skor += 20
    raw = rec.get("raw_payload") or {}
    if isinstance(raw, dict):
        if raw.get("vergi_no") or raw.get("tax_number"):
            skor += 30
        if raw.get("web_sitesi") or raw.get("website"):
            skor += 10
    return skor


def oneri_uret(rec: Dict[str, Any]) -> str:
    raw = rec.get("raw_payload") or {}
    if isinstance(raw, dict) and (raw.get("vergi_no") or raw.get("tax_number")):
        return "raw_payload'dan VKN cikar"
    if rec.get("website_domain"):
        return "GIB API ile website domain + unvan eslestirme"
    if rec.get("source_id") == "ostim":
        return "OSTIM detay verisi kontrol et"
    if rec.get("source_id") in ("ivedik", "baskent"):
        return "OSB detay sayfa yeniden tara (VPN sonrasi)"
    return "KnowYourCustomer API ile isim + adres eslestirme"


def main() -> None:
    ap = argparse.ArgumentParser(description="VKN review queue olusturucu")
    ap.add_argument("--limit", type=int, default=0, help="Maksimum kayit (0=tumu)")
    ap.add_argument("--source", help="Kaynak filtresi (ostim, aso, ivedik, baskent)")
    ap.add_argument("--output", default=str(CIKTI), help="Cikti dosyasi")
    args = ap.parse_args()

    print("VKN eksik firmalar cekiliyor...")
    records = db_vkn_eksik(limit=args.limit, source_filter=args.source)
    print(f"Toplam VKN eksik: {len(records)}")

    queue = []
    for rec in records:
        entry = {
            "company_id": rec["company_id"],
            "legal_name": rec["legal_name"],
            "trade_name": rec["trade_name"],
            "source_id": rec["source_id"],
            "website_domain": rec["website_domain"],
            "nace_code": rec["nace_code"],
            "quality_score": rec["quality_score"],
            "priority_score": priority_skor(rec),
            "oneri": oneri_uret(rec),
            "created_at": datetime.now().isoformat(),
            "status": "pending",
        }
        queue.append(entry)

    queue.sort(key=lambda x: x["priority_score"], reverse=True)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for entry in queue:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"Review queue kaydedildi: {out}")
    print(f"Toplam: {len(queue)} | pending: {sum(1 for e in queue if e['status'] == 'pending')}")
    if queue:
        print(f"En yuksek oncelik: {queue[0]['legal_name']} (skor: {queue[0]['priority_score']})")


if __name__ == "__main__":
    main()
