# -*- coding: utf-8 -*-
"""Cross-source entity resolution (vergi_no birincil, unvan fuzzy yedek)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EntityRecord:
    source: str = ""
    vergi_no: Optional[str] = None
    unvan: str = ""
    nace_code: Optional[str] = None
    nace_name_tr: Optional[str] = None
    sektor: Optional[str] = None
    telefonler: list[str] = field(default_factory=list)
    emailler: list[str] = field(default_factory=list)
    adres: Optional[str] = None
    web_sitesi: Optional[str] = None
    vergi_dairesi: Optional[str] = None
    mersis_no: Optional[str] = None
    raw: dict = field(default_factory=dict)


SOURCE_PRIORITY = ["mersis", "gib", "aso", "odtu_teknokent", "ostim", "diger"]


def merge_entities(records: list[EntityRecord]) -> EntityRecord:
    if not records:
        raise ValueError("Bos liste")
    records_sorted = sorted(records, key=lambda r: SOURCE_PRIORITY.index(r.source) if r.source in SOURCE_PRIORITY else 99)
    base = EntityRecord(source="merged", unvan=records_sorted[0].unvan)
    for r in records_sorted:
        for f in ["vergi_no", "nace_code", "nace_name_tr", "sektor", "adres", "web_sitesi", "vergi_dairesi", "mersis_no"]:
            if getattr(r, f) and not getattr(base, f):
                setattr(base, f, getattr(r, f))
        for f in ["telefonler", "emailler"]:
            existing = set(getattr(base, f, []))
            for v in getattr(r, f, []):
                if v not in existing:
                    existing.add(v)
            setattr(base, f, list(existing))
    return base


def find_dupes(records: list[EntityRecord]) -> list[list[EntityRecord]]:
    groups: dict[str, list[EntityRecord]] = {}
    for r in records:
        if r.vergi_no:
            key = f"vkn:{r.vergi_no}"
        elif r.unvan:
            key = f"unvan:{r.unvan.lower().strip()}"
        else:
            continue
        groups.setdefault(key, []).append(r)
    return [g for g in groups.values() if len(g) > 1]
