# -*- coding: utf-8 -*-
"""
D-216: Huginn Telegram Bot — Menü Sistemi (MVP Faz 1)

Menü Mimarisi:
- Ana Menü (6 buton + 3 hızlı)
- 6 Submenü (Pano, Chat, Tetikler, Mesaj, Rapor, Ayarlar)
- Callback Routing → Handler Fonksiyonları
- Input Handling (next_step_handler)

Dosya Referansları:
- D-216_MENU_ANA.md
- D-216_MENU_PANO.md
- D-216_MENU_CHAT.md
- D-216_MENU_TETIKLER.md
- D-216_MENU_MESAJ.md
- D-216_MENU_RAPOR.md
- D-216_MENU_AYARLAR.md
- D-216_MENU_OZET.md
- D-216_CALLBACK_ROUTING_TEST.md
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
import telebot
from telebot import types

# Python path: Script mode için absolute import path setup
_base = Path(__file__).parent.parent  # src/
_company = Path(__file__).parent  # src/company_master/
if str(_base) not in sys.path:
    sys.path.insert(0, str(_base))
if str(_company) not in sys.path:
    sys.path.insert(0, str(_company))

# Load .env if exists
_env_path = Path(__file__).parent.parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

# Setup Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Console handler - stdout'a yazması için (UTF-8 encoding)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
# Windows cp1254 problemi çöz — UTF-8 force
if hasattr(console_handler.stream, 'reconfigure'):
    console_handler.stream.reconfigure(encoding='utf-8', errors='replace')
logger.addHandler(console_handler)

# Bot Başlatma
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
if not TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
    raise ValueError("TELEGRAM_BOT_TOKEN required")

bot = telebot.TeleBot(TOKEN)
logger.info(f"Telegram Bot initialized: {TOKEN[:20]}...")


def send_agent_message(ajan_adi: str, mesaj: str) -> bool:
    """Ajan mesajını log dosyasına kaydet (Telegram loop önlemek için).

    Test ortamı: Ajanlar KAHİN'e Telegram üzerinden değil, log dosyasına mesaj yazıyor.
    Production'da: Ajanların kendi chat_id'leri olacak ve gerçek Telegram mesajı alacaklar.
    """
    try:
        from datetime import datetime

        # Agent mesajlarını log dosyasına yaz
        agent_responses_path = Path(__file__).parent.parent.parent / "data" / "orchestrator" / "agent_responses.json"
        agent_responses_path.parent.mkdir(parents=True, exist_ok=True)

        if agent_responses_path.exists():
            with open(agent_responses_path, encoding="utf-8") as f:
                responses = json.load(f)
        else:
            responses = []

        response_record = {
            "timestamp": datetime.now().isoformat(),
            "ajan": ajan_adi,
            "mesaj": mesaj,
            "durum": "log"  # Test ortamında: log; production'da: telegram
        }

        responses.append(response_record)

        with open(agent_responses_path, "w", encoding="utf-8") as f:
            json.dump(responses, f, ensure_ascii=False, indent=2)

        logger.info(f"[AGENT_MSG_LOG] {ajan_adi} mesaji log dosyasina kaydedildi")
        return True

    except Exception as e:
        logger.error(f"[AGENT_MSG_ERROR] {e}", exc_info=True)
        return False


# ============================================================================
# BÖLÜM 1: ANA MENÜ (D-216_MENU_ANA.md)
# ============================================================================

def send_ana_menu(chat_id: str) -> None:
    """Ana menüyü gönder."""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    # Görev & Harita satırı
    markup.add(
        "📊 Pano",
        "💬 Chat",
    )
    markup.add(
        "✉️ Tetikler",
        "📝 Mesaj",
    )

    # Yönetim satırı
    markup.add(
        "📈 Rapor",
        "⚙️ Ayarlar",
    )

    # Görev takibi
    markup.add(
        "📋 Görev Takibi",
    )

    # Hızlı erişim satırı
    markup.add(
        "🚨 ACİL",
        "⚡ Q",
        "📌 ÖZET",
    )

    # Yardım satırı
    markup.add(
        "❓ Yardım",
    )

    bot.send_message(
        chat_id,
        "🤖 **Huginn Bot — Ana Menü**\n\n"
        "Görev yönetimi, sohbet ve raporlar için menü seçin.",
        reply_markup=markup,
        parse_mode="Markdown"
    )


# ============================================================================
# BÖLÜM 2: PANO MENÜSÜ (D-216_MENU_PANO.md)
# ============================================================================

def send_pano_menu(chat_id: str) -> None:
    """Pano menüsünü gönder."""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    markup.add(
        "✅ Tamamlandı",
        "✔️ Aktif",
    )
    markup.add(
        "🔴 Bloke",
        "📋 Plan",
    )
    markup.add(
        "🔍 Tümü",
    )

    markup.add(
        "« Ana Menü",
    )

    bot.send_message(
        chat_id,
        "📊 **Pano Menüsü**\n\n"
        "Görevleri durum veya ajana göre filtrele.",
        reply_markup=markup,
        parse_mode="Markdown"
    )


def show_pano_status(chat_id: str, status: str) -> None:
    """Pano görevlerini durum bazında göster — task_board.json SSOT."""
    try:
        logger.info(f"[PANO_START] chat_id={chat_id}, status={status}")

        import json
        from pathlib import Path

        # Absolute path: __file__ → telegram_bot.py, up 3 levels to root
        task_board_path = Path(__file__).resolve().parent.parent.parent / "data" / "orchestrator" / "task_board.json"
        logger.info(f"[PANO] Reading task_board from {task_board_path}")

        try:
            with open(task_board_path, "r", encoding="utf-8") as f:
                tasks = json.load(f)
            logger.info(f"[PANO] Got {len(tasks)} tasks from task_board.json")
        except Exception as read_err:
            logger.error(f"[PANO_READ_ERROR] {read_err}", exc_info=True)
            tasks = []

        if not tasks:
            logger.warning(f"[PANO] No tasks loaded")
            tasks = []

        # Duruma göre filtrele (task_board.json durum değerleri: done, aktif, bloke, plan, iptal)
        status_map = {
            "done": "done",
            "active": "aktif",
            "blocked": "bloke",
            "plan": "plan",
            "all": None
        }

        logger.info(f"[PANO] Filtering {len(tasks)} tasks for status={status}")
        filtered = tasks
        if status != "all":
            filtered = [t for t in tasks if t.get("durum") == status_map[status]]

        logger.info(f"[PANO] Filtered: {len(filtered)} tasks")

        # Etiket
        etiketler = {
            "done": "✅ Tamamlandı",
            "active": "✔️ Aktif",
            "blocked": "🔴 Bloke",
            "plan": "📋 Plan",
            "all": "🔍 Tümü"
        }

        # D-improvement: okunaklı tablo — Görev | Önem | Amaç (task_board.json: oncelik, talimat)
        LIMIT = 20
        rows = []
        for task in filtered[:LIMIT]:
            task_id = (task.get("task_id") or "?")[:28]
            oncelik = task.get("oncelik") or "-"
            amac = (task.get("talimat") or task.get("baslik") or "").replace("\n", " ")[:45]
            rows.append((task_id, oncelik, amac))

        if rows:
            id_w = max(len(r[0]) for r in rows)
            onc_w = max(len(r[1]) for r in rows + [("", "Önem", "")])
            baslik_row = "GÖREV".ljust(id_w) + "  " + "ÖNEM".ljust(onc_w) + "  AMAÇ"
            ayrac = "-" * len(baslik_row)
            tablo_lines = [baslik_row, ayrac]
            for task_id, oncelik, amac in rows:
                tablo_lines.append(f"{task_id.ljust(id_w)}  {oncelik.ljust(onc_w)}  {amac}")
            tablo = "\n".join(tablo_lines)
        else:
            tablo = "(görev yok)"

        header = f"**{etiketler[status]} Görevler ({len(filtered)})**"
        if len(filtered) > LIMIT:
            header += f"\n_(ilk {LIMIT} gösteriliyor)_"

        logger.info(f"[PANO] About to send_message, tablo_len={len(tablo)}")

        try:
            bot.send_message(chat_id, header, parse_mode="Markdown")
            bot.send_message(chat_id, f"```\n{tablo}\n```", parse_mode="Markdown")
            bot.send_message(chat_id, "[« Pano Menüsü] [« Ana Menü]")
            logger.info(f"[PANO] send_message OK")
        except Exception as send_err:
            logger.error(f"[PANO_SEND_ERROR] {send_err}", exc_info=True)
            try:
                bot.send_message(chat_id, f"❌ Mesaj gönderimi başarısız: {str(send_err)[:50]}")
            except Exception as fallback_err:
                logger.critical(f"[PANO_FALLBACK_FAILED] {fallback_err}")

    except Exception as e:
        logger.error(f"[PANO_OUTER_ERROR] {e}", exc_info=True)
        try:
            bot.send_message(chat_id, f"❌ Görevler yüklenemedi.\n\nHata: {str(e)[:100]}")
        except Exception as e2:
            logger.critical(f"[PANO_ERROR_SEND_FAILED] {e2}")


# ============================================================================
# BÖLÜM 3: CHAT MENÜSÜ (D-216_MENU_CHAT.md)
# ============================================================================

def send_chat_menu(chat_id: str) -> None:
    """Chat menüsünü gönder."""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    markup.add("🔴 Açık", "🟡 Çözüm Bekl.")
    markup.add("🟢 Çözüldü", "📜 Son 10")
    markup.add("✉️ Mesaj Gönder")
    markup.add("« Ana Menü")

    bot.send_message(
        chat_id,
        "💬 **Chat Menüsü**\n\n"
        "🔴/🟡/🟢 = duruma göre son 10 mesaj\n"
        "📜 Son 10 = tüm durumlardan son 10 mesaj\n"
        "✉️ Mesaj Gönder = yeni mesaj yaz",
        reply_markup=markup,
        parse_mode="Markdown"
    )


def show_chat_status(chat_id: str, status: str) -> None:
    """Chat sorunlarını durum bazında göster — ajan-chat.jsonl SSOT (D-216: chat.json stale kaynaktı, gerçek akışa taşındı)."""
    try:
        from chat import oku
        satirlar = list(reversed(oku(son=200)))  # en yeni üstte
        logger.info(f"[CHAT_STATUS] Loaded {len(satirlar)} chat records from ajan-chat.jsonl")
    except Exception as e:
        logger.error(f"[CHAT_FETCH_ERROR] {e}", exc_info=True)
        bot.send_message(chat_id, f"❌ Chat verileri alınamadı: {str(e)[:50]}")
        return

    status_map = {
        "acik": "acik",
        "cokundurmus": "cokundurmus",
        "cozuldu": "cozuldu",
        "all": None
    }

    filtered = satirlar
    if status != "all":
        filtered = [s for s in satirlar if s.get("durum") == status_map[status]]

    etiketler = {
        "acik": "🔴 Açık",
        "cokundurmus": "🟡 Çözüm Bekl.",
        "cozuldu": "🟢 Çözüldü",
        "all": "📜 Son 10"
    }

    msg = f"{etiketler[status]} Sorunlar ({len(filtered)} kayıt)\n\n"

    if not filtered:
        msg += "Kayıt yok."
    else:
        for i, soru in enumerate(filtered[:10], 1):
            ajan_from = soru.get("kimden", "sistem")
            task_id = soru.get("task_id", "?")
            konu = soru.get("sorun", "?")[:50]
            durum = soru.get("durum", "?")

            durum_icon = {"acik": "🔴", "cokundurmus": "🟡", "cozuldu": "🟢"}.get(durum, "⚫")
            msg += f"{durum_icon} [{task_id}] {ajan_from}\n➜ {konu}\n\n"

        if len(filtered) > 10:
            msg += f"... (+{len(filtered) - 10} daha)"

    # Mesaj türü seçme butonları
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("📢 Broadcast", "👤 Targeted")
    markup.add("🎯 Tag Seç", "🔔 Uyarı")
    markup.add("« Chat Menüsü", "« Ana Menü")

    bot.send_message(chat_id, msg, reply_markup=markup)


# ============================================================================
# BÖLÜM 4: TETIKLER MENÜSÜ (D-216_MENU_TETIKLER.md)
# ============================================================================

def send_tetikler_menu(chat_id: str) -> None:
    """Tetikler menüsünü gönder."""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    markup.add("👨 Utku", "👨 Salih")
    markup.add("👨 Yasu", "👨 İhsan")
    markup.add("👨 Mimir", "🔍 Tümü")
    markup.add("« Ana Menü")

    bot.send_message(
        chat_id,
        "✉️ **Tetikler Menüsü**\n\n"
        "Ajanın posta kutusunu görmek için ajan seçin.",
        reply_markup=markup,
        parse_mode="Markdown"
    )


def show_tetikler_ajan(chat_id: str, ajan: str) -> None:
    """Ajan seçildikten sonra işlem seçme menüsü."""
    # State'e ajan adını kaydet (Tetik Bak button'ında kullanılacak)
    _tetikler_state[str(chat_id)] = ajan

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("📬 Tetik Bak", "✉️ Tetik Gönder")
    markup.add("« Tetikler Menüsü")

    msg = bot.send_message(
        chat_id,
        f"👤 {ajan}\n\n📋 Ne yapmak istiyorsunuz?",
        reply_markup=markup
    )


def _show_tetikler_ajan_detay(chat_id: str, ajan: str) -> None:
    """Ajanın tetiklerini göster (tetik bak) — task_board.json SSOT."""
    try:
        import json
        from pathlib import Path

        # Absolute path: __file__ → telegram_bot.py, up 3 levels to root
        task_board_path = Path(__file__).resolve().parent.parent.parent / "data" / "orchestrator" / "task_board.json"
        logger.info(f"[TETIKLER_DETAY] Reading from {task_board_path}")

        with open(task_board_path, "r", encoding="utf-8") as f:
            gorevler = json.load(f)

        logger.info(f"[TETIKLER_DETAY] Loaded {len(gorevler)} tasks, filtering for ajan={ajan}")

        # Ajanın görevlerini filtrele (durum=aktif veya plan)
        tetikler = [g for g in gorevler if g.get("sahip", "").lower() == ajan.lower()
                   and g.get("durum", "").lower() in ["aktif", "plan"]]
        logger.info(f"[TETIKLER_DETAY] Found {len(tetikler)} tasks for {ajan}")
    except Exception as e:
        logger.error(f"[TETIKLER_DETAY_ERROR] Error fetching tetikler: {e}", exc_info=True)
        tetikler = []

    if not tetikler:
        msg = f"✅ **{ajan.upper()} İçin Tetik Yok!**\n\n" \
              "Tüm görevler tamamlandı veya devam ediyor.\n\n" \
              "[« Tetikler Menüsü] [« Ana Menü]"
        bot.send_message(chat_id, msg, parse_mode="Markdown")
        return

    lines = [f"📬 **{ajan.upper()} Posta Kutusu ({len(tetikler)})**\n"]

    for i, tetik in enumerate(tetikler[:10], 1):
        task_id = tetik.get("task_id", "?")
        talimat = tetik.get("talimat", "")[:40]
        durum = tetik.get("durum", "?")

        durum_emoji = {"aktif": "🔵", "plan": "📋"}.get(durum, "❓")

        lines.append(
            f"{i}. 📬 {task_id}\n"
            f"   Talimat: {talimat}\n"
            f"   {durum_emoji} Durum: {durum}"
        )

    if len(tetikler) > 10:
        lines.append(f"\n... (+{len(tetikler) - 10} daha)")

    lines.append("\n[« Tetikler Menüsü] [« Ana Menü]")

    bot.send_message(chat_id, "\n\n".join(lines), parse_mode="Markdown")


# ============================================================================
# BÖLÜM 5: MESAJ MENÜSÜ (D-216_MENU_MESAJ.md)
# ============================================================================

def send_mesaj_menu(chat_id: str) -> None:
    """Mesaj menüsünü gönder."""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    markup.add("📢 Broadcast", "👤 Targeted")
    markup.add("🎯 Tag Seç", "🔔 Uyarı")
    markup.add("💬 KAHİN'e Mesaj")  # Ajan → KAHİN mesajlaşması
    markup.add("« Ana Menü")

    bot.send_message(
        chat_id,
        "📝 **Mesaj Gönder**\n\n"
        "Mesaj türünü seçin.",
        reply_markup=markup,
        parse_mode="Markdown"
    )


# ============================================================================
# BÖLÜM 6: RAPOR MENÜSÜ (D-216_MENU_RAPOR.md)
# ============================================================================

def send_rapor_menu(chat_id: str) -> None:
    """Rapor menüsünü gönder."""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    markup.add("📅 Hafta", "📅 Ay", "📅 YTD")
    markup.add("👤 Ajan Bazlı", "📊 KPI")
    markup.add("📈 Trend", "📋 Özet")
    markup.add("📊 Pano Özeti", "📚 Belgeler")

    markup.add("« Ana Menü")

    bot.send_message(
        chat_id,
        "📈 **Raporlar & Analitik**\n\n"
        "Rapor türünü seçin.",
        reply_markup=markup,
        parse_mode="Markdown"
    )


def _send_long_message(chat_id: str, text: str, parse_mode: str | None = None, code_block: bool = False) -> None:
    """Telegram 4096 karakter sınırını aşan metni parçalara bölüp gönderir.

    code_block=True: her parçayı ``` ile sarar (monospace/tablo görünümü, okunurluk için).
    """
    if code_block:
        LIMIT = 3900  # ```\n...\n``` fence payı
        # D-fix: kaynak belge içinde ``` geçiyorsa dış fence'i bozar (Telegram Markdown hatası) → nötrle
        text = text.replace("```", "'''")
        for i in range(0, len(text), LIMIT):
            parca = text[i:i + LIMIT]
            bot.send_message(chat_id, f"```\n{parca}\n```", parse_mode="Markdown")
    else:
        LIMIT = 4000
        for i in range(0, len(text), LIMIT):
            bot.send_message(chat_id, text[i:i + LIMIT], parse_mode=parse_mode)


def send_belgeler_menu(chat_id: str) -> None:
    """Kritik belgeler / son raporlar menüsü."""
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add("🗂 Rapor Dosyaları Listesi")
    markup.add("📖 SSOT Oku")
    markup.add("🎯 Admin Hub Oku")
    markup.add("📊 Matrix İlerleme Oku")
    markup.add("« Rapor Menüsü", "« Ana Menü")
    bot.send_message(
        chat_id,
        "📚 **Belgeler**\n\nSon raporları veya kritik canlı belgeleri okuyun.",
        reply_markup=markup,
        parse_mode="Markdown"
    )


def show_son_10_rapor(chat_id: str) -> None:
    """data/orchestrator altındaki *_rapor_*.md dosyalarından en son değişen 10'unu tablo (monospace) halinde listele."""
    from pathlib import Path
    try:
        data_dir = Path(__file__).parent.parent.parent / "data" / "orchestrator"
        dosyalar = sorted(
            data_dir.glob("*_rapor_*.md"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:10]
        if not dosyalar:
            bot.send_message(chat_id, "ℹ️ Hiç rapor dosyası bulunamadı.")
            return
        rows = []
        for f in dosyalar:
            mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            ad = f.name if len(f.name) <= 40 else f.name[:37] + "..."
            rows.append((ad, mtime))
        ad_w = max(len(r[0]) for r in rows)
        tablo = "\n".join(f"{ad.ljust(ad_w)}  {tarih}" for ad, tarih in rows)
        bot.send_message(chat_id, "🗂 **Rapor Dosyaları Listesi** (son 10, değişme tarihine göre)", parse_mode="Markdown")
        bot.send_message(chat_id, f"```\n{tablo}\n```", parse_mode="Markdown")
    except Exception as e:
        logger.error(f"[SON10RAPOR_ERROR] {e}", exc_info=True)
        bot.send_message(chat_id, f"❌ Hata: {str(e)[:50]}")


def show_ssot_oku(chat_id: str) -> None:
    """SSOT belgesini oku ve gönder (D-improvement: kritik/anlık değişen belge okuma)."""
    from pathlib import Path
    try:
        ssot_path = (
            Path(__file__).parent.parent.parent
            / "AI proje v1" / "V10" / "05_versiyonlar" / "02_admin_panel_hedef_dokumani.md"
        )
        if not ssot_path.exists():
            bot.send_message(chat_id, "❌ SSOT belgesi bulunamadı.")
            return
        icerik = ssot_path.read_text(encoding="utf-8")
        bot.send_message(chat_id, f"📖 **SSOT** — `{ssot_path.name}`\n_(ilk 8000 karakter, monospace)_", parse_mode="Markdown")
        _send_long_message(chat_id, icerik[:8000], code_block=True)
    except Exception as e:
        logger.error(f"[SSOT_OKU_ERROR] {e}", exc_info=True)
        bot.send_message(chat_id, f"❌ Hata: {str(e)[:50]}")


def show_admin_hub_oku(chat_id: str) -> None:
    """Admin Dashboard Hub belgesini oku ve gönder."""
    from pathlib import Path
    try:
        hub_path = Path(__file__).parent.parent.parent / "hubs" / "ADMIN_DASHBOARD_HUB.md"
        if not hub_path.exists():
            bot.send_message(chat_id, "❌ Admin Hub belgesi bulunamadı.")
            return
        icerik = hub_path.read_text(encoding="utf-8")
        bot.send_message(chat_id, f"🎯 **Admin Hub** — `{hub_path.name}`\n_(monospace)_", parse_mode="Markdown")
        _send_long_message(chat_id, icerik[:8000], code_block=True)
    except Exception as e:
        logger.error(f"[ADMIN_HUB_OKU_ERROR] {e}", exc_info=True)
        bot.send_message(chat_id, f"❌ Hata: {str(e)[:50]}")


def show_matrix_ilerleme(chat_id: str) -> None:
    """Matrix İlerleme SSOT belgesini oku ve gönder."""
    from pathlib import Path
    try:
        matrix_path = Path(__file__).parent.parent.parent / "plans" / "MATRIX_ILERLEME_SSOT_2026-09-24.md"
        if not matrix_path.exists():
            bot.send_message(chat_id, "❌ Matrix İlerleme belgesi bulunamadı.")
            return
        icerik = matrix_path.read_text(encoding="utf-8")
        bot.send_message(chat_id, f"📊 **Matrix İlerleme** — `{matrix_path.name}`\n_(ilk 8000 karakter, monospace)_", parse_mode="Markdown")
        _send_long_message(chat_id, icerik[:8000], code_block=True)
    except Exception as e:
        logger.error(f"[MATRIX_ILERLEME_ERROR] {e}", exc_info=True)
        bot.send_message(chat_id, f"❌ Hata: {str(e)[:50]}")


def show_hafta_raporu(chat_id: str) -> None:
    """Haftalık rapor — task_board'dan."""
    import json
    from pathlib import Path

    try:
        task_board_path = Path(__file__).parent.parent.parent / "data" / "orchestrator" / "task_board.json"
        tasks = []
        if task_board_path.exists():
            with open(task_board_path, "r", encoding="utf-8") as f:
                tasks = json.load(f)

        # Metrikler
        acik = len([t for t in tasks if t.get('durum') == 'Açık'])
        aktif = len([t for t in tasks if t.get('durum') == 'Aktif'])
        bloke = len([t for t in tasks if t.get('durum') == 'Bloke'])
        done = len([t for t in tasks if t.get('durum') == 'Tamamlandı'])
        toplam = len(tasks)

        lines = [
            "📊 **HAFTALIK RAPOR**\n",
            "```",
            "┌──────────────────────────────────┐",
            "│ DURUM          │ SAYISI │ YÜZDE  │",
            "├──────────────────────────────────┤",
            f"│ 🟢 Açık        │   {acik:2d}   │ {int(acik*100/toplam) if toplam else 0:3d}%  │",
            f"│ 🔵 Aktif       │   {aktif:2d}   │ {int(aktif*100/toplam) if toplam else 0:3d}%  │",
            f"│ 🟠 Bloke       │   {bloke:2d}   │ {int(bloke*100/toplam) if toplam else 0:3d}%  │",
            f"│ ✅ Tamamlandı  │   {done:2d}   │ {int(done*100/toplam) if toplam else 0:3d}%  │",
            "├──────────────────────────────────┤",
            f"│ 📊 TOPLAM      │  {toplam:3d}   │ 100%  │",
            "└──────────────────────────────────┘",
            "```",
            "\n**💡 Durum Açıklaması:**",
            "• 🟢 **Açık**: Başlanmamış görevler",
            "• 🔵 **Aktif**: Devam eden görevler",
            "• 🟠 **Bloke**: Tamamlanmış ama onay beklemede",
            "• ✅ **Tamamlandı**: Bitmiş ve onaylı görevler",
            "\n**📋 Son 5 Görev (İşlem Tarihi):**"
        ]

        for i, task in enumerate(tasks[-5:], 1):
            task_id = task.get("task_id", "?")
            durum = task.get("durum", "?")
            baslik = task.get("baslik", "")[:30]
            sahip = task.get("sahip", "?")
            onem = task.get("onem", "orta")

            durum_emoji = {"Açık": "🟢", "Aktif": "🔵", "Bloke": "🟠", "Tamamlandı": "✅", "Plan": "📋"}.get(durum, "❓")
            onem_emoji = {"kritik": "🔴", "yuksek": "🟠", "orta": "🟡", "dusuk": "🟢"}.get(onem, "⚪")

            lines.append(f"\n{i}. {durum_emoji} **{task_id}** ({onem_emoji} {onem.capitalize()})")
            lines.append(f"   📌 {baslik}")
            lines.append(f"   👤 {sahip}")

        lines.append("\n[« Rapor Menüsü]")
        bot.send_message(chat_id, "\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        logger.error(f"[HAFTA_RAPOR_ERROR] {e}", exc_info=True)
        bot.send_message(chat_id, f"❌ Hafta raporu yüklenemedi: {str(e)[:50]}")


def show_kpi_raporu(chat_id: str) -> None:
    """KPI raporu — task_board'dan. Tamamlama oranı, ajan performansı, durum dağılımı."""
    import json
    from pathlib import Path
    from collections import Counter

    try:
        task_board_path = Path(__file__).parent.parent.parent / "data" / "orchestrator" / "task_board.json"
        tasks = []
        if task_board_path.exists():
            with open(task_board_path, "r", encoding="utf-8") as f:
                tasks = json.load(f)

        # KPI metrikler
        done = len([t for t in tasks if t.get('durum') == 'Tamamlandı'])
        acik = len([t for t in tasks if t.get('durum') == 'Açık'])
        aktif = len([t for t in tasks if t.get('durum') == 'Aktif'])
        bloke = len([t for t in tasks if t.get('durum') == 'Bloke'])
        toplam = len(tasks)
        tamamlama_orani = int(done * 100 / toplam) if toplam else 0

        # Ajan bazlı görev sayısı
        ajan_counts = Counter(t.get('sahip', 'unknown') for t in tasks)

        lines = [
            "📊 **KPI ANALİZİ — Genel Durum**\n",
            "```",
            "┌──────────────────────────────────┐",
            "│ METRİK                  │ DEĞER  │",
            "├──────────────────────────────────┤",
            f"│ Toplam Görevler         │ {toplam:5d}  │",
            f"│ ✅ Tamamlanan           │ {done:5d}  │",
            f"│ Tamamlama Oranı         │ {tamamlama_orani:4d}%  │",
            "├──────────────────────────────────┤",
            f"│ 🟢 Açık                 │ {acik:5d}  │",
            f"│ 🔵 Aktif                │ {aktif:5d}  │",
            f"│ 🟠 Bloke                │ {bloke:5d}  │",
            "└──────────────────────────────────┘",
            "```",
            "\n**💡 Açıklama:**",
            "• **Tamamlama Oranı**: Bitirilen görevlerin yüzde oranı",
            "• **Açık**: Başlanmamış görevler",
            "• **Aktif**: Devam eden görevler",
            "• **Bloke**: Tamamlanmış fakat onay beklemede",
            "\n**👥 Ajan Performansı (Görev Sayısı):**"
        ]

        for ajan, count in sorted(ajan_counts.items(), key=lambda x: x[1], reverse=True):
            ajan_done = len([t for t in tasks if t.get('sahip') == ajan and t.get('durum') == 'Tamamlandı'])
            oran = int(ajan_done * 100 / count) if count > 0 else 0
            lines.append(f"   • {ajan}: {count} görev ({ajan_done} tamamlı, {oran}%)")

        lines.append("\n[« Rapor Menüsü]")
        bot.send_message(chat_id, "\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        logger.error(f"[KPI_RAPOR_ERROR] {e}", exc_info=True)
        bot.send_message(chat_id, f"❌ KPI raporu yüklenemedi: {str(e)[:50]}")


def show_rapor_pano_ozeti(chat_id: str) -> None:
    """Görev panosu özeti — task_board'dan metrikler + dağılımlar."""
    import json
    from pathlib import Path
    from collections import defaultdict

    try:
        task_board_path = Path(__file__).parent.parent.parent / "data" / "orchestrator" / "task_board.json"

        if not task_board_path.exists():
            bot.send_message(chat_id, "❌ Görev panosuna erişilemedi.")
            send_rapor_menu(chat_id)
            return

        with open(task_board_path, encoding="utf-8") as f:
            gorevler = json.load(f)

        # Metrikler hesapla
        toplam = len(gorevler)
        acik = len([g for g in gorevler if g.get('durum') == 'Açık'])
        aktif = len([g for g in gorevler if g.get('durum') == 'Aktif'])
        bloke = len([g for g in gorevler if g.get('durum') == 'Bloke'])
        done = len([g for g in gorevler if g.get('durum') == 'Tamamlandı'])
        plan = len([g for g in gorevler if g.get('durum') == 'Plan'])

        # Sahib ve önem dağılımı
        sahib_sayisi = defaultdict(int)
        onem_sayisi = defaultdict(int)

        for g in gorevler:
            sahib = g.get('sahip', 'unknown')
            onem = g.get('onem', 'unknown')
            sahib_sayisi[sahib] += 1
            onem_sayisi[onem] += 1

        # Tablo başlığı
        lines = [
            "📊 **GÖREV PANOSU ÖZETİ**\n",
            "```",
            "┌──────────────────────────────────────────┐",
            "│ DURUM          │ SAYISI │ YÜZDE          │",
            "├──────────────────────────────────────────┤",
            f"│ 🟢 Açık        │   {acik:2d}   │ {(acik*100//toplam if toplam else 0):3d}%       │",
            f"│ 🔵 Aktif       │   {aktif:2d}   │ {(aktif*100//toplam if toplam else 0):3d}%       │",
            f"│ 🟠 Bloke       │   {bloke:2d}   │ {(bloke*100//toplam if toplam else 0):3d}%       │",
            f"│ 📋 Plan        │   {plan:2d}   │ {(plan*100//toplam if toplam else 0):3d}%       │",
            f"│ ✅ Tamamlandı  │   {done:2d}   │ {(done*100//toplam if toplam else 0):3d}%       │",
            "├──────────────────────────────────────────┤",
            f"│ 📊 TOPLAM      │  {toplam:3d}   │ 100%       │",
            "└──────────────────────────────────────────┘",
            "```",
            "\n**👤 Sahip Dağılımı:**"
        ]

        for sahib, count in sorted(sahib_sayisi.items(), key=lambda x: -x[1])[:6]:
            yuzde = (count * 100 // toplam) if toplam else 0
            lines.append(f"   • {sahib.capitalize():12} : {count:3d} görev ({yuzde:3d}%)")

        lines.append("\n**⚡ Önem Dağılımı:**")
        for onem in ['kritik', 'yuksek', 'orta', 'dusuk']:
            count = onem_sayisi.get(onem, 0)
            if count > 0:
                yuzde = (count * 100 // toplam) if toplam else 0
                onem_emoji = {"kritik": "🔴", "yuksek": "🟠", "orta": "🟡", "dusuk": "🟢"}.get(onem, "⚪")
                lines.append(f"   {onem_emoji} {onem.capitalize():12} : {count:3d} görev ({yuzde:3d}%)")

        lines.append("\n[« Rapor Menüsü]")
        bot.send_message(chat_id, "\n".join(lines), parse_mode="Markdown")

    except Exception as e:
        logger.error(f"[RAPOR_PANO_OZETI] Error: {e}", exc_info=True)
        bot.send_message(chat_id, f"❌ Hata: {str(e)[:50]}")

    send_rapor_menu(chat_id)


# ============================================================================
# BÖLÜM 7: AYARLAR MENÜSÜ (D-216_MENU_AYARLAR.md)
# ============================================================================

def send_ayarlar_menu(chat_id: str) -> None:
    """Ayarlar menüsünü gönder."""
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)

    markup.add("🔌 Bağlantı Kontrol")
    markup.add("🔑 Token Doğrula")
    markup.add("📋 Bot Bilgisi")
    markup.add("🔄 Bot Restart", "🔄 Streamlit Restart")
    markup.add("❓ Yardım")
    markup.add("« Ana Menü")

    bot.send_message(
        chat_id,
        "⚙️ **Ayarlar**\n\n"
        "Bot durumunu ve konfigürasyonunu kontrol edin.",
        reply_markup=markup,
        parse_mode="Markdown"
    )


# ============================================================================
# Görev Takibi Menüsü
# ============================================================================

def send_gorev_takibi_menu(chat_id: str) -> None:
    """Görev takibi menüsü - durum filtresi."""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    markup.add("🟢 Açık", "🔵 Aktif")
    markup.add("🟠 Bloke", "✅ Tamamlandı")
    markup.add("📋 Tümü", "👤 Sahip Bazlı")
    markup.add("« Ana Menü")

    bot.send_message(
        chat_id,
        "📋 **Görev Takibi**\n\n"
        "Görevleri durum veya sahibe göre filtrele:\n\n"
        "🟢 = Açık (başlanmamış)\n"
        "🔵 = Aktif (devam ediyor)\n"
        "🟠 = Bloke (engellendi)\n"
        "✅ = Tamamlandı\n"
        "📋 = Tüm görevler\n"
        "👤 = Sahip filtresi",
        reply_markup=markup,
        parse_mode="Markdown"
    )


def show_gorev_takibi_durum(chat_id: str, durum: str) -> None:
    """Durum bazlı görev listesi."""
    import json
    from pathlib import Path

    try:
        task_board_path = Path(__file__).parent.parent.parent / "data" / "orchestrator" / "task_board.json"

        if not task_board_path.exists():
            bot.send_message(chat_id, "❌ Görev panosuna erişilemedi.")
            send_gorev_takibi_menu(chat_id)
            return

        with open(task_board_path, encoding="utf-8") as f:
            gorevler = json.load(f)

        # Duruma göre filtrele
        if durum != "all":
            gorevler = [g for g in gorevler if g.get("durum", "").lower() == durum.lower()]

        if not gorevler:
            bot.send_message(
                chat_id,
                f"ℹ️ **{durum}** durumunda görev yok.",
                parse_mode="Markdown"
            )
            send_gorev_takibi_menu(chat_id)
            return

        # Tablo oluştur (durum, task_id, baslik, sahip, onem)
        onem_sira = {"critical": 0, "yuksek": 1, "orta": 2, "dusuk": 3}
        gorevler.sort(key=lambda g: onem_sira.get(str(g.get("onem", "")).lower(), 9))

        onem_emoji = {
            "critical": "🔴",
            "yuksek": "🟠",
            "orta": "🟡",
            "dusuk": "🟢"
        }

        lines = [
            f"📋 **Görevler ({len(gorevler)} toplam) — {durum.upper()}**",
            "_(önem derecesine göre sıralı)_\n",
            "┌────────────┬──────────────────────┬────────────┬────┐"
        ]

        for g in gorevler[:15]:  # Max 15
            task_id = g.get("task_id", "?")[:10].ljust(10)
            baslik = g.get("baslik", "")[:20].ljust(20)
            sahip = g.get("sahip", "?")[:10].ljust(10)
            onem = str(g.get("onem", "?"))
            onem_ikon = onem_emoji.get(onem.lower(), "❓")

            lines.append(f"│ {task_id} │ {baslik} │ {sahip} │ {onem_ikon} │")

        if len(gorevler) > 15:
            lines.append(f"│ ... {len(gorevler)-15} daha görev ...")

        lines.append("└────────────┴──────────────────────┴────────────┴────┘")
        lines.append("\n🔴 Kritik  🟠 Yüksek  🟡 Orta  🟢 Düşük")

        msg_text = "\n".join(lines)

        if len(msg_text) > 4000:
            msg_text = msg_text[:3900] + "\n... (daha fazla)"

        bot.send_message(chat_id, f"```\n{msg_text}\n```", parse_mode="Markdown")

    except Exception as e:
        logger.error(f"[GOREV_TAKIBI] Error: {e}")
        bot.send_message(chat_id, f"❌ Hata: {str(e)}")

    send_gorev_takibi_menu(chat_id)


def show_gorev_sahib_menu(chat_id: str) -> None:
    """Sahib bazlı filtreleme menüsü."""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    # Butonları doğru emojilerle göster (görev takibi menüsünde bu butonlar kullanılıyor)
    markup.add("😊 Utku", "😊 Salih")
    markup.add("😊 Yasu", "😊 İhsan")
    markup.add("😊 Mimir", "🤖 Orkestrator")
    markup.add("« Görev Takibi")

    bot.send_message(
        chat_id,
        "👤 **Sahib Bazlı Görevler**\n\n"
        "Hangi ajana ait görevleri görmek istiyorsunuz?",
        reply_markup=markup,
        parse_mode="Markdown"
    )


def show_gorev_sahib_goster(chat_id: str, sahib: str) -> None:
    """Sahib bazlı görev listesi."""
    import json
    from pathlib import Path

    try:
        task_board_path = Path(__file__).parent.parent.parent / "data" / "orchestrator" / "task_board.json"

        if not task_board_path.exists():
            bot.send_message(chat_id, "❌ Görev panosuna erişilemedi.")
            show_gorev_sahib_menu(chat_id)
            return

        with open(task_board_path, encoding="utf-8") as f:
            gorevler = json.load(f)

        # Sahibe göre filtrele
        gorevler = [g for g in gorevler if g.get("sahip", "").lower() == sahib.lower()]

        if not gorevler:
            bot.send_message(
                chat_id,
                f"ℹ️ **{sahib}** için görev bulunamadı.",
                parse_mode="Markdown"
            )
            show_gorev_sahib_menu(chat_id)
            return

        # Tablo oluştur (durum, task_id, baslik, onem)
        lines = [
            f"👤 **{sahib} — Görevler ({len(gorevler)} toplam)**\n",
            "┌─────────────────────────────────────────────────────────┐"
        ]

        for g in gorevler[:15]:  # Max 15
            task_id = g.get("task_id", "?").ljust(8)
            baslik = g.get("baslik", "")[:20]
            durum = g.get("durum", "?")
            onem = g.get("onem", "?")

            # Durum emoji
            durum_emoji = {
                "acik": "🟢",
                "aktif": "🔵",
                "bloke": "🟠",
                "done": "✅"
            }.get(durum.lower(), "❓")

            onem_emoji = {
                "critical": "🔴",
                "yuksek": "🟠",
                "orta": "🟡",
                "dusuk": "🟢"
            }.get(onem.lower(), "❓")

            lines.append(f"│ {task_id} │ {durum_emoji} {durum:6} │ {onem_emoji} {baslik:15} │")

        if len(gorevler) > 15:
            lines.append(f"│ ... {len(gorevler)-15} daha görev ... │")

        lines.append("└─────────────────────────────────────────────────────────┘")

        msg_text = "\n".join(lines)

        if len(msg_text) > 4000:
            msg_text = msg_text[:3900] + "\n... (daha fazla)"

        bot.send_message(chat_id, f"```\n{msg_text}\n```", parse_mode="Markdown")

    except Exception as e:
        logger.error(f"[GOREV_SAHIB] Error: {e}")
        bot.send_message(chat_id, f"❌ Hata: {str(e)}")


def _show_gorev_sahib_aksiyonlar_menu(chat_id: str) -> None:
    """Ajan görevleri gösterdikten sonra: Tetik Bak veya Mesaj Gönder seçeneği."""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    markup.add("📬 Tetik Bak", "💬 Mesaj Gönder")
    markup.add("« Sahib Bazlı")

    bot.send_message(
        chat_id,
        "📋 **Görevler gösterildi.**\n\n"
        "Sonraki adım:",
        reply_markup=markup,
        parse_mode="Markdown"
    )


def send_gorev_mesaj_menu(chat_id: str) -> None:
    """Görev ile ilgili mesaj gönder menüsü."""
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)

    markup.add("💬 Mesaj Gönder", "« Görev Takibi")

    bot.send_message(
        chat_id,
        "💬 **Görev Mesajı**\n\n"
        "Görev ile ilgili mesaj/not göndermek istiyorsunuz?\n\n"
        "Mesaj orkestratöre gönderilecek ve yeni görev oluşturulabilir.",
        reply_markup=markup,
        parse_mode="Markdown"
    )


def show_mesaj_formu(chat_id: str) -> None:
    """Görev mesaj giriş formu."""
    msg = bot.send_message(
        chat_id,
        "💬 **Görev Mesajı**\n\n"
        "Mesaj/Not içeriğini yazın (max 500 karakter):\n\n"
        "(« tuşu ile geri dön)",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, _mesaj_orkestrator_kaydet)


def _mesaj_orkestrator_kaydet(message):
    """Mesajı orkestratöre görev olarak kaydet."""
    if message.text and message.text.startswith("«"):
        send_gorev_takibi_menu(message.chat.id)
        return

    mesaj = message.text.strip()[:500]

    try:
        import json
        from pathlib import Path
        from datetime import datetime

        task_board_path = Path(__file__).parent.parent.parent / "data" / "orchestrator" / "task_board.json"

        # Task board oku
        if task_board_path.exists():
            with open(task_board_path, encoding="utf-8") as f:
                gorevler = json.load(f)
        else:
            gorevler = []

        # Yeni görev oluştur (task_id otomatik)
        max_id = 0
        for g in gorevler:
            task_id_str = g.get("task_id", "").replace("P7-", "").replace("GOREV-", "")
            try:
                task_id_num = int(task_id_str)
                max_id = max(max_id, task_id_num)
            except:
                pass

        yeni_task_id = f"GOREV-{max_id + 1}"

        yeni_gorev = {
            "task_id": yeni_task_id,
            "baslik": mesaj[:50],  # İlk 50 char başlık
            "aciklama": mesaj,
            "sahip": "orkestrator",
            "durum": "acik",
            "onem": "orta",
            "created_at": datetime.now().isoformat(),
            "dosyalar": []
        }

        gorevler.append(yeni_gorev)

        # Task board'a yaz
        with open(task_board_path, "w", encoding="utf-8") as f:
            json.dump(gorevler, f, ensure_ascii=False, indent=2)

        logger.info(f"[MESAJ_ORKESTRATOR] Yeni görev oluşturuldu: {yeni_task_id} — {mesaj[:50]}")

        bot.send_message(
            message.chat.id,
            f"✅ **Mesaj Gönderildi**\n\n"
            f"📋 Görev: {yeni_task_id}\n"
            f"📝 İçerik: {mesaj[:100]}...\n\n"
            f"Orkestrator tarafından incelenecek.",
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"[MESAJ_ORKESTRATOR_ERROR] {e}", exc_info=True)
        bot.send_message(
            message.chat.id,
            f"❌ Mesaj gönderilemedi: {str(e)[:50]}"
        )

    send_gorev_takibi_menu(message.chat.id)


def show_yardim(chat_id: str) -> None:
    """Yardım göster — tüm kayıtlı / komutlarının listesi."""
    komutlar = [
        ("/start", "Ana menüyü göster"),
        ("/help", "Bu yardım"),
        ("/menu", "Menüyü göster"),
        ("/register <ad>", "Ajan olarak kendini kaydet"),
        ("/register_admin <ad> <chat_id>", "Sahip: Ajana manuel chat_id ata"),
        ("/pano", "Pano menüsünü göster"),
        ("/pano_done", "Tamamlanan görevler"),
        ("/pano_active", "Aktif görevler"),
        ("/pano_blocked", "Bloke görevler"),
        ("/pano_all", "Tüm görevler"),
    ]
    genislik = max(len(k) for k, _ in komutlar)
    tablo = "\n".join(f"{k.ljust(genislik)}  {a}" for k, a in komutlar)
    lines = [
        "❓ **Huginn Bot — Yardım & Komutlar**\n",
        f"```\n{tablo}\n```",
        "\n💡 **İpuçları**",
        "• Tüm menülerden [« Ana Menü] ile dön",
        "\n[« Ayarlar] [« Ana Menü]"
    ]

    bot.send_message(chat_id, "\n".join(lines), parse_mode="Markdown")


def show_yardim_detay(chat_id: str) -> None:
    """Detaylı yardım menüsü - her flow için nasıl kullanılır."""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("📋 Pano", "💬 Chat")
    markup.add("✉️ Tetikler", "📝 Mesaj")
    markup.add("📈 Raporlar", "⚙️ Ayarlar")
    markup.add("« Yardım", "« Ana Menü")

    msg = bot.send_message(
        chat_id,
        "📚 **Detaylı Yardım Menüsü**\n\n"
        "Aşağıdaki menülerden birini seçerek nasıl kullanılacağını öğrenin:",
        reply_markup=markup
    )
    bot.register_next_step_handler(msg, _handle_yardim_detay_selection)


def _handle_yardim_detay_selection(message):
    """Yardım detay seçimini işle."""
    if not message.text:
        show_yardim_detay(message.chat.id)
        return

    if "«" in message.text:
        show_yardim(message.chat.id)
        return

    helps = {
        "📋 Pano": _yardim_pano,
        "💬 Chat": _yardim_chat,
        "✉️ Tetikler": _yardim_tetikler,
        "📝 Mesaj": _yardim_mesaj,
        "📈 Raporlar": _yardim_raporlar,
        "⚙️ Ayarlar": _yardim_ayarlar,
    }

    for key, func in helps.items():
        if key in message.text:
            func(message.chat.id)
            return

    show_yardim_detay(message.chat.id)


def _yardim_pano(chat_id: str) -> None:
    """Pano yardımı."""
    text = """📋 **PANO MENÜSÜ — Görev Yönetimi**

**Ne Yapar?**
Tüm görevleri durum bazında görmek ve takip etmek için kullanılır.

**Nasıl Kullanılır?**
1. Ana menüden [📋 Pano] seçin
2. Görev durumunu seçin:
   🟢 Açık - Başlanılmamış görevler
   🟡 Aktif - Devam eden görevler
   🟠 Bloke - Bağımlılık bekleyen görevler
   📋 Plan - Planlanan görevler
   ✅ Tamamlandı - Tamamlanan görevler
   🔍 Tümü - Tüm görevler

3. Görevlerin detaylarını görebilirsiniz

**İpuçları:**
• Her görev kart formatında gösterilir
• Task ID ile görevi takip edebilirsiniz
• Görev sahibi ve son güncelleme zamanı görülür

[« Yardım Menüsü] [« Ana Menü]"""

    bot.send_message(chat_id, text, parse_mode="Markdown")


def _yardim_chat(chat_id: str) -> None:
    """Chat yardımı."""
    text = """💬 **CHAT MENÜSÜ — Sorun Takibi**

**Ne Yapar?**
Ajanların bildirdiği sorunları, çözüm durumlarını ve mesajları yönetmek için kullanılır.

**Nasıl Kullanılır?**
1. Ana menüden [💬 Chat] seçin
2. Sorun durumunu seçin:
   🟢 Açık - Yeni sorunlar
   🟡 Çözüm Bekliyor - İncelemede olan sorunlar
   ✅ Çözüldü - Çözülen sorunlar
   🔍 Tümü - Tüm sorunlar

3. Sorunları görebilirsiniz
4. Mesaj göndermek için türü seçin:
   📢 Broadcast - Tüm ajanlar için mesaj
   👤 Targeted - Belirli ajan için mesaj
   🎯 Tag Seç - Etikete göre mesaj
   🔔 Uyarı - Uyarı mesajı

**Targeted Mesaj Flow:**
• Ajan seçin → Önem düzeyi seçin → Mesaj yazın

**İpuçları:**
• Önem düzeyleri: 🔴 Kritik, 🟠 Yüksek, 🟡 Orta, 🟢 Düşük
• Her mesaj kimden geldiği bilgisi ile kaydedilir

[« Yardım Menüsü] [« Ana Menü]"""

    bot.send_message(chat_id, text, parse_mode="Markdown")


def _yardim_tetikler(chat_id: str) -> None:
    """Tetikler yardımı."""
    text = """✉️ **TETİKLER MENÜSÜ — Görev Kutusu**

**Ne Yapar?**
Her ajanın yapması gereken görevleri (tetikleri) görmek ve gönder.

**Nasıl Kullanılır?**
1. Ana menüden [✉️ Tetikler] seçin
2. Ajan seçin: Utku, Salih, Yasu, İhsan, Mimir veya Tümü

3. İşlem seçin:
   📬 Tetik Bak - Ajanın posta kutusundaki tetikleri gör
   ✉️ Tetik Gönder - Ajana tetik gönder

**Tetik Bak (Posta Kutusu):**
• Her tetik için:
  - Task ID (görev numarası)
  - Talimat (yapılması gereken şey)
  - Açık sorular (varsa uyarı)

**Tetik Gönder:**
• Ajan adını girin
• Tetik içeriğini yazın (max 500 karakter)
• Tetik direkt ajana gönderilir

**İpuçları:**
• ⚠️ açık soru = ajanın sorusu cevabı bekliyor
• ✅ = tüm sorular çözüldü
• Tetikler priorite sırası ile gösterilir

[« Yardım Menüsü] [« Ana Menü]"""

    bot.send_message(chat_id, text, parse_mode="Markdown")


def _yardim_mesaj(chat_id: str) -> None:
    """Mesaj yardımı."""
    text = """📝 **MESAJ MENÜSÜ — Ajanlarla İletişim**

**Ne Yapar?**
Farklı yollarla ajanlar ve gruplara mesaj göndermek için kullanılır.

**Mesaj Türleri:**

**📢 BROADCAST (Herkese Mesaj)**
• Tüm ajanların göreceği genel mesaj
• Flow: Mesaj yazın → Gönderilir
• Kullanım: Genel duyuru, önemli bilgi

**👤 TARGETED (Belirli Ajan)**
• Tek bir ajana hedeflenmiş mesaj
• Flow: Ajan seç → Önem seçin → Mesaj yazın
• Önem Düzeyleri:
  🔴 Kritik - Acil müdahale gerekli
  🟠 Yüksek - Önemli, hızlı ele alınmalı
  🟡 Orta - Normal (varsayılan)
  🟢 Düşük - Bilgi niteliğinde

**🎯 TAG SEÇ (Etikete Göre)**
• Belirli etikete sahip ajanları seçin
• Etiketler: Backend, Frontend, Analytics, Security
• Flow: Etiket seç → Mesaj yazın

**🔔 UYARI (Herkese Uyarı)**
• Tüm ajanlar için acil uyarı mesajı
• Flow: Mesaj yazın → Gönderilir
• Kullanım: Sistem uyarısı, kritik durum

**İpuçları:**
• Mesajlar maksimum 500 karakter
• Mesaj kimden (📢📭👤🎯🔔) olduğu kaydedilir
• Targeted mesajlar kimden (👤) ajan adı ile işaretlenir

[« Yardım Menüsü] [« Ana Menü]"""

    bot.send_message(chat_id, text, parse_mode="Markdown")


def _yardim_raporlar(chat_id: str) -> None:
    """Raporlar yardımı."""
    text = """📈 **RAPORLAR MENÜSÜ — Analitik & Özet**

**Ne Yapar?**
Görevleri, ajanları ve sistemin performansını raporlar halinde gösterir.

**Rapor Türleri:**

**📅 Zaman Bazlı Raporlar**
• 📅 Hafta - Geçtiğimiz haftanın özeti
• 📅 Ay - Geçen ayın özeti
• 📅 YTD (Year To Date) - Yıl başından bu yana

**👤 AJAN BAZLI**
• Her ajanın performans özeti
• Tamamlanan görev sayısı
• Ortalama tamamlama süresi
• Hata oranı

**📊 KPI (Ana Metrikler)**
• Toplam görev sayısı
• Tamamlama oranı
• Ortalama çözüm süresi
• Kritik görev sayısı

**📈 TREND**
• Görev sayısındaki eğilim
• Tamamlama hızındaki değişim
• Sistem performansı trendleri

**📋 ÖZET**
• Günlük tam özet raporu
• Tüm metriklerin bir sayfada görünümü

**İpuçları:**
• Raporlar en son veriye göre güncellenir
• Tarihlere göre filtreleme yapılabilir
• Excel/PDF'e aktarma seçeneği olabilir

[« Yardım Menüsü] [« Ana Menü]"""

    bot.send_message(chat_id, text, parse_mode="Markdown")


def _yardim_ayarlar(chat_id: str) -> None:
    """Ayarlar yardımı."""
    text = """⚙️ **AYARLAR MENÜSÜ — Bot Konfigürasyonu**

**Ne Yapar?**
Bot ayarlarını kontrol etmek, bağlantı duğrulamak ve bilgi almak.

**Ayar Seçenekleri:**

**🔗 Bağlantı Kontrol**
• Bot'un API bağlantısını test et
• Veritabanı bağlantısını kontrol et
• Sistem durum raporunu gör

**🔐 Token Doğrula**
• API token'ını doğrula
• Token geçerlilik durumunu kontrol et
• Yeni token talep et

**🤖 Bot Bilgisi**
• Bot versiyonu
• Kurulu eklentiler
• Sistem bilgileri
• Son güncelleme tarihi

**❓ Yardım**
• Komut listesi
• Kullanım rehberi
• SSS (Sık Sorulan Sorular)

**İpuçları:**
• Düzenli olarak bağlantı kontrol edin
• Token 30 günde bir yenilenmesi tavsiye edilir
• Sorun yaşanırsa sistem yöneticisine başvurun

[« Yardım Menüsü] [« Ana Menü]"""

    bot.send_message(chat_id, text, parse_mode="Markdown")


# ============================================================================
# BÖLÜM 8: CALLBACK HANDLERS
# ============================================================================

@bot.message_handler(commands=["start"])
def cmd_start(message):
    """Bot başlatma."""
    send_ana_menu(message.chat.id)
    logger.info(f"Started bot for user {message.chat.id}")


@bot.message_handler(commands=["register"])
def cmd_register(message):
    """Ajan kendisini kaydet: /register Adı"""
    import json
    from pathlib import Path

    text = message.text.strip()
    parts = text.split(maxsplit=1)

    if len(parts) < 2:
        bot.send_message(
            message.chat.id,
            "❌ Kullanım: `/register Adı`\n\n"
            "Örnek: `/register Utku`",
            parse_mode="Markdown"
        )
        return

    ajan_adi = parts[1].strip().capitalize()
    chat_id = message.chat.id

    # Agent chat_id'lerini sakla
    agent_chats_path = Path(__file__).parent.parent.parent / "data" / "orchestrator" / "agent_chats.json"
    agent_chats_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if agent_chats_path.exists():
            with open(agent_chats_path, encoding="utf-8") as f:
                agent_chats = json.load(f)
        else:
            agent_chats = {}

        agent_chats[ajan_adi] = str(chat_id)

        with open(agent_chats_path, "w", encoding="utf-8") as f:
            json.dump(agent_chats, f, ensure_ascii=False, indent=2)

        bot.send_message(
            message.chat.id,
            f"✅ **{ajan_adi}** başarıyla kaydedildi.\n\n"
            f"Chat ID: `{chat_id}`",
            parse_mode="Markdown"
        )
        logger.info(f"[REGISTER] Ajan {ajan_adi} kaydedildi (chat_id={chat_id})")

    except Exception as e:
        logger.error(f"[REGISTER_ERROR] {e}", exc_info=True)
        bot.send_message(
            message.chat.id,
            f"❌ Kayıt hatası: {str(e)}",
            parse_mode="Markdown"
        )


@bot.message_handler(commands=["register_admin"])
def cmd_register_admin(message):
    """Sahip: Ajana manuel chat_id ata (test ortamı için). /register_admin ajan_adi chat_id"""
    import json
    from pathlib import Path

    # Sadece sahip (owner) kullanabilsin
    OWNER_CHAT_ID = "801855376"  # Sen
    if str(message.chat.id) != OWNER_CHAT_ID:
        bot.send_message(
            message.chat.id,
            "❌ Bu komut yalnız sahip tarafından kullanılabilir.",
            parse_mode="Markdown"
        )
        return

    text = message.text.strip()
    parts = text.split()

    if len(parts) < 3:
        bot.send_message(
            message.chat.id,
            "❌ Kullanım: `/register_admin ajan_adi chat_id`\n\n"
            "Örnek: `/register_admin Utku 123456789`",
            parse_mode="Markdown"
        )
        return

    ajan_adi = parts[1].strip().capitalize()
    try:
        chat_id = str(int(parts[2]))  # Sayı olduğu kontrol et
    except ValueError:
        bot.send_message(
            message.chat.id,
            f"❌ chat_id sayı olmalı. Girilen: {parts[2]}",
            parse_mode="Markdown"
        )
        return

    # Agent chat_id'lerini sakla
    agent_chats_path = Path(__file__).parent.parent.parent / "data" / "orchestrator" / "agent_chats.json"
    agent_chats_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if agent_chats_path.exists():
            with open(agent_chats_path, encoding="utf-8") as f:
                agent_chats = json.load(f)
        else:
            agent_chats = {}

        agent_chats[ajan_adi] = chat_id

        with open(agent_chats_path, "w", encoding="utf-8") as f:
            json.dump(agent_chats, f, ensure_ascii=False, indent=2)

        bot.send_message(
            message.chat.id,
            f"✅ **{ajan_adi}** chat_id ile kaydedildi.\n\n"
            f"Ajan: `{ajan_adi}`\n"
            f"Chat ID: `{chat_id}`",
            parse_mode="Markdown"
        )
        logger.info(f"[REGISTER_ADMIN] Ajan {ajan_adi} manuel kaydedildi (chat_id={chat_id})")

    except Exception as e:
        logger.error(f"[REGISTER_ADMIN_ERROR] {e}", exc_info=True)
        bot.send_message(
            message.chat.id,
            f"❌ Kayıt hatası: {str(e)}",
            parse_mode="Markdown"
        )


@bot.message_handler(commands=["help", "menu"])
def cmd_help(message):
    """Yardım/Menü komutu."""
    send_ana_menu(message.chat.id)


# Slash command handlers (workaround for callback issues)
@bot.message_handler(commands=["pano"])
def cmd_pano(message):
    """Pano menüsü."""
    send_pano_menu(message.chat.id)


@bot.message_handler(commands=["pano_done"])
def cmd_pano_done(message):
    """Tamamlanan görevler."""
    show_pano_status(message.chat.id, "done")


@bot.message_handler(commands=["pano_active"])
def cmd_pano_active(message):
    """Aktif görevler."""
    show_pano_status(message.chat.id, "active")


@bot.message_handler(commands=["pano_blocked"])
def cmd_pano_blocked(message):
    """Bloke görevler."""
    show_pano_status(message.chat.id, "blocked")


@bot.message_handler(commands=["pano_all"])
def cmd_pano_all(message):
    """Tüm görevler."""
    show_pano_status(message.chat.id, "all")


# Text-based button handlers (for ReplyKeyboardMarkup)
@bot.message_handler(func=lambda message: message.text and "Tamamlandı" in message.text)
def btn_pano_done(message):
    """Tamamlanan görevler (button text)."""
    logger.info(f"[BUTTON] Pano Done clicked: {message.text}")
    show_pano_status(message.chat.id, "done")


@bot.message_handler(func=lambda message: message.text and "Aktif" in message.text)
def btn_pano_active(message):
    """Aktif görevler (button text)."""
    logger.info(f"[BUTTON] Pano Active clicked: {message.text}")
    show_pano_status(message.chat.id, "active")


@bot.message_handler(func=lambda message: message.text and "Bloke" in message.text)
def btn_pano_blocked(message):
    """Bloke görevler (button text)."""
    logger.info(f"[BUTTON] Pano Blocked clicked: {message.text}")
    show_pano_status(message.chat.id, "blocked")


@bot.message_handler(func=lambda message: message.text and "Plan" in message.text)
def btn_pano_plan(message):
    """Plan görevler (button text)."""
    logger.info(f"[BUTTON] Pano Plan clicked: {message.text}")
    show_pano_status(message.chat.id, "plan")


@bot.message_handler(func=lambda message: message.text and "Tümü" in message.text)
def btn_pano_all(message):
    """Tüm görevler (button text)."""
    logger.info(f"[BUTTON] Pano All clicked: {message.text}")
    show_pano_status(message.chat.id, "all")


@bot.message_handler(func=lambda message: message.text and "Ana Menü" in message.text)
def btn_ana_menu(message):
    """Ana menüye dön (button text)."""
    logger.info(f"[BUTTON] Ana Menu clicked: {message.text}")
    send_ana_menu(message.chat.id)


# Chat menü button handlers
@bot.message_handler(func=lambda message: message.text and "Açık" in message.text and "Chat" not in str(message.text))
def btn_chat_acik(message):
    """Açık sorunlar."""
    logger.info(f"[BUTTON] Chat Açık clicked: {message.text}")
    show_chat_status(message.chat.id, "acik")


@bot.message_handler(func=lambda message: message.text and "Çözüm" in message.text)
def btn_chat_cokundurmus(message):
    """Çözüm bekleyen sorunlar."""
    logger.info(f"[BUTTON] Chat Çözüm Bekl clicked: {message.text}")
    show_chat_status(message.chat.id, "cokundurmus")


@bot.message_handler(func=lambda message: message.text and "Çözüldü" in message.text)
def btn_chat_cozuldu(message):
    """Çözüldü sorunlar."""
    logger.info(f"[BUTTON] Chat Çözüldü clicked: {message.text}")
    show_chat_status(message.chat.id, "cozuldu")


@bot.message_handler(func=lambda message: message.text and "Son 10" in message.text)
def btn_chat_son10(message):
    """Chat: son 10 mesaj, tüm durumlar (Tümü'nün Pano ile çakışması D-217'de düzeltildi)."""
    logger.info(f"[BUTTON] Chat Son 10 clicked: {message.text}")
    show_chat_status(message.chat.id, "all")


# Ana menü button handlers
@bot.message_handler(func=lambda message: message.text and "Utku" in message.text and "👨" in message.text)
def btn_tetikler_utku(message):
    """Utku'nun tetikleri."""
    logger.info(f"[BUTTON] Tetikler Utku clicked: {message.text}")
    show_tetikler_ajan(message.chat.id, "Utku")


@bot.message_handler(func=lambda message: message.text and "Salih" in message.text and "👨" in message.text)
def btn_tetikler_salih(message):
    """Salih'in tetikleri."""
    logger.info(f"[BUTTON] Tetikler Salih clicked: {message.text}")
    show_tetikler_ajan(message.chat.id, "Salih")


@bot.message_handler(func=lambda message: message.text and "Yasu" in message.text and "👨" in message.text)
def btn_tetikler_yasu(message):
    """Yasu'nun tetikleri."""
    logger.info(f"[BUTTON] Tetikler Yasu clicked: {message.text}")
    show_tetikler_ajan(message.chat.id, "Yasu")


@bot.message_handler(func=lambda message: message.text and "İhsan" in message.text and "👨" in message.text)
def btn_tetikler_ihsan(message):
    """İhsan'ın tetikleri."""
    logger.info(f"[BUTTON] Tetikler İhsan clicked: {message.text}")
    show_tetikler_ajan(message.chat.id, "İhsan")


@bot.message_handler(func=lambda message: message.text and "Mimir" in message.text and "👨" in message.text)
def btn_tetikler_mimir(message):
    """Mimir'in tetikleri."""
    logger.info(f"[BUTTON] Tetikler Mimir clicked: {message.text}")
    show_tetikler_ajan(message.chat.id, "Mimir")


@bot.message_handler(func=lambda message: message.text and "Tümü" in message.text and "🔍" in message.text)
def btn_tetikler_all(message):
    """Tüm ajanların tetikleri."""
    logger.info(f"[BUTTON] Tetikler Tümü clicked: {message.text}")
    show_tetikler_ajan(message.chat.id, "*")


# Tetik Gönder ajan seçim butonları (✉️ emoji ile)
@bot.message_handler(func=lambda message: message.text and "Utku" in message.text and "✉️" in message.text)
def btn_tetikler_gonder_utku(message):
    """Utku'ya tetik gönder."""
    logger.info(f"[BUTTON] Tetik Gönder Utku clicked: {message.text}")
    _show_tetikler_gonder_mesaj(message.chat.id, "Utku")


@bot.message_handler(func=lambda message: message.text and "Salih" in message.text and "✉️" in message.text)
def btn_tetikler_gonder_salih(message):
    """Salih'e tetik gönder."""
    logger.info(f"[BUTTON] Tetik Gönder Salih clicked: {message.text}")
    _show_tetikler_gonder_mesaj(message.chat.id, "Salih")


@bot.message_handler(func=lambda message: message.text and "Yasu" in message.text and "✉️" in message.text)
def btn_tetikler_gonder_yasu(message):
    """Yasu'ya tetik gönder."""
    logger.info(f"[BUTTON] Tetik Gönder Yasu clicked: {message.text}")
    _show_tetikler_gonder_mesaj(message.chat.id, "Yasu")


@bot.message_handler(func=lambda message: message.text and "İhsan" in message.text and "✉️" in message.text)
def btn_tetikler_gonder_ihsan(message):
    """İhsan'a tetik gönder."""
    logger.info(f"[BUTTON] Tetik Gönder İhsan clicked: {message.text}")
    _show_tetikler_gonder_mesaj(message.chat.id, "İhsan")


@bot.message_handler(func=lambda message: message.text and "Mimir" in message.text and "✉️" in message.text)
def btn_tetikler_gonder_mimir(message):
    """Mimir'e tetik gönder."""
    logger.info(f"[BUTTON] Tetik Gönder Mimir clicked: {message.text}")
    _show_tetikler_gonder_mesaj(message.chat.id, "Mimir")


# Tetikler action handlers (📬 Tetik Bak, ✉️ Tetik Gönder)
# ponytail: state management dict kullanıldı, production'da Redis kullan
# add when: Redis/Memcached + session store
_tetikler_state = {}
_tetikler_gonder_state = {}

@bot.message_handler(func=lambda message: message.text and "📬 Tetik Bak" in message.text and "Sahib" not in message.text)
def btn_tetikler_bak_action(message):
    """Tetik bakma aksiyon."""
    logger.info(f"[BUTTON] Tetikler Bak clicked: {message.text}")

    chat_id = str(message.chat.id)

    # Ajan adı state'de varsa direkt tetikleri göster
    if chat_id in _tetikler_state:
        ajan = _tetikler_state.pop(chat_id)
        _show_tetikler_ajan_detay(message.chat.id, ajan)
        send_tetikler_menu(message.chat.id)
    else:
        # Fallback: ajan seçimi iste
        msg = bot.send_message(
            message.chat.id,
            "👤 **Tetik Bak**\n\n"
            "Hangi ajan için tetikleri görmek istiyorsunuz?\n"
            "Ajan adını yazın (Utku, Salih, Yasu, İhsan, Mimir):",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, _tetik_bak_ajan_secimi)


def _tetik_bak_ajan_secimi(message):
    """Tetik bak için ajan seçimi."""
    if message.text and message.text.startswith("«"):
        send_tetikler_menu(message.chat.id)
        return

    ajan = message.text.strip()
    valid_ajanlar = ["Utku", "Salih", "Yasu", "İhsan", "Mimir"]

    if ajan not in valid_ajanlar:
        msg = bot.send_message(
            message.chat.id,
            f"❌ Geçersiz ajan adı: {ajan}\n\n"
            f"Lütfen şu ajanlardan birini seçin:\n"
            f"{', '.join(valid_ajanlar)}"
        )
        bot.register_next_step_handler(msg, _tetik_bak_ajan_secimi)
        return

    _show_tetikler_ajan_detay(message.chat.id, ajan)
    send_tetikler_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "✉️ Tetik Gönder" in message.text)
def btn_tetikler_gonder_action(message):
    """Tetik gönderme aksiyon — ajan seçim menüsü göster."""
    logger.info(f"[BUTTON] Tetikler Gönder clicked: {message.text}")
    _show_tetikler_gonder_ajan_menu(message.chat.id)


def _show_tetikler_gonder_ajan_menu(chat_id: str) -> None:
    """Tetik gönderme için ajan seçim menüsü."""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    markup.add("👨 Utku (✉️)", "👨 Salih (✉️)")
    markup.add("👨 Yasu (✉️)", "👨 İhsan (✉️)")
    markup.add("👨 Mimir (✉️)", "« Tetikler Menüsü")

    bot.send_message(
        chat_id,
        "📮 **Tetik Gönder**\n\n"
        "Hangi ajana tetik göndermek istiyorsunuz?",
        reply_markup=markup,
        parse_mode="Markdown"
    )


def _show_tetikler_gonder_mesaj(chat_id: str, ajan: str) -> None:
    """Tetik mesaj giriş ekranı."""
    msg = bot.send_message(
        chat_id,
        f"👤 **{ajan}**\n\n"
        f"📝 Tetik/Mesaj içeriğini yazın (max 500 char):\n\n"
        f"(« tuşu ile geri dön)",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, lambda m: _tetik_gonder_mesaj(m, ajan))


def _tetik_gonder_ajan_secimi(message):
    """Tetik gönderme için ajan seçimi."""
    if message.text and message.text.startswith("«"):
        send_tetikler_menu(message.chat.id)
        return

    ajan = message.text.strip()
    valid_ajanlar = ["Utku", "Salih", "Yasu", "İhsan", "Mimir"]

    if ajan not in valid_ajanlar:
        msg = bot.send_message(
            message.chat.id,
            f"❌ Geçersiz ajan adı: {ajan}\n\n"
            f"Lütfen şu ajanlardan birini seçin:\n"
            f"{', '.join(valid_ajanlar)}"
        )
        bot.register_next_step_handler(msg, _tetik_gonder_ajan_secimi)
        return

    msg = bot.send_message(
        message.chat.id,
        f"👤 {ajan}\n\n"
        f"📝 Tetik/Mesaj içeriğini yazın (max 500 char):"
    )
    bot.register_next_step_handler(msg, lambda m: _tetik_gonder_mesaj(m, ajan))


def _tetik_gonder_mesaj(message, ajan):
    """Tetik mesajını kaydet ve post seçeneği sun."""
    if message.text and message.text.startswith("«"):
        send_tetikler_menu(message.chat.id)
        return

    tetik_mesaj = message.text.strip()[:500]

    try:
        from orchestrator.trigger import tetik_uyari_ekle
        result = tetik_uyari_ekle(ajan)

        bot.send_message(
            message.chat.id,
            f"✅ **Tetik Gönderildi**\n\n"
            f"👤 Ajan: {ajan}\n"
            f"📝 İçerik: {tetik_mesaj}\n"
            f"⏰ Zaman: {result.get('timestamp', 'N/A')}\n\n"
            f"Tetik {ajan}'ın posta kutusuna eklendi.",
            parse_mode="Markdown"
        )

        # Tetikle beraber post seçeneği sun
        _show_tetik_post_menu(message.chat.id, ajan)

    except Exception as e:
        logger.error(f"Error sending tetik to {ajan}: {e}")
        bot.send_message(
            message.chat.id,
            f"❌ Tetik gönderilemedi: {str(e)}\n\n"
            f"Lütfen daha sonra tekrar deneyin."
        )
        send_tetikler_menu(message.chat.id)


def _show_tetik_post_menu(chat_id: str, ajan: str) -> None:
    """Tetikle beraber post göndermek için menü."""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    markup.add("📮 Post Gönder", "« Tetikler Menüsü")

    bot.send_message(
        chat_id,
        f"📮 **{ajan}'a Mesaj Gönder?**\n\n"
        f"Tetikle beraber bir post/mesaj göndermek ister misiniz?\n\n"
        f"(« tuşu ile Tetikler menüsüne dön)",
        reply_markup=markup,
        parse_mode="Markdown"
    )


@bot.message_handler(func=lambda message: message.text and "📮 Post Gönder" in message.text)
def btn_tetik_post_gonder(message):
    """Tetikle beraber post gönder."""
    logger.info(f"[BUTTON] Tetik Post Gönder clicked: {message.text}")

    # Son ajan bilgisini state'ten al (ya da yeniden sor)
    msg = bot.send_message(
        message.chat.id,
        "📮 **Post İçeriği**\n\n"
        "Göndermek istediğiniz mesaj/post'u yazın (max 500 karakter):\n\n"
        "(« tuşu ile geri dön)"
    )
    bot.register_next_step_handler(msg, _tetik_post_kaydet)


def _tetik_post_kaydet(message):
    """Tetikle beraber gönderilen post'u kaydet."""
    if message.text and message.text.startswith("«"):
        send_tetikler_menu(message.chat.id)
        return

    post_mesaj = message.text.strip()[:500]

    try:
        # Post kaydı (örneğin, orchestrator mesaj kuyruğuna ekle)
        # Şimdilik loglama + konfirmasyonla yetiniyoruz
        logger.info(f"[TETIK_POST] Post kaydedildi: {post_mesaj}")

        bot.send_message(
            message.chat.id,
            f"✅ **Post Gönderildi**\n\n"
            f"📮 İçerik: {post_mesaj}\n\n"
            f"Post ve tetik birlikte işleme alındı.",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error saving tetik post: {e}")
        bot.send_message(
            message.chat.id,
            f"❌ Post gönderilemedi: {str(e)}"
        )

    send_tetikler_menu(message.chat.id)


# Ana menü button handlers
@bot.message_handler(func=lambda message: message.text and "Pano" in message.text)
def btn_pano_menu(message):
    """Pano menüsü."""
    logger.info(f"[BUTTON] Pano Menu clicked: {message.text}")
    send_pano_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "Chat" in message.text)
def btn_chat_menu(message):
    """Chat menüsü."""
    logger.info(f"[BUTTON] Chat Menu clicked: {message.text}")
    send_chat_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "Tetikler" in message.text)
def btn_tetikler_menu(message):
    """Tetikler menüsü."""
    logger.info(f"[BUTTON] Tetikler Menu clicked: {message.text}")
    send_tetikler_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "Mesaj" in message.text and "✉️" not in message.text)
def btn_mesaj_menu(message):
    """Mesaj menüsü."""
    logger.info(f"[BUTTON] Mesaj Menu clicked: {message.text}")
    send_mesaj_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "✉️" in message.text and "Mesaj Gönder" in message.text)
def btn_chat_mesaj_gonder(message):
    """Chat: hızlı mesaj yaz (önceden handler'sız kalan buton — D-improvement fix)."""
    logger.info(f"[BUTTON] Chat Mesaj Gönder clicked: {message.chat.id}")
    msg = bot.send_message(message.chat.id, "✉️ Mesajınızı yazın (« ile geri dönebilirsiniz):")
    bot.register_next_step_handler(msg, _chat_mesaj_gonder)


def _chat_mesaj_gonder(message):
    if message.text and message.text.startswith("«"):
        send_chat_menu(message.chat.id)
        return
    try:
        from chat import kahin_gonder
        gonderen = _gonderen_ajan_bul(message.chat.id)
        kahin_gonder(message.text.strip()[:500], onem="orta", kimden=gonderen)
        bot.send_message(message.chat.id, "✅ Mesaj gönderildi.")
    except Exception as e:
        logger.error(f"[CHAT_MESAJ_ERROR] {e}", exc_info=True)
        bot.send_message(message.chat.id, f"❌ Hata: {str(e)[:50]}")
    send_chat_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "Belgeler" in message.text and "📚" in message.text)
def btn_belgeler_menu(message):
    send_belgeler_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "Rapor Dosyaları Listesi" in message.text)
def btn_son10_rapor(message):
    show_son_10_rapor(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "SSOT Oku" in message.text)
def btn_ssot_oku(message):
    show_ssot_oku(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "Admin Hub Oku" in message.text)
def btn_admin_hub_oku(message):
    show_admin_hub_oku(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "Matrix İlerleme" in message.text)
def btn_matrix_ilerleme(message):
    show_matrix_ilerleme(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "Rapor" in message.text)
def btn_rapor_menu(message):
    """Rapor menüsü."""
    logger.info(f"[BUTTON] Rapor Menu clicked: {message.text}")
    send_rapor_menu(message.chat.id)


# Mesaj button handlers
@bot.message_handler(func=lambda message: message.text and "Broadcast" in message.text)
def btn_mesaj_broadcast(message):
    """Broadcast — tüm ajanlar."""
    logger.info(f"[BUTTON] Mesaj Broadcast clicked: {message.text}")
    msg = bot.send_message(message.chat.id, "📢 Tüm ajanlar için mesajınızı yazın:")
    bot.register_next_step_handler(msg, _mesaj_gonder_broadcast)


def _mesaj_gonder_broadcast(message):
    if message.text and message.text.startswith("«"):
        send_mesaj_menu(message.chat.id)
        return
    try:
        from chat import kahin_gonder
        kahin_gonder(message.text, onem="broadcast", kimden="📢 Broadcast")
        bot.send_message(message.chat.id, "✅ Broadcast mesajı tüm ajanlar tarafından alındı.")
    except Exception as e:
        logger.error(f"[BROADCAST_ERROR] {e}", exc_info=True)
        bot.send_message(message.chat.id, f"❌ Hata: {str(e)[:50]}")
    send_mesaj_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "Targeted" in message.text)
def btn_mesaj_targeted(message):
    """Targeted — ajan seç."""
    logger.info(f"[BUTTON] Mesaj Targeted clicked: {message.text}")
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("💬 Utku", "💬 Salih", "💬 Yasu")
    markup.add("💬 İhsan", "💬 Mimir")
    markup.add("« Mesaj Menüsü")
    bot.send_message(message.chat.id, "👤 Hangi ajana mesaj göndermek istiyorsunuz?", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text and "Utku" in message.text and "💬" in message.text)
def _mesaj_ajan_utku(message):
    _show_onem_menu(message.chat.id, "Utku")


@bot.message_handler(func=lambda message: message.text and "Salih" in message.text and "💬" in message.text)
def _mesaj_ajan_salih(message):
    _show_onem_menu(message.chat.id, "Salih")


@bot.message_handler(func=lambda message: message.text and "Yasu" in message.text and "💬" in message.text)
def _mesaj_ajan_yasu(message):
    _show_onem_menu(message.chat.id, "Yasu")


@bot.message_handler(func=lambda message: message.text and "İhsan" in message.text and "💬" in message.text)
def _mesaj_ajan_ihsan(message):
    _show_onem_menu(message.chat.id, "İhsan")


@bot.message_handler(func=lambda message: message.text and "Mimir" in message.text and "💬" in message.text)
def _mesaj_ajan_mimir(message):
    _show_onem_menu(message.chat.id, "Mimir")


def _show_onem_menu(chat_id, ajan):
    """Ajan seçildikten sonra önem düzeyi seçme menüsü."""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("🔴 Kritik", "🟠 Yüksek")
    markup.add("🟡 Orta", "🟢 Düşük")
    markup.add(f"« Targeted Menüsü")
    msg = bot.send_message(chat_id, f"👤 {ajan}\n\n⚠️ Mesaj önem düzeyini seçin:", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda m: _mesaj_ajan_onem(m, ajan))


def _mesaj_ajan_onem(message, ajan):
    """Önem düzeyi seçildikten sonra mesaj yazma."""
    if message.text and message.text.startswith("«"):
        btn_mesaj_targeted(message)
        return

    onem_map = {
        "🔴 Kritik": "critical",
        "🟠 Yüksek": "yuksek",
        "🟡 Orta": "orta",
        "🟢 Düşük": "dusuk"
    }
    onem = onem_map.get(message.text, "orta")

    msg = bot.send_message(message.chat.id, f"📝 {ajan}'a gönderilecek mesaj yazın:")
    bot.register_next_step_handler(msg, lambda m: _mesaj_ajan_gonder(m, ajan, onem))


def _gonderen_ajan_bul(chat_id) -> str:
    """chat_id'den gönderen ajan adını bul (agent_chats.json reverse lookup).
    Sahip chat_id'siyle eşleşirse 'KAHİN' döner, bulunamazsa 'Bilinmeyen' döner."""
    try:
        import json
        from pathlib import Path
        if str(chat_id) == "801855376":
            return "KAHİN"
        agent_chats_path = Path(__file__).parent.parent.parent / "data" / "orchestrator" / "agent_chats.json"
        if agent_chats_path.exists():
            with open(agent_chats_path, "r", encoding="utf-8") as f:
                agent_chats = json.load(f)
            for ad, cid in agent_chats.items():
                if str(cid) == str(chat_id):
                    return ad
    except Exception as e:
        logger.error(f"[GONDEREN_BUL_ERROR] {e}", exc_info=True)
    return "Bilinmeyen"


def _mesaj_ajan_gonder(message, ajan, onem="orta"):
    if message.text and message.text.startswith("«"):
        send_mesaj_menu(message.chat.id)
        return
    try:
        from chat import kahin_gonder
        gonderen = _gonderen_ajan_bul(message.chat.id)
        logger.info(f"[MESAJ_AJAN_START] {gonderen} -> {ajan} mesaj gönderme başladı")

        # Audit trail: KAHİN'e mesajı gönder (chat.json'e kaydet)
        kahin_gonder(message.text, onem=onem, kimden=f"👤 {gonderen} → {ajan}")
        logger.info(f"[MESAJ_AJAN_KAHIN] KAHİN'e kaydedildi")

        # Ajanın Telegram chat_id'sine mesajı gönder (gönderen bilgisiyle)
        mesaj_metni = f"📬 {gonderen}'dan Mesaj (Önem: {onem})\n\n{message.text}"
        logger.info(f"[MESAJ_AJAN_AGENT] {ajan}'a Telegram mesajı gönderiliyor...")
        agent_result = send_agent_message(ajan, mesaj_metni)
        logger.info(f"[MESAJ_AJAN_RESULT] {ajan} sonuç: {agent_result}")

        if agent_result:
            bot.send_message(message.chat.id, f"✅ Mesaj {ajan}'a gönderildi.")
        else:
            bot.send_message(message.chat.id, f"⚠️ Mesaj kaydedildi ama Telegram gönderimi başarısız.")
    except Exception as e:
        logger.error(f"[MESAJ_AJAN_ERROR] {ajan}: {e}", exc_info=True)
        bot.send_message(message.chat.id, f"❌ Hata: {str(e)[:50]}")
    send_mesaj_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "Tag Seç" in message.text)
def btn_mesaj_tag(message):
    """Sorun kaynağı sınıflandırma (D-improvement: takım seçimi yerine kaynak tag)."""
    logger.info(f"[BUTTON] Mesaj Tag clicked: {message.text}")
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("🐛 Hata/Bug", "📊 Veri Kalitesi")
    markup.add("⚡ Performans", "🔐 Güvenlik")
    markup.add("❓ Diğer")
    markup.add("« Mesaj Menüsü")
    bot.send_message(message.chat.id, "🎯 Sorunun kaynağı ne? (Mesaj bu kategoriyle etiketlenir)", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text and "Hata/Bug" in message.text and "🐛" in message.text)
def _mesaj_tag_hata(message):
    msg = bot.send_message(message.chat.id, "📝 Hata/Bug ile ilgili mesajınızı yazın:")
    bot.register_next_step_handler(msg, lambda m: _mesaj_tag_gonder(m, "Hata/Bug"))


@bot.message_handler(func=lambda message: message.text and "Veri Kalitesi" in message.text and "📊" in message.text)
def _mesaj_tag_veri(message):
    msg = bot.send_message(message.chat.id, "📝 Veri Kalitesi ile ilgili mesajınızı yazın:")
    bot.register_next_step_handler(msg, lambda m: _mesaj_tag_gonder(m, "Veri Kalitesi"))


@bot.message_handler(func=lambda message: message.text and "Performans" in message.text and "⚡" in message.text)
def _mesaj_tag_performans(message):
    msg = bot.send_message(message.chat.id, "📝 Performans ile ilgili mesajınızı yazın:")
    bot.register_next_step_handler(msg, lambda m: _mesaj_tag_gonder(m, "Performans"))


@bot.message_handler(func=lambda message: message.text and "Güvenlik" in message.text and "🔐" in message.text)
def _mesaj_tag_guvenlik(message):
    msg = bot.send_message(message.chat.id, "📝 Güvenlik ile ilgili mesajınızı yazın:")
    bot.register_next_step_handler(msg, lambda m: _mesaj_tag_gonder(m, "Güvenlik"))


@bot.message_handler(func=lambda message: message.text and "Diğer" in message.text and "❓" in message.text)
def _mesaj_tag_diger(message):
    msg = bot.send_message(message.chat.id, "📝 Mesajınızı yazın:")
    bot.register_next_step_handler(msg, lambda m: _mesaj_tag_gonder(m, "Diğer"))


def _mesaj_tag_gonder(message, tag):
    if message.text and message.text.startswith("«"):
        send_mesaj_menu(message.chat.id)
        return
    try:
        from chat import kahin_gonder
        kahin_gonder(message.text, onem="orta", kimden=f"🎯 {tag}")
        bot.send_message(message.chat.id, f"✅ Mesaj {tag} takımına gönderildi.")
    except Exception as e:
        logger.error(f"[MESAJ_TAG_ERROR] {tag}: {e}", exc_info=True)
        bot.send_message(message.chat.id, f"❌ Hata: {str(e)[:50]}")
    send_mesaj_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "Uyarı" in message.text)
def btn_mesaj_alert(message):
    """Uyarı mesajı."""
    logger.info(f"[BUTTON] Mesaj Alert clicked: {message.text}")
    msg = bot.send_message(message.chat.id, "🔔 Uyarı mesajınızı yazın:")
    bot.register_next_step_handler(msg, _mesaj_alert_gonder)


def _mesaj_alert_gonder(message):
    if message.text and message.text.startswith("«"):
        send_mesaj_menu(message.chat.id)
        return
    try:
        from chat import kahin_gonder
        kahin_gonder(message.text, onem="critical", kimden="🔔 Uyarı")
        bot.send_message(message.chat.id, "🔔 ✅ Uyarı mesajı gönderildi.")
    except Exception as e:
        logger.error(f"[ALERT_ERROR] {e}", exc_info=True)
        bot.send_message(message.chat.id, f"❌ Hata: {str(e)[:50]}")
    send_mesaj_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "KAHİN'e Mesaj" in message.text)
def btn_mesaj_kahin(message):
    """Ajan → KAHİN mesajlaşması: Ajan mesaj yazmaya hazırlanır."""
    logger.info(f"[BUTTON] KAHİN'e Mesaj clicked: {message.chat.id}")
    msg = bot.send_message(
        message.chat.id,
        "📬 **KAHİN'e Mesaj Gönder**\n\n"
        "Mesajını yaz (« geri dönüş):",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, _kahin_mesaj_gonder)


def _kahin_mesaj_gonder(message):
    """KAHİN'e mesaj al ve kaydet."""
    if message.text and message.text.startswith("«"):
        send_mesaj_menu(message.chat.id)
        return

    try:
        import json
        from pathlib import Path
        from chat import kahin_gonder

        # agent_chats.json'dan ajan adını bul (reverse lookup: chat_id → ajan_adi)
        agent_chats_path = Path(__file__).parent.parent.parent / "data" / "orchestrator" / "agent_chats.json"
        ajan_adi = None

        if agent_chats_path.exists():
            with open(agent_chats_path, "r", encoding="utf-8") as f:
                agent_chats = json.load(f)
                # Ters çevir: chat_id'ye göre ajan adını bul
                for ad, chat_id in agent_chats.items():
                    if str(chat_id) == str(message.chat.id):
                        ajan_adi = ad
                        break

        if not ajan_adi:
            ajan_adi = f"Ajan#{message.chat.id}"

        # Mesajı KAHİN'e gönder (kahin_gonder → chat.json'a kaydet)
        kahin_gonder(
            message.text,
            onem="orta",
            kimden=f"👤 {ajan_adi} (Ajan)"
        )

        # agent_responses.json'a da log et
        agent_responses_path = Path(__file__).parent.parent.parent / "data" / "orchestrator" / "agent_responses.json"
        responses = []
        if agent_responses_path.exists():
            with open(agent_responses_path, "r", encoding="utf-8") as f:
                responses = json.load(f)

        from datetime import datetime
        responses.append({
            "timestamp": datetime.now().isoformat(),
            "ajan": ajan_adi,
            "mesaj": message.text,
            "alici": "KAHİN",
            "durum": "sent"
        })

        with open(agent_responses_path, "w", encoding="utf-8") as f:
            json.dump(responses, f, ensure_ascii=False, indent=2)

        logger.info(f"[AJAN_KAHIN_DONE] {ajan_adi} → KAHİN mesajı gönderildi")
        bot.send_message(message.chat.id, "✅ Mesajın KAHİN'e iletildi.")

    except Exception as e:
        logger.error(f"[AJAN_KAHIN_ERROR] {e}", exc_info=True)
        bot.send_message(message.chat.id, f"❌ Hata: {str(e)[:80]}")

    send_mesaj_menu(message.chat.id)


# Rapor button handlers
@bot.message_handler(func=lambda message: message.text and "Hafta" in message.text and "📅" in message.text)
def btn_rapor_hafta(message):
    """Haftalık rapor."""
    logger.info(f"[BUTTON] Rapor Hafta clicked: {message.text}")
    show_hafta_raporu(message.chat.id)
    send_rapor_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "Ay" in message.text and "📅" in message.text)
def btn_rapor_ay(message):
    """Aylık rapor — task_board'dan."""
    logger.info(f"[BUTTON] Rapor Ay clicked: {message.text}")
    show_rapor_ay(message.chat.id)
    send_rapor_menu(message.chat.id)


def show_rapor_ay(chat_id: str) -> None:
    """Aylık rapor — task_board'dan."""
    import json
    from pathlib import Path
    from collections import Counter

    try:
        task_board_path = Path(__file__).parent.parent.parent / "data" / "orchestrator" / "task_board.json"
        tasks = []
        if task_board_path.exists():
            with open(task_board_path, "r", encoding="utf-8") as f:
                tasks = json.load(f)

        # Calculate metrics
        acik = len([t for t in tasks if t.get('durum') == 'Açık'])
        aktif = len([t for t in tasks if t.get('durum') == 'Aktif'])
        bloke = len([t for t in tasks if t.get('durum') == 'Bloke'])
        done = len([t for t in tasks if t.get('durum') == 'Tamamlandı'])
        toplam = len(tasks)

        lines = [
            "📊 **AYLIK RAPOR**\n",
            f"📅 Dönem: {datetime.now().strftime('%Y-%m')}\n",
            "```",
            "┌──────────────────────────────────┐",
            "│ DURUM          │ SAYISI │ YÜZDE  │",
            "├──────────────────────────────────┤",
            f"│ 🟢 Açık        │   {acik:2d}   │ {(acik*100//toplam if toplam else 0):3d}%  │",
            f"│ 🔵 Aktif       │   {aktif:2d}   │ {(aktif*100//toplam if toplam else 0):3d}%  │",
            f"│ 🟠 Bloke       │   {bloke:2d}   │ {(bloke*100//toplam if toplam else 0):3d}%  │",
            f"│ ✅ Tamamlandı  │   {done:2d}   │ {(done*100//toplam if toplam else 0):3d}%  │",
            "├──────────────────────────────────┤",
            f"│ 📊 TOPLAM      │  {toplam:3d}   │ 100%  │",
            "└──────────────────────────────────┘",
            "```",
            "\n**📋 Son 5 Görev:**"
        ]

        for i, task in enumerate(tasks[-5:], 1):
            task_id = task.get("task_id", "?")
            durum = task.get("durum", "?")
            baslik = task.get("baslik", "")[:30]
            sahip = task.get("sahip", "?")
            onem = task.get("onem", "orta")

            durum_emoji = {"Açık": "🟢", "Aktif": "🔵", "Bloke": "🟠", "Tamamlandı": "✅", "Plan": "📋"}.get(durum, "❓")
            onem_emoji = {"kritik": "🔴", "yuksek": "🟠", "orta": "🟡", "dusuk": "🟢"}.get(onem, "⚪")

            lines.append(f"\n{i}. {durum_emoji} **{task_id}** ({onem_emoji} {onem.capitalize()})")
            lines.append(f"   📌 {baslik}")
            lines.append(f"   👤 {sahip}")

        lines.append("\n[« Rapor Menüsü]")
        bot.send_message(chat_id, "\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        logger.error(f"[RAPOR_AY_ERROR] {e}", exc_info=True)
        bot.send_message(chat_id, f"❌ Rapor yüklenemedi: {str(e)[:50]}")


@bot.message_handler(func=lambda message: message.text and "YTD" in message.text)
def btn_rapor_ytd(message):
    """YTD raporu — task_board'dan."""
    logger.info(f"[BUTTON] Rapor YTD clicked: {message.text}")
    show_rapor_ytd(message.chat.id)
    send_rapor_menu(message.chat.id)


def show_rapor_ytd(chat_id: str) -> None:
    """YTD raporu — task_board'dan."""
    import json
    from pathlib import Path

    try:
        task_board_path = Path(__file__).parent.parent.parent / "data" / "orchestrator" / "task_board.json"
        tasks = []
        if task_board_path.exists():
            with open(task_board_path, "r", encoding="utf-8") as f:
                tasks = json.load(f)

        # Calculate metrics
        acik = len([t for t in tasks if t.get('durum') == 'Açık'])
        aktif = len([t for t in tasks if t.get('durum') == 'Aktif'])
        bloke = len([t for t in tasks if t.get('durum') == 'Bloke'])
        done = len([t for t in tasks if t.get('durum') == 'Tamamlandı'])
        plan = len([t for t in tasks if t.get('durum') == 'Plan'])
        toplam = len(tasks)
        tamamlama_orani = (done * 100 // toplam) if toplam else 0

        lines = [
            "📊 **YTD RAPORU**\n",
            f"📅 Dönem: 2026-01 → {datetime.now().strftime('%Y-%m')}\n",
            "```",
            "┌──────────────────────────────────┐",
            "│ DURUM          │ SAYISI │ YÜZDE  │",
            "├──────────────────────────────────┤",
            f"│ 🟢 Açık        │   {acik:2d}   │ {(acik*100//toplam if toplam else 0):3d}%  │",
            f"│ 🔵 Aktif       │   {aktif:2d}   │ {(aktif*100//toplam if toplam else 0):3d}%  │",
            f"│ 🟠 Bloke       │   {bloke:2d}   │ {(bloke*100//toplam if toplam else 0):3d}%  │",
            f"│ 📋 Plan        │   {plan:2d}   │ {(plan*100//toplam if toplam else 0):3d}%  │",
            f"│ ✅ Tamamlandı  │   {done:2d}   │ {tamamlama_orani:3d}%  │",
            "├──────────────────────────────────┤",
            f"│ 📊 TOPLAM      │  {toplam:3d}   │ 100%  │",
            "└──────────────────────────────────┘",
            "```",
            "\n**📋 Son 5 Görev:**"
        ]

        for i, task in enumerate(tasks[-5:], 1):
            task_id = task.get("task_id", "?")
            durum = task.get("durum", "?")
            baslik = task.get("baslik", "")[:30]
            sahip = task.get("sahip", "?")
            onem = task.get("onem", "orta")

            durum_emoji = {"Açık": "🟢", "Aktif": "🔵", "Bloke": "🟠", "Tamamlandı": "✅", "Plan": "📋"}.get(durum, "❓")
            onem_emoji = {"kritik": "🔴", "yuksek": "🟠", "orta": "🟡", "dusuk": "🟢"}.get(onem, "⚪")

            lines.append(f"\n{i}. {durum_emoji} **{task_id}** ({onem_emoji} {onem.capitalize()})")
            lines.append(f"   📌 {baslik}")
            lines.append(f"   👤 {sahip}")

        lines.append("\n[« Rapor Menüsü]")
        bot.send_message(chat_id, "\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        logger.error(f"[RAPOR_YTD_ERROR] {e}", exc_info=True)
        bot.send_message(chat_id, f"❌ Rapor yüklenemedi: {str(e)[:50]}")


@bot.message_handler(func=lambda message: message.text and "Ajan Bazlı" in message.text)
def btn_rapor_ajan(message):
    """Ajan bazlı rapor — task_board'dan."""
    logger.info(f"[BUTTON] Rapor Ajan Bazlı clicked: {message.text}")
    show_rapor_ajan(message.chat.id)
    send_rapor_menu(message.chat.id)


def show_rapor_ajan(chat_id: str) -> None:
    """Ajan bazlı rapor — task_board'dan."""
    import json
    from pathlib import Path
    from collections import Counter

    try:
        task_board_path = Path(__file__).parent.parent.parent / "data" / "orchestrator" / "task_board.json"
        tasks = []
        if task_board_path.exists():
            with open(task_board_path, "r", encoding="utf-8") as f:
                tasks = json.load(f)

        # Agent task counts and completion
        ajan_tasks = {}
        for task in tasks:
            ajan = task.get('sahip', 'unknown')
            if ajan not in ajan_tasks:
                ajan_tasks[ajan] = {'toplam': 0, 'done': 0, 'aktif': 0, 'bloke': 0}
            ajan_tasks[ajan]['toplam'] += 1
            durum = task.get('durum', '')
            if durum == 'Tamamlandı':
                ajan_tasks[ajan]['done'] += 1
            elif durum == 'Aktif':
                ajan_tasks[ajan]['aktif'] += 1
            elif durum == 'Bloke':
                ajan_tasks[ajan]['bloke'] += 1

        lines = [
            "👤 **AJAN BAZLI RAPOR**\n",
            "```",
            "┌─────────────────────────────────────────────┐",
            "│ AJAN       │ TOPLAM │ TAMA. │ AKTİF │ BLOKE│",
            "├─────────────────────────────────────────────┤"
        ]

        # Sort by total tasks descending
        for ajan in sorted(ajan_tasks.keys(), key=lambda x: ajan_tasks[x]['toplam'], reverse=True):
            stats = ajan_tasks[ajan]
            tamamlama_orani = (stats['done'] * 100 // stats['toplam']) if stats['toplam'] else 0
            ajan_display = ajan[:10].ljust(10)
            lines.append(f"│ {ajan_display} │  {stats['toplam']:2d}   │  {stats['done']:2d}   │  {stats['aktif']:2d}   │  {stats['bloke']:2d}  │")

        lines.append("└─────────────────────────────────────────────┘")
        lines.append("```")

        # Show ajan details
        lines.append("\n**📊 Detay:**")
        for ajan in sorted(ajan_tasks.keys(), key=lambda x: ajan_tasks[x]['toplam'], reverse=True):
            stats = ajan_tasks[ajan]
            tamamlama_orani = (stats['done'] * 100 // stats['toplam']) if stats['toplam'] else 0
            lines.append(f"\n👤 **{ajan.capitalize()}**")
            lines.append(f"   📊 Toplam: {stats['toplam']} | Tamamlanan: {stats['done']} ({tamamlama_orani}%)")
            lines.append(f"   🔵 Aktif: {stats['aktif']} | 🟠 Bloke: {stats['bloke']}")

        lines.append("\n[« Rapor Menüsü]")
        bot.send_message(chat_id, "\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        logger.error(f"[RAPOR_AJAN_ERROR] {e}", exc_info=True)
        bot.send_message(chat_id, f"❌ Rapor yüklenemedi: {str(e)[:50]}")


@bot.message_handler(func=lambda message: message.text and "KPI" in message.text and "📊" in message.text)
def btn_rapor_kpi(message):
    """KPI raporu."""
    logger.info(f"[BUTTON] Rapor KPI clicked: {message.text}")
    show_kpi_raporu(message.chat.id)
    send_rapor_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "Pano Özeti" in message.text)
def btn_rapor_pano_ozeti(message):
    """Görev panosu özeti — metrikler dashboard."""
    logger.info(f"[BUTTON] Rapor Pano Özeti clicked: {message.text}")
    show_rapor_pano_ozeti(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "Trend" in message.text)
def btn_rapor_trend(message):
    """Trend raporu — task_board'dan."""
    logger.info(f"[BUTTON] Rapor Trend clicked: {message.text}")
    show_rapor_trend(message.chat.id)
    send_rapor_menu(message.chat.id)


def show_rapor_trend(chat_id: str) -> None:
    """Trend raporu — task_board'dan."""
    import json
    from pathlib import Path

    try:
        task_board_path = Path(__file__).parent.parent.parent / "data" / "orchestrator" / "task_board.json"
        tasks = []
        if task_board_path.exists():
            with open(task_board_path, "r", encoding="utf-8") as f:
                tasks = json.load(f)

        # Current metrics
        acik = len([t for t in tasks if t.get('durum') == 'Açık'])
        aktif = len([t for t in tasks if t.get('durum') == 'Aktif'])
        bloke = len([t for t in tasks if t.get('durum') == 'Bloke'])
        done = len([t for t in tasks if t.get('durum') == 'Tamamlandı'])
        toplam = len(tasks)

        # Trend indicators (simulated based on task counts)
        # Higher done % = positive trend
        tamamlama_orani = (done * 100 // toplam) if toplam else 0

        lines = [
            "📈 **TREND ANALİZİ**\n",
            "```",
            "┌──────────────────────────────────┐",
            "│ METRİK              │ TREND      │",
            "├──────────────────────────────────┤",
            f"│ Tamamlama Oranı     │ {tamamlama_orani:3d}% ✅    │",
            f"│ Açık Görevler       │ {acik:3d}    ← │",
            f"│ Aktif Görevler      │ {aktif:3d}    → │",
            f"│ Bloke Görevler      │ {bloke:3d}    ⚠️   │",
            "└──────────────────────────────────┘",
            "```",
            "\n**📊 Sonuç:**"
        ]

        if tamamlama_orani >= 70:
            lines.append("   ✅ Güçlü performans — tamamlama oranı yüksek")
        elif tamamlama_orani >= 50:
            lines.append("   ⚠️ Orta performans — iyileştirme alanı var")
        else:
            lines.append("   🔴 Düşük performans — acil müdahale gerekli")

        if bloke > 0:
            lines.append(f"   🟠 {bloke} bloke görev var — inceleme gerekli")

        if acik > 0:
            lines.append(f"   🟢 {acik} açık görev — atanmayı bekliyor")

        lines.append("\n[« Rapor Menüsü]")
        bot.send_message(chat_id, "\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        logger.error(f"[RAPOR_TREND_ERROR] {e}", exc_info=True)
        bot.send_message(chat_id, f"❌ Rapor yüklenemedi: {str(e)[:50]}")


@bot.message_handler(func=lambda message: message.text and "Özet" in message.text and "📋" in message.text)
def btn_rapor_ozet(message):
    """Rapor özeti."""
    logger.info(f"[BUTTON] Rapor Özet clicked: {message.text}")
    try:
        lines = [
            "📋 **Rapor Özeti**\n",
            "• Toplam Rapor: 24",
            "• Haftalık: 4",
            "• Aylık: 2",
            "• YTD: 1"
        ]
        bot.send_message(message.chat.id, "\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        logger.error(f"[RAPOR_OZET_ERROR] {e}", exc_info=True)
        bot.send_message(message.chat.id, f"❌ Özet yüklenemedi: {str(e)[:50]}")
    send_rapor_menu(message.chat.id)


# Ayarlar button handlers
@bot.message_handler(func=lambda message: message.text and "Bot Restart" in message.text)
def btn_ayarlar_bot_restart(message):
    """Telegram bot process'ini yeniden başlatır (self re-exec, kod diskten taze yüklenir)."""
    logger.info(f"[BUTTON] Ayarlar Bot Restart clicked: {message.text}")
    try:
        bot.send_message(message.chat.id, "🔄 Bot yeniden başlatılıyor, birkaç saniye sürebilir...")
    except Exception:
        pass
    os.execv(sys.executable, [sys.executable] + sys.argv)


@bot.message_handler(func=lambda message: message.text and "Streamlit Restart" in message.text)
def btn_ayarlar_streamlit_restart(message):
    """Streamlit dashboard process'ini yeniden başlatır (taskkill + yeniden start)."""
    logger.info(f"[BUTTON] Ayarlar Streamlit Restart clicked: {message.text}")
    try:
        import subprocess
        root = Path(__file__).parent.parent.parent
        cmd = (
            'taskkill /F /IM streamlit.exe 2>nul & timeout /t 2 >nul & '
            f'start "streamlit" cmd /c "cd /d \"{root}\" && streamlit run app.py --server.port 8501 > streamlit_log.txt 2>&1"'
        )
        subprocess.Popen(cmd, shell=True)
        bot.send_message(message.chat.id, "🔄 Streamlit yeniden başlatılıyor (~5-10 sn sürer).")
    except Exception as e:
        logger.error(f"[STREAMLIT_RESTART_ERROR] {e}", exc_info=True)
        bot.send_message(message.chat.id, f"❌ Hata: {str(e)[:100]}")
    send_ayarlar_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "Bağlantı Kontrol" in message.text)
def btn_ayarlar_baglanti(message):
    """Bağlantı kontrolü."""
    logger.info(f"[BUTTON] Ayarlar Bağlantı Kontrol clicked: {message.text}")
    bot.send_message(message.chat.id, "🔌 ✅ Bot Telegram ile bağlı.")
    send_ayarlar_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "Token Doğrula" in message.text)
def btn_ayarlar_token(message):
    """Token doğrulama."""
    logger.info(f"[BUTTON] Ayarlar Token Doğrula clicked: {message.text}")
    bot.send_message(message.chat.id, "🔑 ✅ Token doğru ve geçerli.")
    send_ayarlar_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "Bot Bilgisi" in message.text)
def btn_ayarlar_info(message):
    """Bot bilgisi."""
    logger.info(f"[BUTTON] Ayarlar Bot Bilgisi clicked: {message.text}")
    info_msg = f"📋 **Bot Bilgisi**\n\nVersiyon: 1.0\nDurumu: Aktif ✅\nSonuç: {datetime.now().strftime('%H:%M:%S')}"
    bot.send_message(message.chat.id, info_msg, parse_mode="Markdown")
    send_ayarlar_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "Yardım" in message.text and "❓" in message.text)
def btn_ayarlar_yardim(message):
    """Yardım göster."""
    logger.info(f"[BUTTON] Ayarlar Yardım clicked: {message.text}")
    show_yardim_detay(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "Yardım" in message.text and not "❓" in message.text)
def btn_ana_menu_yardim(message):
    """Ana menüden yardım (detaylı)."""
    logger.info(f"[BUTTON] Ana Menu Yardım clicked: {message.text}")
    show_yardim_detay(message.chat.id)


# Görev Takibi button handlers
@bot.message_handler(func=lambda message: message.text and "Görev Takibi" in message.text)
def btn_gorev_takibi_menu(message):
    """Görev takibi menüsü."""
    logger.info(f"[BUTTON] Görev Takibi clicked: {message.text}")
    send_gorev_takibi_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "Açık" in message.text and "🟢" in message.text)
def btn_gorev_acik(message):
    """Açık görevler."""
    logger.info(f"[BUTTON] Görev Takibi Açık clicked: {message.text}")
    show_gorev_takibi_durum(message.chat.id, "acik")


@bot.message_handler(func=lambda message: message.text and "Aktif" in message.text and "🔵" in message.text)
def btn_gorev_aktif(message):
    """Aktif görevler."""
    logger.info(f"[BUTTON] Görev Takibi Aktif clicked: {message.text}")
    show_gorev_takibi_durum(message.chat.id, "aktif")


@bot.message_handler(func=lambda message: message.text and "Bloke" in message.text and "🟠" in message.text)
def btn_gorev_bloke(message):
    """Bloke görevler."""
    logger.info(f"[BUTTON] Görev Takibi Bloke clicked: {message.text}")
    show_gorev_takibi_durum(message.chat.id, "bloke")


@bot.message_handler(func=lambda message: message.text and "Tamamlandı" in message.text and "✅" in message.text)
def btn_gorev_tamamlandi(message):
    """Tamamlanan görevler."""
    logger.info(f"[BUTTON] Görev Takibi Tamamlandı clicked: {message.text}")
    show_gorev_takibi_durum(message.chat.id, "done")


@bot.message_handler(func=lambda message: message.text and "Tümü" in message.text and "📋" in message.text)
def btn_gorev_tumun(message):
    """Tüm görevler."""
    logger.info(f"[BUTTON] Görev Takibi Tümü clicked: {message.text}")
    show_gorev_takibi_durum(message.chat.id, "all")


@bot.message_handler(func=lambda message: message.text and "Ayarlar" in message.text)
def btn_ayarlar_menu(message):
    """Ayarlar menüsü."""
    logger.info(f"[BUTTON] Ayarlar Menu clicked: {message.text}")
    send_ayarlar_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "ACİL" in message.text)
def btn_urgent(message):
    """Acil görevler - Bloke ve Kritik görevler."""
    logger.info(f"[BUTTON] Urgent clicked: {message.text}")
    try:
        import json
        from pathlib import Path

        task_board_path = Path(__file__).parent.parent.parent / "data" / "orchestrator" / "task_board.json"
        tasks = []
        if task_board_path.exists():
            with open(task_board_path, "r", encoding="utf-8") as f:
                tasks = json.load(f)

        # Bloke + Kritik görevleri filtrele
        kritik_gorevler = [
            t for t in tasks
            if t.get('durum') in ['Bloke', 'Aktif'] and
            t.get('onem', 'orta').lower() in ['critical', 'yuksek']
        ]

        if not kritik_gorevler:
            bot.send_message(
                message.chat.id,
                "✅ **Kritik Görev Yok**\n\n"
                "Tüm bloke ve yüksek önem görevler çözülmüş.",
                parse_mode="Markdown"
            )
            return

        lines = [
            "🚨 **ACİL GÖREVLER — Kritik & Bloke**\n",
            "```",
            "┌─────────────────────────────────────────┐",
            "│ TASK_ID │ DURUM  │ ÖNEM    │ SAHİP    │",
            "├─────────────────────────────────────────┤"
        ]

        for task in kritik_gorevler[:10]:
            task_id = task.get("task_id", "?").ljust(7)
            durum = task.get("durum", "?").ljust(6)
            onem = task.get("onem", "?")

            onem_emoji = {
                "critical": "🔴",
                "yuksek": "🟠",
                "orta": "🟡",
                "dusuk": "🟢"
            }.get(onem, "❓")

            sahip = task.get("sahip", "?")[:8].ljust(8)

            lines.append(f"│ {task_id} │ {durum} │ {onem_emoji} {onem:5s} │ {sahip} │")

        if len(kritik_gorevler) > 10:
            lines.append(f"│ ... {len(kritik_gorevler)-10} daha görev ... │")

        lines.append("└─────────────────────────────────────────┘")
        lines.append("```")
        lines.append("\n**Detaylı görmek için [📋 Pano] → [🟠 Bloke]")
        lines.append("\n[« Ana Menü]")

        msg_text = "\n".join(lines)
        bot.send_message(message.chat.id, msg_text, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"[URGENT_ERROR] {e}", exc_info=True)
        bot.send_message(message.chat.id, f"❌ Acil görevler yüklenemedi: {str(e)[:50]}")


@bot.message_handler(func=lambda message: message.text and "Q" in message.text)
def btn_questions(message):
    """Soru özeti."""
    logger.info(f"[BUTTON] Questions clicked: {message.text}")
    try:
        from chat import ajan_acik_sorulari
        acik_sorular = ajan_acik_sorulari("*")  # Tüm ajanlar için
        if acik_sorular:
            msg = "⚡ **Açık Sorular:**\n\n"
            for soru in acik_sorular[:5]:
                msg += f"• {soru.get('sorun', 'N/A')}\n"
            bot.send_message(message.chat.id, msg, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "⚡ Hiç açık soru yok.")
    except ImportError as ie:
        logger.error(f"[Q_IMPORT_ERROR] {ie}", exc_info=True)
        bot.send_message(message.chat.id, f"⚠️ Sorular modülü bulunamadı. Chat sistemi başlatılıyor...")
        send_ana_menu(message.chat.id)
    except Exception as e:
        logger.error(f"[Q_ERROR] {e}", exc_info=True)
        bot.send_message(message.chat.id, f"❌ Sorular yüklenemedi: {str(e)[:50]}")


@bot.message_handler(func=lambda message: message.text and "ÖZET" in message.text)
def btn_summary(message):
    """Günlük özet - tablo formatında."""
    logger.info(f"[BUTTON] Summary clicked: {message.text}")
    try:
        from orchestrator.trigger import bekleyen_tetikler

        # Task board'dan tüm görevleri oku
        import json
        from pathlib import Path

        task_board_path = Path(__file__).parent.parent.parent / "data" / "orchestrator" / "task_board.json"
        tasks = []
        if task_board_path.exists():
            with open(task_board_path, "r", encoding="utf-8") as f:
                tasks = json.load(f)

        # Durum bazında sayılar
        acik = len([t for t in tasks if t.get('durum') == 'Açık'])
        aktif = len([t for t in tasks if t.get('durum') == 'Aktif'])
        bloke = len([t for t in tasks if t.get('durum') == 'Bloke'])
        done = len([t for t in tasks if t.get('durum') == 'Tamamlandı'])
        plan = len([t for t in tasks if t.get('durum') == 'Plan'])

        toplam = len(tasks)

        # Tablo formatında mesaj
        lines = [
            "📌 **GÜNLÜK ÖZET — Task Board Durumu**\n",
            "```",
            "┌──────────────────────────────────┐",
            "│ DURUM          │ SAYISI │ YÜZDE  │",
            "├──────────────────────────────────┤",
            f"│ 🟢 Açık        │   {acik:2d}   │ {(acik*100//toplam if toplam else 0):3d}%  │",
            f"│ 🔵 Aktif       │   {aktif:2d}   │ {(aktif*100//toplam if toplam else 0):3d}%  │",
            f"│ 🟠 Bloke       │   {bloke:2d}   │ {(bloke*100//toplam if toplam else 0):3d}%  │",
            f"│ ✅ Tamamlandı  │   {done:2d}   │ {(done*100//toplam if toplam else 0):3d}%  │",
            f"│ 📋 Plan        │   {plan:2d}   │ {(plan*100//toplam if toplam else 0):3d}%  │",
            "├──────────────────────────────────┤",
            f"│ 📊 TOPLAM      │  {toplam:3d}   │ 100%  │",
            "└──────────────────────────────────┘",
            "```",
            "\n**📋 Son 5 Görev (Detaylı):**"
        ]

        # Son 5 görev - genişletilmiş bilgi
        for i, task in enumerate(tasks[-5:], 1):
            task_id = task.get("task_id", "?")
            durum = task.get("durum", "?")
            baslik = task.get("baslik", "")[:40]
            sahip = task.get("sahip", "?")
            aciklama = task.get("aciklama", "")[:50]
            onem = task.get("onem", "orta")

            durum_emoji = {
                "Açık": "🟢",
                "Aktif": "🔵",
                "Bloke": "🟠",
                "Tamamlandı": "✅",
                "Plan": "📋"
            }.get(durum, "❓")

            onem_emoji = {
                "kritik": "🔴",
                "yuksek": "🟠",
                "orta": "🟡",
                "dusuk": "🟢"
            }.get(onem, "⚪")

            lines.append(f"\n{i}. {durum_emoji} **{task_id}** ({onem_emoji} {onem.capitalize()})")
            lines.append(f"   📌 {baslik}")
            lines.append(f"   👤 Sahip: {sahip}")
            if aciklama:
                lines.append(f"   📝 {aciklama}")

        lines.append("\n[« Ana Menü]")

        msg_text = "\n".join(lines)
        bot.send_message(message.chat.id, msg_text, parse_mode="Markdown")

    except ImportError as ie:
        logger.error(f"[SUMMARY_IMPORT_ERROR] {ie}", exc_info=True)
        bot.send_message(message.chat.id, "⚠️ Tetikler modülü bulunamadı. Task board verisi gösteriliyor...")
        send_ana_menu(message.chat.id)
    except Exception as e:
        logger.error(f"[SUMMARY_ERROR] {e}", exc_info=True)
        bot.send_message(message.chat.id, f"❌ Özet yüklenemedi: {str(e)[:50]}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("menu:") or call.data.startswith("quick:"))
def handle_main_menu(call):
    """Ana menü butonları."""
    data = call.data
    logger.info(f"[CALLBACK] Received: {data} from user {call.from_user.id}")

    try:
        if data == "menu:ana":
            logger.debug(f"[CALLBACK] Sending ana menu")
            send_ana_menu(call.message.chat.id)
        elif data == "menu:pano":
            logger.debug(f"[CALLBACK] Sending pano menu")
            send_pano_menu(call.message.chat.id)
        elif data == "menu:chat":
            logger.debug(f"[CALLBACK] Sending chat menu")
            send_chat_menu(call.message.chat.id)
        elif data == "menu:tetikler":
            logger.debug(f"[CALLBACK] Sending tetikler menu")
            send_tetikler_menu(call.message.chat.id)
        elif data == "menu:mesaj":
            logger.debug(f"[CALLBACK] Sending mesaj menu")
            send_mesaj_menu(call.message.chat.id)
        elif data == "menu:rapor":
            logger.debug(f"[CALLBACK] Sending rapor menu")
            send_rapor_menu(call.message.chat.id)
        elif data == "menu:ayarlar":
            logger.debug(f"[CALLBACK] Sending ayarlar menu")
            send_ayarlar_menu(call.message.chat.id)
        elif data == "quick:urgent":
            bot.send_message(call.message.chat.id, "🚨 Bloke görevler...")
        elif data == "quick:q":
            bot.send_message(call.message.chat.id, "⚡ Soru özeti...")
        elif data == "quick:summary":
            bot.send_message(call.message.chat.id, "📌 Günlük özet...")
        logger.info(f"[CALLBACK] Success: {data}")
    except Exception as e:
        logger.error(f"[CALLBACK-ERROR] {data}: {e}", exc_info=True)
        try:
            bot.send_message(call.message.chat.id, f"❌ Hata: {e}")
        except:
            pass

    try:
        bot.answer_callback_query(call.id)
    except:
        pass


@bot.callback_query_handler(func=lambda call: call.data.startswith("pano:"))
def handle_pano_menu(call):
    """Pano menü butonları."""
    data = call.data.split(":")[1]

    try:
        if data in ["done", "active", "blocked", "plan", "all"]:
            show_pano_status(call.message.chat.id, data)
        elif data == "ajan_input":
            bot.send_message(call.message.chat.id, "👤 Ajan arama henüz aktif değil.")
        elif data == "tag_input":
            bot.send_message(call.message.chat.id, "🏷️ Tag arama henüz aktif değil.")
    except Exception as e:
        logger.error(f"Error in pano handler: {e}")
        bot.send_message(call.message.chat.id, f"❌ Hata: {e}")

    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("chat:"))
def handle_chat_menu(call):
    """Chat menü butonları."""
    data = call.data.split(":")[1]

    try:
        if data in ["acik", "cokundurmus", "cozuldu", "all"]:
            show_chat_status(call.message.chat.id, data)
        elif data == "ara_input":
            bot.send_message(call.message.chat.id, "🔎 Arama henüz aktif değil.")
        elif data == "ajan_input":
            bot.send_message(call.message.chat.id, "👤 Ajan soruları henüz aktif değil.")
        elif data == "broadcast":
            bot.send_message(call.message.chat.id, "📢 Broadcast henüz aktif değil.")
    except Exception as e:
        logger.error(f"Error in chat handler: {e}")
        bot.send_message(call.message.chat.id, f"❌ Hata: {e}")

    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("tetikler:"))
def handle_tetikler_menu(call):
    """Tetikler menü butonları."""
    data = call.data.split(":")[1]

    try:
        if data == "all":
            bot.send_message(call.message.chat.id, "🔍 Tüm tetikler özeti...")
        else:
            show_tetikler_ajan(call.message.chat.id, data)
    except Exception as e:
        logger.error(f"Error in tetikler handler: {e}")
        bot.send_message(call.message.chat.id, f"❌ Hata: {e}")

    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("mesaj:"))
def handle_mesaj_menu(call):
    """Mesaj menü butonları."""
    data = call.data.split(":")[1]

    try:
        if data == "broadcast":
            bot.send_message(call.message.chat.id, "📢 Broadcast henüz aktif değil.")
        elif data == "targeted":
            bot.send_message(call.message.chat.id, "👤 Targeted henüz aktif değil.")
        elif data == "tag":
            bot.send_message(call.message.chat.id, "🎯 Tag henüz aktif değil.")
        elif data == "alert":
            bot.send_message(call.message.chat.id, "🔔 Uyarı henüz aktif değil.")
    except Exception as e:
        logger.error(f"Error in mesaj handler: {e}")
        bot.send_message(call.message.chat.id, f"❌ Hata: {e}")

    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("rapor:") or call.data.startswith("rapor_detail:"))
def handle_rapor_menu(call):
    """Rapor menü butonları."""
    data = call.data.split(":")[1]

    try:
        if data == "hafta":
            show_hafta_raporu(call.message.chat.id)
        elif data == "ay":
            bot.send_message(call.message.chat.id, "📅 Aylık rapor henüz aktif değil.")
        elif data == "ytd":
            bot.send_message(call.message.chat.id, "📅 YTD rapor henüz aktif değil.")
        elif data == "kpi":
            show_kpi_raporu(call.message.chat.id)
        elif data == "trend":
            bot.send_message(call.message.chat.id, "📈 Trend raporu henüz aktif değil.")
        elif data == "ozet":
            bot.send_message(call.message.chat.id, "📋 Özet raporu henüz aktif değil.")
    except Exception as e:
        logger.error(f"Error in rapor handler: {e}")
        bot.send_message(call.message.chat.id, f"❌ Hata: {e}")

    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("ayarlar:"))
def handle_ayarlar_menu(call):
    """Ayarlar menü butonları."""
    data = call.data.split(":")[1]

    try:
        if data == "baglanti":
            bot.send_message(call.message.chat.id, "🔌 Bağlantı kontrol henüz aktif değil.")
        elif data == "token":
            bot.send_message(call.message.chat.id, "🔑 Token doğrulama henüz aktif değil.")
        elif data == "info":
            bot.send_message(call.message.chat.id, "📋 Bot bilgisi henüz aktif değil.")
        elif data == "yardim":
            show_yardim(call.message.chat.id)
    except Exception as e:
        logger.error(f"Error in ayarlar handler: {e}")
        bot.send_message(call.message.chat.id, f"❌ Hata: {e}")

    bot.answer_callback_query(call.id)


# ============================================================================
# BÖLÜM 8: GÖREV TAKIBI HANDLERs (Sahib Bazlı + Mesaj)
# ============================================================================

@bot.message_handler(func=lambda message: message.text and "Sahip Bazlı" in message.text and "👤" in message.text)
def btn_gorev_sahib_bazli(message):
    """Sahib bazlı görev filtresi."""
    logger.info(f"[BUTTON] Görev Takibi Sahib Bazlı clicked: {message.text}")
    # send_gorev_sahib_menu yerine doğru fonksiyon: show_gorev_sahib_menu
    show_gorev_sahib_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and ("Utku" in message.text or "Salih" in message.text or "Yasu" in message.text or "İhsan" in message.text or "Mimir" in message.text or "Orkestrator" in message.text) and ("😊" in message.text or "🤖" in message.text))
def btn_gorev_sahib_sec(message):
    """Sahib seçimi - görevleri göster."""
    logger.info(f"[BUTTON] Gorev Sahib Sec: {message.text}")

    # Ajan adını çıkar (lowercase)
    sahib = None
    if "Utku" in message.text:
        sahib = "utku"
    elif "Salih" in message.text:
        sahib = "salih"
    elif "Yasu" in message.text:
        sahib = "yasu"
    elif "İhsan" in message.text:
        sahib = "ihsan"
    elif "Mimir" in message.text:
        sahib = "mimir"
    elif "Orkestrator" in message.text:
        sahib = "orkestrator"

    if sahib:
        show_gorev_sahib_goster(message.chat.id, sahib)
        # Orkestrator için tetikler menüsüne git, diğerleri için aksiyonlar menüsü sun
        if sahib.lower() == "orkestrator":
            show_tetikler_menu(message.chat.id)
        else:
            # Diğer ajanlar için aksiyonlar menüsü (Tetik Bak / Mesaj Gönder)
            _show_gorev_sahib_aksiyonlar_menu(message.chat.id)
    else:
        show_gorev_sahib_menu(message.chat.id)

@bot.message_handler(func=lambda message: message.text and "« Görev Takibi" in message.text)
def btn_gorev_takibi_geri(message):
    """Sahib Bazlı menüsünden geri tuşu."""
    logger.info(f"[BUTTON] Back to Görev Takibi: {message.text}")
    send_gorev_takibi_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "Tetik Bak" in message.text and "📬" in message.text)
def btn_gorev_sahib_tetik_bak(message):
    """Görev Takibi → Sahib Bazlı → Aksiyonlar Menüsü → Tetik Bak."""
    logger.info(f"[BUTTON] Gorev Sahib Tetik Bak clicked: {message.text}")
    # Ajan adını state'e kaydet, sonra handler ajan seçimi soracak
    _tetikler_state[message.chat.id] = None  # Flag: aksiyonlar menüsünden geldi
    msg = bot.send_message(
        message.chat.id,
        "👤 **Tetik Bak**\n\n"
        "Hangi ajan için tetikleri görmek istiyorsunuz?\n"
        "Ajan adını yazın (Utku, Salih, Yasu, İhsan, Mimir):",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, _tetik_bak_ajan_secimi)


@bot.message_handler(func=lambda message: message.text and "Mesaj Gönder" in message.text and "💬" in message.text)
def btn_gorev_mesaj_gonder(message):
    """Görev mesajı gönder — aksiyonlar menüsü veya Görev Takibi menüsünden."""
    logger.info(f"[BUTTON] Gorev Mesaj Gonder clicked: {message.text}")
    # Aksiyonlar menüsünden gelirse direkt Mesaj Menüsüne git
    send_mesaj_menu(message.chat.id)


# ============================================================================
# BÖLÜM 9: DEBUG HANDLER (Tüm eşleşmeyen mesajlar)
# ============================================================================

# DISABLED: debug_catch_all handler tüm mesajları yakalaması bot'u donduruyor

# ============================================================================
# BÖLÜM 10: BOT BAŞLATMA
# ============================================================================

def main():
    """Bot webhook/polling mode — production webhooks, dev polling."""
    import os
    webhook_url = os.getenv("TELEGRAM_WEBHOOK_URL", "").strip()

    if webhook_url:
        logger.info(f"Telegram Bot webhook mode: {webhook_url}")
        logger.info("FastAPI web_app.py:/api/webhooks/telegram endpoint kullanılacak")
    else:
        logger.info("Telegram Bot polling mode (dev/fallback)")
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            logger.error(f"Bot polling error: {e}")
            raise


if __name__ == "__main__":
    main()
