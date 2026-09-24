#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Multi-OSB birlesik veriyi DB'ye ingest et (P1-4 son adimi).

data/merged/multi_osb_merged.jsonl -> companies tablosu (idempotent upsert).

Eşleştirme stratejisi:
  1. vergi_no (10 hane) varsa tax_number ile eşleştir
  2. yoksa unvan (LOWER(TRIM(trade_name))) ile eşleştir
  3. hiçbiri yoksa yeni kayıt ekle

Kullanim:
    python scripts/ingest_merged.py              # tam ingest
    python scripts/ingest_merged.py --limit 20   # smoke test
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# Windows konsol/pipe kodlamasi Turkce karakterleri kesebilir; UTF-8'e zorla
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

from sqlalchemy import text  # noqa: E402
from company_master.db.connection import get_engine  # noqa: E402

INPUT_FILE = ROOT / "data" / "merged" / "multi_osb_merged.jsonl"


def has_column(conn, table: str, column: str) -> bool:
    r = conn.execute(
        text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name = :t AND column_name = :c"
        ),
        {"t": table, "c": column},
    ).fetchone()
    return r is not None


def bul(conn, rec: dict, adres_var: bool) -> str | None:
    """VKN -> unvan sirasiyla mevcut kaydi bulur."""
    vkn = rec.get("vergi_no")
    if vkn and len(str(vkn)) == 10:
        r = conn.execute(
            text("SELECT company_id FROM companies WHERE tax_number = :v"),
            {"v": str(vkn)},
        ).fetchone()
        if r:
            return str(r[0])
    unvan = (rec.get("unvan") or "").strip()
    if unvan:
        r = conn.execute(
            text(
                "SELECT company_id FROM companies "
                "WHERE LOWER(TRIM(COALESCE(trade_name, legal_name))) = :u"
            ),
            {"u": unvan.lower()},
        ).fetchone()
        if r:
            return str(r[0])


def main() -> None:
    # Tek-instance kilidi: ayni scriptin iki kopyasi birbirini deadlock'lamasin
    lock = ROOT / "logs" / "ingest_merged.lock"
    if lock.exists():
        print("Baska bir ingest_merged.py calisiyor (lock var). Cikiliyor.", flush=True)
        sys.exit(0)
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_text(str(os.getpid()), encoding="utf-8")

    ap = argparse.ArgumentParser(description="Merged JSONL -> companies ingest")
    ap.add_argument("--limit", type=int, default=0, help="Ilk N kayit (0=tumu)")
    ap.add_argument("--batch", type=int, default=500, help="Commit blogu buyuklugu")
    args = ap.parse_args()

    if not INPUT_FILE.exists():
        print(f"HATA: Girdi yok: {INPUT_FILE} — once multi_osb_merger.py calistirin",
              flush=True)
        sys.exit(1)

    lines = [
        ln for ln in INPUT_FILE.read_text(encoding="utf-8").splitlines() if ln.strip()
    ]
    if args.limit:
        lines = lines[: args.limit]
    print(f"Merged dosya: {len(lines)} kayit islenecek (batch={args.batch})", flush=True)

    inserted = updated = skipped = errors = 0
    engine = get_engine()

    def isle(conn, bas: int, bit: int) -> None:
        nonlocal inserted, updated, skipped, errors
        adres_var = has_column(conn, "companies", "adres")
        # Batch-level timeout: baska ajanin uzun transaction'ina takilmayalim
        conn.execute(text("SET LOCAL statement_timeout = '120s'"))
        for i in range(bas, bit):
            ln = lines[i]
            try:
                rec = json.loads(ln)
                unvan = (rec.get("unvan") or "").strip()[:255]
                if not unvan:
                    skipped += 1
                    continue
                vkn = rec.get("vergi_no")
                vkn = str(vkn) if vkn and len(str(vkn)) == 10 else None
                tel_list = rec.get("telefonlar") or []
                email_list = rec.get("emailler") or []
                p = {
                    "tn": unvan,
                    "vkn": vkn,
                    "nace": rec.get("nace_kod") or None,
                    "phone": str(tel_list[0]) if tel_list else None,
                    "email": str(email_list[0]) if email_list else None,
                    "web": rec.get("web_sitesi") or None,
                    "adres": (rec.get("adres") or "").strip() or None,
                }
                # SAVEPOINT: tek kayit hatasi tum batch'i goturmesin
                with conn.begin_nested():
                    mevcut = bul(conn, rec, adres_var)
                    if mevcut:
                        ekstra = (", adres = COALESCE(adres, :adres)"
                                  if adres_var else "")
                        conn.execute(
                            text(
                                "UPDATE companies SET "
                                "tax_number = COALESCE(tax_number, :vkn), "
                                "nace_code = COALESCE(nace_code, :nace), "
                                "nace_validity = COALESCE(nace_validity, :nace), "
                                "primary_phone = COALESCE(primary_phone, :phone), "
                                "primary_email = COALESCE(primary_email, :email), "
                                "web_sitesi = COALESCE(web_sitesi, :web), "
                                "website_domain = COALESCE(website_domain, :web), "
                                f"updated_at = NOW(){ekstra} "
                                "WHERE company_id = :cid"
                            ),
                            {**p, "cid": mevcut},
                        )
                        updated += 1
                    else:
                        cid = str(uuid.uuid4())
                        cols = ("company_id, legal_name, trade_name, tax_number, "
                                "nace_code, nace_validity, primary_phone, "
                                "primary_email, website_domain, web_sitesi, "
                                "is_ankara, is_osb_member")
                        vals = (":cid, :tn, :tn, :vkn, :nace, :nace, :phone, "
                                ":email, :web, :web, TRUE, TRUE")
                        p2 = {"cid": cid, **p}
                        if adres_var and p["adres"]:
                            cols += ", adres"
                            vals += ", :adres"
                        conn.execute(
                            text(f"INSERT INTO companies ({cols}) VALUES ({vals})"),
                            p2,
                        )
                        inserted += 1
            except Exception as e:  # noqa: BLE001 — kayit bazli izolasyon
                errors += 1
                ad = type(e).__name__
                mesaj = str(e).encode("ascii", errors="replace").decode("ascii")
                print(f"[{i}] HATA ({ad}): {mesaj[:300]}", flush=True)
                # Deadlock/abort/timeout: transaction iptal olur, batch terk edilir
                if ad in ("DeadlockDetected", "InFailedSqlTransaction",
                          "PendingRollbackError", "OperationalError"):
                    print("  -> transaction iptal, batch kalani atlanıyor.",
                          flush=True)
                    break
                if errors >= 50:
                    print("50 hatayi asti, durduruluyor.", flush=True)
                    break

    toplam = len(lines)
    tekrar: list[tuple[int, int]] = []
    for bas in range(0, toplam, args.batch):
        bit = min(bas + args.batch, toplam)
        try:
            with engine.begin() as conn:
                isle(conn, bas, bit)
        except Exception as e:  # noqa: BLE001 — batch hatasi izole edilir
            errors += 1
            tekrar.append((bas, bit))
            mesaj = str(e).encode("ascii", errors="replace").decode("ascii")
            print(f"[BATCH {bas}-{bit}] batch hatasi: {mesaj[:200]}", flush=True)
        print(f"  ilerleme: {bit}/{toplam} (eklendi={inserted} "
              f"guncellendi={updated} hata={errors})", flush=True)

    # Deadlock/kilit kurbanı batch'ler: idempotent oldugu icin bir kez daha dene
    if tekrar:
        print(f"\n{len(tekrar)} batch tekrar deneniyor...", flush=True)
        for bas, bit in tekrar:
            try:
                with engine.begin() as conn:
                    isle(conn, bas, bit)
            except Exception as e:  # noqa: BLE001
                mesaj = str(e).encode("ascii", errors="replace").decode("ascii")
                print(f"[TEKRAR {bas}-{bit}] basarisiz: {mesaj[:200]}", flush=True)
            print(f"  tekrar bitti: {bit}/{toplam}", flush=True)

    print("\nMerged ingest tamamlandi:", flush=True)
    print(f"  Yeni eklendi : {inserted}", flush=True)
    print(f"  Guncellendi  : {updated}", flush=True)
    print(f"  Atlandi      : {skipped}", flush=True)
    print(f"  Hata         : {errors}", flush=True)
    try:
        lock.unlink()
    except OSError:
        pass


if __name__ == "__main__":
    main()
