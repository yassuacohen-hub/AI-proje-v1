# D-216: Telegram Menü — ANA MENÜ

## Görüntü

```
╔═════════════════════════════════╗
║  🤖 Huginn Bot — Ana Menü      ║
╚═════════════════════════════════╝

┌─ GÖREV & HARITA ──────────────────┐
│ [📊 Pano]    [💬 Chat]            │
│ [✉️ Tetikler] [📝 Mesaj]          │
└────────────────────────────────────┘

┌─ YÖNETİM ────────────────────────┐
│ [📈 Rapor]   [⚙️ Ayarlar]        │
└────────────────────────────────────┘

┌─ HIZLI ERIŞIM ───────────────────┐
│ [🚨 ACİL]  [⚡ Q]  [📌 ÖZET]   │
└────────────────────────────────────┘

─────────────────────────────────────
/help — Tüm komutlar
/start — Ana menüye dön
```

## Buton Callback Tanımları

| Buton | callback_data | Hedif |
|-------|---------------|-------|
| 📊 Pano | `menu:pano` | Pano Menüsü |
| 💬 Chat | `menu:chat` | Chat Menüsü |
| ✉️ Tetikler | `menu:tetikler` | Tetikler Menüsü |
| 📝 Mesaj | `menu:mesaj` | Mesaj Menüsü |
| 📈 Rapor | `menu:rapor` | Rapor Menüsü |
| ⚙️ Ayarlar | `menu:ayarlar` | Ayarlar Menüsü |
| 🚨 ACİL | `quick:urgent` | Kritik görevler (bloke) |
| ⚡ Q | `quick:q` | Soru özeti |
| 📌 ÖZET | `quick:summary` | Günlük özet |

## Python Kodu (telebot)

```python
from telebot import types

def send_ana_menu(bot, chat_id: str) -> None:
    """Ana menüyü gönder."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Görev & Harita satırı
    markup.add(
        types.InlineKeyboardButton("📊 Pano", callback_data="menu:pano"),
        types.InlineKeyboardButton("💬 Chat", callback_data="menu:chat"),
    )
    markup.add(
        types.InlineKeyboardButton("✉️ Tetikler", callback_data="menu:tetikler"),
        types.InlineKeyboardButton("📝 Mesaj", callback_data="menu:mesaj"),
    )
    
    # Yönetim satırı
    markup.add(
        types.InlineKeyboardButton("📈 Rapor", callback_data="menu:rapor"),
        types.InlineKeyboardButton("⚙️ Ayarlar", callback_data="menu:ayarlar"),
    )
    
    # Hızlı erişim satırı
    markup.add(
        types.InlineKeyboardButton("🚨 ACİL", callback_data="quick:urgent"),
        types.InlineKeyboardButton("⚡ Q", callback_data="quick:q"),
        types.InlineKeyboardButton("📌 ÖZET", callback_data="quick:summary"),
    )
    
    bot.send_message(
        chat_id,
        "🤖 **Huginn Bot — Ana Menü**\n\n"
        "Görev yönetimi, sohbet ve raporlar için menü seçin.",
        reply_markup=markup,
        parse_mode="Markdown"
    )
```

## Callback Handler

```python
@bot.callback_query_handler(func=lambda call: call.data.startswith("menu:") or call.data.startswith("quick:"))
def handle_main_menu(call):
    """Ana menü butonlarını işle."""
    data = call.data
    
    if data == "menu:pano":
        send_pano_menu(bot, call.message.chat.id)
    elif data == "menu:chat":
        send_chat_menu(bot, call.message.chat.id)
    elif data == "menu:tetikler":
        send_tetikler_menu(bot, call.message.chat.id)
    elif data == "menu:mesaj":
        send_mesaj_menu(bot, call.message.chat.id)
    elif data == "menu:rapor":
        send_rapor_menu(bot, call.message.chat.id)
    elif data == "menu:ayarlar":
        send_ayarlar_menu(bot, call.message.chat.id)
    elif data == "quick:urgent":
        show_urgent_tasks(bot, call.message.chat.id)
    elif data == "quick:q":
        show_q_summary(bot, call.message.chat.id)
    elif data == "quick:summary":
        show_daily_summary(bot, call.message.chat.id)
    
    bot.answer_callback_query(call.id)  # Dropdown indicator kapat
```

## Akış

1. User `/start` yazar
2. Bot: Ana Menü gönder
3. User: Buton tıkla (menu:X veya quick:X)
4. Bot: İlgili menüyü/sonucu gönder
5. User: Geri dön `[« Ana Menü]` butonuyla

## Notlar

- **Ana Menü hiç kapanmaz**: Her menüden `[« Ana Menü]` ile dön
- **Hızlı erişim 3'ü**: Sık kullanılan sorgular
- **Tüm menüler 2x3 grid**: Mobil-dostu
