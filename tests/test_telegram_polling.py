# -*- coding: utf-8 -*-
"""Unit tests for scripts/telegram_polling.py.

Hiçbir test gerçek Telegram API'sine baglanmaz; requests.post/get
ve os.environ monkeypatch ile gecilir. _load_env no-op yapilir
boylece .env'deki gercek tokenlar testleri etkilemez. task_board
atomik yazma icin tmp_path izole edilir.
"""
import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# scripts/telegram_polling.py modulunu dinamik yukle (scripts/ paket degildir)
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "telegram_polling", ROOT / "scripts" / "telegram_polling.py"
)
telegram_polling = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(telegram_polling)

# task_board modulunu onizden yukle (set_task_status icin)
from src.company_master.orchestrator import task_board as tb_module

import src.company_master.utils.telegram_bot as tb_mod


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _clear_env(monkeypatch):
    """Telegram env degiskenlerini temizle ve _load_env'i no-op yap.

    .env dosyasindaki gercek token/chat_id'lerin testleri etkilememesi
    icin load_dotenv cagrisini bypass ederiz.
    """
    for key in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID", "TELEGRAM_BOT_USERNAME",
                "ETL_RESTART_CMD"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setattr(tb_mod, "_load_env", lambda: None)
    yield


@pytest.fixture
def _tmp_board(tmp_path, monkeypatch):
    """task_board.json ve ilgili dosyalari tmp_path'e yonlendir."""
    data_dir = tmp_path / "data" / "orchestrator"
    data_dir.mkdir(parents=True)
    board_path = data_dir / "task_board.json"
    board_path.write_text("[]", encoding="utf-8")

    # telegram_polling modulundeki ROOT'u tmp_path'e yonlendir
    monkeypatch.setattr(telegram_polling, "ROOT", tmp_path)
    # tb_modul yol degiskenlerini tmp_path'e yonlendir
    monkeypatch.setattr(tb_module, "STATE_DIR", data_dir)
    monkeypatch.setattr(tb_module, "TASK_BOARD", board_path)
    monkeypatch.setattr(tb_module, "FILE_LOCKS", data_dir / "file_locks.json")
    monkeypatch.setattr(tb_module, "STATE_JSON", data_dir / "state.json")
    monkeypatch.setattr(tb_module, "TASK_MD", data_dir / "gorev_panosu.md")
    # FIX-SYNC-01: agent_sync_yaz() gercek kok AGENT_SYNC.md'ye sizmasin (T7 artigi)
    monkeypatch.setattr(tb_module, "AGENT_SYNC_MD", tmp_path / "AGENT_SYNC.md")
    monkeypatch.setattr(tb_module, "AGENT_SYNC_MD_KOPYA", data_dir / "AGENT_SYNC.md")

    # V10 wiki komutları için canonical dizin ve örnek sayfalar
    v10 = tmp_path / "AI proje v1" / "V10"
    v10.mkdir(parents=True, exist_ok=True)
    (v10 / "00-Home.md").write_text("# Home", encoding="utf-8")
    (v10 / "project_state.md").write_text("# Proje Durumu", encoding="utf-8")
    (v10 / "10_ankara_osb_sentez.md").write_text("# OSINT Sentez", encoding="utf-8")
    osint_dir = v10 / "11_osint_motoru"
    osint_dir.mkdir(parents=True, exist_ok=True)
    (osint_dir / "OSINT_Scraper_Motoru.md").write_text("# OSINT Motoru", encoding="utf-8")

    # kalite raporu icin gerekli dosyalari olustur
    kpi_path = tmp_path / "data" / "kpi_raporu.md"
    kpi_path.parent.mkdir(parents=True, exist_ok=True)
    kpi_path.write_text(
        "# KPI\n- Ortalama Kimlik Dosyasi Tamligi: 3.71 / 6.50 ulaşılabilir\n",
        encoding="utf-8",
    )

    quality_path = tmp_path / "data" / "ostim" / "kalite_raporu.md"
    quality_path.parent.mkdir(parents=True, exist_ok=True)
    quality_path.write_text("# Kalite Raporu\nTest", encoding="utf-8")

    return board_path


def _write_board(path, tasks):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# read_* functions tests
# ---------------------------------------------------------------------------

def test_read_task_board_empty(_tmp_board):
    board = telegram_polling.read_task_board()
    assert board == []


def test_read_task_board_with_tasks(_tmp_board):
    _write_board(_tmp_board, [
        {"task_id": "T1", "baslik": "Test", "durum": "done", "sahip": "kilo"},
        {"task_id": "T2", "baslik": "Active", "durum": "aktif", "sahip": "kilo"},
    ])
    board = telegram_polling.read_task_board()
    assert len(board) == 2
    assert board[0]["task_id"] == "T1"


def test_read_active_tasks(_tmp_board):
    _write_board(_tmp_board, [
        {"task_id": "T1", "durum": "done"},
        {"task_id": "T2", "durum": "aktif"},
        {"task_id": "T3", "durum": "plan"},
        {"task_id": "T4", "durum": "review"},
    ])
    active = telegram_polling.read_active_tasks()
    assert len(active) == 3
    active_ids = [t["task_id"] for t in active]
    assert "T2" in active_ids
    assert "T3" in active_ids
    assert "T4" in active_ids


def test_read_done_count(_tmp_board):
    _write_board(_tmp_board, [
        {"task_id": "T1", "durum": "done"},
        {"task_id": "T2", "durum": "done"},
        {"task_id": "T3", "durum": "aktif"},
    ])
    assert telegram_polling.read_done_count() == 2


def test_read_tamlik_metni(_tmp_board):
    """D-250/7: ayristirilan metin olcegini kendisi tasir, '/100' yok."""
    tamlik = telegram_polling.read_tamlik_metni()
    assert tamlik == "3.71 / 6.50 ulaşılabilir"
    assert "/100" not in telegram_polling.cmd_status("/status")


def test_read_tamlik_metni_rapor_yoksa_bilinmiyor(_tmp_board, monkeypatch):
    """Rapor yoksa sayi uydurulmaz."""
    (telegram_polling.ROOT / "data" / "kpi_raporu.md").unlink()
    assert telegram_polling.read_tamlik_metni() == "bilinmiyor"


def test_read_task_board_missing_file(monkeypatch):
    """task_board.json yoksa bos liste doner."""
    monkeypatch.setattr(telegram_polling, "ROOT", Path("/nonexistent/path"))
    assert telegram_polling.read_task_board() == []


def test_read_file_not_found():
    """Dosya yoksa hata mesaji doner."""
    result = telegram_polling._read_file("nonexistent_file.md")
    assert "[ dosya bulunamadi:" in result


# ---------------------------------------------------------------------------
# parse_command tests
# ---------------------------------------------------------------------------

def test_parse_command_start():
    result = telegram_polling.parse_command("/start", "MyBot")
    assert result is not None
    assert result["command"] == "start"


def test_parse_command_start_with_bot():
    result = telegram_polling.parse_command("/start@MyBot arg", "MyBot")
    assert result["command"] == "start"
    assert result["bot"] == "MyBot"
    assert result["args"] == ["arg"]


def test_parse_command_other_bot_filtered():
    result = telegram_polling.parse_command("/start@OtherBot", "MyBot")
    assert result is None


def test_parse_command_non_command():
    assert telegram_polling.parse_command("merhaba", "MyBot") is None


def test_parse_command_empty():
    assert telegram_polling.parse_command("", "MyBot") is None
    assert telegram_polling.parse_command(None, "MyBot") is None


# ---------------------------------------------------------------------------
# is_authorized tests
# ---------------------------------------------------------------------------

def test_is_authorized_no_env():
    assert telegram_polling.is_authorized("123") is False


def test_is_authorized_match(monkeypatch):
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "999")
    assert telegram_polling.is_authorized("999") is True


def test_is_authorized_mismatch(monkeypatch):
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "999")
    assert telegram_polling.is_authorized("111") is False


def test_is_authorized_allowed_list(monkeypatch):
    """TELEGRAM_ALLOWED_CHAT_IDS virgul listesi ek izin verir."""
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "999")
    monkeypatch.setenv("TELEGRAM_ALLOWED_CHAT_IDS", "111, 222, 333")
    assert telegram_polling.is_authorized("999") is True
    assert telegram_polling.is_authorized("111") is True
    assert telegram_polling.is_authorized("222") is True
    assert telegram_polling.is_authorized("333") is True
    assert telegram_polling.is_authorized("444") is False


def test_is_authorized_allowed_list_whitespace(monkeypatch):
    """Whitespace iceren bos ogeler yoksayilir."""
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "999")
    monkeypatch.setenv("TELEGRAM_ALLOWED_CHAT_IDS", " , 111 , ,, 222 , ")
    assert telegram_polling.is_authorized("111") is True
    assert telegram_polling.is_authorized("222") is True


# ---------------------------------------------------------------------------
# Command handler tests
# ---------------------------------------------------------------------------

def test_cmd_start(_tmp_board):
    result = telegram_polling.cmd_start("/start")
    assert "Ankara B2B" in result
    assert "/help" in result


def test_cmd_help():
    result = telegram_polling.cmd_help("/help")
    assert "/start" in result
    assert "/status" in result
    assert "/gorev" in result
    assert "/rapor" in result
    assert "/wiki" in result
    assert "/set_status" in result
    assert "/at" in result
    assert "/pano" in result
    assert "/onaylar" in result
    assert "/onayla" in result
    assert "/reddet" in result
    assert "/nobet" in result
    assert "/nobet_ayar" in result


def test_cmd_status(_tmp_board):
    _write_board(_tmp_board, [
        {"task_id": "T1", "durum": "aktif", "baslik": "Task 1", "sahip": "kilo"},
        {"task_id": "T2", "durum": "done", "baslik": "Task 2", "sahip": "kilo"},
    ])
    # ornek dosyalari olustur
    v10 = telegram_polling.ROOT / "AI proje v1" / "V10"
    v10.mkdir(parents=True, exist_ok=True)
    (v10 / "00-Home.md").write_text("# Home", encoding="utf-8")
    (v10 / "project_state.md").write_text("# Proje Durumu Testi\n", encoding="utf-8")
    jsonl = telegram_polling.ROOT / "data" / "ostim"
    jsonl.mkdir(parents=True, exist_ok=True)
    (jsonl / "firmalar_sayfa1.jsonl").write_text("line1\nline2\n", encoding="utf-8")

    result = telegram_polling.cmd_status("/status")
    assert "PROJE DURUMU" in result
    assert "Proje Durumu Testi" in result
    assert "satir" in result
    assert ".md" in result
    assert "Aktif" in result
    assert "T1" in result


def test_cmd_gorev(_tmp_board):
    _write_board(_tmp_board, [
        {"task_id": "T1", "durum": "aktif", "baslik": "Aktif task", "sahip": "kilo"},
        {"task_id": "T2", "durum": "done", "baslik": "Done task", "sahip": "kilo"},
    ])
    result = telegram_polling.cmd_gorev("/gorev")
    assert "GOREV PANOSU" in result
    assert "AKTIF" in result
    assert "DONE" in result


def test_cmd_gorev_empty(_tmp_board):
    result = telegram_polling.cmd_gorev("/gorev")
    assert "bos" in result or "BOS" in result


def test_cmd_rapor(_tmp_board):
    result = telegram_polling.cmd_rapor("/rapor")
    assert "<pre>" in result
    assert "KPI" in result


def test_cmd_rapor_fallback_to_quality(_tmp_board):
    """KPI dosyasi yoksa kalite raporu fallback."""
    kpi_path = telegram_polling.ROOT / "data" / "kpi_raporu.md"
    kpi_path.unlink()
    result = telegram_polling.cmd_rapor("/rapor")
    assert "<pre>" in result
    assert "Kalite" in result


def test_cmd_wiki(_tmp_board):
    result = telegram_polling.cmd_wiki("/wiki")
    assert "V10 WIKI" in result
    assert "00-Home.md" in result
    assert "project_state.md" in result
    assert "OSINT" in result
    assert "OSTIM kalite raporu" not in result
    assert "Kalite metrikleri" in result


def test_cmd_degisiklik(_tmp_board):
    result = telegram_polling.cmd_degisiklik("/degisiklik")
    assert "bulunamadi" in result.lower() or "CHANGELOG" in result


def test_cmd_gunluk(_tmp_board):
    _write_board(_tmp_board, [
        {"task_id": "T1", "durum": "aktif", "baslik": "Task A"},
        {"task_id": "T2", "durum": "done", "baslik": "Task B"},
    ])
    result = telegram_polling.cmd_gunluk("/gunluk")
    assert "GUNLUK OZET" in result
    assert "aktif" in result.lower()


def test_cmd_izleme(_tmp_board):
    result = telegram_polling.cmd_izleme("/izleme")
    assert "IZLEME" in result


# ---------------------------------------------------------------------------
# restart_etl tests
# ---------------------------------------------------------------------------

def test_restart_etl_success(monkeypatch):
    """ETL restart subprocess ile calisir (shell kapali)."""
    monkeypatch.delenv("ETL_RESTART_CMD", raising=False)
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.communicate.return_value = ("ETL OK", "")
    with patch("subprocess.Popen", return_value=mock_proc) as mock_popen:
        result = telegram_polling.restart_etl()
        assert result["ok"] is True
        assert result["returncode"] == 0
        call_kwargs = mock_popen.call_args.kwargs
        assert "cwd" in call_kwargs
        assert "shell" not in call_kwargs or call_kwargs.get("shell") is not True
        # argv listesi string degil
        cmd_arg = mock_popen.call_args.args[0]
        assert isinstance(cmd_arg, list)


def test_restart_etl_failure(monkeypatch):
    """ETL hata donerse."""
    mock_proc = MagicMock()
    mock_proc.returncode = 1
    mock_proc.communicate.return_value = ("output", "ETL Error: database connection failed")
    with patch("subprocess.Popen", return_value=mock_proc):
        result = telegram_polling.restart_etl()
        assert result["ok"] is False
        assert "database" in result.get("stderr", "") or "database" in result.get("stdout", "")


def test_restart_etl_timeout(monkeypatch):
    """ETL timeout yakalanir."""
    import subprocess as sp
    mock_proc = MagicMock()
    mock_proc.communicate.side_effect = sp.TimeoutExpired(cmd="test", timeout=30)
    with patch("subprocess.Popen", return_value=mock_proc):
        result = telegram_polling.restart_etl()
        assert result["ok"] is False
        assert "timeout" in result["error"].lower()


def test_restart_etl_custom_cmd():
    """Ozel komut calistirilir."""
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.communicate.return_value = ("custom", "")
    with patch("subprocess.Popen", return_value=mock_proc):
        result = telegram_polling.restart_etl(cmd="echo custom_etl")
        assert result["ok"] is True


# ---------------------------------------------------------------------------
# set_task_status tests
# ---------------------------------------------------------------------------

def test_set_task_status_valid(_tmp_board):
    """set_task_status atomik guncelleme yapar."""
    _write_board(_tmp_board, [
        {"task_id": "TG-01", "durum": "aktif", "baslik": "Test", "sahip": "kilo"},
    ])
    result = telegram_polling.set_task_status("TG-01", "done")
    assert result["ok"] is True
    assert result["task"]["durum"] == "done"
    # dosyada kalicilsin mi kontrol et
    updated = json.loads(_tmp_board.read_text(encoding="utf-8"))
    assert updated[0]["durum"] == "done"


def test_set_task_status_not_found(_tmp_board):
    result = telegram_polling.set_task_status("NONEXIST", "done")
    assert result["ok"] is False
    assert "bulunamadi" in result["error"]


def test_set_task_status_invalid_status(_tmp_board):
    result = telegram_polling.set_task_status("TG-01", "invalid_status")
    assert result["ok"] is False
    assert "Gecersiz" in result["error"]


# ---------------------------------------------------------------------------
# handle_update tests
# ---------------------------------------------------------------------------

def _make_update(text: str, chat_id: str = "999") -> dict:
    return {
        "update_id": 42,
        "message": {
            "message_id": 1,
            "chat": {"id": chat_id, "type": "private"},
            "text": text,
        },
    }


def test_handle_update_start():
    result = telegram_polling.handle_update(_make_update("/start"))
    assert result is not None
    assert "Ankara B2B" in result


def test_handle_update_help():
    result = telegram_polling.handle_update(_make_update("/help"))
    assert result is not None
    assert "KOMUTLAR" in result.upper()


def test_handle_update_status(_tmp_board):
    _write_board(_tmp_board, [
        {"task_id": "T1", "durum": "aktif", "baslik": "Task"},
    ])
    result = telegram_polling.handle_update(_make_update("/status"))
    assert result is not None
    assert "DURUM" in result.upper()


def test_handle_update_gorev(_tmp_board):
    _write_board(_tmp_board, [
        {"task_id": "T1", "durum": "done", "baslik": "Task", "sahip": "kilo"},
    ])
    result = telegram_polling.handle_update(_make_update("/gorev"))
    assert result is not None
    assert "PANOSU" in result


def test_handle_update_rapor(_tmp_board):
    result = telegram_polling.handle_update(_make_update("/rapor"))
    assert result is not None
    assert "pre" in result


def test_handle_update_wiki(_tmp_board):
    result = telegram_polling.handle_update(_make_update("/wiki"))
    assert result is not None


def test_handle_update_degisiklik():
    result = telegram_polling.handle_update(_make_update("/degisiklik"))
    assert result is not None


def test_handle_update_gunluk(_tmp_board):
    result = telegram_polling.handle_update(_make_update("/gunluk"))
    assert result is not None
    assert "OZET" in result.upper()


def test_handle_update_izleme(_tmp_board):
    result = telegram_polling.handle_update(_make_update("/izleme"))
    assert result is not None


def test_handle_update_set_status_unauthorized():
    """Yetkisiz kullanici set_status alamaz."""
    result = telegram_polling.handle_update(_make_update("/set_status TG-01 done"))
    assert result is not None
    assert "Yetkisiz" in result or "yetkili" in result


def test_handle_update_set_status_adds_note(_tmp_board, monkeypatch):
    """Yetkili /set_status project_state.md icinde Eklenen Notlar altina not ekler."""
    from pathlib import Path as _P
    v10 = telegram_polling.ROOT / "AI proje v1" / "V10"
    v10.mkdir(parents=True, exist_ok=True)
    state_path = v10 / "project_state.md"
    state_path.write_text("# Proje\n\n### Eklenen Notlar\n", encoding="utf-8")
    with patch.dict("os.environ", {"TELEGRAM_CHAT_ID": "999"}):
        result = telegram_polling.handle_update(_make_update("/set_status test not mesaji"))
    assert result is not None
    assert "Not eklendi" in result
    updated = state_path.read_text(encoding="utf-8")
    assert "### Eklenen Notlar" in updated
    assert "test not mesaji" in updated
    assert "- [" in updated


def test_handle_update_set_task_status_authorized(_tmp_board):
    """Yetkili /set_task_status task board durumunu gunceller."""
    _write_board(_tmp_board, [
        {"task_id": "TG-01", "durum": "aktif", "baslik": "Test", "sahip": "kilo"},
    ])
    with patch.dict("os.environ", {"TELEGRAM_CHAT_ID": "999"}):
        result = telegram_polling.handle_update(_make_update("/set_task_status TG-01 done"))
    assert result is not None
    assert "guncellendi" in result.lower() or "Guncellendi" in result
    board = json.loads(_tmp_board.read_text(encoding="utf-8"))
    assert board[0]["durum"] == "done"


def test_cmd_set_status_limit_500(_tmp_board, monkeypatch):
    """/set_status mesaji 500 karakterle sinirlanir."""
    v10 = telegram_polling.ROOT / "AI proje v1" / "V10"
    v10.mkdir(parents=True, exist_ok=True)
    state_path = v10 / "project_state.md"
    state_path.write_text("# Proje\n", encoding="utf-8")
    long_msg = "x" * 800
    with patch.dict("os.environ", {"TELEGRAM_CHAT_ID": "999"}):
        result = telegram_polling.handle_update(_make_update("/set_status " + long_msg))
    assert "Not eklendi" in result
    updated = state_path.read_text(encoding="utf-8")
    assert "x" * 500 in updated
    assert "x" * 501 not in updated


def test_handle_update_restart_etl_unauthorized():
    """Yetkisiz kullanici restart_etl alamaz."""
    result = telegram_polling.handle_update(_make_update("/restart_etl"))
    assert result is not None
    assert "Yetkisiz" in result or "yetkili" in result


def test_handle_update_restart_etl_authorized():
    """Yetkili kullanici restart_etl kullanabilir."""
    with patch.dict("os.environ", {"TELEGRAM_CHAT_ID": "999"}):
        with patch("subprocess.Popen") as mock_popen:
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.communicate.return_value = ("ETL OK", "")
            mock_popen.return_value = mock_proc
            result = telegram_polling.handle_update(_make_update("/restart_etl"))
            assert result is not None
            assert "baslatildi" in result.lower() or "yap" in result.lower()


def test_handle_update_unknown_command():
    result = telegram_polling.handle_update(_make_update("/unknown_cmd"))
    assert result is not None
    assert "bilinmeyen" in result.lower() or "unknown" in result.lower()


def test_handle_update_non_command():
    """Normal mesaj yardim yaniti dondurur."""
    result = telegram_polling.handle_update(_make_update("merhaba dunya"))
    assert result is not None
    assert "help" in result.lower() or "yardim" in result.lower()


def test_handle_update_empty_text():
    result = telegram_polling.handle_update({"update_id": 1, "message": {"chat": {"id": "1"}}})
    assert result is None


# ---------------------------------------------------------------------------
# update introspection tests
# ---------------------------------------------------------------------------

def test_get_chat_id_from_update():
    update = {"message": {"chat": {"id": 42}}}
    assert telegram_polling.get_chat_id_from_update(update) == 42


def test_get_text_from_update():
    update = {"message": {"text": "/start"}}
    assert telegram_polling.get_text_from_update(update) == "/start"


def test_get_chat_id_no_message():
    assert telegram_polling.get_chat_id_from_update({}) is None


def test_get_text_no_message():
    assert telegram_polling.get_text_from_update({}) is None


# ---------------------------------------------------------------------------
# Yeni orkestrator komut testleri
# ---------------------------------------------------------------------------


def test_cmd_at_unauthorized(_tmp_board):
    result = telegram_polling.handle_update(_make_update("/at T1 kilo Test Gorev"))
    assert result is not None
    assert "Yetkisiz" in result or "yetkili" in result


def test_cmd_at_authorized(_tmp_board):
    with patch.dict("os.environ", {"TELEGRAM_CHAT_ID": "999"}):
        result = telegram_polling.handle_update(_make_update('/at T1 kilo "Test Gorev"'))
    assert result is not None
    assert "Gorev eklendi" in result
    board = json.loads(_tmp_board.read_text(encoding="utf-8"))
    assert any(t["task_id"] == "T1" and t["sahip"] == "kilo" for t in board)


def test_cmd_pano(_tmp_board):
    with patch.dict("os.environ", {"TELEGRAM_CHAT_ID": "999"}):
        telegram_polling.handle_update(_make_update('/at T1 kilo "Test Gorev"'))
        result = telegram_polling.handle_update(_make_update("/pano"))
    assert result is not None
    assert "PANO" in result
    assert "T1" in result


def test_cmd_onaylar(_tmp_board):
    with patch.dict("os.environ", {"TELEGRAM_CHAT_ID": "999"}):
        telegram_polling.handle_update(_make_update("/at T2 kilo Test"))
        telegram_polling._trigger.teslim_et("T2", "kilo", "ozet")
        result = telegram_polling.handle_update(_make_update("/onaylar"))
    assert result is not None
    assert "ONAY BEKLEYEN" in result
    assert "T2" in result


def test_cmd_onayla(_tmp_board):
    with patch.dict("os.environ", {"TELEGRAM_CHAT_ID": "999"}):
        telegram_polling.handle_update(_make_update("/at T3 kilo Test"))
        telegram_polling._trigger.teslim_et("T3", "kilo", "ozet")
        result = telegram_polling.handle_update(_make_update("/onayla T3"))
    assert result is not None
    assert "Onaylandi" in result or "onaylandi" in result or "done" in result
    task = telegram_polling._task_board.gorev_getir("T3")
    assert task is not None and task["durum"] == "done"


def test_cmd_reddet(_tmp_board):
    with patch.dict("os.environ", {"TELEGRAM_CHAT_ID": "999"}):
        telegram_polling.handle_update(_make_update("/at T4 kilo Test"))
        telegram_polling._trigger.teslim_et("T4", "kilo", "ozet")
        result = telegram_polling.handle_update(_make_update("/reddet T4 Neden"))
    assert result is not None
    assert "Reddedildi" in result or "reddet" in result.lower()
    task = telegram_polling._task_board.gorev_getir("T4")
    assert task is not None and task["durum"] == "aktif"


def test_cmd_nobet(_tmp_board):
    with patch.dict("os.environ", {"TELEGRAM_CHAT_ID": "999"}):
        result = telegram_polling.handle_update(_make_update("/nobet"))
    assert result is not None
    assert "NOBET" in result


def test_cmd_nobet_ayar(_tmp_board):
    with patch.dict("os.environ", {"TELEGRAM_CHAT_ID": "999"}):
        result = telegram_polling.handle_update(_make_update("/nobet_ayar 600"))
    assert result is not None
    assert "600" in result
    ayar = telegram_polling._nobetci.nobetci_ayar_oku()
    assert ayar["kademe_sn"] == 600


def test_cmd_menu(_tmp_board):
    result = telegram_polling.handle_update(_make_update("/menu"))
    assert result is not None
    assert "ANA MENÜ" in result or "ana menü" in result.lower()


def test_cmd_teslim(_tmp_board):
    with patch.dict("os.environ", {"TELEGRAM_CHAT_ID": "999"}):
        telegram_polling.handle_update(_make_update("/at T5 kilo Test"))
        result = telegram_polling.handle_update(_make_update("/teslim T5 Ozet"))
    assert result is not None
    assert "Teslim" in result or "teslim" in result.lower() or "review" in result.lower()


def test_cmd_teslim_missing_args(_tmp_board):
    with patch.dict("os.environ", {"TELEGRAM_CHAT_ID": "999"}):
        result = telegram_polling.handle_update(_make_update("/teslim"))
    assert result is not None
    assert "Kullanim" in result or "Ornek" in result or "usag" in result.lower()


def test_alias_gorev_ekle(_tmp_board):
    with patch.dict("os.environ", {"TELEGRAM_CHAT_ID": "999"}):
        result = telegram_polling.handle_update(_make_update("/gorev-ekle T6 kilo Test"))
    assert result is not None
    assert "Gorev eklendi" in result
    board = json.loads(_tmp_board.read_text(encoding="utf-8"))
    assert any(t["task_id"] == "T6" for t in board)


def test_alias_durum(_tmp_board):
    with patch.dict("os.environ", {"TELEGRAM_CHAT_ID": "999"}):
        result = telegram_polling.handle_update(_make_update("/durum"))
    assert result is not None
    assert "PROJE DURUMU" in result or "DURUM" in result.upper()


def test_alias_gorev_durum(_tmp_board):
    with patch.dict("os.environ", {"TELEGRAM_CHAT_ID": "999"}):
        telegram_polling.handle_update(_make_update("/at T7 kilo Test"))
        result = telegram_polling.handle_update(_make_update("/gorev-durum T7 review"))
    assert result is not None
    assert "guncellendi" in result.lower() or "Guncellendi" in result
    task = telegram_polling._task_board.gorev_getir("T7")
    assert task is not None and task["durum"] == "review"


def test_alias_nobet_ayar(_tmp_board):
    with patch.dict("os.environ", {"TELEGRAM_CHAT_ID": "999"}):
        result = telegram_polling.handle_update(_make_update("/nobet-ayar 300"))
    assert result is not None
    assert "300" in result
    ayar = telegram_polling._nobetci.nobetci_ayar_oku()
    assert ayar["kademe_sn"] == 300


def test_cmd_at_usage_example(_tmp_board):
    with patch.dict("os.environ", {"TELEGRAM_CHAT_ID": "999"}):
        result = telegram_polling.handle_update(_make_update("/at"))
    assert result is not None
    assert "Ornek" in result or "Kullanim" in result


def test_cmd_onayla_usage_example(_tmp_board):
    with patch.dict("os.environ", {"TELEGRAM_CHAT_ID": "999"}):
        result = telegram_polling.handle_update(_make_update("/onayla"))
    assert result is not None
    assert "Ornek" in result or "Kullanim" in result


def test_cmd_reddet_usage_example(_tmp_board):
    with patch.dict("os.environ", {"TELEGRAM_CHAT_ID": "999"}):
        result = telegram_polling.handle_update(_make_update("/reddet"))
    assert result is not None
    assert "Ornek" in result or "Kullanim" in result


def test_cmd_help_has_categories(_tmp_board):
    result = telegram_polling.cmd_help("/help")
    assert "GÖREV YÖNETİMİ" in result
    assert "ONAY" in result.upper() or "Onay" in result
    assert "DURUM" in result.upper() or "Durum" in result
    assert "NÖBETÇİ" in result or "NOBET" in result


def test_cmd_help_commands_are_plain_and_spaced():
    """Komutlar inline HTML içine alınmaz ve komutlar boş satırla ayrılır."""
    result = telegram_polling.cmd_help("/help")
    lines = result.splitlines()
    command_indexes = [index for index, line in enumerate(lines) if line.startswith("/")]

    for index in command_indexes:
        line = lines[index]
        assert "<code>" not in line
        assert "</code>" not in line
        assert "<i>" not in line
        assert "</i>" not in line
        if index != command_indexes[-1]:
            assert lines[index + 1] == ""

    # Son komuttan sonra da Telegram'a bir satır sonu ulaşır.
    assert result.endswith("\n")


def test_cmd_help_lists_all_privileged_commands():
    result = telegram_polling.cmd_help("/help")
    expected = {
        "/restart_etl",
        "/set_status",
        "/set_task_status",
        "/gorev-ekle",
        "/pano",
        "/onaylar",
        "/onayla",
        "/reddet",
        "/teslim",
        "/nobet",
        "/nobet-ayar",
    }
    assert all(command in result for command in expected)


def test_cmd_help_distinguishes_status_aliases():
    result = telegram_polling.cmd_help("/help")
    assert "/set_status — project_state.md'ye not ekler" in result
    assert "/set_task_status — Task board durumunu gunceller" in result
    assert "/gorev-durum — Görev durumunu günceller (alias: /set_task_status)" in result
