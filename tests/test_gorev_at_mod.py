# -*- coding: utf-8 -*-
"""D-63: Architect Modu Kapısı (gorev_at.py / task_board.py) regresyon testleri.

Kapsam:
- --mod architect parametresi yalnız ihsan (roo) veya utku (kilo)'ya atanabilir
- Başka ajana (salih/yasu) --mod architect atanınca exit 5 ve HATA (D-63)
- İzinli ajana atanınca task dict `mod: "architect"` ve tetik brifinde hatırlatma satırı
- --mod verilmezse (varsayılan "code") task dict `mod: "code"` ve hatırlatma satırı eklenmez
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import gorev_at  # noqa: E402
from src.company_master.orchestrator import task_board as tb  # noqa: E402
from src.company_master.orchestrator import trigger  # noqa: E402


@pytest.fixture(autouse=True)
def izole_pano(tmp_path, monkeypatch):
    # D-66 kapisi artik brif dosyasini ZORUNLU ariyor (eskiden --talimat ile
    # atlanabiliyordu). Mod testleri kapiyi degil modu olctugu icin brifler
    # izole KOK altinda hazir yazilir.
    monkeypatch.setattr(gorev_at, "KOK", tmp_path)
    (tmp_path / "plans").mkdir(exist_ok=True)
    for ajan in ("ihsan", "utku", "salih", "yasu"):
        for tid in ("UI-01", "UI-02", "UI-03"):
            (tmp_path / "plans" / f"brief_{ajan}_{tid}.md").write_text("brif", encoding="utf-8")
    monkeypatch.setattr(tb, "AUTO_SYNC", False)
    monkeypatch.setattr(tb, "STATE_DIR", tmp_path)
    monkeypatch.setattr(tb, "TASK_BOARD", tmp_path / "task_board.json")
    monkeypatch.setattr(tb, "FILE_LOCKS", tmp_path / "file_locks.json")
    monkeypatch.setattr(tb, "STATE_JSON", tmp_path / "state.json")
    monkeypatch.setattr(tb, "TASK_MD", tmp_path / "gorev_panosu.md")
    monkeypatch.setattr(tb, "AGENT_SYNC_MD", tmp_path / "AGENT_SYNC.md")
    monkeypatch.setattr(tb, "AGENT_SYNC_MD_KOPYA", tmp_path / "AGENT_SYNC_kopya.md")
    return tmp_path


def _args(task_id="UI-01", baslik="[UI] Ayarlar sayfasını yaz → admin_ayarlar.py (2s)", ajan="ihsan", mod="code", talimat="") -> argparse.Namespace:
    return argparse.Namespace(
        task_id=task_id,
        baslik=baslik,
        ajan=ajan,
        oncelik="P1",
        dosya=None,
        talimat=talimat,
        mod=mod,
        cagiran=None,
    )


def test_architect_modu_salih_yasu_reddedilir(capsys):
    for izinsiz in ("salih", "yasu"):
        # D-63 kapisi D-66/D-80'den ONCE calisir: gecersiz atamada brif/talimat sorulmaz.
        rc = gorev_at.cmd_at(_args(task_id="UI-01", ajan=izinsiz, mod="architect"))
        err = capsys.readouterr().err
        assert rc == 5
        assert "HATA (D-63)" in err
        assert izinsiz in err


def test_architect_modu_ihsan_utku_kabul_edilir(tmp_path, capsys):
    for i, izinli in enumerate(("ihsan", "utku")):
        tid = f"UI-0{i+1}"
        rc = gorev_at.cmd_at(_args(task_id=tid, ajan=izinli, mod="architect", talimat="Planlama yap"))
        out = capsys.readouterr().out
        assert rc == 0
        assert "mod=architect" in out
        assert "Architect modunda açılmalıdır" in out

        # Pano kaydı doğrulama
        g = tb.gorev_getir(tid)
        assert g is not None
        assert g.get("mod") == "architect"

        # Tetik brifi doğrulama
        tetikler = trigger.bekleyen_tetikler(izinli, data_dir=tmp_path)
        assert len(tetikler) >= 1
        t = [x for x in tetikler if x["task_id"] == tid][0]
        assert "⚠️ Bu görev Architect modunda açılmalıdır." in t["talimat"]


def test_code_modu_varsayilan_hatirlatma_eklemez(tmp_path, capsys):  # noqa: D103
    rc = gorev_at.cmd_at(_args(task_id="UI-03", ajan="salih", mod="code", talimat="Kod yaz"))
    assert rc == 0
    g = tb.gorev_getir("UI-03")
    assert g is not None
    assert g.get("mod") == "code"

    tetikler = trigger.bekleyen_tetikler("salih", data_dir=tmp_path)
    t = [x for x in tetikler if x["task_id"] == "UI-03"][0]
    assert "Architect modunda açılmalıdır" not in t["talimat"]
