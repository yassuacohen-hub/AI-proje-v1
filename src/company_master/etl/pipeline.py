"""ETL pipeline ana giriş noktası.

V10/03_mimari/01_etl_mimarisi.md akışını uygular:

    SOURCE → RAW INGESTION → NORMALIZATION → VALIDATION →
    ENTITY RESOLUTION → COMPANY MASTER

Şu an gerçekleştirilen adım: OSTİM jsonl → `source_records` (RAW INGESTION).
Sonraki adımlar (normalize + entity resolution) ayrı modüller olarak eklenecek.

Kullanım:
    python -m company_master.etl.pipeline                 # hepsini çalıştır
    python -m company_master.etl.pipeline --count         # kaç kayıt yazılacak
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy import text

from ..db.connection import get_engine, get_session

# OSTİM scraped veri (Kilo Code tarafından üretilmiş)
OSTIM_JSONL = Path(__file__).resolve().parents[4] / "data" / "ostim" / "firmalar_full.jsonl"

OSB_NAME = "OSTİM OSB"


@dataclass
class IngestionResult:
    source_id: str | None = None
    fetched_count: int = 0
    accepted_count: int = 0
    rejected_count: int = 0
    errors: List[str] = field(default_factory=list)


def ensure_source() -> str:
    """sources tablosunda ostim.org.tr'yi bul veya oluştur; source_id döndür."""
    with get_session() as s:
        row = s.execute(
            text("SELECT source_id FROM sources WHERE source_name = 'ostim.org.tr'")
        ).first()
        if row:
            return str(row[0])
        result = s.execute(
            text(
                """INSERT INTO sources (source_name, source_type, url, collection_method, authority_score)
                VALUES ('ostim.org.tr', 'osb', 'https://www.ostim.org.tr/', 'web_scrape', 0.9)
                ON CONFLICT DO NOTHING RETURNING source_id"""
            )
        )
        s.commit()
        row = result.fetchone()
        if row:
            return str(row[0])
        row = s.execute(
            text("SELECT source_id FROM sources WHERE source_name = 'ostim.org.tr'")
        ).first()
        return str(row[0])


def _content_hash(payload: Dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _iter_ostim_records(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def ingest_source(source_name: str = "ostim.org.tr") -> IngestionResult:
    """OSTİM jsonl kayıtlarını source_records'a yazar."""
    res = IngestionResult()
    if not OSTIM_JSONL.exists():
        res.errors.append(f"Veri dosyası yok: {OSTIM_JSONL}")
        return res

    source_id = ensure_source()
    res.source_id = source_id

    engine = get_engine()
    existing = set()
    with engine.begin() as conn:
        rows = conn.execute(
            text("SELECT content_hash FROM source_records WHERE source_id = :sid"),
            {"sid": source_id},
        ).fetchall()
        existing = {r[0] for r in rows}

    # Yeni kayıtları topla, aynı content_hash zaten varsa atla
    batch = []
    for rec in _iter_ostim_records(OSTIM_JSONL):
        res.fetched_count += 1
        h = _content_hash(rec)
        if h in existing:
            existing.add(h)
            continue
        existing.add(h)
        batch.append(
            {
                "sid": source_id,
                "ext": rec.get("slug"),
                "name": rec.get("unvan"),
                "addr": rec.get("adres"),
                "phone": "; ".join(rec.get("telefonler") or []),
                "email": "; ".join(rec.get("emailler") or []),
                "web": rec.get("web_sitesi"),
                "vkn": rec.get("vergi_no"),
                "nace": rec.get("nace_code"),
                "payload": json.dumps(rec, ensure_ascii=False),
                "hash": h,
            }
        )

    # Toplu (bulk) yaz; psycopg executemany ile tek ağ turu
    if batch:
        with engine.begin() as conn:
            conn.execute(
                text(
                    """INSERT INTO source_records
                    (source_id, external_id, raw_name, raw_address, raw_phone, raw_email,
                     raw_website, raw_tax_number, raw_nace, raw_payload, content_hash)
                    VALUES (:sid, :ext, :name, :addr, :phone, :email, :web, :vkn, :nace, :payload, :hash)"""
                ),
                batch,
            )

    res.accepted_count = len(batch)
    return res


def normalize(raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ham kayıtları companies tablosuna yazılmaya hazır hale getirir.

    Yalnızca zorunlu alanı (legal_name = unvan) sağlayanları normalize eder;
    geçersiz kayıtları atlar.
    """
    out: List[Dict[str, Any]] = []
    for r in raw_records:
        name = (r.get("raw_name") or r.get("unvan") or "").strip()
        if not name:
            continue
        phones = (r.get("raw_phone") or "").split("; ")
        out.append(
            {
                "legal_name": name,
                "website_domain": r.get("raw_website"),
                "primary_phone": phones[0] if phones else None,
                "primary_email": r.get("raw_email"),
                "tax_number": r.get("raw_tax_number"),
            }
        )
    return out


def main() -> int:
    res = ingest_source()
    print(f"Kaynak: {res.source_id}")
    print(f"Okunan: {res.fetched_count}")
    print(f"Yazılan: {res.accepted_count}")
    print(f"Reddedilen: {res.rejected_count}")
    for e in res.errors:
        print(f"HATA: {e}")
    return 0 if not res.errors else 1


if __name__ == "__main__":
    sys.exit(main())