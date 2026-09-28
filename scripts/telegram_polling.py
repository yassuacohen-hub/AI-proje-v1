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
    /gorev-durum (alias /set_task_status) - Task board'da gorev durumunu guncelle (yetkili)
    /rapor              - KPI raporu (data/kpi_raporu.md)
    /wiki               - V10 wiki sayfalarini listeler
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

    Alias: /at = /gorev-ekle, /set_task_status = /gorev-durum, /status = /durum, /nobet_ayar = /nobet-ayar

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
    "gorev": ("Task board'daki tum gorevleri listeler", ""),
    "gorev-ekle": ("Panoya gorev ekle (alias: /at)", ""),
    "at": ("Panoya gorev ekle (alias: /gorev-ekle)", ""),
    "gorev-durum": ("Task board durumunu guncelle: /gorev-durum <id> <durum>", ""),
    "set_status": ("project_state.md not ekle: /set_status <mesaj>", ""),
    "set_task_status": ("Task board durumunu guncelle: /set_task_status <id> <durum>", ""),
    "rapor": ("KPI raporunu gosterir", ""),
    "wiki": ("V10 wiki sayfalarini listeler", ""),
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
    """Task board'dan aktif (yapımda) gorevleri getirir."""
    board = read_task_board()
    return [t for t in board if t.get("durum") not in ("done",)]


def read_done_count() -> int:
    """Task board'daki tamamlanmis gorev sayisini getirir."""
    board = read_task_board()
    return len([t for t in board if t.get("durum") == "done"])


def read_tamlik_metni() -> str:
    """Kimlik dosyasi tamligini kpi_raporu.md'den cikarir; sunuma hazir metin.

    D-250/7: donen dize zaten olcegi tasir ("3.71 / 6.50 ulasilabilir").
    Cagiran ustune "/100" eklemez --- eski hali 0-10'luk puani 0-100 diye
    sunuyordu. Eski ad ("quality score") da bir beyandi.

    Eski ikinci kaynak (data/ostim/kalite_raporu.md) kaldirildi: o rapor
    "| Ortalama skor | **75.5** / 100 |" yaziyor, yani desenle hicbir zaman
    eslesmedi --- olu fallback'ti. Ayrica orasi JSONL'den hesaplanan ayri bir
    0-100 metrigi; kimlik dosyasi tamligi degil, yerine gecemez.
    """
    match = re.search(
        r"Ortalama Kimlik Dosyasi Tamligi:\s*(.+)", _read_file("data/kpi_raporu.md")
    )
    return match.group(1).strip() if match else "bilinmiyor"


def count_lines(rel_path: str) -> int:
    """Dosyadaki bos olmayan satir sayisini dondurur (yoksa 0)."""
    path = ROOT / rel_path
    if not path.exists():
        return 0
    try:
        return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    except Exception:
        return 0


def count_markdown(rel_dir: str) -> int:
    """Dizin altindaki .md dosya sayisini dondurur (yoksa 0)."""
    path = ROOT / rel_dir
    if not path.exists():
        return 0
    try:
        return sum(1 for _ in path.rglob("*.md"))
    except Exception:
        return 0


# ---------------------------------------------------------------------------
# Atomik project_state not ekleme
# ---------------------------------------------------------------------------

PROJECT_STATE_PATH = "AI proje v1/V10/project_state.md"


def project_state_not_ekle(mesaj: str, tarih: str | None = None) -> dict[str, Any]:
    """project_state.md altina tarihli notu atomik ekler.

    Returns: {"ok": True/False, "error": "...", "dosya": "..."}
    """
    path = ROOT / PROJECT_STATE_PATH
    if not path.exists():
        return {"ok": False, "error": f"project_state.md bulunamadi: {PROJECT_STATE_PATH}"}

    tarih = tarih or time.strftime("%Y-%m-%d")
    entry = f"- [{tarih}] {mesaj.strip()}"
    try:
        content = path.read_text(encoding="utf-8")
        marker = "### Eklenen Notlar"
        if marker in content:
            content = content.replace(marker, f"{marker}\n\n{entry}")
        else:
            content = content.rstrip() + f"\n\n{marker}\n\n{entry}\n"

        # Atomik yaz (tmp + os.replace)
        import os as _os

        tmp = path.with_name(f".{path.name}.{_os.getpid()}.tmp")
        tmp.write_text(content, encoding="utf-8")
        _os.replace(tmp, path)
        return {"ok": True, "dosya": str(path)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


# ---------------------------------------------------------------------------
# Atomik set_status (task_board.json)
# ---------------------------------------------------------------------------

def _count_lines(rel_path: str) -> int:
    """Dosyadaki bos olmayan satir sayisini dondurur; yoksa 0."""
    path = ROOT / rel_path
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return sum(1 for line in fh if line.strip())
    except (FileNotFoundError, OSError):
        return 0


def _count_markdown(rel_dir: str) -> int:
    """Dizin altindaki .md dosyalarini sayar; yoksa 0."""
    path = ROOT / rel_dir
    try:
        if not path.exists():
            return 0
        return len(list(path.rglob("*.md")))
    except OSError:
        return 0


def read_project_state_title() -> str:
    """project_state.md icindeki ilk H1 basligini dondurur."""
    for line in read_project_state().split("\n"):
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return "bilinmiyor"


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
        "<b>🤖 Ankara B2B Intelligence Bot</b>\n\n"
        "Hoş geldiniz! Komutlar mavi görünür, dokunarak seçebilirsiniz.\n\n"
        "<b>Başlangıç:</b>\n"
        "/start — Botu başlat\n\n"
        "/help — Komut listesi\n\n"
        "/menu — Ana menü"
    )


def cmd_help(text: str) -> str:
    """/help komutu — sade ve seçilebilir komut listesi.

    Komutlar HTML code etiketi içine alınmaz; böylece Telegram onları
    mavi, dokunulabilir bot_command olarak render eder. Her komut
    altında bir boş satır bırakılır (karışıklık önlenir).
    """
    lines = [
        "<b>📖 Yardım — Komutlar</b>\n",
        "<b>GÖREV YÖNETİMİ</b>",
        "/gorev — Tüm görevleri duruma göre listeler",
        "",
        "/gorev-ekle — Panoya görev ekler (alias: /at)",
        "",
        "/gorev-durum — Görev durumunu günceller (alias: /set_task_status)",
        "",
        "<b>ONAY VE İNCELEME</b>",
        "/onaylar — Onay bekleyen teslimleri listeler",
        "",
        "/onayla — Görevi onaylar",
        "",
        "/reddet — Görevi reddeder",
        "",
        "/teslim — Görevi incelemeye gönderir",
        "",
        "<b>DURUM VE RAPOR</b>",
        "/durum — Proje durumu (alias: /status)",
        "",
        "/pano — Tetik ve onay özeti",
        "",
        "/rapor — KPI raporu",
        "",
        "/wiki — Wiki sayfaları",
        "",
        "/gunluk — Günlük özet",
        "",
        "/izleme — Kalite ve proje izleme",
        "",
        "/degisiklik — Değişiklik bildirimi",
        "",
        "<b>NÖBETÇİ</b>",
        "/nobet — Nöbetçi turu atar",
        "",
        "/nobet-ayar — Alarm süresini günceller (alias: /nobet_ayar)",
        "",
        "<b>Yardım</b>",
        "/menu — Ana menü",
        "",
        "/start — Başlangıç",
        "",
        "/help — Bu liste",
        "",
        "<b>Yetkili komutlar</b>",
        "/restart_etl — ETL pipeline'ini yeniden baslatir",
        "",
        "/set_status — project_state.md'ye not ekler",
        "",
        "/set_task_status — Task board durumunu gunceller",
        "",
        "/gorev-ekle — Panoya gorev ekler (alias: /at)",
        "",
        "/pano — Tetik ve onay ozeti",
        "",
        "/onaylar — Onay bekleyen teslimler",
        "",
        "/onayla — Gorevi onaylar",
        "",
        "/reddet — Gorevi reddeder",
        "",
        "/teslim — Gorevi incelemeye gonderir",
        "",
        "/nobet — Nobetci turu atar",
        "",
        "/nobet-ayar — Alarm suresini gunceller (alias: /nobet_ayar)",
        "",
    ]
    return "\n".join(lines)


def cmd_menu(text: str) -> str:
    """/menu komutu — etkileşimli ana menü."""
    lines = [
        "<b>📋 Ana Menü</b>\n",
        "1. /gorev — Görevler\n\n"
        "2. /gorev-ekle — Görev ekle\n\n"
        "3. /gorev-durum — Durum güncelle\n\n"
        "4. /onaylar — Onay bekleyenler\n\n"
        "5. /durum — Proje durumu\n\n"
        "6. /rapor — KPI raporu\n\n"
        "7. /wiki — Wiki sayfaları\n\n"
        "8. /nobet — Nöbetçi\n\n"
        "9. /help — Komut listesi",
    ]
    return "\n".join(lines)


def cmd_status(text: str) -> str:
    """/status komutu — proje durumu + aktif goresv."""
    active = read_active_tasks()
    done = read_done_count()
    tamlik = read_tamlik_metni()
    title = read_project_state_title()
    jsonl_count = _count_lines("data/ostim/firmalar_sayfa1.jsonl")
    md_count = _count_markdown("AI proje v1/V10")

    lines = ["<b>PROJE DURUMU</b>"]
    lines.append(f"<b>Proje:</b> {html_escape(title)}")
    lines.append(f"OSTIM kaydi: <b>{jsonl_count:,}</b> satir")
    lines.append(f"V10 wiki: <b>{md_count}</b> adet .md")
    lines.append(f"Toplam gorev: {len(read_task_board())}")
    lines.append(f"Aktif gorev: <b>{len(active)}</b>")
    lines.append(f"Tamamlandi: <b>{done}</b>")
    lines.append(f"Kimlik dosyasi tamligi: <b>{tamlik}</b>")

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
    """/rapor komutu — KPI raporu; bulunamazsa kalite raporu fallback."""
    kpi_path = ROOT / "data/kpi_raporu.md"
    quality_path = ROOT / "data/ostim/kalite_raporu.md"
    if kpi_path.exists():
        content = read_kpi_report()
    elif quality_path.exists():
        content = read_quality_report()
    else:
        content = "<b>KPI veya kalite raporu bulunamadi.</b>"
    truncated = content[:2000] if len(content) > 2000 else content
    return f"<pre>{html_escape(truncated)}</pre>"


def cmd_wiki(text: str) -> str:
    """/wiki komutu — V10 wiki sayfalarini canonical relative path + aciklama listeler."""
    v10_root = ROOT / "AI proje v1/V10"
    if not v10_root.exists():
        return "<b>V10 wiki dizini bulunamadi.</b>"
    known = {
        "00-Home.md": "Ana sayfa / yonlendirme",
        "TODO.md": "Plan ve hedefler",
        "project_state.md": "Proje durumu",
        "10_ankara_osb_sentez.md": "Ankara OSB sentez raporu",
        "01_kalite_skoru_ek_metrikleri.md": "Kalite metrikleri",
        "11_osint_motoru/OSINT_Scraper_Motoru.md": "OSINT motoru",
        "09_kurallar_ve_promptlar/09_telegram_bot_rehberi.md": "Telegram bot rehberi",
    }
    lines = ["<b>V10 WIKI SAYFALARI</b>"]
    for rel, desc in known.items():
        marker = "[x]" if (v10_root / rel).exists() else "[ ]"
        lines.append(f"{marker} <code>{html_escape(rel)}</code> — {html_escape(desc)}")
    extra = sorted(p.relative_to(v10_root).as_posix() for p in v10_root.rglob("*.md"))
    others = [r for r in extra if r not in known]
    if others:
        lines.append("\n<b>Diger sayfalar:</b>")
        for rel in others[:20]:
            lines.append(f"  <code>{html_escape(rel)}</code>")
    lines.append(f"\n<i>{time.strftime('%H:%M:%S')}</i>")
    return "\n".join(lines)


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
    tamlik = read_tamlik_metni()
    today = time.strftime("%Y-%m-%d")

    lines = [f"<b>GUNLUK OZET — {today}</b>\n"]
    lines.append(f"Toplam gorev: {len(board)}")
    lines.append(f"Aktif: {len(active)} | Tamamlandi: {done}")
    lines.append(f"Kimlik dosyasi tamligi: {tamlik}")
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
    """/izleme komutu — tamlik ve proje izleme."""
    tamlik = read_tamlik_metni()
    state = read_project_state()
    active = read_active_tasks()

    lines = ["<b>IZLEME PANELI</b>\n"]
    lines.append(f"Kimlik dosyasi tamligi: <b>{tamlik}</b>")
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
    """/set_status <mesaj> — project_state.md icinde ### Eklenen Notlar altina tarihli not ekler (yetkili)."""
    if not args:
        return "<b>Kullanim:</b> <code>/set_status &lt;mesaj&gt;</code>"
    msg = " ".join(args).strip()
    msg = msg[:500]
    if not msg:
        return "<b>Mesaj bos.</b>"
    state_path = ROOT / "AI proje v1" / "V10" / "project_state.md"
    if not state_path.exists():
        current = "\n# Proje Durumu\n\n## Genel Bakis\n\n### Eklenen Notlar\n"
    else:
        current = state_path.read_text(encoding="utf-8")
    date_str = time.strftime("%Y-%m-%d")
    note = f"- [{date_str}] {msg}"
    marker = "### Eklenen Notlar"
    if marker in current:
        idx = current.find(marker)
        line_end = current.find("\n", idx)
        insert_at = line_end + 1 if line_end >= 0 else len(current)
        new_content = current[:insert_at] + "\n" + note + current[insert_at:]
    else:
        new_content = current.rstrip() + "\n\n" + marker + "\n" + note + "\n"
    tmp_path = state_path.with_suffix(".md.tmp")
    tmp_path.write_text(new_content, encoding="utf-8")
    import os as _os
    _os.replace(str(tmp_path), str(state_path))
    return f"<b>Not eklendi</b>\n<code>{html_escape(note)}</code>\n<i>{time.strftime('%H:%M:%S')}</i>"


def cmd_set_task_status(text: str, args: list[str]) -> str:
    """/set_task_status <id> <durum> — task board durumunu gunceller (yetkili)."""
    if len(args) < 2:
        return (
            "<b>Kullanim:</b> <code>/set_task_status &lt;task_id&gt; &lt;durum&gt;</code>\n"
            "<i>Gecerli durumlar: plan, aktif, review, done, blocked</i>"
        )
    task_id = args[0]
    durum = args[1].lower()
    result = set_task_status(task_id, durum)
    if result["ok"]:
        t = result["task"]
        return (
            "<b>Gorev durumu guncellendi</b>\n"
            f"<code>{html_escape(t.get('task_id', '?'))}</code> → "
            f"<b>{html_escape(t.get('durum', ''))}</b>\n"
            f"<i>{html_escape(t.get('baslik', '')[:60])}</i>"
        )
    return f"<b>Guncelleme basarisiz:</b> {html_escape(result.get('error', 'bilinmiyor'))}"


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
    "set_task_status": (cmd_set_task_status, True, True),
    "gorev-durum": (cmd_set_task_status, True, True),
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
        return "Komut degil. Yardim icin /help yazin."

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
