"""PostgreSQL Full Text Search motoru.

`idx_companies_legal_name_trgm` (GIN trigram) kullanarak hızlı unvan araması yapar.
ILIKE '%..%' sorguları pg_trgm GIN index ile desteklenir; sonuçlar similarity'ye göre sıralanır.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from ..db.connection import get_engine


def search_companies(query: str, limit: int = 20) -> List[Dict]:
    """Trigram tabanlı benzerlik araması (GIN). Kısmi ve kısa sorguları da bulur."""
    engine = get_engine()
    sql = text("""
        SELECT company_id, legal_name, tax_number, website_domain
        FROM companies
        WHERE legal_name ILIKE '%' || :q || '%'
        ORDER BY similarity(legal_name, :q) DESC
        LIMIT :limit
    """)
    with engine.connect() as conn:
        res = conn.execute(sql, {"q": query, "limit": limit}).fetchall()
        return [{"company_id": r[0], "legal_name": r[1], "tax_number": r[2], "website_domain": r[3]} for r in res]


def _as_list(value: Any) -> list:
    if isinstance(value, list):
        return [str(v) for v in value if v]
    if isinstance(value, str) and value.strip():
        return [p.strip() for p in value.split(";") if p.strip()]
    return []


def _row_to_dashboard(row: Dict[str, Any]) -> Dict[str, Any]:
    payload = row.get("raw_payload") or {}
    if not isinstance(payload, dict):
        payload = {}
    phones = _as_list(payload.get("telefonler")) or _as_list(row.get("raw_phone")) or _as_list(row.get("primary_phone"))
    emails = _as_list(payload.get("emailler")) or _as_list(row.get("raw_email")) or _as_list(row.get("primary_email"))
    web = (
        payload.get("web_sitesi")
        or row.get("web_sitesi")
        or row.get("website_domain")
        or row.get("raw_website")
    )
    source_name = row.get("source_name") or payload.get("kaynak") or "DB"
    return {
        "company_id": str(row["company_id"]) if row.get("company_id") else None,
        "unvan": row.get("legal_name") or payload.get("unvan") or "",
        "sektor": payload.get("sektor") or row.get("sektor"),
        "telefonler": phones,
        "emailler": emails,
        "web_sitesi": web,
        "adres": payload.get("adres") or row.get("raw_address"),
        "sosyal_medya": payload.get("sosyal_medya") or {},
        "vergi_no": payload.get("vergi_no") or row.get("tax_number") or row.get("vergi_no"),
        "osb_parsel": payload.get("osb_parsel") or row.get("osb_parsel"),
        "nace_code": payload.get("nace_code") or row.get("raw_nace"),
        "kaynak_tipi": source_name,
        "data_quality_score": row.get("data_quality_score"),
    }


def fetch_dashboard_companies(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """companies + source_records birleşimi; Streamlit dashboard şemasına uygun."""
    engine = get_engine()
    sql = """
        SELECT
            c.company_id,
            c.legal_name,
            c.website_domain,
            c.web_sitesi,
            c.primary_phone,
            c.primary_email,
            c.tax_number,
            c.vergi_no,
            c.osb_parsel,
            c.data_quality_score,
            sr.raw_phone,
            sr.raw_email,
            sr.raw_address,
            sr.raw_website,
            sr.raw_nace,
            sr.raw_payload,
            src.source_name
        FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        LEFT JOIN sources src ON src.source_id = sr.source_id
        ORDER BY c.legal_name
    """
    if limit:
        sql += " LIMIT :limit"
    with engine.connect() as conn:
        params = {"limit": limit} if limit else {}
        rows = conn.execute(text(sql), params).mappings().all()
        return [_row_to_dashboard(dict(r)) for r in rows]


def _data_root() -> Path:
    here = Path(__file__).resolve()
    for candidate in [here.parent, *here.parents]:
        if (candidate / "data" / "ostim").exists():
            return candidate
    return here.parents[3]


def search_jsonl(query: str, unvan: str = "", nace_code: str = "", limit: int = 20) -> list[dict]:
    """JSONL dosyalarından firmaları filtrele (DB aktarımı öncesi / fallback)."""
    ROOT = _data_root()
    files = [
        ROOT / "data" / "ostim" / "firmalar_full.jsonl",
        ROOT / "data" / "aso" / "aso_full.jsonl",
    ]
    results = []
    for file in files:
        if not file.exists():
            continue
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                rec_unvan = (rec.get("unvan") or rec.get("firma_unvan") or "").upper()
                if query and query.upper() not in rec_unvan:
                    continue
                if unvan and unvan.upper() not in rec_unvan:
                    continue
                if nace_code and (rec.get("nace_code") or rec.get("naceKod")) != nace_code:
                    continue
                results.append(rec)
                if len(results) >= limit:
                    return results
    return results


def count_ankara_osb_companies() -> int:
    """Ankara + OSB filtresine uyan toplam firma sayisi."""
    engine = get_engine()
    sql_text = text("""
        SELECT COUNT(*) FROM companies
        WHERE is_ankara = TRUE AND is_osb_member = TRUE
    """)
    with engine.connect() as conn:
        return int(conn.execute(sql_text).scalar() or 0)


def fetch_filtered_companies(
    q: str = "",
    sectors=None,
    kalite_min: float = 0,
    kalite_max: float = 100,
    has_phone: bool = False,
    has_email: bool = False,
    has_web: bool = False,
    limit: int = 50,
    offset: int = 0,
):
    """DB seviyesinde filtrelenmis firma listesi (parametreli sorgu)."""
    engine = get_engine()
    where = ["c.is_ankara = TRUE", "c.is_osb_member = TRUE"]
    params = {"limit": limit, "offset": offset, "kalite_min": kalite_min, "kalite_max": kalite_max}
    if q and q.strip():
        where.append("(c.legal_name ILIKE '%' || :q || '%' OR sr.raw_payload->>'unvan' ILIKE '%' || :q || '%')")
        params["q"] = q.strip()
    if sectors:
        where.append("(sr.raw_payload->>'sektor') = ANY(:sectors)")
        params["sectors"] = list(sectors)
    if has_phone:
        where.append("((c.primary_phone IS NOT NULL AND c.primary_phone <> '') OR (sr.raw_phone IS NOT NULL AND sr.raw_phone <> ''))")
    if has_email:
        where.append("((c.primary_email IS NOT NULL AND c.primary_email <> '') OR (sr.raw_email IS NOT NULL AND sr.raw_email <> ''))")
    if has_web:
        where.append("((c.website_domain IS NOT NULL AND c.website_domain <> '') OR (c.web_sitesi IS NOT NULL AND c.web_sitesi <> '') OR (sr.raw_website IS NOT NULL AND sr.raw_website <> ''))")
    if has_phone:
        where.append("((c.primary_phone IS NOT NULL AND c.primary_phone <> "") OR (sr.raw_phone IS NOT NULL AND sr.raw_phone <> ""))")
    if has_email:
        where.append("((c.primary_email IS NOT NULL AND c.primary_email <> "") OR (sr.raw_email IS NOT NULL AND sr.raw_email <> ""))")
    if has_web:
        where.append("((c.website_domain IS NOT NULL AND c.website_domain <> "") OR (c.web_sitesi IS NOT NULL AND c.web_sitesi <> "") OR (sr.raw_website IS NOT NULL AND sr.raw_website <> ""))")
    where.append("COALESCE(c.data_quality_score, 0) >= :kalite_min")
    where.append("COALESCE(c.data_quality_score, 0) <= :kalite_max")
    sql = (
        "SELECT c.company_id, c.legal_name, c.website_domain, c.web_sitesi, "
        "c.primary_phone, c.primary_email, c.tax_number, c.vergi_no, "
        "c.osb_parsel, c.data_quality_score, "
        "sr.raw_phone, sr.raw_email, sr.raw_address, sr.raw_website, "
        "sr.raw_nace, sr.raw_payload, src.source_name "
        "FROM companies c "
        "LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id "
        "LEFT JOIN sources src ON src.source_id = sr.source_id "
        "WHERE " + " AND ".join(where) + " "
        "ORDER BY c.legal_name LIMIT :limit OFFSET :offset"
    )
    with engine.connect() as conn:
        rows = conn.execute(text(sql), params).mappings().all()
        return [_row_to_dashboard(dict(r)) for r in rows]
