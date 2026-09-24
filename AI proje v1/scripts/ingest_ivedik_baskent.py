# -*- coding: utf-8 -*-
"""Y2: Ivedik + Baskent RAW ingest (OSTIM pipeline.py deseniyle).

Kullanim:
    python scripts/ingest_ivedik_baskent.py          # yaz
    python scripts/ingest_ivedik_baskent.py --count  # sadece say, yazma
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sqlalchemy import text  # noqa: E402

from company_master.db.connection import get_engine, get_session  # noqa: E402

FILES = {
    "ivedik.org.tr": (ROOT / "data" / "ivedik" / "firmalar.jsonl", "ivedik.org.tr",
                      "https://www.ivedik.org.tr/", "Ivedik OSB"),
    "baskentosb.org.tr": (ROOT / "data" / "baskent" / "firmalar.jsonl", "baskentosb.org.tr",
                          "https://www.baskentosb.org.tr/", "Baskent OSB"),
}


def ensure_source(name: str, url: str) -> str:
    """sources'ta bul veya olustur; source_id dondur."""
    with get_session() as s:
        row = s.execute(
            text("SELECT source_id FROM sources WHERE source_name = :n"),
            {"n": name},
        ).first()
        if row:
            return str(row[0])
        res = s.execute(
            text(
                "INSERT INTO sources (source_name, source_type, url, collection_method, authority_score)"
                " VALUES (:n, 'osb', :u, 'web_scrape', 0.9)"
                " ON CONFLICT DO NOTHING RETURNING source_id"
            ),
            {"n": name, "u": url},
        )
        s.commit()
        r2 = res.fetchone()
        if r2:
            return str(r2[0])
        row = s.execute(
            text("SELECT source_id FROM sources WHERE source_name = :n"),
            {"n": name},
        ).first()
        return str(row[0])


def _content_hash(payload: dict) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _iter(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def ingest(source_key: str, path: Path, domain: str, dry: bool) -> dict:
    recs = list(_iter(path)) if path.exists() else []
    if not recs:
        return {"kaynak": source_key, "okunan": 0, "yazilan": 0, "not": "dosya yok/bos"}
    if dry:
        sid = None
        with get_session() as s:
            row = s.execute(
                text("SELECT source_id FROM sources WHERE source_name = :n"),
                {"n": domain},
            ).first()
            sid = str(row[0]) if row else None
        existing: set = set()
        if sid:
            eng = get_engine()
            with eng.connect() as conn:
                rows = conn.execute(
                    text("SELECT content_hash FROM source_records WHERE source_id = :s"),
                    {"s": sid},
                ).fetchall()
            existing = {r[0] for r in rows}
        yeni = sum(1 for rec in recs if _content_hash(rec) not in existing)
        return {"kaynak": source_key, "okunan": len(recs), "yazilan": yeni}
    sid = ensure_source(domain, f"https://{domain}/")
    eng = get_engine()
    with eng.connect() as conn:
        rows = conn.execute(
            text("SELECT content_hash FROM source_records WHERE source_id = :s"),
            {"s": sid},
        ).fetchall()
    existing = {r[0] for r in rows}
    batch = []
    for rec in recs:
        h = _content_hash(rec)
        if h in existing:
            continue
        existing.add(h)
        batch.append({
            "sid": sid,
            "ext": rec.get("slug"),
            "name": rec.get("unvan"),
            "addr": rec.get("adres"),
            "phone": "; ".join(rec.get("telefonlar") or []),
            "email": "; ".join(rec.get("emailler") or []),
            "web": rec.get("web_sitesi"),
            "vkn": rec.get("vergi_no"),
            "nace": rec.get("sektor"),
            "payload": json.dumps(rec, ensure_ascii=False),
            "hash": h,
        })
    if batch and not dry:
        with eng.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO source_records"
                    " (source_id, external_id, raw_name, raw_address, raw_phone, raw_email,"
                    "  raw_website, raw_tax_number, raw_nace, raw_payload, content_hash)"
                    " VALUES (:sid, :ext, :name, :addr, :phone, :email, :web, :vkn, :nace, :payload, :hash)"
                ),
                batch,
            )
    return {"kaynak": source_key, "okunan": len(recs), "yazilan": len(batch)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", action="store_true", help="sadece say, yazma")
    a = ap.parse_args()
    for key, (path, domain, _url, _lbl) in FILES.items():
        r = ingest(key, path, domain, dry=a.count)
        print(f"{r['kaynak']}: okunan={r['okunan']} yazilacak/yazilan={r['yazilan']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
