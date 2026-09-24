#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NACE Phase 2: (1) Kalan sektorsuz firmalara yeni nace_bul() ile NACE tahmini,
(2) JSONL'deki nace_code'u DB'ye senkronize et.
"""
import json
import sys
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.db.connection import get_database_url  # noqa: E402
from company_master.etl.nace_mapper import nace_bul  # noqa: E402

DATA = ROOT / "data" / "ostim" / "firmalar_full.jsonl"


def get_conn():
    url = get_database_url()
    # SQLAlchemy dialect prefix'ini kaldir; psycopg3 URI'yi dogrudan kabul eder.
    if url.startswith("postgresql+psycopg://"):
        url = url.replace("postgresql+psycopg://", "postgresql://", 1)
    return psycopg.connect(url, prepare_threshold=None, autocommit=True)


def main():
    # ---- Faz 1: Kalan firmalara yeni matcher ile NACE tahmini ----
    records = []
    with open(DATA, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    print(f"JSONL toplam: {len(records)}")

    eklenen = 0
    for rec in records:
        if rec.get("nace_code"):
            continue
        unvan = rec.get("unvan", "")
        sektor = rec.get("sektor")
        matches = nace_bul(unvan or "", None, sektor)
        if matches:
            best = matches[0]
            rec["nace_code"] = best.code
            rec["nace_name_tr"] = best.name_tr
            rec["nace_confidence"] = (
                "high" if best.relevance == "Yüksek" else "medium"
            )
            rec["nace_source"] = "unvan_taxonomy"
            eklenen += 1

    nace_dolu = sum(1 for r in records if r.get("nace_code"))
    print(f"Yeni matcher ile eklenen: {eklenen}")
    print(f"JSONL NACE doluluk: {nace_dolu}/{len(records)} ({100.0 * nace_dolu / max(len(records), 1):.1f}%)")

    # Güncellenen kayıtları yaz (atomik)
    tmp = DATA.with_suffix(".tmp.jsonl")
    with open(tmp, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    tmp.replace(DATA)
    print(f"JSONL guncellendi: {DATA.stat().st_size:,} bytes")

    # ---- Faz 2: DB senkronizasyonu (batch: COPY + tek UPDATE JOIN) ----
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM companies")
        total = cur.fetchone()[0]
        cur.execute(
            "SELECT COUNT(*) FROM companies "
            "WHERE nace_code IS NOT NULL AND nace_code <> ''"
        )
        dolu_db = cur.fetchone()[0]
        print(f"DB once: {dolu_db}/{total} NACE dolu")

        # Staging tablosu (kalici): pgbouncer transaction pooling temp
        # tablolari backend'ler arasinda tasıyamadigi icin kalici kullanilir.
        cur.execute("DROP TABLE IF EXISTS _tmp_nace_stage")
        cur.execute(
            "CREATE TABLE _tmp_nace_stage (unvan TEXT, nace_code TEXT)"
        )
        rows = [
            ((rec.get("unvan") or "").strip(), rec["nace_code"])
            for rec in records
            if rec.get("nace_code") and (rec.get("unvan") or "").strip()
        ]
        with cur.copy(
            "COPY _tmp_nace_stage (unvan, nace_code) FROM STDIN"
        ) as copy:
            for unvan, code in rows:
                copy.write_row((unvan, code))
        print(f"Temp tabloya yuklenen: {len(rows)}")

        # Tek UPDATE ile esleseni guncelle
        cur.execute(
            "UPDATE companies c SET nace_code = t.nace_code, "
            "nace_source = 'predicted' "
            "FROM _tmp_nace_stage t "
            "WHERE c.legal_name = t.unvan "
            "AND (c.nace_code IS NULL OR c.nace_code = '')"
        )
        print(f"DB guncellenen: {cur.rowcount}")

        cur.execute(
            "SELECT COUNT(*) FROM companies "
            "WHERE nace_code IS NOT NULL AND nace_code <> ''"
        )
        dolu_db2 = cur.fetchone()[0]
        print(
            f"DB son: {dolu_db2}/{total} "
            f"({100.0 * dolu_db2 / max(total, 1):.1f}%) NACE dolu"
        )

    conn.close()
    # Staging tablosunu temizle (baglanti bagimsiz)
    conn2 = get_conn()
    with conn2.cursor() as cur2:
        cur2.execute("DROP TABLE IF EXISTS _tmp_nace_stage")
    conn2.close()
    print("NACE Phase 2 tamam!")


if __name__ == "__main__":
    main()
