#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Entity resolution with rapidfuzz optimization."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from rapidfuzz import fuzz

from sqlalchemy import text

from ..db.connection import get_engine


@dataclass
class ResolutionResult:
    processed: int = 0
    exact_vkn: int = 0
    fuzzy_name: int = 0
    new_company: int = 0
    errors: List[str] = field(default_factory=list)


def run_entity_resolution(limit: Optional[int] = None, threshold: float = 0.80) -> ResolutionResult:
    """source_records -> companies entity resolution (rapidfuzz ile).
    
    1. VKN exact match (100% confidence)
    2. Name fuzzy match (rapidfuzz, threshold >= 0.80)
    """
    res = ResolutionResult()
    engine = get_engine()

    with engine.begin() as conn:
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

        companies = conn.execute(
            text("SELECT company_id, tax_number, legal_name FROM companies")
        ).mappings().all()
        
        vkn_index = {c["tax_number"]: c for c in companies if c["tax_number"]}
        name_list = [(c["company_id"], c["legal_name"]) for c in companies]

        batch = []
        for row in rows:
            src_id = row["source_record_id"]
            vkn = row["raw_tax_number"]
            name = (row["raw_name"] or "").strip()
            
            if not name:
                continue

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

            best_score = 0.0
            best_cid = None
            for cid, cname in name_list:
                score = fuzz.ratio(name.lower(), cname.lower()) / 100
                if score > best_score:
                    best_score = score
                    best_cid = cid

            if best_score >= threshold:
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
