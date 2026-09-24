# -*- coding: utf-8 -*-
"""ORKESTRA-NAMING-AUDIT-02 — D-55/D-57 adlandirma denetimi.

Kapsam ve KAPSAM DISI karari:
- Denetim YALNIZ acik gorevleri (durum ∉ tb.KAPALI_DURUMLAR) olcer.
  Brif "285 uygunsuz → 0" istiyordu; olcum bunu curuttu: 306 ihlalin 300'u
  done/archive/iptal kaydinda. Kapali kaydin basligini degistirmek denetim
  izini bozar (gecmisi yeniden yazmak). Acik yuzey 6 kayit; muafiyet listesi
  asagida, her biri gerekcesiyle.
- Ikinci bir regex YAZILMAZ; uretimdeki gorev_at._d57_dogrula tek kaynaktir.
  Denetim ile atama kapisi ayrisamaz.
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import gorev_at  # noqa: E402
from src.company_master.orchestrator import task_board as tb  # noqa: E402

# Muaf: ihlalin tek sebebi task_id on eki; duzeltmek kimligi kirar (brief
# yollari, raporlar, tetik kuyrugu, wikilink'ler bu id'ye bagli).
# ponytail: tavan = elle bakim. Yukseltme yolu = "id degistir + yonlendirme
# kaydi birak" komutu; o gelince bu liste bosalir.
MUAF: dict[str, str] = {}
# ORCH-08: COP-26, ALTYAPI-D66-BYPASS-TETIKLEME-01, AGENTS-MERGE-UU,
# VAULT-CLEANUP-BATCH kapandi (durum=done) -> _acik_gorevler() disinda,
# muafiyet gerekmiyor, listeden dusuruldu (2026-09-23, ihsan).
# TUR-B: ALTYAPI-D66-BYPASS-TETIKLEME de acik gorevler arasinda kalmadi;
# liste bosaldi. Yeni muafiyet eklemek bilincli karardir, gerekce zorunlu.


# conftest'teki izolasyon fixture'i tb.TASK_BOARD'u tmp_path'e cevirdigi icin
# tb.gorev_listesi() bos doner -- denetim BOS listede "gecer", sahte yesil.
# Bu yuzden uretim panosu dogrudan, sabit yoldan ve SALT OKUNUR acilir.
_URETIM_PANO = ROOT / "data" / "orchestrator" / "task_board.json"


def _acik_gorevler() -> list[dict]:
    if not _URETIM_PANO.exists():  # pragma: no cover
        pytest.skip("uretim panosu yok")
    kayitlar = json.loads(_URETIM_PANO.read_text(encoding="utf-8"))
    return [g for g in kayitlar if g.get("durum") not in tb.KAPALI_DURUMLAR]


def test_acik_gorevlerde_yeni_d57_ihlali_yok() -> None:
    ihlal = {}
    for g in _acik_gorevler():
        tid = g.get("task_id", "")
        sebep = gorev_at._d57_dogrula(tid, g.get("baslik", ""), g.get("sahip", ""))
        if sebep and tid not in MUAF:
            ihlal[tid] = sebep
    assert not ihlal, f"acik gorevlerde D-57 ihlali: {ihlal}"


def test_muafiyet_listesi_bayatlamadi() -> None:
    """Muaf kayit duzelince/kapaninca listeden dusmeli; liste cop olmasin."""
    acik = {g.get("task_id") for g in _acik_gorevler()}
    hala_ihlalli = {
        g.get("task_id")
        for g in _acik_gorevler()
        if gorev_at._d57_dogrula(g.get("task_id", ""), g.get("baslik", ""), g.get("sahip", ""))
    }
    gereksiz = set(MUAF) - hala_ihlalli
    assert not gereksiz, f"MUAF'tan dusmesi gereken kayitlar: {gereksiz} (acik: {acik & gereksiz})"


# --- onarim yolu: guncelle --baslik / --sahip ---------------------------------

def _gargs(**kw) -> argparse.Namespace:
    temel = dict(
        task_id="UI-01", baslik=None, baslik_b64=None, sahip=None,
        brief=None, talimat=None, oncelik=None, durum=None, cagiran="ihsan",
    )
    temel.update(kw)
    return argparse.Namespace(**temel)


@pytest.fixture(autouse=True)
def _izole(tmp_path, monkeypatch):
    # D-58 kapisi gercek orchestrator.json'u okuyor; test ortamda aktif
    # orkestratoru sabitler, aksi halde devralmaya gore kirilgan olur.
    monkeypatch.setattr(gorev_at, "_orkestrator_oku", lambda: {"ajan": "ihsan"})
    monkeypatch.setattr(tb, "AUTO_SYNC", False)
    monkeypatch.setattr(tb, "STATE_DIR", tmp_path)
    monkeypatch.setattr(tb, "TASK_BOARD", tmp_path / "task_board.json")
    monkeypatch.setattr(tb, "FILE_LOCKS", tmp_path / "file_locks.json")
    monkeypatch.setattr(tb, "STATE_JSON", tmp_path / "state.json")
    monkeypatch.setattr(tb, "TASK_MD", tmp_path / "gorev_panosu.md")
    monkeypatch.setattr(tb, "AGENT_SYNC_MD", tmp_path / "AGENT_SYNC.md")
    monkeypatch.setattr(tb, "AGENT_SYNC_MD_KOPYA", tmp_path / "AGENT_SYNC_kopya.md")
    return tmp_path


def _gorev_kur(baslik="[UI] Ayarlar sayfasini yaz → a.py (2s)", sahip="ihsan"):
    tb.gorev_ekle("UI-01", baslik, sahip, "P1")


def test_guncelle_baslik_d57_ihlalini_reddeder(capsys) -> None:
    _gorev_kur()
    kod = gorev_at.cmd_guncelle(_gargs(baslik="bozuk baslik"))
    assert kod == 3
    assert "D-57" in capsys.readouterr().err
    assert tb.gorev_getir("UI-01")["baslik"].startswith("[UI]")


def test_guncelle_baslik_gecerliyse_yazar() -> None:
    _gorev_kur()
    yeni = "[UI] Ayarlar sayfasini duzelt → b.py (3s)"
    assert gorev_at.cmd_guncelle(_gargs(baslik=yeni)) == 0
    assert tb.gorev_getir("UI-01")["baslik"] == yeni


def test_guncelle_baslik_b64_turkce_bozulmaz() -> None:
    """D-86: '→' ve Turkce karakter cmd.exe'de ancak base64 ile guvenli gecer."""
    _gorev_kur()
    yeni = "[UI] Ayarlar sayfasını düzelt → b.py (3s)"
    b64 = base64.b64encode(yeni.encode("utf-8")).decode("ascii")
    assert gorev_at.cmd_guncelle(_gargs(baslik_b64=b64)) == 0
    assert tb.gorev_getir("UI-01")["baslik"] == yeni


def test_guncelle_kanonik_olmayan_sahip_reddedilir(capsys) -> None:
    _gorev_kur()
    kod = gorev_at.cmd_guncelle(_gargs(sahip="roo"))
    assert kod == 3
    assert "D-60" in capsys.readouterr().err
    assert tb.gorev_getir("UI-01")["sahip"] == "ihsan"


def test_guncelle_sahip_duzeltir() -> None:
    _gorev_kur()
    assert gorev_at.cmd_guncelle(_gargs(sahip="yasu")) == 0
    assert tb.gorev_getir("UI-01")["sahip"] == "yasu"


# --- D-86: cmd.exe 'set X=roo && ' sondaki boslugu degere katar ---------------

def test_orkestrator_kapisi_sondaki_boslugu_yok_sayar(monkeypatch) -> None:
    monkeypatch.setattr(gorev_at, "_orkestrator_oku", lambda: {"ajan": "ihsan"})
    assert gorev_at._orkestrator_kapisi("ihsan ") is None
    assert gorev_at._orkestrator_kapisi(" ihsan") is None
    assert gorev_at._orkestrator_kapisi("yasu") is not None


# --- YA-01: eslemesiz gitlink (mode 160000) depoya girmesin -------------------

def test_eslemesiz_gitlink_yok() -> None:
    """Taze klonun icerigi eksik getirmesini onler.

    `.gitmodules` eslemesi olmayan mode 160000 girdisi klonda bos klasor
    birakir; YA-01'de 507 satirlik SSOT tam bu yuzden kayboldu.
    """
    import subprocess

    try:
        cikti = subprocess.run(
            ["git", "ls-files", "-s"],
            cwd=ROOT, capture_output=True, text=True, timeout=120,
        )
    except (OSError, subprocess.SubprocessError):  # pragma: no cover
        pytest.skip("git calistirilamadi")
    if cikti.returncode != 0:  # pragma: no cover
        pytest.skip("git ls-files basarisiz (depo disi calisma)")

    gitlinkler = {
        satir.split("\t", 1)[1]
        for satir in cikti.stdout.splitlines()
        if satir.startswith("160000 ")
    }
    eslemeler = set()
    gitmodules = ROOT / ".gitmodules"
    if gitmodules.exists():
        eslemeler = {
            s.split("=", 1)[1].strip()
            for s in gitmodules.read_text(encoding="utf-8").splitlines()
            if s.strip().startswith("path")
        }
    assert not (gitlinkler - eslemeler), (
        f"`.gitmodules` eslemesi olmayan gitlink: {sorted(gitlinkler - eslemeler)}"
    )
