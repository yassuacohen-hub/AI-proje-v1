# -*- coding: utf-8 -*-
"""Test fixtures for MCP + webhook test suites.

Isolates tests from the real persistent spend log
(data/orchestrator/mcp_spend_log.jsonl) which already contains
today-spend entries and would otherwise exhaust the default
daily_spend_limit (5.0) and break unpatched tests.
"""

from __future__ import annotations

import importlib
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def isolated_spend_log(tmp_path, monkeypatch):
    """Point every test at a fresh, empty spend log."""
    log_file = tmp_path / "mcp_spend_log.jsonl"
    monkeypatch.setattr(
        "company_master.mcp.policy_engine.SPEND_LOG", log_file
    )
    # Also cover any module that captured the path at import time.
    monkeypatch.setenv("MCP_SPEND_LOG", str(log_file))
    yield log_file


@pytest.fixture(autouse=True)
def _pano_dosyalari_yalitim(tmp_path, monkeypatch):
    """TEST-SYNC-01 / TEST-ISO-02: testler gercek pano dosyalarini ezemesin.

    Turetilmis (salt-okunur kabul edilen) uc dosya korunur:
      * ``AGENT_SYNC.md``        (kok senkron ozeti)
      * ``data/orchestrator/gorev_panosu.md``  (Obsidian gorunumu)
      * ``AGENT_SYNC_kopya.md``  (orchestrator kopyasi)

    Neden gerekli:
      * ``AUTO_SYNC=False`` yalnizca otomatik senkronu kapatir; panoya yazan
        bir test (or. ``tests/test_isbirligi.py``, ``tests/test_gorev_kutusu_cli.py``)
        gercek dosyalari yine uretir.
      * ``TASK_MD`` / ``AGENT_SYNC_MD`` modul import aninda ``STATE_DIR``'den
        turetilir; testte yalnizca ``STATE_DIR`` yamamak bu sabitleri
        degistirmez ve yazim gercek yola gider.
      * Testler iki farkli modul kimligi kullanabiliyor:
        ``company_master.orchestrator.task_board`` (``src/`` sys.path'te) ve
        ``src.company_master.orchestrator.task_board`` (kok sys.path'te).
        Ikisi ayri sabit nesneleridir; yalnizca biri yamalanirsa digeri
        gercek dosyayi yazmaya devam eder. Bu yuzden ikisi de yamalanir.
    """
    moduller = []
    for ad in (
        "company_master.orchestrator.task_board",
        "src.company_master.orchestrator.task_board",
    ):
        try:
            modul = importlib.import_module(ad)
        except Exception:  # noqa: BLE001 - modul yoksa koruma gerekmez
            continue
        if not any(modul is m for m in moduller):
            moduller.append(modul)
    if not moduller:  # pragma: no cover - src import edilemiyorsa atlanir
        yield
        return

    yollar = {
        "AUTO_SYNC": False,
        "AGENT_SYNC_MD": tmp_path / "AGENT_SYNC.md",
        "AGENT_SYNC_MD_KOPYA": tmp_path / "orchestrator" / "AGENT_SYNC.md",
        "TASK_MD": tmp_path / "gorev_panosu.md",
    }
    for modul in moduller:
        for ad, deger in yollar.items():
            monkeypatch.setattr(modul, ad, deger, raising=False)
    yield


@pytest.fixture(autouse=True)
def _no_real_env_secrets(monkeypatch):
    """Ensure tests never accidentally read production env secrets."""
    for key in ("APIFY_TOKEN", "APIFY_API_TOKEN", "APIFY_API_KEY", "TELEGRAM_BOT_TOKEN"):
        monkeypatch.delenv(key, raising=False)


# ALTYAPI-TEST-HERMETIK-01: "Testler uretim verisine dokunmaz" kurali.
# Yalitim fixture'lari yamalama ile calisir; bir test yeni bir yol yakalarsa
# sessizce canli panoya yazar (nitekim yaziyordu). Bu bariyer yazimi tespit
# eder, dosyayi geri yukler ve testi kirar -- ihlal bir daha sessiz kalamaz.
KORUMALI = (
    ROOT / "data" / "orchestrator" / "task_board.json",
    ROOT / "data" / "orchestrator" / "onay_kuyrugu.json",
    ROOT / "data" / "orchestrator" / "file_locks.json",
    ROOT / "data" / "orchestrator" / "gorev_panosu.md",
    ROOT / "AGENT_SYNC.md",
)


@pytest.fixture(autouse=True)
def _uretim_verisi_dokunulmaz():
    """Korumali uretim dosyalari degisirse geri yukle ve testi kir."""
    onceki = {p: p.read_bytes() for p in KORUMALI if p.exists()}
    yield
    kirlenen = []
    for yol, icerik in onceki.items():
        if yol.read_bytes() != icerik:
            yol.write_bytes(icerik)  # once geri yukle, sonra sikayet et
            kirlenen.append(yol.name)
    if kirlenen:
        raise AssertionError(
            "Test uretim verisine yazdi (geri yuklendi): " + ", ".join(kirlenen)
        )


@pytest.fixture(autouse=True)
def _streamlit_form_durumu_temiz():
    """D-226 mandali: bare modda `st.form` main_dg'ye form kimligi yapistirir.

    Olculen mekanizma (2026-09-28):
      * ScriptRunContext yokken `DeltaGenerator._block` erken `return dg`
        yapar (`_cursor is None`), yani form blogu main_dg'nin KENDISIDIR.
      * `st.form` donen bloga `_form_data = FormData(key)` yazar; `with`
        cikisi bunu temizlemez -> main_dg kalici olarak "form icinde" olur.
      * `is_in_form` once `this_dg._form_data`ya bakar; sonraki `AppTest`
        kosusu bu yuzden "Forms cannot be nested in other forms." verir.

    Kanit: `render_decision_tab([])` oncesi main_form_id=None, sonrasi
    main_form_id='yeni_karar'. Kirleten test tek basina gecer, kurbani
    (`tests/test_app_menu_rol.py`) ayni surecte dusurur.

    Mandal: geri yukle ve testi kir -- ihlal sessiz kalamaz.
    """
    yield
    try:
        from streamlit.delta_generator_singletons import get_dg_singleton_instance

        ana = get_dg_singleton_instance().main_dg
    except Exception:  # noqa: BLE001 - streamlit yoksa korunacak durum da yok
        return
    if getattr(ana, "_form_data", None) is not None:
        kimlik = ana._form_data.form_id
        ana._form_data = None  # once geri yukle, sonra sikayet et
        raise AssertionError(
            f"Test main_dg'ye form durumu birakti (form_id={kimlik!r}, geri "
            "yuklendi). ScriptRunContext'siz `st.form` kullanan uretim "
            "fonksiyonunu cagiran test, cagri sonrasi main_dg._form_data'yi "
            "geri koymalidir (D-226)."
        )

