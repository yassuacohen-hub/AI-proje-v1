#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""VKN batch enrichment - lokal kaynaklardan VKN cikarma.

P3-2, P4-3, Y10 engellerini asmak icin mevcut lokal veri kaynaklarindan
VKN cikarmaya calisir. Dis API baglantisi olmadan calisir.

Kaynaklar:
    1. raw_payload (source_records.raw_payload->vergi_no)
    2. raw_payload icindeki metinlerden regex ile VKN adayi
    3. raw_tax_number (source_records.raw_tax_number)

Kullanim:
    python scripts/vkn_batch_enrich.py --dry-run
    python scripts/vkn_batch_enrich.py --apply
    python scripts/vkn_batch_enrich.py --source ostim --limit 100
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

try:
    import requests
    from sqlalchemy import text
    from company_master.db.connection import get_engine
except ImportError as e:
    print(f"Bagimlilik hatasi: {e}")
    sys.exit(1)

VKN_PATTERN = re.compile(r"\b(\d{10,11})\b")
VKN_KEYWORDS = [
    "vergi no", "vergi numarasi", "vkn", "vergi dairesi",
    "tax number", "tax id", "vergino"
]
CIKTI = ROOT / "data" / "orchestrator" / "vkn_enrich_result.jsonl"


def vkn_gecerli_mi(v: str) -> bool:
    if len(v) != 10 or not v.isdigit():
        return False
    d = [int(c) for c in v]
    toplam = 0
    for i in range(9):
        t = (d[i] + 10 - (i + 1)) % 10
        toplam += (t * (2 ** (9 - i))) % 9
    return (10 - (toplam % 10)) % 10 == d[9]


def vkn_metinden_cikar(metin: str) -> List[str]:
    if not metin:
        return []
    sonuclar = []
    for m in VKN_PATTERN.finditer(str(metin)):
        v = m.group(1)
        if len(v) == 11:
            v = v[:10]
        if not vkn_gecerli_mi(v):
            continue
        bas = max(0, m.start() - 80)
        bit = min(len(metin), m.end() + 80)
        ctx = str(metin[bas:bit]).lower()
        if any(k in ctx for k in VKN_KEYWORDS):
            if v not in sonuclar:
                sonuclar.append(v)
    return sonuclar


def db_vkn_eksik(limit: int = 0, source_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    engine = get_engine()
    query = """
        SELECT
            c.company_id,
            c.legal_name,
            COALESCE(c.tax_number, c.vergi_no) as mevcut_vkn,
            sr.source_id,
            sr.raw_payload,
            sr.raw_tax_number,
            sr.raw_text
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
            "mevcut_vkn": row[2],
            "source_id": row[3],
            "raw_payload": row[4] if len(row) > 4 else None,
            "raw_tax_number": row[5] if len(row) > 5 else None,
            "raw_text": row[6] if len(row) > 6 else None,
        })
    return results


def cikar_ve_topla(rec: Dict[str, Any]) -> List[str]:
    adaylar = []
    raw_tax = rec.get("raw_tax_number")
    if raw_tax and str(raw_tax).strip():
        v = str(raw_tax).strip()
        if vkn_gecerli_mi(v):
            adaylar.append(v)
    raw = rec.get("raw_payload") or {}
    if isinstance(raw, dict):
        for key in ("vergi_no", "tax_number", "vergiNo", "taxNo"):
            val = raw.get(key)
            if val and str(val).strip():
                v = str(val).strip()
                if vkn_gecerli_mi(v):
                    adaylar.append(v)
        payload_str = json.dumps(raw, ensure_ascii=False)
        adaylar.extend(vkn_metinden_cikar(payload_str))
    raw_text = rec.get("raw_text")
    if raw_text:
        adaylar.extend(vkn_metinden_cikar(str(raw_text)))
    seen = set()
    unique = []
    for v in adaylar:
        if v not in seen:
            seen.add(v)
            unique.append(v)
    return unique


def main() -> None:
    ap = argparse.ArgumentParser(description="VKN batch enrichment")
    ap.add_argument("--dry-run", action="store_true", help="Sadece goster, DB'ye yazma")
    ap.add_argument("--apply", action="store_true", help="DB'ye VKN yaz")
    ap.add_argument("--source", help="Kaynak filtresi (ostim, aso, ivedik, baskent)")
    ap.add_argument("--limit", type=int, default=0, help="Maksimum kayit (0=tumu)")
    ap.add_argument("--output", default=str(CIKTI), help="Cikti dosyasi")
    args = ap.parse_args()

    if not args.dry_run and not args.apply:
        print("Hata: --dry-run veya --apply gerekli")
        return

    print("VKN eksik firmalar cekiliyor...")
    records = db_vkn_eksik(limit=args.limit, source_filter=args.source)
    print(f"Toplam VKN eksik: {len(records)}")

    sonuclar = []
    bulunan = 0
    for rec in records:
        adaylar = cikar_ve_topla(rec)
        secilen = adaylar[0] if adaylar else None
        if secilen:
            bulunan += 1
        entry = {
            "company_id": rec["company_id"],
            "legal_name": rec["legal_name"],
            "source_id": rec["source_id"],
            "adaylar": adaylar,
            "secilen_vkn": secilen,
            "durum": "bulundu" if secilen else "bulunamadi",
            "checked_at": datetime.now().isoformat(),
        }
        sonuclar.append(entry)
        if secilen:
            print(f"[{rec['company_id']}] {rec['legal_name'][:40]} -> {secilen}")
        elif args.dry_run and adaylar:
            print(f"[{rec['company_id']}] {rec['legal_name'][:40]} -> aday: {adaylar} (gecersiz checksum)")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for entry in sonuclar:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"\nSonuc dosyasi: {out}")
    print(f"Toplam: {len(sonuclar)} | Bulunan: {bulunan} | Oran: %{bulunan/len(sonuclar)*100:.1f}" if sonuclar else "Veri yok")

    if args.apply and bulunan > 0:
        engine = get_engine()
        guncellenen = 0
        with engine.begin() as conn:
            for entry in sonuclar:
                if not entry["secilen_vkn"]:
                    continue
                try:
                    conn.execute(text("""
                        UPDATE companies
                        SET tax_number = COALESCE(:vkn, tax_number),
                            vergi_no = COALESCE(:vkn, vergi_no),
                            updated_at = :upd
                        WHERE company_id = :cid
                          AND (tax_number IS NULL OR tax_number = '')
                    """), {
                        "vkn": entry["secilen_vkn"],
                        "upd": datetime.now().isoformat(),
                        "cid": entry["company_id"],
                    })
                    conn.execute(text("""
                        UPDATE source_records sr
                        SET raw_tax_number = COALESCE(:vkn, raw_tax_number)
                        FROM companies c
                        WHERE sr.source_record_id = c.source_record_id
                          AND c.company_id = :cid
                    """), {
                        "vkn": entry["secilen_vkn"],
                        "cid": entry["company_id"],
                    })
                    guncellenen += 1
                except Exception as e:
                    print(f"Hata [{entry['company_id']}]: {e}")
        print(f"DB guncelleme tamamlandi: {guncellenen} firma")
        engine.dispose()


if __name__ == "__main__":
    main()
