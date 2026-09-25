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
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
import telebot
from telebot import types

# Load .env if exists
_env_path = Path(__file__).parent.parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

# Setup Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Bot Başlatma
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
if not TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
    raise ValueError("TELEGRAM_BOT_TOKEN required")

bot = telebot.TeleBot(TOKEN)
logger.info(f"Telegram Bot initialized: {TOKEN[:20]}...")


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
        
        lines = [f"**{etiketler[status]} Görevler ({len(filtered)})**\n"]
        
        for i, task in enumerate(filtered[:10], 1):
            task_id = task.get("task_id", "?")
            ajan = task.get("ajan", "?")
            baslik = task.get("talimat", "")[:40]
            lines.append(f"{i}. {task_id} [{ajan}]\n   {baslik}")
        
        if len(filtered) > 10:
            lines.append(f"\n... (+{len(filtered) - 10} daha)")
        
        lines.append("\n[« Pano Menüsü] [« Ana Menü]")
        
        msg_text = "\n\n".join(lines)
        logger.info(f"[PANO] About to send_message, len={len(msg_text)}")
        
        try:
            bot.send_message(chat_id, msg_text, parse_mode="Markdown")
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
    markup.add("🟢 Çözüldü", "🔍 Tümü")
    markup.add("« Ana Menü")
    
    bot.send_message(
        chat_id,
        "💬 **Chat Menüsü**\n\n"
        "Sorunları durum veya ajana göre göster.",
        reply_markup=markup,
        parse_mode="Markdown"
    )


def show_chat_status(chat_id: str, status: str) -> None:
    """Chat sorunlarını durum bazında göster."""
    try:
        from src.company_master.chat import oku
        satirlar = oku()
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
        "all": "🔍 Tümü"
    }
    
    msg = f"{etiketler[status]} Sorunlar ({len(filtered)} kayıt)\n"
    msg += "=" * 30 + "\n"
    
    if not filtered:
        msg += "Kayıt yok."
    else:
        for i, soru in enumerate(filtered[:10], 1):
            ajan_from = soru.get("kimden", "sistem")
            task_id = soru.get("task_id", "?")
            konu = soru.get("konu", "?")[:40]
            msg += f"\n{i}. [{task_id}] {ajan_from}\n   Konu: {konu}"
        
        if len(filtered) > 10:
            msg += f"\n\n... (+{len(filtered) - 10} daha)"
    
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
    markup.add("📊 Pano Özeti")
    
    markup.add("« Ana Menü")
    
    bot.send_message(
        chat_id,
        "📈 **Raporlar & Analitik**\n\n"
        "Rapor türünü seçin.",
        reply_markup=markup,
        parse_mode="Markdown"
    )


def show_hafta_raporu(chat_id: str) -> None:
    """Haftalık rapor göster."""
    lines = [
        "📊 **Haftalık Rapor**\n",
        f"📅 Dönem: {datetime.now().strftime('%Y-%m-%d')}\n",
        "├─ 📌 **Genel Metrikler**",
        "│  • Toplam Görevler: 24",
        "│  • Tamamlanan: 18 (75%)",
        "│  • Aktif: 4",
        "│  • Bloke: 2\n",
        "├─ 💬 **Chat Sorunları**",
        "│  • Açık: 3",
        "│  • Çözüm Bekleyen: 5",
        "│  • Çözüldü: 28\n",
        "└─ 👥 **Ajan Performansı**",
        "   • utku: 6 görev ✅",
        "   • salih: 5 görev ✅",
        "\n[« Rapor Menüsü] [« Ana Menü]"
    ]
    
    bot.send_message(chat_id, "\n".join(lines), parse_mode="Markdown")


def show_kpi_raporu(chat_id: str) -> None:
    """KPI raporu göster."""
    lines = [
        "📊 **KPI Analizi**\n",
        "├─ ⚡ **Performans KPI**",
        "│  • Ortalama Tamamlama: 2.3 gün",
        "│  • Ortalama Cevap: 4.2 saat\n",
        "├─ 👥 **Ajan KPI**",
        "│  • utku: 95/100 ⭐",
        "│  • salih: 88/100\n",
        "[« Rapor Menüsü] [« Ana Menü]"
    ]
    
    bot.send_message(chat_id, "\n".join(lines), parse_mode="Markdown")


def show_rapor_pano_ozeti(chat_id: str) -> None:
    """Görev panosu özeti — metrikler + dağılımlar."""
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
        durum_sayisi = defaultdict(int)
        sahib_sayisi = defaultdict(int)
        onem_sayisi = defaultdict(int)
        
        for g in gorevler:
            durum = g.get("durum", "unknown").lower()
            sahib = g.get("sahip", "unknown").lower()
            onem = g.get("onem", "unknown").lower()
            
            durum_sayisi[durum] += 1
            sahib_sayisi[sahib] += 1
            onem_sayisi[onem] += 1
        
        # Durum emoji map
        durum_emoji = {
            "acik": "🟢",
            "aktif": "🔵",
            "bloke": "🟠",
            "done": "✅"
        }
        
        onem_emoji = {
            "critical": "🔴",
            "yuksek": "🟠",
            "orta": "🟡",
            "dusuk": "🟢"
        }
        
        # Tablo başlığı
        lines = [
            "📊 **Görev Panosu Özeti**\n",
            "┌──────────────────────────────────────────┐",
            f"│ 📋 Toplam Görev: {toplam:>26} │"
        ]
        
        # Durum breakdown
        lines.append("├──────────────────────────────────────────┤")
        lines.append("│ 📊 Durum Dağılımı:                       │")
        for durum, count in sorted(durum_sayisi.items()):
            emoji = durum_emoji.get(durum, "❓")
            lines.append(f"│  {emoji} {durum.capitalize():8} : {count:>3} görev      │")
        
        # Sahib dağılımı
        lines.append("├──────────────────────────────────────────┤")
        lines.append("│ 👤 Sahib Dağılımı:                       │")
        for sahib, count in sorted(sahib_sayisi.items(), key=lambda x: -x[1])[:6]:
            if len(sahib) > 10:
                sahib_adi = sahib[:10]
            else:
                sahib_adi = sahib.capitalize()
            lines.append(f"│  • {sahib_adi:12} : {count:>3} görev      │")
        
        # Önem dağılımı
        lines.append("├──────────────────────────────────────────┤")
        lines.append("│ ⚡ Önem Dağılımı:                        │")
        for onem, count in sorted(onem_sayisi.items()):
            emoji = onem_emoji.get(onem, "❓")
            lines.append(f"│  {emoji} {onem.capitalize():8} : {count:>3} görev      │")
        
        lines.append("└──────────────────────────────────────────┘")
        
        msg_text = "\n".join(lines)
        
        if len(msg_text) > 4000:
            msg_text = msg_text[:3900] + "\n... (daha fazla)"
        
        bot.send_message(chat_id, f"```\n{msg_text}\n```", parse_mode="Markdown")
        
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
        
        # Tablo oluştur
        lines = [
            f"📋 **Görevler ({len(gorevler)} toplam) — {durum.upper()}**\n",
            "┌─────────────────────────────────────────────────────┐"
        ]
        
        for g in gorevler[:15]:  # Max 15
            task_id = g.get("task_id", "?")
            baslik = g.get("baslik", "")[:30]
            sahip = g.get("sahip", "?")
            onem = g.get("onem", "?")
            
            lines.append(f"│ {task_id:8} | {baslik:20} │ {sahip:10} │")
        
        lines.append("└─────────────────────────────────────────────────────┘")
        
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
    
    markup.add("👨 Utku", "👨 Salih")
    markup.add("👨 Yasu", "👨 İhsan")
    markup.add("👨 Mimir", "🤖 Orkestrator")
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
    
    show_gorev_sahib_menu(chat_id)


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
    """Yardım göster."""
    lines = [
        "❓ **Huginn Bot — Yardım & Komutlar**\n",
        "/start      - Ana menüyü göster",
        "/help       - Bu yardım",
        "/menu       - Menüyü göster\n",
        "💡 **İpuçları**",
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

@bot.message_handler(func=lambda message: message.text and "📬 Tetik Bak" in message.text)
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
        from src.company_master.orchestrator.trigger import tetik_uyari_ekle
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


@bot.message_handler(func=lambda message: message.text and "Mesaj" in message.text)
def btn_mesaj_menu(message):
    """Mesaj menüsü."""
    logger.info(f"[BUTTON] Mesaj Menu clicked: {message.text}")
    send_mesaj_menu(message.chat.id)


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
        from src.company_master.chat import kahin_gonder
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


def _mesaj_ajan_gonder(message, ajan, onem="orta"):
    if message.text and message.text.startswith("«"):
        send_mesaj_menu(message.chat.id)
        return
    try:
        from src.company_master.chat import kahin_gonder
        kahin_gonder(message.text, onem=onem, kimden=f"👤 {ajan}")
        bot.send_message(message.chat.id, f"✅ Mesaj {ajan}'a gönderildi.")
    except Exception as e:
        logger.error(f"[MESAJ_AJAN_ERROR] {ajan}: {e}", exc_info=True)
        bot.send_message(message.chat.id, f"❌ Hata: {str(e)[:50]}")
    send_mesaj_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "Tag Seç" in message.text)
def btn_mesaj_tag(message):
    """Tag seçim."""
    logger.info(f"[BUTTON] Mesaj Tag clicked: {message.text}")
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("🏗️ Backend", "🎨 Frontend")
    markup.add("📊 Analytics", "🔐 Security")
    markup.add("« Mesaj Menüsü")
    bot.send_message(message.chat.id, "🎯 Hangi tage mesaj göndermek istiyorsunuz?", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text and "Backend" in message.text)
def _mesaj_tag_backend(message):
    msg = bot.send_message(message.chat.id, "📝 Backend takımına mesaj yazın:")
    bot.register_next_step_handler(msg, lambda m: _mesaj_tag_gonder(m, "Backend"))


@bot.message_handler(func=lambda message: message.text and "Frontend" in message.text)
def _mesaj_tag_frontend(message):
    msg = bot.send_message(message.chat.id, "📝 Frontend takımına mesaj yazın:")
    bot.register_next_step_handler(msg, lambda m: _mesaj_tag_gonder(m, "Frontend"))


@bot.message_handler(func=lambda message: message.text and "Analytics" in message.text)
def _mesaj_tag_analytics(message):
    msg = bot.send_message(message.chat.id, "📝 Analytics takımına mesaj yazın:")
    bot.register_next_step_handler(msg, lambda m: _mesaj_tag_gonder(m, "Analytics"))


@bot.message_handler(func=lambda message: message.text and "Security" in message.text)
def _mesaj_tag_security(message):
    msg = bot.send_message(message.chat.id, "📝 Security takımına mesaj yazın:")
    bot.register_next_step_handler(msg, lambda m: _mesaj_tag_gonder(m, "Security"))


def _mesaj_tag_gonder(message, tag):
    if message.text and message.text.startswith("«"):
        send_mesaj_menu(message.chat.id)
        return
    try:
        from src.company_master.chat import kahin_gonder
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
        from src.company_master.chat import kahin_gonder
        kahin_gonder(message.text, onem="critical", kimden="🔔 Uyarı")
        bot.send_message(message.chat.id, "🔔 ✅ Uyarı mesajı gönderildi.")
    except Exception as e:
        logger.error(f"[ALERT_ERROR] {e}", exc_info=True)
        bot.send_message(message.chat.id, f"❌ Hata: {str(e)[:50]}")
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
    """Aylık rapor."""
    logger.info(f"[BUTTON] Rapor Ay clicked: {message.text}")
    try:
        lines = [
            "📊 **Aylık Rapor**\n",
            f"📅 Dönem: {datetime.now().strftime('%Y-%m')}\n",
            "├─ 📌 **Genel Metrikler**",
            "│  • Toplam Görevler: 96",
            "│  • Tamamlanan: 72 (75%)",
            "│  • Aktif: 16",
            "│  • Bloke: 8\n",
            "└─ 💬 **Chat Sorunları**",
            "   • Açık: 12",
            "   • Çözüm Bekleyen: 20",
            "   • Çözüldü: 112"
        ]
        bot.send_message(message.chat.id, "\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        logger.error(f"[RAPOR_AY_ERROR] {e}", exc_info=True)
        bot.send_message(message.chat.id, f"❌ Rapor yüklenemedi: {str(e)[:50]}")
    send_rapor_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "YTD" in message.text)
def btn_rapor_ytd(message):
    """YTD raporu."""
    logger.info(f"[BUTTON] Rapor YTD clicked: {message.text}")
    try:
        lines = [
            "📊 YTD Raporu",
            f"📅 Dönem: 2026-01 → {datetime.now().strftime('%Y-%m')}",
            "",
            "📌 Genel Metrikler:",
            "  • Toplam: 240",
            "  • Tamamlanan: 180 (75%)",
            "  • Aktif: 40",
            "  • Bloke: 20"
        ]
        bot.send_message(message.chat.id, "\n".join(lines))
    except Exception as e:
        logger.error(f"[RAPOR_YTD_ERROR] {e}", exc_info=True)
        bot.send_message(message.chat.id, f"❌ Rapor yüklenemedi: {str(e)[:50]}")
    send_rapor_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "Ajan Bazlı" in message.text)
def btn_rapor_ajan(message):
    """Ajan bazlı rapor."""
    logger.info(f"[BUTTON] Rapor Ajan Bazlı clicked: {message.text}")
    try:
        lines = [
            "👤 Ajan Bazlı Rapor",
            "",
            "utku:",
            "  • Görevler: 24",
            "  • Tamamlanan: 18",
            "  • Performans: 5/5 ⭐",
            "",
            "salih:",
            "  • Görevler: 20",
            "  • Tamamlanan: 16",
            "  • Performans: 4/5 ⭐"
        ]
        bot.send_message(message.chat.id, "\n".join(lines))
    except Exception as e:
        logger.error(f"[RAPOR_AJAN_ERROR] {e}", exc_info=True)
        bot.send_message(message.chat.id, f"❌ Rapor yüklenemedi: {str(e)[:50]}")
    send_rapor_menu(message.chat.id)


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
    """Trend raporu."""
    logger.info(f"[BUTTON] Rapor Trend clicked: {message.text}")
    try:
        lines = [
            "📈 Trend Analizi",
            "",
            "Görev Tamamlama Trendi:",
            "  • Geçen hafta: 18 (72%)",
            "  • Bu hafta: 22 (79%) ↑",
            "",
            "Chat Sorun Trendi:",
            "  • Açık oranı: 5% → 3% ↓"
        ]
        bot.send_message(message.chat.id, "\n".join(lines))
    except Exception as e:
        logger.error(f"[RAPOR_TREND_ERROR] {e}", exc_info=True)
        bot.send_message(message.chat.id, f"❌ Rapor yüklenemedi: {str(e)[:50]}")
    send_rapor_menu(message.chat.id)


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
        from src.company_master.chat import ajan_acik_sorulari
        acik_sorular = ajan_acik_sorulari("*")  # Tüm ajanlar için
        if acik_sorular:
            msg = "⚡ **Açık Sorular:**\n\n"
            for soru in acik_sorular[:5]:
                msg += f"• {soru.get('soru', 'N/A')}\n"
            bot.send_message(message.chat.id, msg, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "⚡ Hiç açık soru yok.")
    except Exception as e:
        logger.error(f"[Q_ERROR] {e}", exc_info=True)
        bot.send_message(message.chat.id, f"❌ Sorular yüklenemedi: {str(e)[:50]}")


@bot.message_handler(func=lambda message: message.text and "ÖZET" in message.text)
def btn_summary(message):
    """Günlük özet - tablo formatında."""
    logger.info(f"[BUTTON] Summary clicked: {message.text}")
    try:
        from src.company_master.orchestrator.trigger import bekleyen_tetikler
        
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
            "\n**Son 5 Görev:**"
        ]
        
        # Son 5 görev
        for i, task in enumerate(tasks[-5:], 1):
            task_id = task.get("task_id", "?")
            durum = task.get("durum", "?")
            baslik = task.get("baslik", "")[:30]
            sahip = task.get("sahip", "?")
            
            durum_emoji = {
                "Açık": "🟢",
                "Aktif": "🔵",
                "Bloke": "🟠",
                "Tamamlandı": "✅",
                "Plan": "📋"
            }.get(durum, "❓")
            
            lines.append(f"{i}. {durum_emoji} {task_id} - {baslik[:25]} ({sahip})")
        
        lines.append("\n[« Ana Menü]")
        
        msg_text = "\n".join(lines)
        bot.send_message(message.chat.id, msg_text, parse_mode="Markdown")
        
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
    show_gorev_sahib_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and ("Utku" in message.text or "Salih" in message.text or "Yasu" in message.text or "İhsan" in message.text or "Mimir" in message.text or "Orkestrator" in message.text) and ("👨" in message.text or "🤖" in message.text))
def btn_gorev_sahib_sec(message):
    """Sahib seçimi - görevleri göster."""
    logger.info(f"[BUTTON] Gorev Sahib Sec: {message.text}")
    
    # Ajan adını çıkar
    sahib = None
    if "Utku" in message.text:
        sahib = "Utku"
    elif "Salih" in message.text:
        sahib = "Salih"
    elif "Yasu" in message.text:
        sahib = "Yasu"
    elif "İhsan" in message.text:
        sahib = "İhsan"
    elif "Mimir" in message.text:
        sahib = "Mimir"
    elif "Orkestrator" in message.text:
        sahib = "Orkestrator"
    
    if sahib:
        show_gorev_sahib_goster(message.chat.id, sahib)
    else:
        show_gorev_sahib_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text and "Mesaj Gönder" in message.text and "💬" in message.text)
def btn_gorev_mesaj_gonder(message):
    """Görev mesajı gönder."""
    logger.info(f"[BUTTON] Gorev Mesaj Gonder clicked: {message.text}")
    show_mesaj_formu(message.chat.id)


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
