# D-216: Telegram Menü Sistemi — ÖZET HARİTASI

## 🗺️ Menü Mimarisi (6 Seviye)

```
┌─────────────────────────────────────────────┐
│     🤖 ANA MENÜ (D-216_MENU_ANA.md)         │
│                                             │
│  [📊 Pano] [💬 Chat] [✉️ Tetikler]        │
│  [📝 Mesaj] [📈 Rapor] [⚙️ Ayarlar]       │
│                                             │
│  [🚨 ACİL] [⚡ Q] [📌 ÖZET]               │
└─────────────────────────────────────────────┘
           |        |        |        |        |        |
           ↓        ↓        ↓        ↓        ↓        ↓
         ┌────┐  ┌────┐  ┌────┐  ┌────┐  ┌────┐  ┌────┐
         │ 📊 │  │ 💬 │  │ ✉️ │  │ 📝 │  │ 📈 │  │ ⚙️ │
         │ PANO│  │CHAT│  │TEK │  │MES │  │RAP │  │AYA │
         └────┘  └────┘  └────┘  └────┘  └────┘  └────┘
           │        │        │        │        │        │
           ↓        ↓        ↓        ↓        ↓        ↓
    ┌──────────┐ ┌────────┐ ┌─────┐ ┌──────┐ ┌────┐ ┌──────┐
    │ 4 Durum  │ │3 Durum │ │6 Ajan│ │3 Tip │ │4 Zaman│ │9 Ayar │
    │ Filtre   │ │ Filtre │ │ Seç  │ │ Seç  │ │Dilimi │ │ Seç  │
    └──────────┘ └────────┘ └─────┘ └──────┘ └────┘ └──────┘
```

## 📋 Menü Dosyaları & Yollar

| # | Dosya | Menü | Buton Sayısı | Işlevsellik |
|---|-------|------|--------------|-------------|
| 1 | [`D-216_MENU_ANA.md`](D-216_MENU_ANA.md) | 🤖 ANA MENÜ | 9 buton | Giriş noktası, 6 ana + 3 hızlı |
| 2 | [`D-216_MENU_PANO.md`](D-216_MENU_PANO.md) | 📊 PANO | 7 buton | 4 durum + 2 sorgu + geri |
| 3 | [`D-216_MENU_CHAT.md`](D-216_MENU_CHAT.md) | 💬 CHAT | 8 buton | 4 durum + 2 sorgu + broadcast + geri |
| 4 | [`D-216_MENU_TETIKLER.md`](D-216_MENU_TETIKLER.md) | ✉️ TETIKLER | 7 buton | 6 ajan + tümü + geri |
| 5 | [`D-216_MENU_MESAJ.md`](D-216_MENU_MESAJ.md) | 📝 MESAJ | 7 buton | 4 tip + ajan seç + geri |
| 6 | [`D-216_MENU_RAPOR.md`](D-216_MENU_RAPOR.md) | 📈 RAPOR | 7 buton | 3 zaman + 4 detay + geri |
| 7 | [`D-216_MENU_AYARLAR.md`](D-216_MENU_AYARLAR.md) | ⚙️ AYARLAR | 10 buton | 3 durum + 3 config + 3 yönetim + geri |

## 🎯 Callback Data Routing Haritası

### Ana Menü → Submenüler

```
Buton Tıklaması          callback_data      Handler Fonksiyonu      Çıkış
─────────────────────────────────────────────────────────────────────────
📊 Pano                  menu:pano          send_pano_menu()        Pano Menüsü
💬 Chat                  menu:chat          send_chat_menu()        Chat Menüsü
✉️ Tetikler             menu:tetikler      send_tetikler_menu()    Tetikler Menüsü
📝 Mesaj                 menu:mesaj         send_mesaj_menu()       Mesaj Menüsü
📈 Rapor                 menu:rapor         send_rapor_menu()       Rapor Menüsü
⚙️ Ayarlar              menu:ayarlar       send_ayarlar_menu()     Ayarlar Menüsü

🚨 ACİL                  quick:urgent       show_urgent_tasks()     Bloke Görevler
⚡ Q                     quick:q            show_q_summary()        Soru Özeti
📌 ÖZET                  quick:summary      show_daily_summary()    Günlük Özet
```

### Pano Menüsü → Görevler

```
pano:done        → show_pano_status(..., "done")
pano:active      → show_pano_status(..., "active")
pano:blocked     → show_pano_status(..., "blocked")
pano:plan        → show_pano_status(..., "plan")
pano:all         → show_pano_status(..., "all")
pano:ajan_input  → handle_ajan_input() → process_ajan_filter()
pano:tag_input   → [Henüz Aktif Değil]
```

### Chat Menüsü → Sorunlar

```
chat:acik        → show_chat_status(..., "acik")
chat:cokundurmus → show_chat_status(..., "cokundurmus")
chat:cozuldu     → show_chat_status(..., "cozuldu")
chat:all         → show_chat_status(..., "all")
chat:ara_input   → handle_chat_search() → process_chat_search()
chat:ajan_input  → handle_ajan_chat() → process_ajan_chat()
chat:broadcast   → handle_broadcast_message() → process_broadcast()
```

### Tetikler Menüsü → Ajanlar

```
tetikler:utku    → show_tetikler_ajan(..., "utku")
tetikler:salih   → show_tetikler_ajan(..., "salih")
tetikler:yasu    → show_tetikler_ajan(..., "yasu")
tetikler:ihsan   → show_tetikler_ajan(..., "ihsan")
tetikler:mimir   → show_tetikler_ajan(..., "mimir")
tetikler:all     → show_tetikler_all()
```

### Mesaj Menüsü → İşlemler

```
mesaj:broadcast     → handle_broadcast_message() → process_broadcast()
mesaj:targeted      → send_targeted_ajan_menu() [ajan seçim]
mesaj:tag           → [Henüz Aktif Değil]
mesaj:alert         → send_alert_templates()

mesaj_targeted:utku   → handle_targeted_input(..., "utku")
mesaj_targeted:salih  → handle_targeted_input(..., "salih")
[vs.]

mesaj_alert:sistem_hatasi    → handle_alert_input(..., "sistem_hatasi")
mesaj_alert:deadline         → handle_alert_input(..., "deadline")
mesaj_alert:guvenlik         → handle_alert_input(..., "guvenlik")
mesaj_alert:metrik           → handle_alert_input(..., "metrik")
```

### Rapor Menüsü → Analizler

```
rapor:hafta   → show_hafta_raporu()
rapor:ay      → [Henüz Aktif Değil]
rapor:ytd     → [Henüz Aktif Değil]

rapor_detail:ajan   → [Henüz Aktif Değil]
rapor_detail:kpi    → show_kpi_raporu()
rapor_detail:trend  → show_trend_raporu()
rapor_detail:ozet   → show_ozet_raporu()
```

### Ayarlar Menüsü → Konfigürasyon

```
ayarlar:baglanti    → check_baglanti()
ayarlar:token       → show_token_status()
ayarlar:info        → show_bot_info()
ayarlar:bildirim    → [Henüz Aktif Değil]
ayarlar:email       → [Henüz Aktif Değil]
ayarlar:tercih      → [Henüz Aktif Değil]
ayarlar:yardim      → show_yardim()
ayarlar:changelog   → [Henüz Aktif Değil]
ayarlar:destek      → show_destek()
```

### Geri Dön Butonları

```
Tüm alt menülerden:
« Ana Menü      → callback: menu:ana    → send_ana_menu()
« [Menü Adı]    → callback: menu:[type] → send_[type]_menu()
```

## 📊 Veri Kaynakları

| Menü | Veri Kaynağı | Import | Fonksiyon |
|------|--------------|--------|-----------|
| Pano | `task_board.json` | `orchestrator.trigger` | `bekleyen_tetikler()` |
| Chat | `ajan-chat.jsonl` | `company_master.chat` | `oku()`, `ac()`, `kahin_gonder()` |
| Tetikler | `tetik kutusu` | `orchestrator.trigger` | `bekleyen_tetikler()` |
| Mesaj | Chat Log | `company_master.chat` | `kahin_gonder()`, `ac()` |
| Rapor | Task Board + Chat | `orchestrator.trigger`, `chat` | `bekleyen_tetikler()`, `oku()` |
| Ayarlar | Bot Runtime | `telebot`, `datetime` | Health checks, version info |

## 🔄 Input Akışı (User Interactions)

```
1. /start KOMUT
   ↓
2. Ana Menü Gönder (6 buton + 3 hızlı)
   ↓
3. User: Buton Tıkla (callback)
   ↓
4. Handler: callback_data Ayrıştır
   ↓
5. Submenü Gönder VEYA Sorgu Çalıştır
   ↓
6. User: Submenüden Seç VEYA Input Yaz
   ↓
7. Handler: İşle → Sonuç Gönder
   ↓
8. User: « Ana Menü Tıkla
   ↓
9. [4. adıma dön] (Loop)
```

## 📱 Telegram Bot Setup (main.py)

```python
import telebot
from telebot import types

# Bot başlatma
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# 🔹 Tüm Decorator'lar
@bot.message_handler(commands=["start"])
def cmd_start(message):
    send_ana_menu(bot, message.chat.id)

@bot.message_handler(commands=["help"])
def cmd_help(message):
    show_yardim(bot, message.chat.id)

@bot.message_handler(commands=["menu"])
def cmd_menu(message):
    send_ana_menu(bot, message.chat.id)

# 🔹 Ana Menü Callback
@bot.callback_query_handler(func=lambda call: call.data.startswith("menu:"))
def handle_main_menu(call):
    # Routing logic...

# 🔹 Submenü Callbacks
@bot.callback_query_handler(func=lambda call: call.data.startswith("pano:"))
def handle_pano_menu(call):
    # Routing logic...

@bot.callback_query_handler(func=lambda call: call.data.startswith("chat:"))
def handle_chat_menu(call):
    # Routing logic...

# [vs. tüm menüler]

# 🔹 Polling (Local Dev)
bot.infinity_polling()

# 🔹 Webhook (Production)
@app.post("/api/webhooks/telegram")
def telegram_webhook(request: dict):
    update = types.Update.de_json(request)
    bot.process_new_updates([update])
    return {"ok": True}
```

## ✅ Kontrol Listesi (MVP Faz 1)

- [x] Ana Menü tasarımı (6 buton + 3 hızlı)
- [x] Pano Menüsü (durum filtresi)
- [x] Chat Menüsü (sorun filtresi + broadcast)
- [x] Tetikler Menüsü (ajan seçim)
- [x] Mesaj Menüsü (broadcast + targeted + uyarı)
- [x] Rapor Menüsü (hafta + KPI + trend + özet)
- [x] Ayarlar Menüsü (durum + token + bilgi + yardım)
- [ ] Webhook endpoint (`/api/webhooks/telegram`)
- [ ] Callback routing tüm handlers
- [ ] Input handling (next_step_handler)
- [ ] Error handling & timeout
- [ ] Test (curl, Telegram bot)
- [ ] Telegram environment variables check

## 🚀 Sonraki Adımlar

**Faz 1 (MVP) — Kodlama:**
1. `telegram_bot.py` oluştur → 7 menü dosyasından kodu al
2. `webhook.py` oluştur → `web_app.py` entegrasyonu
3. `.env` check → `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `TELEGRAM_WEBHOOK_URL`
4. Test → `/start`, menü navigasyonu, callback routings

**Faz 2 (Standard) — 12 komut ekle:**
- `/pano done` → direct command (button olmadan)
- `/task [id]` → görev detayı
- `/sorun [ajan]` → ajan soruları
- [vs.]

**Faz 3 (Advanced) — Otomasyon:**
- Scheduled reports (cron)
- Webhook feedback (ajan → bot)
- Alert escalation

## 📌 Notlar

- **Geri Dön**: Her menüden `« Ana Menü` ile ana menüye dön (loop sonsuz)
- **Input Timeout**: 5 dakika sonra timeout, menüye dön
- **Pagination**: 10 kayıt göster + "... (+X daha)"
- **Emoji**: Standart Telegram emoji (✅, 🔴, 🟡, 🟢, 📊, 💬, ⚙️, vb.)
- **Parsing**: Markdown mode (`parse_mode="Markdown"`)
- **Callback Update**: Tüm callback'ler sonunda `bot.answer_callback_query(call.id)` (dropdown kapanır)
