# -*- coding: utf-8 -*-
"""ALTYAPI-9ROUTER-ANAHTAR-01: anahtar betiginin guvenligi.

Kritik kural (D-288): anahtar degeri ne ciktiya ne loga yazilir.
Buradaki her test sahte anahtarla calisir; gercek .env'e DOKUNMAZ.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
BETIK = KOK / "scripts" / "ninerouter_anahtar_guncelle.py"

_spec = importlib.util.spec_from_file_location("nr9_guncelle", BETIK)
m = importlib.util.module_from_spec(_spec)
sys.modules["nr9_guncelle"] = m
_spec.loader.exec_module(m)

GIZLI = "ntn_TESTGIZLI_0123456789abcdef"


def _env(tmp_path: Path, icerik: str = "A=1\nNINEROUTER_KEY=eski\nB=2\n") -> Path:
    p = tmp_path / ".env"
    p.write_text(icerik, encoding="utf-8")
    return p


def test_anahtar_degisir_ve_yedek_olur(tmp_path):
    env = _env(tmp_path)
    yedek, adet, maske = m._guncelle(env, GIZLI)
    sonuc = env.read_text(encoding="utf-8")
    assert GIZLI in sonuc
    assert "eski" not in sonuc
    assert adet == 1
    assert yedek.exists()


def test_diger_satirlar_korunur(tmp_path):
    env = _env(tmp_path)
    m._guncelle(env, GIZLI)
    sonuc = env.read_text(encoding="utf-8")
    assert "A=1" in sonuc and "B=2" in sonuc
    assert len(sonuc.strip().splitlines()) == 3


def test_anahtar_ciktida_yazmaz(tmp_path):
    """D-288: maske en fazla GOSTER karakter, tam anahtar hicbir yerde."""
    env = _env(tmp_path)
    _, _, maske = m._guncelle(env, GIZLI)
    assert maske == GIZLI[:m.GOSTER]
    assert len(maske) == m.GOSTER
    assert GIZLI not in maske


def test_yedek_eskisini_icerir(tmp_path):
    """Yedek yazma ONCESI alinir; eski deger orada kalir."""
    env = _env(tmp_path)
    yedek, _, _ = m._guncelle(env, GIZLI)
    assert "eski" in yedek.read_text(encoding="utf-8")
    assert GIZLI not in yedek.read_text(encoding="utf-8")


def test_idempotans_tek_satir(tmp_path):
    env = _env(tmp_path)
    m._guncelle(env, GIZLI)
    m._guncelle(env, GIZLI)
    assert m._satir_sayisi(env.read_text(encoding="utf-8")) == 1


def test_anahtar_yoksa_eklenir(tmp_path):
    env = _env(tmp_path, "A=1\nB=2\n")
    m._guncelle(env, GIZLI)
    assert m._satir_sayisi(env.read_text(encoding="utf-8")) == 1


def test_bom_lu_env_okunur(tmp_path):
    env = tmp_path / ".env"
    env.write_bytes("\ufeffA=1\nNINEROUTER_KEY=eski\n".encode("utf-8"))
    m._guncelle(env, GIZLI)
    assert GIZLI in env.read_text(encoding="utf-8")


def test_geri_yukle_eski_hale_getirir(tmp_path):
    env = _env(tmp_path)
    yedek, _, _ = m._guncelle(env, GIZLI)
    m._geri_yukle(yedek, env)
    assert "eski" in env.read_text(encoding="utf-8")
    assert GIZLI not in env.read_text(encoding="utf-8")


def test_satir_sayimi_cift_satiri_yakalar(tmp_path):
    metin = "NINEROUTER_KEY=a\nNINEROUTER_KEY=b\n"
    assert m._satir_sayisi(metin) == 2


def test_kuru_mod_hicbir_dosyaya_yazmaz(tmp_path, capsys):
    """--kuru: .env aynen kalir, yedek dosya olusmaz."""
    env = _env(tmp_path)
    import subprocess
    r = subprocess.run(
        [sys.executable, str(BETIK), "--kuru", "--env", str(env), GIZLI],
        capture_output=True, text=True)
    assert r.returncode == 0
    assert env.read_text(encoding="utf-8") == "A=1\nNINEROUTER_KEY=eski\nB=2\n"
    assert list(tmp_path.glob("*.bak_*")) == []
    assert GIZLI not in r.stdout