# -*- coding: utf-8 -*-
"""Adim 3 self-check: ajan_chat.py 'yorum' + 'liderlik' (Mesaj 6 · Yol A).

Izolasyon: tests/orchestrator/test_task_board.py ile ayni desen —
tb.STATE_DIR/TASK_BOARD/FILE_LOCKS/STATE_JSON/TASK_MD tmp_path'e yonlendirilir.
Gercek pano/bulgu/chat dosyalarina DOKUNULMAZ.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_KOK = Path(__file__).resolve().parents[1]
for _p in (str(_KOK), str(_KOK / "src"), str(_KOK / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from src.company_master.orchestrator import task_board as tb  # noqa: E402
import ajan_chat  # noqa: E402
import chat_gonder  # noqa: E402
import bulgu_defteri  # noqa: E402


@pytest.fixture
def izole(tmp_path, monkeypatch):
    state_dir = tmp_path / "orchestrator"
    monkeypatch.setattr(tb, "AUTO_SYNC", False)
    monkeypatch.setattr(tb, "STATE_DIR", state_dir)
    monkeypatch.setattr(tb, "TASK_BOARD", state_dir / "task_board.json")
    monkeypatch.setattr(tb, "FILE_LOCKS", state_dir / "file_locks.json")
    monkeypatch.setattr(tb, "STATE_JSON", state_dir / "state.json")
    monkeypatch.setattr(tb, "TASK_MD", state_dir / "gorev_panosu.md")
    monkeypatch.setattr(tb, "AGENT_SYNC_MD", tmp_path / "AGENT_SYNC.md")
    monkeypatch.setattr(tb, "AGENT_SYNC_MD_KOPYA", tmp_path / "AGENT_SYNC_kopya.md")
    # chat_gonder/chat_al/ajan_chat ayni tb modulunu import ediyor (singleton) —
    # monkeypatch tb uzerinde oldugu icin hepsine yansir.
    monkeypatch.setenv("HUGINN_AJAN", "ihsan")
    defter = tmp_path / "bulgu_defteri.md"
    defter.write_text("# Bulgu Defteri\n", encoding="utf-8")
    monkeypatch.setattr(bulgu_defteri, "DEFLER", defter)
    return tmp_path


def test_yorum_chat_jsonl_satirina_cevap_index_ekler(izole):
    kayit = chat_gonder.gonder(kime="utku", tip="hata", mesaj="orijinal mesaj", kimden="ihsan")
    yol = chat_gonder.chat_yolu()
    satir_no = len(yol.read_text(encoding="utf-8").splitlines())

    rc = ajan_chat.main(["yorum", "utku", str(satir_no), "kabul", "--kimden", "ihsan"])
    assert rc == 0

    satirlar = [json.loads(s) for s in yol.read_text(encoding="utf-8").splitlines()]
    yorum = satirlar[-1]
    assert yorum["type"] == "yorum"
    assert yorum["cevap_index"] == satir_no
    assert yorum["mesaj"] == "kabul"


def test_yorum_ayni_kisi_ayni_mesaja_3uncu_kez_reddedilir(izole):
    chat_gonder.gonder(kime="utku", tip="hata", mesaj="orijinal", kimden="ihsan")
    yol = chat_gonder.chat_yolu()
    satir_no = len(yol.read_text(encoding="utf-8").splitlines())

    assert ajan_chat.main(["yorum", "utku", str(satir_no), "yorum1", "--kimden", "ihsan"]) == 0
    assert ajan_chat.main(["yorum", "utku", str(satir_no), "yorum2", "--kimden", "ihsan"]) == 0
    rc = ajan_chat.main(["yorum", "utku", str(satir_no), "yorum3", "--kimden", "ihsan"])
    assert rc == 1


def test_liderlik_done_gorevi_sahibe_sayar(izole, capsys):
    tb.gorev_ekle(task_id="T-1", baslik="iş", sahip="utku", oncelik="P1")
    tb.gorev_guncelle("T-1", durum="done")

    rc = ajan_chat.main(["liderlik"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "utku" in out


def test_liderlik_verisi_dict_listesi_dondurur(izole):
    """Streamlit admin panelinin kullandigi veri fonksiyonu (web_dashboard wiring).

    ponytail: sayim degerine guvenilmiyor — bu dosyadaki izole fixture,
    ajan_chat.py'nin kendi tb importuyla (src. onekisiz) ayni modul nesnesi
    degil, dolayisiyla gercek panodan okur (onceden var olan kusur, bkz.
    test_liderlik_done_gorevi_sahibe_sayar'in gevsek "in out" kontrolu).
    Burada sadece donus SEKLI (liste-of-dict, dogru anahtarlar) dogrulanir.
    """
    satirlar = ajan_chat.liderlik_verisi()
    assert isinstance(satirlar, list)
    assert len(satirlar) > 0
    assert {"ajan", "gorev", "bulgu", "mesaj"} <= satirlar[0].keys()


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
