# -*- coding: utf-8 -*-
"""Telegram bot — canonical long-polling motoru.

Bu modul, python-telegram-bot kutuphanesine bagimlilik kurmadan
doğrudan Telegram Bot API getUpdates long-polling metodunu kullanir.

Komutlar:
    /start              - Botu baslat, hos gelesmesi
    /help               - Yardim metni
    /menu               - Etkileşimli komut menüsü
    /status (alias /durum) - Aktif gorevler + proje durumu
    /gorev              - Task_board.json'dan tum gorevleri listele
    /gorev-ekle (alias /at) - Panoya gorev ekle ve tetik at
    /gorev-durum (alias /set_status) - Task board'da gorev durumunu guncelle (yetkili)
    /rapor              - KPI raporu (data/kpi_raporu.md)
    /wiki               - OSTİM kalite raporu (data/ostim/kalite_raporu.md)
    /restart_etl        - ETL pipeline yeniden baslatin
    /degisiklik         - CHANGELOG.md'yi goster
    /gunluk             - Gunluk ozet
    /izleme             - Kalite + proje izleme
    /onaylar            - Onay bekleyen teslimleri listeler
    /onayla <id>        - Gorevi onayla (done) (yetkili)
    /reddet <id> <neden> - Gorevi reddet (aktife geri dönder) (yetkili)
    /teslim <id> <ozet> - Gorevi incelemeye gönder (yetkili)
    /nobet              - Nöbetçi turu attırır
    /nobet-ayar <sn>    - Nöbetci alarm suresini günceller (yetkili)

    Alias: /at = /gorev-ekle, /set_status = /gorev-durum, /status = /durum, /nobet_ayar = /nobet-ayar

    Calisma zamani degiskenleri (.env):
    TELEGRAM_BOT_TOKEN
    TELEGRAM_CHAT_ID
    TELEGRAM_BOT_USERNAME (opsiyonel; @BotName parsing icin)
    ETL_RESTART_CMD (opsiyonel; varsayilan: python scripts/refresh_pipeline.py)

    Kullanim:
    set TELEGRAM_BOT_TOKEN=...
    set TELEGRAM_CHAT_ID=...
    python scripts/telegram_polling.py
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Optional

import requests
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(ROOT))

from src.company_master.utils.telegram_bot import (
    DEFAULT_TIMEOUT,
    get_updates,
    html_escape,
    is_authorized,
    masked_token,
    parse_command,
    send_message,
    _get_chat_id,
    _get_token,
    _get_bot_username,
    _load_env,
)
from src.company_master.orchestrator import trigger as _trigger
from src.company_master.orchestrator import nobetci as _nobetci
from src.company_master.orchestrator import task_board as _task_board

POLL_TIMEOUT = 30
POLL_RETRY_DELAY = 5
POLL_LIMIT = 100

ALLOWED_UPDATES = ["message"]
COMMANDS_INFO = {
    "start": ("Botu baslatir / hos gelesmesi", ""),
    "help": ("Bu yardim metnini gosterir", ""),
    "menu": ("Etkilesimli ana menu", ""),
    "status": ("Proje durumu + aktif gorevler (alias: /durum)", ""),
    "durum": ("Proje durumu + aktif gorevler (alias: /status)", ""),
    "gorev": ("Task board'daki tum goeveleri listeler", ""),
    "gorev-ekle": ("Panoya gorev ekle (alias: /at)", ""),
    "at": ("Panoya gorev ekle (alias: /gorev-ekle)", ""),
    "gorev-durum": ("Gorev durumunu guncelle (alias: /set_status)", ""),
    "set_status": ("Gorev durumunu guncelle (alias: /gorev-durum)", ""),
    "rapor": ("KPI raporunu gosterir", ""),
    "wiki": ("OSTIM kalite raporunu gosterir", ""),
    "restart_etl": ("ETL pipeline'i yeniden baslatir", ""),
    "degisiklik": ("CHANGELOG.md'yi gosterir", ""),
    "gunluk": ("Gunluk ozet raporu gonderir", ""),
    "izleme": ("Kalite + proje izleme", ""),
    "pano": ("Bekleyen tetik ve onay ozeti", ""),
    "onaylar": ("Onay bekleyen teslimleri listeler", ""),
    "onayla": ("Gorevi onayla (done): /onayla <task_id>", ""),
    "reddet": ("Gorevi reddet: /reddet <task_id> <neden>", ""),
    "teslim": ("Gorevi incelemeye gond: /teslim <task_id> <ozet>", ""),
    "nobet": ("Nobetci turu attirir", ""),
    "nobet-ayar": ("Nobet alarm suresini gunceller (alias: /nobet_ayar)", ""),
    "nobet_ayar": ("Nobet alarm suresini gunceller (alias: /nobet-ayar)", ""),
}


# ---------------------------------------------------------------------------
# Veri kaynaklari (statik dosyalardan okuma)
# ---------------------------------------------------------------------------

def _read_file(rel_path: str) -> str:
    """Proje kokeliginden dosya okur; yoksa hata mesaji done."""
    path = ROOT / rel_path
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"[ dosya bulunamadi: {rel_path} ]"
    except Exception as exc:
        return f"[ okuma hatasi: {exc} ]"


def read_project_state() -> str:
    """V10/project_state.md'yi okur."""
    return _read_file("AI proje v1/V10/project_state.md")


def read_task_board() -> list[dict[str, Any]]:
    """data/orchestrator/task_board.json'u dinamik okur."""
    path = ROOT / "data" / "orchestrator" / "task_board.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        if isinstance(data, list):
            return data
        return []
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    except Exception:
        return []


def read_kpi_report() -> str:
    """data/kpi_raporu.md'yi okur."""
    return _read_file("data/kpi_raporu.md")


def read_quality_report() -> str:
    """data/ostim/kalite_raporu.md'yi okur."""
    return _read_file("data/ostim/kalite_raporu.md")


def read_changelog() -> str:
    """AI proje v1/V10/CHANGELOG.md'yi okur."""
    return _read_file("AI proje v1/V10/CHANGELOG.md")


def read_active_tasks() -> list[dict[str, Any]]:
    """Task board'dan aktif (yapımda) goeveleri getirir."""
    board = read_task_board()
    return [t for t in board if t.get("durum") not in ("done",)]


def read_done_count() -> int:
    """Task board'daki tamamlanmis gorev sayisini getirir."""
    board = read_task_board()
    return len([t for t in board if t.get("durum") == "done"])


def read_quality_score() -> str:
    """Kalite skorunu kpi_raporu.md'den cikarir."""
    text = read_kpi_report()
    match = re.search(r"Ortalama Kalite Skoru:\s*([\d.]+)/100", text, re.IGNORECASE)
    if match:
        return match.group(1)
    return "bilinmiyor"


# ---------------------------------------------------------------------------
# Atomik set_status (task_board.json)
# ---------------------------------------------------------------------------

def set_task_status(task_id: str, durum: str) -> dict[str, Any]:
    """Task board'da bir gorevin durumunu atomik olarak gunceller.

    Returns: {"ok": True/False, "error": "...", "task": {...}}
    """
    from src.company_master.orchestrator.task_board import (
        gorev_guncelle,
        gorev_getir,
    )

    # Gecerli durum kontrolu
    valid_statuses = ("plan", "aktif", "review", "done", "blocked")
    if durum not in valid_statuses:
        return {"ok": False, "error": f"Gecersiz durum: {durum}. Gecerli: {', '.join(valid_statuses)}"}

    task = gorev_getir(task_id)
    if not task:
        return {"ok": False, "error": f"Gorev bulunamadi: {task_id}"}

    result = gorev_guncelle(task_id, durum=durum)
    if result:
        return {"ok": True, "task": result}
    return {"ok": False, "error": "Guncelleme basarisiz"}


# ---------------------------------------------------------------------------
# ETL restart (subprocess ile dogru cwd)
# ---------------------------------------------------------------------------

def restart_etl(cmd: str | list[str] | None = None) -> dict[str, Any]:
    """ETL pipeline'i yeniden baslatir.

    cmd verilmezse env'den ETL_RESTART_CMD okunur,
    yoksa varsayilan: [sys.executable, scripts/refresh_pipeline.py].
    Liste-form argv kullanilir; shell kapali (komut enjeksiyonuna karsi).
    """
    import shlex

    if cmd is None:
        env_cmd = os.environ.get("ETL_RESTART_CMD")
        if env_cmd:
            cmd = shlex.split(env_cmd)
        else:
            cmd = [sys.executable, str(ROOT / "scripts" / "refresh_pipeline.py")]
    elif isinstance(cmd, str):
        cmd = shlex.split(cmd)

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = proc.communicate(timeout=30)
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": stdout[:500],
            "stderr": stderr[:500],
        }
    except subprocess.TimeoutExpired:
        proc.kill()
        return {"ok": False, "error": "ETL timeout (30s)"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


# ---------------------------------------------------------------------------
# Komut handler'lari
# ---------------------------------------------------------------------------

def cmd_start(text: str) -> str:
    """/start komutu."""
    return (
        "<b>Ankara B2B Intelligence Bot</b>\n\n"
        "Hosgeldiniz! Komutlari gormek icin <code>/help</code> veya "
        "<code>/menu</code> yazin.\n\n"
        "Kategoriler:\n"
        "<code>/gorev*</code> Görev yönetimi\n"
        "<code>/onay* /teslim*</code> Onay ve inceleme\n"
        "<code>/durum /rapor /wiki /gunluk /izleme*</code> Durum ve raporlama\n"
        "<code>/nobet*</code> Nöbetçi\n"
        "<code>/help /menu /start</code> Yardım"
    )


def cmd_help(text: str) -> str:
    """/help komutu — kategorize komut listesi ve örnekler."""
    lines = [
        "<b>KOMUTLAR</b>\n",
        "<b>GÖREV YÖNETİMİ</b>",
        "<code>/gorev-ekle</code> (alias <code>/at</code>) — Panoya görev ekle ve tetik at",
        "   <i>Kullanım: /gorev-ekle &lt;task_id&gt; &lt;ajan&gt; &lt;baslik&gt;</i>",
        "<code>/gorev</code> — Tüm görevleri duruma göre listele",
        "<code>/gorev-durum</code> (alias <code>/set_status</code>) — Görev durumunu güncelle",
        "   <i>Kullanım: /gorev-durum &lt;task_id&gt; &lt;durum&gt;</i>",
        "",
        "<b>ONAY &amp; İNCELEME</b>",
        "<code>/onaylar</code> — Onay bekleyen teslimleri listeler",
        "<code>/onayla</code> — Görevi onayla (done)",
        "   <i>Kullanım: /onayla &lt;task_id&gt;</i>",
        "<code>/reddet</code> — Görevi reddet (aktife geri dönder)",
        "   <i>Kullanım: /reddet &lt;task_id&gt; &lt;neden&gt;</i>",
        "<code>/teslim</code> — Görevi incelemeye gönder",
        "   <i>Kullanım: /teslim &lt;task_id&gt; &lt;ozet&gt;</i>",
        "",
        "<b>DURUM &amp; RAPORLAMA</b>",
        "<code>/durum</code> (alias <code>/status</code>) — Proje durumu + aktif görevler",
        "<code>/pano</code> — Bekleyen tetik ve onay özeti",
        "<code>/rapor</code> — KPI raporu",
        "<code>/wiki</code> — OSTİM kalite raporu",
        "<code>/gunluk</code> — Günlük özet",
        "<code>/izleme</code> — Kalite + proje izleme",
        "<code>/degisiklik</code> — CHANGELOG.md",
        "",
        "<b>NÖBETÇİ</b>",
        "<code>/nobet</code> — Nöbetçi turu attırır",
        "<code>/nobet-ayar</code> (alias <code>/nobet_ayar</code>) — Alarm süresini güncelle",
        "   <i>Kullanım: /nobet-ayar &lt;kademe_sn&gt;</i>",
        "",
        "<b>YARDIM</b>",
        "<code>/menu</code> — Etkileşimli komut menüsü",
        "<code>/help</code> — Bu yardım metni",
        "<code>/start</code> — Başlangıç",
        "",
        "<i>Yetkili komutlar: /gorev-durum, /onayla, /reddet, /teslim, /nobet-ayar</i>",
    ]
    return "\n".join(lines)


def cmd_menu(text: str) -> str:
    """/menu komutu — etkileşimli ana menü."""
    lines = [
        "<b>📋 ANA MENÜ</b>\n",
        "1. <b>Görev yönetimi</b> — /gorev, /gorev-ekle, /gorev-durum",
        "2. <b>Onay &amp; inceleme</b> — /onaylar, /onayla, /reddet, /teslim",
        "3. <b>Durum &amp; raporlama</b> — /durum, /pano, /rapor, /wiki, /gunluk",
        "4. <b>Nöbetçi</b> — /nobet, /nobet-ayar",
        "5. <b>Yardım</b> — /help, /menu, /start",
        "",
        "Bir komut yazin veya <code>/help</code> ile detayları görüntüleyin.",
    ]
    return "\n".join(lines)


def cmd_status(text: str) -> str:
    """/status komutu — proje durumu + aktif goresv."""
    active = read_active_tasks()
    done = read_done_count()
    quality = read_quality_score()

    lines = ["<b>PROJE DURUMU</b>\n"]
    lines.append(f"Toplam gorev: {len(read_task_board())}")
    lines.append(f"Aktif gorev: <b>{len(active)}</b>")
    lines.append(f"Tamamlandi: <b>{done}</b>")
    lines.append(f"Kalite skoru: <b>{quality}</b>/100")

    if active:
        lines.append("\n<b>Aktif Gorevler:</b>")
        for t in active[:10]:
            lines.append(
                f"  <code>{html_escape(t.get('task_id', '?'))}</code> "
                f"[{html_escape(t.get('durum', ''))}] "
                f"{html_escape(t.get('baslik', '')[:50])}"
            )
        if len(active) > 10:
            lines.append(f"  ... ve {len(active) - 10} daha")

    lines.append(f"\n<i>{time.strftime('%H:%M:%S')}</i>")
    return "\n".join(lines)


def cmd_gorev(text: str) -> str:
    """/gorev komutu — tum goresv listesi."""
    board = read_task_board()
    if not board:
        return "<b>Gorev listesi bos veya dosya bulunamadi.</b>"

    lines = [f"<b>GOREV PANOSU</b> ({len(board)} gorev)\n"]
    by_durum: dict[str, list[dict]] = {}
    for t in board:
        d = t.get("durum", "bilinmiyor")
        by_durum.setdefault(d, []).append(t)

    for durum in ("aktif", "plan", "review", "done", "blocked"):
        tasks = by_durum.get(durum, [])
        if not tasks:
            continue
        lines.append(f"\n<b>{html_escape(durum.upper())}</b> ({len(tasks)}):")
        for t in tasks[:15]:
            lines.append(
                f"  <code>{html_escape(t.get('task_id', '?'))}</code> "
                f"[{html_escape(t.get('sahip', ''))}] "
                f"{html_escape(t.get('baslik', '')[:60])}"
            )
        if len(tasks) > 15:
            lines.append(f"  ... ve {len(tasks) - 15} daha")

    lines.append(f"\n<i>{time.strftime('%H:%M:%S')}</i>")
    return "\n".join(lines)


def cmd_rapor(text: str) -> str:
    """/rapor komutu — KPI raporu."""
    content = read_kpi_report()
    truncated = content[:2000] if len(content) > 2000 else content
    return f"<pre>{html_escape(truncated)}</pre>"


def cmd_wiki(text: str) -> str:
    """/wiki komutu — OSTİM kalite raporu."""
    content = read_quality_report()
    truncated = content[:2000] if len(content) > 2000 else content
    return f"<pre>{html_escape(truncated)}</pre>"


def cmd_degisiklik(text: str) -> str:
    """/degisiklik komutu — changelog."""
    content = read_changelog()
    if not content or content.startswith("[ "):
        return "<b>CHANGELOG.md bulunamadi veya bos.</b>"
    truncated = content[:2000] if len(content) > 2000 else content
    return f"<pre>{html_escape(truncated)}</pre>"


def cmd_gunluk(text: str) -> str:
    """/gunluk komutu — gunluk ozet."""
    board = read_task_board()
    active = read_active_tasks()
    done = read_done_count()
    quality = read_quality_score()
    today = time.strftime("%Y-%m-%d")

    lines = [f"<b>GUNLUK OZET — {today}</b>\n"]
    lines.append(f"Toplam gorev: {len(board)}")
    lines.append(f"Aktif: {len(active)} | Tamamlandi: {done}")
    lines.append(f"Kalite skoru: {quality}/100")
    lines.append(f"API tabanli: {bool(board)}")

    # Son 5 tamamlanmamis gorev
    not_done = [t for t in board if t.get("durum") != "done"][-5:]
    if not_done:
        lines.append("\n<b>Son aktif gorevler:</b>")
        for t in not_done[-5:]:
            lines.append(
                f"  {html_escape(t.get('task_id', '?'))}: "
                f"{html_escape(t.get('baslik', '')[:50])} "
                f"[{html_escape(t.get('durum', ''))}]"
            )
    lines.append(f"\n<i>{time.strftime('%H:%M:%S')}</i>")
    return "\n".join(lines)


def cmd_izleme(text: str) -> str:
    """/izleme komutu — kalite ve proje izleme."""
    quality = read_quality_score()
    state = read_project_state()
    active = read_active_tasks()

    lines = ["<b>IZLEME PANELI</b>\n"]
    lines.append(f"Kalite skoru: <b>{quality}</b>/100")
    lines.append(f"Aktif gorev: <b>{len(active)}</b>")

    # State dosyasindan basliklari cikar
    state_lines = state.split("\n")[:50]
    for sl in state_lines:
        sl = sl.strip()
        if sl.startswith("#") or sl.startswith("-") or sl.startswith("•") or not sl:
            lines.append(f"<code>{html_escape(sl[:100])}</code>")
    lines.append(f"\n<i>{time.strftime('%H:%M:%S')}</i>")
    return "\n".join(lines)


def cmd_restart_etl(text: str) -> str:
    """/restart_etl komutu — ETL pipeline yeniden baslat."""
    result = restart_etl()
    if result["ok"]:
        msg = f"<b>ETL yeniden baslatildi</b>\n"
        msg += f"<code>{html_escape(result.get('stdout', '')[:300])}</code>\n"
        msg += f"<i>{time.strftime('%H:%M:%S')}</i>"
    else:
        msg = f"<b>ETL hatasi</b>\n"
        msg += f"<code>{html_escape(result.get('error', 'bilinmiyor')[:300])}</code>\n"
        msg += f"<i>{time.strftime('%H:%M:%S')}</i>"
    return msg


def cmd_set_status(text: str, args: list[str]) -> str:
    """/gorev-durum (alias /set_status) — gorev durumunu guncelle (yetkili)."""
    if len(args) < 2:
        return (
            "<b>Kullanim:</b> <code>/gorev-durum &lt;task_id&gt; &lt;durum&gt;</code>\n"
            "<i>Ornek: /gorev-durum TASK-01 review</i>\n"
            "<i>Gecerli durumlar: plan, aktif, review, done, blocked</i>"
        )
    task_id = args[0]
    durum = args[1].lower()

    result = set_task_status(task_id, durum)
    if result["ok"]:
        t = result["task"]
        msg = (
            "<b>Gorev durumu guncellendi</b>\n"
            f"<code>{html_escape(t.get('task_id', '?'))}</code> → "
            f"<b>{html_escape(t.get('durum', ''))}</b>\n"
            f"<i>{html_escape(t.get('baslik', '')[:60])}</i>\n"
            f"<i>{time.strftime('%H:%M:%S')}</i>"
        )
    else:
        msg = f"<b>Guncelleme basarisiz:</b> {html_escape(result.get('error', 'bilinmiyor'))}"
    return msg


# ---------------------------------------------------------------------------
# Yeni orkestrator komutlari
# ---------------------------------------------------------------------------

def cmd_at(text: str, args: list[str]) -> str:
    """/at (alias /gorev-ekle) — panoya gorev ekle ve ajan postasina tetik at."""
    if len(args) < 3:
        return (
            "<b>Kullanim:</b> <code>/gorev-ekle &lt;task_id&gt; &lt;ajan&gt; &lt;baslik&gt;</code>\n"
            "<i>Ornek: /gorev-ekle TASK-01 kilo \"Test gorev\"</i>"
        )
    task_id = args[0]
    ajan = args[1]
    baslik = " ".join(args[2:]).strip().strip('"')
    try:
        task = _task_board.gorev_ekle(
            task_id=task_id,
            baslik=baslik,
            sahip=ajan,
            dosyalar=[],
            source="ic",
        )
        _trigger.tetik_ekle(
            task_id=task_id,
            ajan=ajan,
            talimat=f"Telegram /gorev-ekle: {baslik}",
        )
        return (
            "<b>Gorev eklendi</b>\n"
            f"<code>{html_escape(task_id)}</code> → "
            f"<b>{html_escape(ajan)}</b>\n"
            f"<i>{html_escape(baslik[:100])}</i>"
        )
    except _trigger.TriggerError as exc:
        return f"<b>⚠️</b> {html_escape(str(exc))}"
    except ValueError as exc:
        return f"<b>⚠️</b> {html_escape(str(exc))}"
    except Exception as exc:
        return f"<b>❌ Hata:</b> {html_escape(str(exc))}"


def cmd_teslim(text: str, args: list[str]) -> str:
    """/teslim komutu — görevi incelemeye gönder (yetkili)."""
    if len(args) < 2:
        return (
            "<b>Kullanim:</b> <code>/teslim &lt;task_id&gt; &lt;ozet&gt;</code>\n"
            "<i>Ornek: /teslim TASK-01 Parse tamamlandi</i>"
        )
    task_id = args[0]
    ozet = " ".join(args[1:]).strip().strip('"')
    try:
        result = _trigger.teslim_et(
            task_id=task_id,
            ajan="telegram_bot",
            ozet=ozet,
        )
        return (
            f"<b>Teslim edildi</b>\n"
            f"<code>{html_escape(task_id)}</code> → <b>review</b>\n"
            f"<i>{html_escape(ozet[:100])}</i>\n"
            f"<i>Onay kuyruguna eklendi.</i>"
        )
    except _trigger.TriggerError as exc:
        return f"<b>⚠️</b> {html_escape(str(exc))}"
    except Exception as exc:
        return f"<b>❌ Hata:</b> {html_escape(str(exc))}"


def cmd_pano(text: str, args: list[str] | None = None) -> str:
    """/pano komutu — bekleyen tetik ve onay ozeti."""
    lines = ["<b>PANO ÖZETİ</b>\n"]

    triggers_dir = _task_board.STATE_DIR / "triggers"
    if triggers_dir.exists():
        for dosya in sorted(triggers_dir.glob("*.jsonl")):
            ajan = dosya.stem
            bekleyen = _trigger.bekleyen_tetikler(ajan)
            if bekleyen:
                lines.append(f"<b>{html_escape(ajan)}</b> ({len(bekleyen)} tetik bekliyor):")
                for k in bekleyen[:10]:
                    lines.append(
                        f"  <code>{html_escape(k.get('task_id', '?'))}</code> "
                        f"{html_escape(k.get('talimat', '')[:60])} "
                        f"<i>{html_escape(k.get('tarih', ''))}</i>"
                    )

    onaylar = _trigger.onay_bekleyenler()
    if onaylar:
        lines.append(f"\n<b>ONAY BEKLEYEN TESLİMLER</b> ({len(onaylar)}):")
        for k in onaylar[:10]:
            lines.append(
                f"  <code>{html_escape(k.get('task_id', '?'))}</code> — "
                f"<b>{html_escape(k.get('ajan', ''))}</b> "
                f"{html_escape(k.get('ozet', '')[:80])}"
            )
    else:
        lines.append("\n<i>Onay bekleyen teslim yok.</i>")

    lines.append(f"\n<i>{time.strftime('%H:%M:%S')}</i>")
    return "\n".join(lines)


def cmd_onaylar(text: str, args: list[str] | None = None) -> str:
    """/onaylar komutu — inceleme bekleyen teslimleri listeler."""
    onaylar = _trigger.onay_bekleyenler()
    if not onaylar:
        return "<b>Onay bekleyen teslim yok.</b>"

    lines = [f"<b>ONAY BEKLEYENLER</b> ({len(onaylar)})\n"]
    for k in onaylar[:20]:
        lines.append(
            f"  <code>{html_escape(k.get('task_id', '?'))}</code> — "
            f"{html_escape(k.get('ajan', ''))}: "
            f"{html_escape(k.get('ozet', '')[:80])}"
        )
    lines.append(f"\n<i>{time.strftime('%H:%M:%S')}</i>")
    return "\n".join(lines)


def cmd_onayla(text: str, args: list[str]) -> str:
    """/onayla komutu — görevi onayla (done)."""
    if not args:
        return (
            "<b>Kullanim:</b> <code>/onayla &lt;task_id&gt;</code>\n"
            "<i>Ornek: /onayla TASK-01</i>"
        )
    task_id = args[0]
    try:
        _trigger.onayla(task_id, onaylayan="telegram_bot")
        task = _task_board.gorev_getir(task_id)
        title = html_escape(task.get("baslik", "")[:80]) if task else ""
        return (
            f"<b>✅ Onaylandı</b>\n"
            f"<code>{html_escape(task_id)}</code> → <b>done</b>\n"
            f"<i>{title}</i>\n"
            f"<i>Kilitli dosyalar serbest bırakildi.</i>"
        )
    except _trigger.TriggerError as exc:
        return f"<b>⚠️</b> {html_escape(str(exc))}"
    except Exception as exc:
        return f"<b>❌ Hata:</b> {html_escape(str(exc))}"


def cmd_reddet(text: str, args: list[str]) -> str:
    """/reddet komutu — görevi reddet (aktife geri dönder)."""
    if len(args) < 2:
        return (
            "<b>Kullanim:</b> <code>/reddet &lt;task_id&gt; &lt;neden&gt;</code>\n"
            "<i>Ornek: /reddet TASK-01 Gereksiz duzeltme</i>"
        )
    task_id = args[0]
    neden = " ".join(args[1:]).strip().strip('"')
    try:
        _trigger.reddet(task_id, onaylayan="telegram_bot", neden=neden)
        return (
            f"<b>Reddedildi</b>\n"
            f"<code>{html_escape(task_id)}</code> → <b>aktif</b>\n"
            f"<i>Neden: {html_escape(neden[:100])}</i>"
        )
    except _trigger.TriggerError as exc:
        return f"<b>⚠️</b> {html_escape(str(exc))}"
    except Exception as exc:
        return f"<b>❌ Hata:</b> {html_escape(str(exc))}"


def cmd_nobet(text: str, args: list[str] | None = None) -> str:
    """/nobet komutu — nöbetçi turu attırır."""
    try:
        results = _nobetci.nobet_tut()
        if not results:
            return f"<b>NOBET:</b> geciken tetik yok.\n<i>{time.strftime('%H:%M:%S')}</i>"

        lines = [f"<b>NOBET RAPORU</b> ({len(results)} geciken tetik)\n"]
        for r in results:
            lines.append(
                f"  <code>{html_escape(r.get('task_id', ''))}</code> — "
                f"{html_escape(r.get('ajan', ''))} — "
                f"{html_escape(str(r.get('gecikme_dk', '')))} dk gecikme"
            )
        lines.append(f"\n<i>{time.strftime('%H:%M:%S')}</i>")
        return "\n".join(lines)
    except Exception as exc:
        return f"<b>❌ Hata:</b> {html_escape(str(exc))}"


def cmd_nobet_ayar(text: str, args: list[str]) -> str:
    """/nobet-ayar (alias /nobet_ayar) — nöbetci alarm suresini günceller."""
    if not args:
        return (
            "<b>Kullanim:</b> <code>/nobet-ayar &lt;kademe_sn&gt;</code>\n"
            "<i>Ornek: /nobet-ayar 600</i>"
        )
    try:
        kademe_sn = int(args[0])
        if kademe_sn <= 0:
            raise ValueError
    except ValueError:
        return "<b>⚠️</b> Kademe_sn pozitif tamsayı olmalı."

    try:
        ayar = _nobetci.nobetci_ayar_oku()
        ayar["kademe_sn"] = kademe_sn
        _nobetci.nobetci_ayar_yaz(ayar)
        return f"<b>Nöbet ayarı güncellendi</b>: {kademe_sn} saniye"
    except Exception as exc:
        return f"<b>❌ Hata:</b> {html_escape(str(exc))}"


# Komut dispatch table
COMMAND_HANDLERS: dict[str, Any] = {
    "start": (cmd_start, False, False),
    "help": (cmd_help, False, False),
    "menu": (cmd_menu, False, False),
    "status": (cmd_status, False, False),
    "durum": (cmd_status, False, False),
    "gorev": (cmd_gorev, False, False),
    "rapor": (cmd_rapor, False, False),
    "wiki": (cmd_wiki, False, False),
    "restart_etl": (cmd_restart_etl, True, False),
    "degisiklik": (cmd_degisiklik, False, False),
    "gunluk": (cmd_gunluk, False, False),
    "izleme": (cmd_izleme, False, False),
    "set_status": (cmd_set_status, True, True),
    "gorev-durum": (cmd_set_status, True, True),
    "at": (cmd_at, True, True),
    "gorev-ekle": (cmd_at, True, True),
    "pano": (cmd_pano, True, False),
    "onaylar": (cmd_onaylar, True, False),
    "onayla": (cmd_onayla, True, True),
    "reddet": (cmd_reddet, True, True),
    "teslim": (cmd_teslim, True, True),
    "nobet": (cmd_nobet, True, False),
    "nobet-ayar": (cmd_nobet_ayar, True, True),
    "nobet_ayar": (cmd_nobet_ayar, True, True),
}


# ---------------------------------------------------------------------------
# Update isleme
# ---------------------------------------------------------------------------

def get_chat_id_from_update(update: dict[str, Any]) -> str | int | None:
    """Update dict'inden chat_id'yi cikarir."""
    message = update.get("message") or update.get("edited_message")
    if not message:
        return None
    chat = message.get("chat")
    if chat:
        return chat.get("id")
    return None


def get_text_from_update(update: dict[str, Any]) -> str | None:
    """Update dict'inden mesaj metnini cikarir."""
    message = update.get("message") or update.get("edited_message")
    if not message:
        return None
    return message.get("text")


def handle_update(update: dict[str, Any]) -> Optional[str]:
    """Bir update'i isler, yanit metni dondurur (veya None)."""
    chat_id = get_chat_id_from_update(update)
    text = get_text_from_update(update)
    if not text:
        return None

    bot_username = _get_bot_username()
    parsed = parse_command(text, bot_username)
    if parsed is None:
        return None

    command = parsed["command"]
    args = parsed["args"]

    handler_entry = COMMAND_HANDLERS.get(command)
    if not handler_entry:
        return f"<b>Bilinmeyen komut:</b> {html_escape(command)}\n{html_escape('Detay icin /help yazin.')}"

    handler, needs_auth, takes_args = handler_entry

    if needs_auth and not is_authorized(chat_id):
        return (
            "<b>Yetkisiz:</b> Bu komut yetkili kullanicilar icindir.\n"
            f"<i>{time.strftime('%H:%M:%S')}</i>"
        )

    try:
        if takes_args:
            return handler(text, args)
        return handler(text)
    except Exception as exc:
        err = traceback.format_exc()[-400:]
        return f"<b>Handler hatasi:</b> {html_escape(str(exc))}\n<pre>{html_escape(err)}</pre>"


# ---------------------------------------------------------------------------
# Long-polling dongusu
# ---------------------------------------------------------------------------

def run_polling(max_iterations: int = 0, once: bool = False) -> None:
    """Telegram getUpdates long-polling dongusu.

    Args:
        max_iterations: 0 = sonsuz, >0 = o kadar update sonra dur
        once: Tek seferlik calistir (bir update al, isle, cik)
    """
    _load_env()
    token = _get_token()
    if not token:
        print("TELEGRAM_BOT_TOKEN bulunamadi. .env dosyasini kontrol edin.", file=sys.stderr)
        sys.exit(1)

    chat_id = _get_chat_id()
    if not chat_id:
        print("TELEGRAM_CHAT_ID bulunamadi. .env dosyasini kontrol edin.", file=sys.stderr)
        sys.exit(1)

    print(f"Telegram bot polling baslatildi (chat_id={chat_id}, bot={masked_token(token)[:10]}...).", flush=True)

    offset = 0
    iteration = 0

    while True:
        try:
            result = get_updates(
                offset=offset,
                timeout=POLL_TIMEOUT,
                limit=POLL_LIMIT,
                allowed_updates=ALLOWED_UPDATES,
            )

            if not result["ok"]:
                print(f"[polling] getUpdates hatasi: {result['error']}", file=sys.stderr)
                time.sleep(POLL_RETRY_DELAY)
                continue

            updates = result.get("result", [])
            new_offset = result.get("next_offset", 0)

            for update in updates:
                update_id = update.get("update_id", 0)
                try:
                    response = handle_update(update)
                    if response:
                        msg_result = send_message(response)
                        if not msg_result.get("ok"):
                            print(f"[polling] mesaj gonderme hatasi: {msg_result.get('error')}", file=sys.stderr)
                except Exception:
                    print(f"[polling] update islenirken hata: {traceback.format_exc()}", file=sys.stderr)

                # offset'u bir sonraki update'den ileri al (confirmed)
                offset = max(offset, update_id + 1)

            iteration += 1
            if once:
                break
            if max_iterations > 0 and iteration >= max_iterations:
                break

            # long-polling: blocking call, yeni mesaj gelene kadar bekle
            if not updates:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\nPolling durduruldu.")
            break
        except Exception as exc:
            print(f"[polling] beklenmeyen hata: {exc}", file=sys.stderr)
            time.sleep(POLL_RETRY_DELAY)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Telegram bot — canonical long-polling motoru"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=0,
        help="Maksimum update sayisi (0 = sonsuz, varsayilan)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Tek seferlik calistir: bir update al, isle, cik",
    )
    args = parser.parse_args()

    run_polling(max_iterations=args.max_iterations, once=args.once)


if __name__ == "__main__":
    main()
