# -*- coding: utf-8 -*-
"""D-198 simulasyon kapisi testleri.

Ilgili Nodlar:
- [[Huginn Data Insights/AGENTS]] (D-198)
- [[scripts/gorev_kutusu]]
- [[Huginn Data Insights/docs/GOREV_PANOSU_KULLANIM_KILAVUZU]] (§10)
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "src"))
sys.path.insert(0, str(KOK / "scripts"))

import gorev_kutusu as gk  # noqa: E402

# DIKKAT: gorev_kutusu "src.company_master..." yolundan import eder; testte
# "company_master..." yazmak ayri bir modul nesnesi yaratir ve monkeypatch
# komutu etkilemez. Bu yuzden modul komutun kendi referansindan alinir.
tb = gk.tb


def test_gercek_panoda_cikis_kodu_sozlesmesi():
    """Komut gercek panoda calisir; 8 kontrolu basar; kod 0/1/2 disina cikmaz."""
    sonuc = subprocess.run(
        [sys.executable, "scripts/gorev_kutusu.py", "simulasyon", "--kuru"],
        cwd=KOK, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert sonuc.returncode in (0, 1, 2), sonuc.stdout + sonuc.stderr
    assert "SONUC: cikis kodu" in sonuc.stdout
    for no in range(1, 9):
        assert f"\n{no}. " in sonuc.stdout, f"{no}. kontrol basilmadi"


def test_arsiv_cakismasi_hata_kodu_2_uretir(tmp_path, monkeypatch, capsys):
    """B-01: arsivde kapanmis task_id panoya girerse kapi 2 dondurur."""
    monkeypatch.setattr(tb, "STATE_DIR", tmp_path)
    monkeypatch.setattr(tb, "TASK_BOARD", tmp_path / "task_board.json")
    (tmp_path / "task_board_arsiv_2026-Q3.json").write_text(
        json.dumps([{"task_id": "TEST-CAKISMA-01", "durum": "done"}]), encoding="utf-8")
    tb.TASK_BOARD.write_text(json.dumps([{
        "task_id": "TEST-CAKISMA-01", "durum": "plan",
        "brief": "plans/_brief_sablon.md", "dosyalar": ["x.py"],
    }]), encoding="utf-8")

    kod = gk.cmd_simulasyon(argparse.Namespace(kuru=False))
    cikti = capsys.readouterr().out
    assert kod == 2, cikti
    assert "HATA" in cikti
    assert "TEST-CAKISMA-01" in cikti


def test_temiz_panoda_cakisma_kontrolu_sessiz(tmp_path, monkeypatch, capsys):
    """Arsivde olmayan task_id yanlis alarm uretmez."""
    monkeypatch.setattr(tb, "STATE_DIR", tmp_path)
    monkeypatch.setattr(tb, "TASK_BOARD", tmp_path / "task_board.json")
    tb.TASK_BOARD.write_text(json.dumps([{
        "task_id": "TEST-TEMIZ-01", "durum": "plan",
        "brief": "plans/_brief_sablon.md", "dosyalar": ["x.py"],
    }]), encoding="utf-8")

    gk.cmd_simulasyon(argparse.Namespace(kuru=True))
    cikti = capsys.readouterr().out
    assert "Pano<->arsiv task_id cakismasi (B-01): OK" in cikti


def test_atlanan_kontrol_cikis_kodunu_etkiler(tmp_path, monkeypatch, capsys):
    """YA-02: SSOT diskte yoksa kontrol 5/6 ATLANDI basar ve kod 0 OLAMAZ.

    Aksi halde SSOT'suz bir ortamda D-198 kapisi iki kontrol hic calismadan
    "temiz" der. Atlanmak hata degil -> kod 2 degil, uyari mertebesinde kalir.
    """
    monkeypatch.setattr(tb, "STATE_DIR", tmp_path)
    monkeypatch.setattr(tb, "TASK_BOARD", tmp_path / "task_board.json")
    monkeypatch.setattr(gk, "_SSOT", tmp_path / "diskte-olmayan-ssot.md")
    tb.TASK_BOARD.write_text(json.dumps([{
        "task_id": "TEST-ATLANDI-01", "durum": "plan",
        "brief": "plans/_brief_sablon.md", "dosyalar": ["x.py"],
    }]), encoding="utf-8")

    kod = gk.cmd_simulasyon(argparse.Namespace(kuru=True))
    cikti = capsys.readouterr().out
    assert "5. SSOT yuzde satiri" in cikti and "ATLANDI" in cikti
    assert kod != 0, f"atlanan kontrol cikis kodunu ortuyor:\n{cikti}"
    assert kod == 1, f"atlanmak hata degil, uyari olmali:\n{cikti}"
