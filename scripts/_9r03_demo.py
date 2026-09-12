#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""9R-03 Demo: Apify pilot JSONL uzerinde 9Router chat tabanli zenginlestirme.

Apify pilot verisi  (data/job_intelligence/apify_run-*.jsonl) icindeki ilanlari
ChatEnricher ile zenginlestirir (sektor + pozisyon + skills). 9Router tünel
canliysa chat kullanilir; degilse/fail ise regex tabanli fallback devreye girer.

Kullanim:
    python scripts/_9r03_demo.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Windows cp1254 konsolunda Türkçe/özel karakter encode hatası almamak için
# stdout'u UTF-8'e sabitle (kontrol karakterlerini de tolere et).
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.intelligence.job_intelligence.pipeline.chat_enricher import (  # noqa: E402
    build_default_enricher,
)
from company_master.intelligence.job_intelligence.pipeline.analyzer import (  # noqa: E402
    ENRICH_SKILL_KEYWORDS,
)


def _jsonl_oku(path: Path) -> list[dict]:
    """JSONL dosyasini satirlari sozluk olarak okur."""
    rows: list[dict] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def main() -> int:
    data_dir = ROOT / "data" / "job_intelligence"
    dosyalar = sorted(data_dir.glob("apify_run-*.jsonl"))
    if not dosyalar:
        print(f"[9R-03] Veri bulunamadi: {data_dir}/apify_run-*.jsonl")
        return 1

    records: list[dict] = []
    kaynak_dosya: dict[str, str] = {}
    for p in dosyalar:
        rows = _jsonl_oku(p)
        records.extend(rows)
        for r in rows:
            kaynak_dosya.setdefault(json.dumps(r, ensure_ascii=False), p.name)
        print(f"[9R-03] {p.name}: {len(rows)} ilan okundu")

    print(f"[9R-03] Toplam {len(records)} ilan zenginlestiriliyor...\n")
    if not records:
        return 1

    enricher = build_default_enricher(skill_keywords=ENRICH_SKILL_KEYWORDS)
    print(f"[9R-03] Enricher available={enricher.available}")

    sonuclar = enricher.enrich_many(records)

    chat_sayisi = sum(1 for r in sonuclar if r.kaynak == "chat")
    fallback_sayisi = sum(1 for r in sonuclar if r.kaynak == "fallback")
    hata_sayisi = sum(1 for r in sonuclar if r.hata)

    print("\n================ ISTATISTIK ================")
    print(f"İlan: {len(sonuclar)}  |  Chat: {chat_sayisi}  |  Fallback: {fallback_sayisi}")
    if hata_sayisi:
        print(f"Not: {hata_sayisi} kayitta hata bilgisi var (fallback uygulandi).")
    print("=============================================\n")

    for posting, res in zip(records, sonuclar):
        dosya = kaynak_dosya.get(json.dumps(posting, ensure_ascii=False), "?")
        baslik = posting.get("title") or posting.get("position") or "(basliksiz)"
        print(f"--- [{dosya}] Baslik: {baslik!r}")
        print(f"    Kaynak : {res.kaynak}"
              + (f"  (hata: {res.hata})" if res.hata else ""))
        print(f"    Sektor : {res.sektor}")
        print(f"    Pozisyon: {res.pozisyon or '-'}")
        skills = ", ".join(res.skills) if res.skills else "-"
        print(f"    Skills : {skills}")

    # Kaynak dagilimi ozeti
    from collections import Counter
    sektor_dagitimi = Counter(r.sektor for r in sonuclar)
    print("\n================ SEKTOR DAGILIMI ================")
    for sektor, sayi in sektor_dagitimi.most_common():
        print(f"  {sayi:<3} {sektor}")
    print("==================================================")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())