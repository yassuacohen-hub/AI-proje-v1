# D-216: Telegram Menu UI Tasarımı — İnteraktif Arayüz

## 1. Telegram InlineKeyboard Mimarisi

Telegram Bot API `InlineKeyboard` kullanarak buton menüsü:
```python
InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton("📊 Pano", callback_data="menu_pano")],
        [InlineKeyboardButton("💬 Chat", callback_data="menu_chat")],
        ...
    ]
)
```

---

## 2. ANA MENU (Başlangıç)

```
┌─────────────────────────────────┐
│  🤖 Huginn Bot — Ana Menü      │
└─────────────────────────────────┘

[📊 Pano]    [💬 Chat]    [✉️ Tetikler]

[📝 Mesaj]   [📈 Rapor]   [⚙️ Ayarlar]

┌─────────────────────────────────┐
│ /help — Tüm komutlar            │
└─────────────────────────────────┘
```

### İşlev:
- Başlangıçta gelen ilk ekran
- Her komuttan sonra ana menüye dön (`[« Ana Menü]`)
- 6 ana kategori

---

## 3. SUBMENU YAPILARI

### **SUBMENU 1: 📊 PANO MENU**

```
┌─────────────────────────────────┐
│  📊 Pano Menüsü                │
└─────────────────────────────────┘

┌─ DURUM FİLTRESİ ─────────────┐
│ [✅ Tamamlandi]  [✔ Aktif]   │
│ [🔴 Bloke]       [📋 Plan]   │
│ [🔍 Tümü]                     │
└────────────────────────────────┘

┌─ SORGU ──────────────────────┐
│ [👤 Ajan Ara]  [🏷️ Tag Ara] │
└────────────────────────────────┘

[« Ana Menü]
```

**Komutlar:**
- `[✅ Tamamlandi]` → `/pano done`
- `[✔ Aktif]` → `/pano active`
- `[🔴 Bloke]` → `/pano blocked`
- `[📋 Plan]` → `/pano plan`
- `[👤 Ajan Ara]` → `/tasklar [ajan_adı]` (prompt)

**Çıkış Örneği:**
```
✅ Tamamlandı Görevler (12)

1. API-15 [utku] ✓ 2026-09-24
2. UI-8  [salih] ✓ 2026-09-23
3. DOC-4 [yasu]  ✓ 2026-09-22
...

[« Pano Menüsü] [« Ana Menü]
```

---

### **SUBMENU 2: 💬 CHAT MENU**

```
┌─────────────────────────────────┐
│  💬 Chat Menüsü                │
└─────────────────────────────────┘

┌─ SORUN DURUMU ────────────────┐
│ [🔴 Açık]      [🟡 Çözüm Bek] │
│ [🟢 Çözüldü]   [🔍 Tümü]      │
└────────────────────────────────┘

┌─ SORGU ──────────────────────┐
│ [🔎 Arama]   [👤 Ajan Sorusu]│
└────────────────────────────────┘

[📢 Broadcast Mesaj]

[« Ana Menü]
```

**Komutlar:**
- `[🔴 Açık]` → `/chat acik`
- `[🟡 Çözüm Bek]` → `/chat cokundurmus`
- `[🟢 Çözüldü]` → `/chat cozuldu`
- `[👤 Ajan Sorusu]` → `/sorun [ajan]` (prompt)
- `[📢 Broadcast Mesaj]` → `/mesaj` input

**Çıkış Örneği:**
```
🔴 Açık Sorunlar (8)

1️⃣ utku→yasu | API-12: "Token expire" [15:30]
2️⃣ salih→ihsan | UI-5: "Tema renkler" [14:15]
...

[« Chat Menüsü] [« Ana Menü]
```

---

### **SUBMENU 3: ✉️ TETIKLER MENU**

```
┌─────────────────────────────────┐
│  ✉️ Tetikler (Posta Kutusu)     │
└─────────────────────────────────┘

┌─ AJAN SEÇ ────────────────────┐
│ [👨 Utku]    [👨 Salih]       │
│ [👨 Yasu]    [👨 İhsan]       │
│ [👨 Mimir]   [🔍 Tümü]        │
└────────────────────────────────┘

[« Ana Menü]
```

**Komutlar:**
- `[👨 Utku]` → `/tetikler utku`
- `[🔍 Tümü]` → `/tetikler`

**Çıkış Örneği:**
```
utku'nun Bekleyen Tetikleri (2)

📬 T-1 (API-12) — Talimat: "API v2 uyumlu hale getir"
   ⚠️ 2 açık soru
   📅 2026-09-25 14:00

📬 T-2 (UI-3) — Talimat: "Dark theme ekle"
   ✅ 0 açık soru
   📅 2026-09-25 13:00

[« Tetikler Menüsü] [« Ana Menü]
```

---

### **SUBMENU 4: 📝 MESAJ MENU**

```
┌─────────────────────────────────┐
│  📝 Mesaj Gönder               │
└─────────────────────────────────┘

[📢 Broadcast] [👤 Targeted]

[🎯 Tag Seç]   [🔔 Uyarı]

[« Ana Menü]
```

**Komutlar:**
- `[📢 Broadcast]` → `/mesaj <metin>` (popup input)
- `[👤 Targeted]` → `/mesaj-ajan <ajan> <metin>`
- `[🔔 Uyarı]` → Kritik uyarı şablonu

**Örnek Flow:**
```
1. Kullanıcı: [📢 Broadcast] tıkla
2. Bot: "Mesajınızı girin (max 500 char)"
3. Kullanıcı: "Maintenance başlıyor"
4. Bot: ✅ Gönderildi!
   Chat: kahin → * (genel)
   Telegram: 🟡 KAHİN Mesajı...
5. [« Mesaj Menüsü] [« Ana Menü]
```

---

### **SUBMENU 5: 📈 RAPOR MENU**

```
┌─────────────────────────────────┐
│  📈 Raporlar & Analitik         │
└─────────────────────────────────┘

┌─ ZAMaN ─────────────────────┐
│ [📅 Hafta]  [📆 Ay]  [📊 YTD]│
└────────────────────────────────┘

┌─ DETAY ──────────────────────┐
│ [👤 Ajan] [📌 KPI] [💹 Trend]│
└────────────────────────────────┘

[« Ana Menü]
```

**Komutlar:**
- `[📅 Hafta]` → `/rapor hafta`
- `[📆 Ay]` → `/rapor ay`
- `[👤 Ajan]` → `/ajan-rapor [ajan]` (prompt)
- `[📌 KPI]` → `/metrik`

**Çıkış Örneği:**
```
📊 Haftalık Özet (2026-09-19 → 2026-09-25)

💬 Chat Metrikleri:
  🔴 Açık: 8 sorun
  🟡 Çözüm Bekleniyor: 3 sorun
  🟢 Çözüldü: 12 sorun

📋 Pano Metrikleri:
  ✅ Tamamlandı: 8 görev
  🔄 Aktif: 5 görev
  🔴 Bloke: 2 görev

[« Rapor Menüsü] [« Ana Menü]
```

---

### **SUBMENU 6: ⚙️ AYARLAR MENU**

```
┌─────────────────────────────────┐
│  ⚙️ Ayarlar & Kontrol          │
└─────────────────────────────────┘

[✅ Bağlantı Test]  [🔐 Token]

[🔔 Notifications]  [📱 Webhook]

[🆘 Yardım]  [📋 Komutlar]

[« Ana Menü]
```

**Komutlar:**
- `[✅ Bağlantı Test]` → `/baslat`
- `[🔐 Token]` → Yapılandırmayı göster (masked)
- `[🆘 Yardım]` → `/help`
- `[📋 Komutlar]` → Tüm komutlar listesi

---

## 4. KIŞAYOL MENÜ (Quick Access)

Ana menü altında fixed kısayollar:

```
┌─────────────────────────────────┐
│ ⚡ Hızlı Erişim                 │
│ [🚨 ACİL]  [⚡ Q]  [📌 ÖZet]   │
└─────────────────────────────────┘
```

- `[🚨 ACİL]` → Tüm kritik işler (bloke + açık sorunlar)
- `[⚡ Q]` → Quick status (1 satırda)
- `[📌 ÖZET]` → 1 dakikalık dashboard

---

## 5. NAVIGASYON FLOW DİYAGRAMI

```
                      Ana Menü
                         │
          ┌──────────────┼──────────────┐
          │              │              │
       📊 Pano        💬 Chat        ✉️ Tetikler
          │              │              │
      [Filtre]       [Durum]        [Ajan]
          │              │              │
      Tablo           Tablo          Tablo
      Çıkış          Çıkış          Çıkış
          │              │              │
          └──────────┬───┴───┬──────────┘
                   [« Menü] [« Ana Menü]

         📝 Mesaj    📈 Rapor    ⚙️ Ayarlar
            │           │           │
        [Input]     [Filtre]     [Config]
            │           │           │
         Onay       Tablo        Durum
            │           │           │
            └───────┬───┴───┬───────┘
                  [« Menü] [« Ana Menü]
```

---

## 6. Telegram API InlineKeyboard Syntax

```python
from telebot import types

def menu_ana():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("📊 Pano", callback_data="menu:pano"),
        types.InlineKeyboardButton("💬 Chat", callback_data="menu:chat"),
    )
    markup.add(
        types.InlineKeyboardButton("✉️ Tetikler", callback_data="menu:tetikler"),
        types.InlineKeyboardButton("📝 Mesaj", callback_data="menu:mesaj"),
    )
    markup.add(
        types.InlineKeyboardButton("📈 Rapor", callback_data="menu:rapor"),
        types.InlineKeyboardButton("⚙️ Ayarlar", callback_data="menu:ayarlar"),
    )
    markup.add(
        types.InlineKeyboardButton("⚡ Hızlı Erişim", callback_data="menu:quick"),
    )
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith("menu:"))
def handle_menu(call):
    menu_type = call.data.split(":")[1]
    
    if menu_type == "pano":
        text = "📊 Pano Menüsü\n\n"
        markup = menu_pano()
    elif menu_type == "chat":
        text = "💬 Chat Menüsü\n\n"
        markup = menu_chat()
    # ... vs
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=markup
    )
```

---

## 7. İmplementasyon Checklist

- [ ] `telegram_bot.py` → `menu_ana()`, `menu_pano()`, `menu_chat()` vs
- [ ] Callback handlers → `handle_menu()`, `handle_pano_filter()` vs
- [ ] Input dialogs → Mesaj gönderme, ajan seçimi (popup)
- [ ] Back buttons → `[« Menü]` ve `[« Ana Menü]`
- [ ] Emoji + emojis konsistentliği
- [ ] Mobile responsiveness (Telegram mobilde)

---

## 8. Örnek User Journey

```
1. Kullanıcı: /start
   Bot gösterir: Ana Menü (6 buton)

2. Kullanıcı: [📊 Pano]
   Bot gösterir: Pano Filtre Menüsü (4 durum)

3. Kullanıcı: [🔴 Bloke]
   Bot gösterir: Bloke görevler tablosu
              + [« Pano Menüsü] [« Ana Menü]

4. Kullanıcı: [« Pano Menüsü]
   Bot geri gider: Pano Menüsü

5. Kullanıcı: [« Ana Menü]
   Bot geri gider: Ana Menü

6. Kullanıcı: [💬 Chat]
   Bot gösterir: Chat Durum Menüsü
   ...
```

---

## Commit

```bash
git commit -m "D-216: Telegram UI — İnteraktif Menü Tasarımı (6 submenu + kısayol)"
```
