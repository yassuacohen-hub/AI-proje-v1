# -*- coding: utf-8 -*-
"""ALTYAPI-MOJIBAKE-BARIYER-01: onarim araci hasari artiramaz.

Kok neden: 2026-09-23'te mojibake_onar.py dogru UTF-8 kaynak dosyalarda ters
yonde calisti (Gorev -> GÃ¶rev); 110 satir bozuldu, regresyon 7 -> 14 kirmizi.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
BETIK = KOK / "scripts" / "mojibake_onar.py"

_spec = importlib.util.spec_from_file_location("mojibake_onar", BETIK)
mo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mo)


def _calistir(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-X", "utf8", str(BETIK), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(KOK),
    )


def test_temiz_utf8_dosya_degismez(tmp_path):
    """Dogru UTF-8 metin bozulmadan kalmali (bariyerin asil isi)."""
    dosya = tmp_path / "temiz.md"
    icerik = "Görev ajanına kuyruğunda düzeltme var.\n"
    dosya.write_text(icerik, encoding="utf-8")
    mo.dosya_onar(dosya)
    assert dosya.read_text(encoding="utf-8") == icerik


def test_hasar_artarsa_yazilmaz(tmp_path, monkeypatch, capsys):
    """Bariyerin kendisi: onarim hasari artirirsa yazim iptal, duzeltilen=0.

    satir_onar bilerek hasar ureten bir surumle degistirilir; boylece bariyer
    'onarim ters yonde calisti' senaryosunda dogrudan sinanir.
    """
    dosya = tmp_path / "tuzak.md"
    dosya.write_text("GÃ¶rev\n", encoding="utf-8")
    onceki_bayt = dosya.read_bytes()
    monkeypatch.setattr(mo, "satir_onar", lambda s: "GÃƒÂ¶rev GÃƒÂ¶rev")
    duz, _atl, kalan = mo.dosya_onar(dosya)
    assert duz == 0
    assert kalan > 1
    assert dosya.read_bytes() == onceki_bayt
    assert "IPTAL" in capsys.readouterr().out


def test_bozuk_dosya_hala_onarilir(tmp_path):
    """Bariyer gercek onarimi engellememeli."""
    dosya = tmp_path / "bozuk.md"
    dosya.write_text("GÃ¶rev\n", encoding="utf-8")
    duz, _atl, kalan = mo.dosya_onar(dosya)
    assert duz == 1
    assert kalan == 0
    assert "Görev" in dosya.read_text(encoding="utf-8")


def test_kaynak_uzantisi_zorla_olmadan_reddedilir(tmp_path):
    """.py dosyasi --zorla olmadan onarilamaz (exit 3)."""
    dosya = tmp_path / "kod.py"
    icerik = "# Görev listesi\n"
    dosya.write_text(icerik, encoding="utf-8")
    r = _calistir(str(dosya))
    assert r.returncode == 3, r.stdout + r.stderr
    assert "REDDEDILDI" in r.stdout
    assert dosya.read_text(encoding="utf-8") == icerik


def test_ozet_satiri_degisen_sayisini_basar(tmp_path):
    """L140 etiket hatasi: 'degisen' alani kalan degil gercek degisen sayisi."""
    dosya = tmp_path / "bozuk.md"
    dosya.write_text("GÃ¶rev\n", encoding="utf-8")
    r = _calistir(str(dosya))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "degisen=1" in r.stdout
    assert "kalan=0" in r.stdout.splitlines()[-1]
