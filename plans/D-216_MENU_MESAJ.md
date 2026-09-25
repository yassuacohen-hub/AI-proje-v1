# D-216: Telegram Menü — 📝 MESAJ MENÜSÜ

## Görüntü

```
╔═════════════════════════════════╗
║  📝 Mesaj Gönder               ║
╚═════════════════════════════════╝

[📢 Broadcast]     [👤 Targeted]

[🎯 Tag Seç]       [🔔 Uyarı]

[« Ana Menü]
```

## Mesaj Tipleri

| Tip | Buton | callback_data | Anlamı |
|-----|-------|---------------|--------|
| Broadcast | 📢 Broadcast | `mesaj:broadcast` | Tüm ajanlar (KAHİN) |
| Targeted | 👤 Targeted | `mesaj:targeted` | Spesifik ajan seç |
| Tag | 🎯 Tag Seç | `mesaj:tag` | Etiket bazlı seç |
| Uyarı | 🔔 Uyarı | `mesaj:alert` | Kritik uyarı şablonu |

## Çıkış Örnekleri

### Örnek 1: Broadcast (📢 Broadcast)

```
📢 **KAHİN Mesajı Gönder**

Mesajınızı yazın (max 500 karakter):
(İpucu: /cancel yazarak iptal edebilirsiniz)

┌─────────────────────────────────┐
│ Örnek: "Maintenance başlıyor"   │
│        "Daily standup 15:00"    │
└─────────────────────────────────┘

[Kullanıcı yazar: "API v2 deploy yarın"]

✅ **Mesaj Gönderildi!**

📌 KAHİN Mesajı
   Metin: "API v2 deploy yarın"
   Task ID: `gen-1727152800`
   Alıcı: * (Tüm Ajanlar)

Chat Log: ajan-chat.jsonl
Telegram: Broadcast grup mesajı

[« Mesaj Menüsü] [« Ana Menü]
```

### Örnek 2: Targeted (👤 Targeted)

```
👤 **Ajan Seçin**

[👨 Utku]    [👨 Salih]
[👨 Yasu]    [👨 İhsan]
[👨 Mimir]

[« Mesaj Menüsü]

[Kullanıcı tıklar: Utku]

📝 **Utku'ya Mesaj Gönder**

Mesajınızı yazın (max 500 karakter):

[Kullanıcı yazar: "API-12 hakkında soru var mı?"]

✅ **Mesaj Gönderildi!**

📌 Özel Mesaj
   Metin: "API-12 hakkında soru var mı?"
   Alıcı: utku
   Task ID: `utku-1727152800`

[« Mesaj Menüsü] [« Ana Menü]
```

### Örnek 3: Uyarı (🔔 Uyarı)

```
🔔 **Kritik Uyarı Şablonları**

[🚨 Sistem Hatası]
[⏰ Deadline Yaklaşıyor]
[🔒 Güvenlik Uyarısı]
[📊 Metrik Düştü]

[« Mesaj Menüsü]

[Kullanıcı tıklar: 🚨 Sistem Hatası]

🚨 **Sistem Hatası Uyarısı**

Ek not ekleyin (opsiyonel):
[Boş geçilebilir]

[Kullanıcı yazar: "DB bağlantısı koptu"]

✅ **Uyarı Gönderildi!**

🚨 KRITIK: Sistem Hatası
   DB bağlantısı koptu
   Alıcı: * (Tüm Ajanlar)
   Önem: kritik

[« Mesaj Menüsü] [« Ana Menü]
```

## Python Kodu (telebot)

```python
from telebot import types

def send_mesaj_menu(bot, chat_id: str) -> None:
    """Mesaj menüsünü gönder."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    markup.add(
        types.InlineKeyboardButton("📢 Broadcast", callback_data="mesaj:broadcast"),
        types.InlineKeyboardButton("👤 Targeted", callback_data="mesaj:targeted"),
    )
    markup.add(
        types.InlineKeyboardButton("🎯 Tag Seç", callback_data="mesaj:tag"),
        types.InlineKeyboardButton("🔔 Uyarı", callback_data="mesaj:alert"),
    )
    
    markup.add(
        types.InlineKeyboardButton("« Ana Menü", callback_data="menu:ana"),
    )
    
    bot.send_message(
        chat_id,
        "📝 **Mesaj Gönder**\n\n"
        "Mesaj türünü seçin:\n"
        "• 📢 Broadcast: Tüm ajanlar (KAHİN)\n"
        "• 👤 Targeted: Spesifik ajan\n"
        "• 🎯 Tag: Etiket bazlı\n"
        "• 🔔 Uyarı: Kritik uyarı şablonu",
        reply_markup=markup,
        parse_mode="Markdown"
    )


def handle_broadcast_message(bot, chat_id: str) -> None:
    """Broadcast mesaj için input iste."""
    msg = bot.send_message(
        chat_id,
        "📢 **KAHİN Mesajı Gönder**\n\n"
        "Mesajınızı yazın (max 500 karakter):\n\n"
        "_İpucu: `/cancel` yazarak iptal edebilirsiniz_",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, lambda m: process_broadcast(bot, chat_id, m))


def process_broadcast(bot, chat_id: str, message) -> None:
    """Broadcast mesajını gönder."""
    if message.text.lower() == "/cancel":
        send_mesaj_menu(bot, chat_id)
        return
    
    mesaj = message.text.strip()[:500]
    
    from src.company_master.chat import kahin_gonder
    try:
        result = kahin_gonder(mesaj=mesaj, task_id="", onem="orta")
        
        bot.send_message(
            chat_id,
            f"✅ **Mesaj Gönderildi!**\n\n"
            f"📌 KAHİN Mesajı\n"
            f"   Metin: `{mesaj[:50]}...`\n"
            f"   Alıcı: * (Tüm Ajanlar)\n"
            f"   Task ID: `{result.get('task_id', '—')}`\n\n"
            f"[« Mesaj Menüsü] [« Ana Menü]",
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.send_message(
            chat_id,
            f"❌ **Hata:** {str(e)}\n\n"
            f"[« Mesaj Menüsü] [« Ana Menü]",
            parse_mode="Markdown"
        )


def send_targeted_ajan_menu(bot, chat_id: str) -> None:
    """Targeted mesaj için ajan seçim menüsü."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    ajanlar = [
        ("👨 Utku", "mesaj_targeted:utku"),
        ("👨 Salih", "mesaj_targeted:salih"),
        ("👨 Yasu", "mesaj_targeted:yasu"),
        ("👨 İhsan", "mesaj_targeted:ihsan"),
        ("👨 Mimir", "mesaj_targeted:mimir"),
    ]
    
    for label, callback in ajanlar:
        markup.add(types.InlineKeyboardButton(label, callback_data=callback))
    
    markup.add(
        types.InlineKeyboardButton("« Mesaj Menüsü", callback_data="menu:mesaj"),
    )
    
    bot.send_message(
        chat_id,
        "👤 **Ajan Seçin**\n\n"
        "Mesaj göndermek istediğiniz ajanı seçin.",
        reply_markup=markup,
        parse_mode="Markdown"
    )


def handle_targeted_input(bot, chat_id: str, ajan: str) -> None:
    """Targeted mesaj input iste."""
    msg = bot.send_message(
        chat_id,
        f"📝 **{ajan.upper()}'ya Mesaj Gönder**\n\n"
        f"Mesajınızı yazın (max 500 karakter):\n\n"
        f"_İpucu: `/cancel` yazarak iptal edebilirsiniz_",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, lambda m: process_targeted(bot, chat_id, ajan, m))


def process_targeted(bot, chat_id: str, ajan: str, message) -> None:
    """Targeted mesajı gönder."""
    if message.text.lower() == "/cancel":
        send_mesaj_menu(bot, chat_id)
        return
    
    mesaj = message.text.strip()[:500]
    
    from src.company_master.chat import ac
    try:
        result = ac(
            ajan=ajan,
            task_id="",
            sorun=mesaj,
            cozum="",
            kimden="kahin",
            onem="orta"
        )
        
        bot.send_message(
            chat_id,
            f"✅ **Mesaj Gönderildi!**\n\n"
            f"📌 Özel Mesaj\n"
            f"   Metin: `{mesaj[:50]}...`\n"
            f"   Alıcı: {ajan}\n"
            f"   Task ID: `{result.get('task_id', '—')}`\n\n"
            f"[« Mesaj Menüsü] [« Ana Menü]",
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.send_message(
            chat_id,
            f"❌ **Hata:** {str(e)}\n\n"
            f"[« Mesaj Menüsü] [« Ana Menü]",
            parse_mode="Markdown"
        )


def send_alert_templates(bot, chat_id: str) -> None:
    """Uyarı şablonlarını gönder."""
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    templates = [
        ("🚨 Sistem Hatası", "mesaj_alert:sistem_hatasi"),
        ("⏰ Deadline Yaklaşıyor", "mesaj_alert:deadline"),
        ("🔒 Güvenlik Uyarısı", "mesaj_alert:guvenlik"),
        ("📊 Metrik Düştü", "mesaj_alert:metrik"),
    ]
    
    for label, callback in templates:
        markup.add(types.InlineKeyboardButton(label, callback_data=callback))
    
    markup.add(
        types.InlineKeyboardButton("« Mesaj Menüsü", callback_data="menu:mesaj"),
    )
    
    bot.send_message(
        chat_id,
        "🔔 **Kritik Uyarı Şablonları**\n\n"
        "Uyarı türünü seçin (ek not yazabilirsiniz).",
        reply_markup=markup,
        parse_mode="Markdown"
    )


def handle_alert_input(bot, chat_id: str, template: str) -> None:
    """Uyarı şablonu için ek not iste."""
    template_names = {
        "sistem_hatasi": "🚨 Sistem Hatası",
        "deadline": "⏰ Deadline Yaklaşıyor",
        "guvenlik": "🔒 Güvenlik Uyarısı",
        "metrik": "📊 Metrik Düştü"
    }
    
    msg = bot.send_message(
        chat_id,
        f"{template_names.get(template, '🔔 Uyarı')}\n\n"
        f"Ek not ekleyin (opsiyonel, Enter atlamak için /skip yazın):\n\n"
        f"_İpucu: `/cancel` yazarak iptal edebilirsiniz_",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, lambda m: process_alert(bot, chat_id, template, m))


def process_alert(bot, chat_id: str, template: str, message) -> None:
    """Uyarı mesajını gönder."""
    if message.text.lower() == "/cancel":
        send_mesaj_menu(bot, chat_id)
        return
    
    ek_not = "" if message.text.lower() == "/skip" else message.text.strip()[:200]
    
    template_messages = {
        "sistem_hatasi": ("🚨 KRITIK: Sistem Hatası", "kritik"),
        "deadline": ("⏰ UYARI: Deadline Yaklaşıyor", "yuksek"),
        "guvenlik": ("🔒 UYARI: Güvenlik Tehdidi", "kritik"),
        "metrik": ("📊 UYARI: Metrik Düştü", "yuksek")
    }
    
    baslik, onem = template_messages.get(template, ("🔔 Uyarı", "orta"))
    
    # Mesaj oluştur
    if ek_not:
        mesaj_tam = f"{baslik}\n{ek_not}"
    else:
        mesaj_tam = baslik
    
    from src.company_master.chat import kahin_gonder
    try:
        result = kahin_gonder(mesaj=mesaj_tam, task_id="", onem=onem)
        
        bot.send_message(
            chat_id,
            f"✅ **Uyarı Gönderildi!**\n\n"
            f"{baslik}\n"
            f"Alıcı: * (Tüm Ajanlar)\n"
            f"Önem: {onem}\n"
            f"Task ID: `{result.get('task_id', '—')}`\n\n"
            f"[« Mesaj Menüsü] [« Ana Menü]",
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.send_message(
            chat_id,
            f"❌ **Hata:** {str(e)}\n\n"
            f"[« Mesaj Menüsü] [« Ana Menü]",
            parse_mode="Markdown"
        )
```

## Callback Handlers

```python
@bot.callback_query_handler(func=lambda call: call.data.startswith("mesaj:"))
def handle_mesaj_menu(call):
    """Mesaj menü butonlarını işle."""
    data = call.data.split(":")[1]
    
    if data == "broadcast":
        handle_broadcast_message(bot, call.message.chat.id)
    elif data == "targeted":
        send_targeted_ajan_menu(bot, call.message.chat.id)
    elif data == "tag":
        bot.send_message(call.message.chat.id, "🎯 Tag arama henüz aktif değil.")
    elif data == "alert":
        send_alert_templates(bot, call.message.chat.id)
    elif data == "ana":
        send_ana_menu(bot, call.message.chat.id)
    
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("mesaj_targeted:"))
def handle_mesaj_targeted(call):
    """Targeted ajan seçimi."""
    ajan = call.data.split(":")[1]
    handle_targeted_input(bot, call.message.chat.id, ajan)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("mesaj_alert:"))
def handle_mesaj_alert(call):
    """Uyarı şablonu seçimi."""
    template = call.data.split(":")[1]
    handle_alert_input(bot, call.message.chat.id, template)
    bot.answer_callback_query(call.id)
```

## Notlar

- **Broadcast**: `kahin_gonder()` → tüm ajanlar (D-210, D-212)
- **Targeted**: `ac()` (chat.açık) → spesifik ajan
- **Uyarı**: Kritik şablonlar + ek not
- **Önem Seviyeleri**: kritik, yuksek, orta, dusuk
- **Input Timeout**: 5 dakika
- **Iptal**: `/cancel` yazarak menüye dön
