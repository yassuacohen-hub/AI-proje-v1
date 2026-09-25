# D-216: Telegram Menü — 💬 CHAT MENÜSÜ

## Görüntü

```
╔═════════════════════════════════╗
║  💬 Chat Menüsü                ║
╚═════════════════════════════════╝

┌─ SORUN DURUMU ────────────────────┐
│ [🔴 Açık]       [🟡 Çözüm Bekl.]  │
│ [🟢 Çözüldü]    [🔍 Tümü]        │
└────────────────────────────────────┘

┌─ SORGU ───────────────────────────┐
│ [🔎 Arama]     [👤 Ajan Sorusu]   │
└────────────────────────────────────┘

┌─ İŞLEM ───────────────────────────┐
│ [📢 Broadcast Mesaj]              │
└────────────────────────────────────┘

[« Ana Menü]
```

## Durum Tanımları

| Durum | Buton | callback_data | Anlamı |
|-------|-------|---------------|--------|
| Açık | 🔴 Açık | `chat:acik` | Cevap beklenen sorular |
| Çözüm Bekl. | 🟡 Çözüm Bekl. | `chat:cokundurmus` | Çözüm bekleyen sorular |
| Çözüldü | 🟢 Çözüldü | `chat:cozuldu` | Kapalı sorular |
| Tümü | 🔍 Tümü | `chat:all` | Tüm sorunlar |
| Arama | 🔎 Arama | `chat:ara_input` | Prompt: arama terimi sor |
| Ajan Sorusu | 👤 Ajan Sorusu | `chat:ajan_input` | Prompt: ajan adı sor |
| Broadcast | 📢 Broadcast Mesaj | `chat:broadcast` | KAHİN mesajı gönder |

## Çıkış Örneği (🔴 Açık)

```
🔴 Açık Sorunlar (8)

📅 Tarih Aralığı: 2026-09-24 → 2026-09-25

1️⃣ utku → yasu | API-12
   Sorun: "Token expire kontrolü ne zaman?"
   ⏰ 15:30 (4s önce)
   
2️⃣ salih → ihsan | UI-5
   Sorun: "Tema renkleri uyumlu mu?"
   ⏰ 14:15 (2s önce)
   
3️⃣ yasu → utku | DOC-3
   Sorun: "API docs hangi format?"
   ⏰ 13:00 (6s önce)

... (5 daha)

[« Chat Menüsü] [« Ana Menü]
```

## Python Kodu (telebot)

```python
from telebot import types
from pathlib import Path

def send_chat_menu(bot, chat_id: str) -> None:
    """Chat menüsünü gönder."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Durum filtreleri
    markup.add(
        types.InlineKeyboardButton("🔴 Açık", callback_data="chat:acik"),
        types.InlineKeyboardButton("🟡 Çözüm Bekl.", callback_data="chat:cokundurmus"),
    )
    markup.add(
        types.InlineKeyboardButton("🟢 Çözüldü", callback_data="chat:cozuldu"),
        types.InlineKeyboardButton("🔍 Tümü", callback_data="chat:all"),
    )
    
    # Sorgu butonları
    markup.add(
        types.InlineKeyboardButton("🔎 Arama", callback_data="chat:ara_input"),
        types.InlineKeyboardButton("👤 Ajan Sorusu", callback_data="chat:ajan_input"),
    )
    
    # İşlem butonları
    markup.add(
        types.InlineKeyboardButton("📢 Broadcast Mesaj", callback_data="chat:broadcast"),
    )
    
    # Geri dön
    markup.add(
        types.InlineKeyboardButton("« Ana Menü", callback_data="menu:ana"),
    )
    
    bot.send_message(
        chat_id,
        "💬 **Chat Menüsü**\n\n"
        "Sorunları durum veya ajana göre göster.",
        reply_markup=markup,
        parse_mode="Markdown"
    )


def show_chat_status(bot, chat_id: str, status: str) -> None:
    """Chat sorunlarını durum bazında göster."""
    from src.company_master.chat import oku
    
    # DB'den verileri oku
    try:
        satirlar = oku()
    except:
        satirlar = []
    
    # Duruma göre filtrele
    status_map = {
        "acik": "acik",
        "cokundurmus": "cokundurmus",
        "cozuldu": "cozuldu",
        "all": None
    }
    
    filtered = satirlar
    if status != "all":
        filtered = [s for s in satirlar if s.get("durum") == status_map[status]]
    
    # Etiket seç
    etiketler = {
        "acik": "🔴 Açık",
        "cokundurmus": "🟡 Çözüm Bekl.",
        "cozuldu": "🟢 Çözüldü",
        "all": "🔍 Tümü"
    }
    
    # Formatla
    lines = [f"**{etiketler[status]} Sorunlar ({len(filtered)})**\n"]
    
    for i, soru in enumerate(filtered[:10], 1):  # İlk 10'u göster
        ajan_from = soru.get("ajan", "?")
        task_id = soru.get("task_id", "?")
        sorun_text = soru.get("sorun", "")[:40]
        
        lines.append(f"{i}️⃣ {ajan_from} | {task_id}\n   {sorun_text}")
    
    if len(filtered) > 10:
        lines.append(f"\n... (+{len(filtered) - 10} daha)")
    
    lines.append("\n[« Chat Menüsü] [« Ana Menü]")
    
    bot.send_message(
        chat_id,
        "\n\n".join(lines),
        parse_mode="Markdown"
    )


def handle_chat_search(bot, chat_id: str) -> None:
    """Chat arama için input iste."""
    msg = bot.send_message(
        chat_id,
        "🔎 **Arama terimini girin** (örn: 'token', 'tema', 'api')"
    )
    bot.register_next_step_handler(msg, lambda m: process_chat_search(bot, chat_id, m))


def process_chat_search(bot, chat_id: str, message) -> None:
    """Chat arama uygula."""
    term = message.text.strip().lower()
    
    from src.company_master.chat import oku
    try:
        satirlar = oku()
    except:
        satirlar = []
    
    # Arama terimini içerenleri filtrele
    filtered = [
        s for s in satirlar
        if term in s.get("sorun", "").lower() or term in s.get("cozum", "").lower()
    ]
    
    lines = [f"**Arama Sonuçları: '{term}' ({len(filtered)})**\n"]
    for i, soru in enumerate(filtered[:10], 1):
        ajan = soru.get("ajan", "?")
        task_id = soru.get("task_id", "?")
        sorun_text = soru.get("sorun", "")[:40]
        durum = soru.get("durum", "?")
        
        durum_emoji = {
            "acik": "🔴",
            "cokundurmus": "🟡",
            "cozuldu": "🟢"
        }.get(durum, "❓")
        
        lines.append(f"{i}. {durum_emoji} {ajan} | {task_id}\n   {sorun_text}")
    
    if len(filtered) > 10:
        lines.append(f"... (+{len(filtered) - 10} daha)")
    
    lines.append("\n[« Chat Menüsü] [« Ana Menü]")
    
    bot.send_message(chat_id, "\n\n".join(lines), parse_mode="Markdown")


def handle_ajan_chat(bot, chat_id: str) -> None:
    """Ajan soruları için ajan adı sor."""
    msg = bot.send_message(
        chat_id,
        "👤 **Ajan adını girin** (örn: utku, salih, yasu, ihsan, mimir)"
    )
    bot.register_next_step_handler(msg, lambda m: process_ajan_chat(bot, chat_id, m))


def process_ajan_chat(bot, chat_id: str, message) -> None:
    """Ajan soruları göster."""
    ajan = message.text.strip().lower()
    
    from src.company_master.chat import oku
    try:
        satirlar = oku()
    except:
        satirlar = []
    
    # Ajan'ın sorularını filtrele
    filtered = [s for s in satirlar if s.get("ajan", "").lower() == ajan]
    
    lines = [f"**{ajan.upper()} Soruları ({len(filtered)})**\n"]
    for i, soru in enumerate(filtered[:10], 1):
        task_id = soru.get("task_id", "?")
        sorun_text = soru.get("sorun", "")[:40]
        durum = soru.get("durum", "?")
        
        durum_emoji = {
            "acik": "🔴",
            "cokundurmus": "🟡",
            "cozuldu": "🟢"
        }.get(durum, "❓")
        
        lines.append(f"{i}. {durum_emoji} {task_id}\n   {sorun_text}")
    
    if len(filtered) > 10:
        lines.append(f"... (+{len(filtered) - 10} daha)")
    
    lines.append("\n[« Chat Menüsü] [« Ana Menü]")
    
    bot.send_message(chat_id, "\n\n".join(lines), parse_mode="Markdown")


def handle_broadcast_message(bot, chat_id: str) -> None:
    """Broadcast mesaj gönder (KAHİN)."""
    msg = bot.send_message(
        chat_id,
        "📢 **KAHİN Mesajı Gönder**\n\n"
        "Mesajınızı yazın (max 500 karakter):\n"
        "(İpucu: /cancel yazarak iptal edebilirsiniz)"
    )
    bot.register_next_step_handler(msg, lambda m: process_broadcast(bot, chat_id, m))


def process_broadcast(bot, chat_id: str, message) -> None:
    """Broadcast mesajını gönder."""
    if message.text.lower() == "/cancel":
        send_chat_menu(bot, chat_id)
        return
    
    mesaj = message.text.strip()[:500]
    
    from src.company_master.chat import kahin_gonder
    try:
        result = kahin_gonder(mesaj=mesaj, task_id="", onem="orta")
        bot.send_message(
            chat_id,
            f"✅ **Mesaj Gönderildi!**\n\n"
            f"Task ID: `{result.get('task_id', '—')}`\n\n"
            "[« Chat Menüsü] [« Ana Menü]",
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.send_message(
            chat_id,
            f"❌ **Hata:** {str(e)}\n\n"
            "[« Chat Menüsü] [« Ana Menü]",
            parse_mode="Markdown"
        )
```

## Callback Handler

```python
@bot.callback_query_handler(func=lambda call: call.data.startswith("chat:"))
def handle_chat_menu(call):
    """Chat menü butonlarını işle."""
    data = call.data.split(":")[1]
    
    if data in ["acik", "cokundurmus", "cozuldu", "all"]:
        show_chat_status(bot, call.message.chat.id, data)
    elif data == "ara_input":
        handle_chat_search(bot, call.message.chat.id)
    elif data == "ajan_input":
        handle_ajan_chat(bot, call.message.chat.id)
    elif data == "broadcast":
        handle_broadcast_message(bot, call.message.chat.id)
    elif data == "ana":
        send_ana_menu(bot, call.message.chat.id)
    
    bot.answer_callback_query(call.id)
```

## Notlar

- **Pagination**: 10 soru göster
- **Broadcast**: D-212 `kahin_gonder()` çağır
- **DB**: `chat.oku()` → ajan-chat.jsonl
- **Durum Emojileri**: 🔴 (açık), 🟡 (bekleyen), 🟢 (kapalı)
- **Arama**: Sorun + Çözüm alanlarında full-text arama
