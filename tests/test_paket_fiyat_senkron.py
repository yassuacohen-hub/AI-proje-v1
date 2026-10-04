# -*- coding: utf-8 -*-
"""VERI-PAKET-FIYAT-SENKRON-01: paket fiyat katalogu tek kaynak.

OLCUM: `scripts/sync_paket_fiyatlari.py` `ROOT` hesabinda BIR SEVIYE
fazla gidiyordu (`c:\\Huginn Data Projesi`, repo DISI). Sonuc: `sys.path`
yanlis yone bakti ve `company_master` bulunamadi -> **betik hicbir zaman
calismadi**. Test bu regresyonu kapatir.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
BETIK = KOK / "scripts" / "sync_paket_fiyatlari.py"
sys.path.insert(0, str(KOK / "src"))


def test_repo_koku_gercekten_repo():
    """En kritik regresyon: ROOT repo disina tasarsa import cokerek
    butun senkron sessizce oluyordu.

    Metin taramasi yerine CALISMA ZAMANI olcumu: yorumda gecen ayni
    ifade hatayi tetiklerdi (bu hatayi yasadik).
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("sync_paket", BETIK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)          # import edilebilirligi de olcer
    assert mod.ROOT == KOK, f"ROOT yanlis: {mod.ROOT} != {KOK}"
    assert (mod.ROOT / "src" / "company_master").is_dir()
    assert mod.ROOT.name == "Huginn Data Insights"


def test_betik_import_edilebiliyor():
    """Betigin en azindan import satiri calismali."""
    cp = subprocess.run([sys.executable, "-X", "utf8", str(BETIK), "--check"],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", cwd=str(KOK), timeout=180)
    assert "ModuleNotFoundError" not in (cp.stdout + cp.stderr), cp.stderr[:300]
    assert "Traceback" not in (cp.stdout + cp.stderr), cp.stdout[-300:]
    assert cp.returncode == 0, cp.stdout[-300:]


def test_katalog_dort_tier_ve_fiyatli():
    from company_master.paketler import fiyat_katalogu
    katalog = fiyat_katalogu()
    assert len(katalog) == 4
    for t in katalog:
        assert t["price"] > 0, t["name"]
        assert t["features"] and t["description"] and t["icon"], t["name"]


def test_katalog_json_repo_icinde():
    """JSON repo icinde olmali; disarida degil."""
    yol = KOK / "data" / "demo" / "fiyat_katalogu.json"
    assert yol.is_file(), f"katalog JSON yok: {yol}"
    veri = json.loads(yol.read_text(encoding="utf-8"))
    assert isinstance(veri, list) and len(veri) == 4


def test_json_kaynakla_ayni():
    """JSON, canli kaynakla ayni degerleri tasiyin (tek kaynak kurali)."""
    from company_master.paketler import fiyat_katalogu
    yol = KOK / "data" / "demo" / "fiyat_katalogu.json"
    if not yol.is_file():
        return
    canli = {t["name"]: t["price"] for t in fiyat_katalogu()}
    dosya = {t["name"]: t["price"] for t in
             json.loads(yol.read_text(encoding="utf-8"))}
    assert canli == dosya, f"fark var: {canli} != {dosya}"