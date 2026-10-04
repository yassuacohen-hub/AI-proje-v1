# -*- coding: utf-8 -*-
"""VERI-02 kapisi: ihale scraper'in SQL kolonlari canli semayla birebir ayni.

[[VERI-NACE-COKLU-01]] ve [[VERI-RISK-MOTORU-01]] teslimlerinde ortaya cikan
sekizinci yari-goc varyanti (D-258/4 deseni): tablo dogrusu, kod yanlis.

  - 0043 `il` ASCII-Turkce kolonu `province` yapti, sema dogru.
  - osb_tender_monitor.py `il = :il` yazmaya devam ediyordu; ilk INSERT'te
    UndefinedColumn ile patlardi. Dosya hic calismamis oldugu icin teslim
    "yesil test" gorunuyordu.

Bu test canli semayi okur. Canli DB erisilemezse ATLAR (D-245: erisememek
"temiz" demek degil, "olculemedi" demektir).
"""
from __future__ import annotations

import pathlib
import re
import sys

KOK = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "src"))

SCRAPER = KOK / "src" / "company_master" / "etl" / "scrapers" / "osb_tender_monitor.py"
TABLO = "ihale_ilanlari"

# Kodda yazilmayan ama semada olan kolonlar: sunucu tarafinden uretilir,
# INSERT'te yazilmamasi dogru (ilan_id, created_at, updated_at).
SUNUCU_KOLONLARI = {"ilan_id", "created_at", "updated_at"}


def _kod_kolonlari() -> list[str]:
    metin = SCRAPER.read_text(encoding="utf-8")
    bloklar = re.findall(rf"INSERT INTO {TABLO}\s*\(([^)]*)\)", metin, re.S)
    assert bloklar, f"{TABLO} INSERT bulunamadi ({SCRAPER.name})"
    return [k.strip() for k in bloklar[0].split(",") if k.strip()]


def _sema_kolonlari() -> list[str]:
    from sqlalchemy import text

    from company_master.db.connection import get_engine

    with get_engine().connect() as conn:
        satirlar = conn.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = :t AND table_schema = 'public'"),
            {"t": TABLO}).fetchall()
    return [r[0] for r in satirlar]


def test_kod_kolonlari_sema_tanimli() -> None:
    """Koddaki her kolon canli semada olmali; yoksa ilk INSERT patlar."""
    kod = set(_kod_kolonlari())
    sema = set(_sema_kolonlari())
    yok = sorted(kod - sema)
    assert not yok, (
        f"{TABLO}: kodda yazan ama semada olmayan kolon -> UndefinedColumn "
        f"(D-258/4 yari-goc): {yok}"
    )


def test_ascii_turkce_kolon_kalmadi() -> None:
    """Turkce ASCII sutun kodu semayla birebir ayni olmali.

    `il` -> `province` cevrilmesi 0043'te yapildi; kodda kalmasi yarim goc.
    """
    kod = _kod_kolonlari()
    assert "il" not in kod, (
        "ihale_ilanlari.il semada yok (0043 province'a cevirdi); "
        "kod hala 'il' yaziyor - INSERT patlar")
    assert "province" in kod, "province kolonu INSERT'te yok"
    assert "ilan.il" not in SCRAPER.read_text(encoding="utf-8"), (
        "IhaleIlan.il alani semayla uyusmuyor (province olmali)")


def test_kod_semada_butun_istenen_kolonlari_yaziyor() -> None:
    """Sema kolonlarindan sunucu disi hicbiri eksik olmamali."""
    kod = set(_kod_kolonlari())
    sema = set(_sema_kolonlari())
    eksik = sorted(sema - kod - SUNUCU_KOLONLARI)
    assert not eksik, (
        f"{TABLO}: semada var ama INSERT yazmiyor -> sessiz veri kaybi: {eksik}")


def test_insert_ve_update_kolonlari_ayni() -> None:
    """UPDATE ve INSERT ayni kolonlari yazmali; aksi halde yenileme yarim."""
    metin = SCRAPER.read_text(encoding="utf-8")
    ins = [k.strip() for k in re.findall(
        rf"INSERT INTO {TABLO}\s*\(([^)]*)\)", metin, re.S)[0].split(",") if k.strip()]
    upd = [k.strip() for k in re.findall(
        rf"UPDATE {TABLO} SET(.*?)WHERE", metin, re.S)[0].split(",")
        if "=" in k]
    upd = [u.split("=")[0].strip() for u in upd]
    # updated_at UPDATE'te NOW() ile yazilir, INSERT'te sunucu doldurur.
    fark = set(upd) - set(ins) - {"updated_at"}
    assert not fark, (
        f"UPDATE yaziyor ama INSERT etmiyor -> yenileme kaybolur: {sorted(fark)}")


if __name__ == "__main__":
    sys.exit(0 if (__import__("pytest").main([__file__, "-q"]) == 0) else 1)
