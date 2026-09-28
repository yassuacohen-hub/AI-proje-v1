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


# D-261 / BORC-DEDUP-KAYNAK-01: hash YALNIZ kimlik alanlarindan hesaplanir.
# Onceki surum tum kaydi hashliyordu; icinde `cekilme_tarihi` (mikrosaniyeli)
# vardi, bu yuzden ayni firma her kosuda yeni hash uretip yeni satir aciyordu
# (ivedik: 3134 satir -> 14 benzersiz).
KIMLIK_ALANLARI = (
    "unvan", "adres", "telefonlar", "emailler", "web_sitesi",
    "vergi_no", "sektor", "slug",
)


def _content_hash(payload: dict) -> str:
    kimlik = {k: payload.get(k) for k in KIMLIK_ALANLARI}
    return hashlib.sha256(
        json.dumps(kimlik, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _external_id(payload: dict, h: str) -> str:
    """slug yoksa hash'ten turetilmis kimlik. baskentosb slug uretmiyordu;
    external_id NULL kalinca UNIQUE(source_id, external_id) korumasi calismaz."""
    return payload.get("slug") or f"auto:{h[:32]}"


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
            "ext": _external_id(rec, h),
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
            # Goc 0031 UNIQUE(source_id, external_id) koydu. content_hash suzgeci
            # yalniz hash'e bakar: ayni slug'in adresi degisirse yeni hash cikar,
            # duz INSERT kisiti ihlal eder ve TUM kosu coker. Ayni dis kimlik =
            # ayni firma demek; yeni satir degil, mevcut satir TAZELENIR.
            conn.execute(
                text(
                    "INSERT INTO source_records"
                    " (source_id, external_id, raw_name, raw_address, raw_phone, raw_email,"
                    "  raw_website, raw_tax_number, raw_nace, raw_payload, content_hash)"
                    " VALUES (:sid, :ext, :name, :addr, :phone, :email, :web, :vkn, :nace, :payload, :hash)"
                    " ON CONFLICT (source_id, external_id) DO UPDATE SET"
                    "   raw_name = EXCLUDED.raw_name,"
                    "   raw_address = EXCLUDED.raw_address,"
                    "   raw_phone = EXCLUDED.raw_phone,"
                    "   raw_email = EXCLUDED.raw_email,"
                    "   raw_website = EXCLUDED.raw_website,"
                    "   raw_tax_number = EXCLUDED.raw_tax_number,"
                    "   raw_nace = EXCLUDED.raw_nace,"
                    "   raw_payload = EXCLUDED.raw_payload,"
                    "   content_hash = EXCLUDED.content_hash"
                    " WHERE source_records.content_hash IS DISTINCT FROM EXCLUDED.content_hash"
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
