"""Entity Resolution — Companies tablosu ile entegre.

VKN exact match → name fuzzy match → entity_resolution tablosuna yazar.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import List, Dict, Optional

from sqlalchemy import text

from ..db.connection import get_engine


@dataclass
class ResolutionResult:
    processed: int = 0
    exact_vkn: int = 0
    fuzzy_name: int = 0
    new_company: int = 0
    errors: List[str] = field(default_factory=list)


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def run_entity_resolution(limit: Optional[int] = None) -> ResolutionResult:
    """source_records -> companies entity resolution çalıştırır.
    
    İşlenmemiş source_record'ları alır:
    1. tax_number (VKN) exact match varsa -> matched
    2. legal_name fuzzy match (>=0.85) varsa -> possible_match
    3. Hiçbiri yoksa -> new_company
    Sonuçları entity_resolution tablosuna yazar.
    """
    res = ResolutionResult()
    engine = get_engine()

    with engine.begin() as conn:
        # Henüz resolve edilmemiş source_record'ları al
        sql = text("""
            SELECT sr.source_record_id, sr.raw_tax_number, sr.raw_name, sr.raw_payload
            FROM source_records sr
            LEFT JOIN entity_resolution er ON er.source_record_id = sr.source_record_id
            WHERE er.resolution_id IS NULL
            ORDER BY sr.collected_at
        """)
        rows = conn.execute(sql).mappings().all()
        if limit:
            rows = rows[:limit]

        res.processed = len(rows)
        if not rows:
            return res

        # Tüm companies'i bir kez çek (VKN ve legal_name için)
        companies = conn.execute(
            text("SELECT company_id, tax_number, legal_name FROM companies WHERE tax_number IS NOT NULL")
        ).mappings().all()
        
        # VKN index
        vkn_index = {c["tax_number"]: c for c in companies if c["tax_number"]}
        # Name list for fuzzy
        name_list = [(c["company_id"], c["legal_name"]) for c in companies]

        batch = []
        for row in rows:
            src_id = row["source_record_id"]
            vkn = row["raw_tax_number"]
            name = (row["raw_name"] or "").strip()
            
            if not name:
                continue

            # 1. Exact VKN match
            if vkn and vkn in vkn_index:
                match = vkn_index[vkn]
                batch.append({
                    "source_record_id": src_id,
                    "company_id": match["company_id"],
                    "match_score": 100.0,
                    "match_method": "vkn_exact",
                    "decision": "matched",
                })
                res.exact_vkn += 1
                continue

            # 2. Fuzzy name match
            best_score = 0.0
            best_cid = None
            for cid, cname in name_list:
                score = _similarity(name, cname)
                if score > best_score:
                    best_score = score
                    best_cid = cid

            if best_score >= 0.85:
                batch.append({
                    "source_record_id": src_id,
                    "company_id": best_cid,
                    "match_score": round(best_score * 100, 2),
                    "match_method": "name_fuzzy",
                    "decision": "possible_match",
                })
                res.fuzzy_name += 1
            else:
                batch.append({
                    "source_record_id": src_id,
                    "company_id": None,
                    "match_score": 0.0,
                    "match_method": "name_fuzzy",
                    "decision": "new_company",
                })
                res.new_company += 1

        if batch:
            conn.execute(
                text("""
                    INSERT INTO entity_resolution
                    (source_record_id, company_id, match_score, match_method, decision)
                    VALUES
                    (:source_record_id, :company_id, :match_score, :match_method, :decision)
                """),
                batch,
            )

    return res


if __name__ == "__main__":
    import sys
    res = run_entity_resolution()
    print(f"Processed: {res.processed}")
    print(f"VKN exact: {res.exact_vkn}")
    print(f"Fuzzy name: {res.fuzzy_name}")
    print(f"New company: {res.new_company}")
    for e in res.errors:
        print(f"ERROR: {e}")
    sys.exit(0 if not res.errors else 1)