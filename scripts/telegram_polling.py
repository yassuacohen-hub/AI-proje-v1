# -*- coding: utf-8 -*-
"""Telegram bot — canonical long-polling motoru.

Bu modul, python-telegram-bot kutuphanesine bagimlilik kurmadan
doğrudan Telegram Bot API getUpdates long-polling metodunu kullanir.

Komutlar:
    /start              - Botu baslat, hos gelesmesi
    /help               - Yardim metni
    /status             - Aktif gorevler + proje durumu
    /gorev              - Task_board.json'dan tum gorevleri listele
    /rapor              - KPI raporu (data/kpi_raporu.md)
    /wiki               - OSTİM kalite raporu (data/ostim/kalite_raporu.md)
    /restart_etl        - ETL pipeline yeniden baslatin
    /degisiklik         - CHANGELOG.md'yi goster
    /gunluk             - Gunluk ozet
    /izleme             - Kalite + proje izleme
    /set_status <id> <durum> - Task board'da gorev durumunu guncelle (yetkili)

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

POLL_TIMEOUT = 30
POLL_RETRY_DELAY = 5
POLL_LIMIT = 100

ALLOWED_UPDATES = ["message"]
COMMANDS_INFO = {
    "start": ("Botu baslatir", ""),
    "help": ("Bu yardim metnini gosterir", ""),
    "status": ("Proje durumu + aktif gorevler", ""),
    "gorev": ("Task board'daki tum goeveleri listeler", ""),
    "rapor": ("KPI raporunu gosterir", ""),
    "wiki": ("OSTIM kalite raporunu gosterir", ""),
    "restart_etl": ("ETL pipeline'i yeniden baslatir", ""),
    "degisiklik": ("CHANGELOG.md'yi gosterir", ""),
    "gunluk": ("Gunluk ozet raporu gonderir", ""),
    "izleme": ("Kalite + proje izleme", ""),
    "set_status": ("Gorev durumunu gunceller: /set_status <id> <durum>", ""),
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

def restart_etl(cmd: str | None = None) -> dict[str, Any]:
    """ETL pipeline'i yeniden baslatir.

    cmd parametresi verilmezse env'den ETL_RESTART_CMD okunur,
    yoksa varsayilan: python scripts/refresh_pipeline.py
    """
    if not cmd:
        cmd = os.environ.get("ETL_RESTART_CMD", f"{sys.executable} scripts/refresh_pipeline.py")

    try:
        proc = subprocess.Popen(
            cmd,
            shell=True,
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
        "Hosgeldiniz! Komutlari gormek icin <code>/help</code> yazin.\n\n"
        "Kullanilabilir komutlar:\n"
        "<code>/start</code> <code>/help</code> <code>/status</code> "
        "<code>/gorev</code> <code>/rapor</code> <code>/wiki</code> "
        "<code>/restart_etl</code> <code>/gunluk</code> <code>/izleme</code> "
        "<code>/set_status</code>"
    )


def cmd_help(text: str) -> str:
    """/help komutu."""
    lines = ["<b>KOMUTLAR</b>\n"]
    for cmd, (desc, _) in sorted(COMMANDS_INFO.items()):
        lines.append(f"<code>/{cmd}</code> — {html_escape(desc)}")
    lines.append("")
    lines.append("<i>Yetkili komut: /set_status &lt;task_id&gt; &lt;durum&gt;</i>")
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
    """/set_status komutu — gorev durumunu guncelle (yetkili)."""
    if len(args) < 2:
        return (
            "<b>Kullanim:</b> <code>/set_status &lt;task_id&gt; &lt;durum&gt;</code>\n"
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


# Komut dispatch table
COMMAND_HANDLERS: dict[str, Any] = {
    "start": (cmd_start, False),
    "help": (cmd_help, False),
    "status": (cmd_status, False),
    "gorev": (cmd_gorev, False),
    "rapor": (cmd_rapor, False),
    "wiki": (cmd_wiki, False),
    "restart_etl": (cmd_restart_etl, True),   # yetkili
    "degisiklik": (cmd_degisiklik, False),
    "gunluk": (cmd_gunluk, False),
    "izleme": (cmd_izleme, False),
    "set_status": (cmd_set_status, True),     # yetkili
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

    handler, needs_auth = handler_entry

    if needs_auth and not is_authorized(chat_id):
        return (
            "<b>Yetkisiz:</b> Bu komut yetkili kullanicilar icindir.\n"
            f"<i>{time.strftime('%H:%M:%S')}</i>"
        )

    try:
        if handler == cmd_set_status:
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
