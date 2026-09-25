# D-216: Telegram Entegrasyonu — Tam Komut Seti & Test Protokolü

## 1. Hedef
Admin panel + Telegram bot = iki taraflı senkron iş akışı
- **Admin → Telegram**: KAHİN mesajları, görev güncellemeleri
- **Telegram → Admin**: Ajan raporları, hızlı sorun bildirimi

---

## 2. Mimari Katmanlar

### 2.1 Bot Webhook Katmanı (`web_app.py`)
```
POST /api/webhooks/telegram — Telegram Bot API webhook
  ├─ Mesaj tipi belirleme
  ├─ Komut parsing
  └─ Yanıt işlemesi
```

**Komutlar**:
| Komut | Açıklama | Yanıt |
|-------|----------|-------|
| `/baslat` | Bot aktif mi kontrol et | "Bot aktif ✅" |
| `/pano` | Görev panosu özeti (tamamlandi/beklemede/bloke) | Tablo (4 bölüm) |
| `/chat` | Son 5 açık sorun | Liste (task_id, gönderen, sorun) |
| `/tetikler` | Ajan adı → o ajana ait bekleyen tetikler | JSON array |
| `/mesaj <metin>` | Broadcast mesaj gönder (kahin_gonder) | Onay + task_id |
| `/rapor` | Haftalık özet (chat + pano metrikler) | PDF/markdown |
| `/ayarlar` | Telegram ayarları (chat_id, token doğrulama) | Durum |

### 2.2 Bot Logic Katmanı (`telegram_bot.py` — YENİ)
```
telegram_bot.py:
  ├─ TelegramBot class
  │   ├─ __init__(token, chat_id)
  │   ├─ send_message(text, parse_mode="Markdown")
  │   ├─ send_table(headers, rows)
  │   ├─ handle_message(update) → komut parse
  │   └─ handle_command(cmd, args) → işlemci routing
  │
  └─ Komut işlemciler
      ├─ cmd_pano() → 4 bölüm tablo
      ├─ cmd_chat() → son 5 açık sorun
      ├─ cmd_tetikler(ajan) → tetik listesi
      ├─ cmd_mesaj(metin) → kahin_gonder() çağrı
      └─ cmd_rapor() → haftalık özet
```

### 2.3 Chat Logu Katmanı (`chat.py`)
- Zaten var: `kahin_gonder()` → Telegram gidiyor
- Yeni: `telegram_ajan_raporu()` — Telegram'dan ajan kaydı

---

## 3. Test Protokolü

### 3.1 Ön Koşul
```bash
# 1. Telegram Bot Token (BotFather'dan)
export TELEGRAM_BOT_TOKEN="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"

# 2. Telegram Chat ID (grup veya kişi)
export TELEGRAM_CHAT_ID="-1001234567890"

# 3. Webhook URL (production)
export TELEGRAM_WEBHOOK_URL="https://yourdomain.com/api/webhooks/telegram"
```

### 3.2 Test Adımları (Sıralı)

#### Test 1: Bot Sağlık Kontrolü
```bash
curl -X POST http://localhost:8000/api/webhooks/telegram \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "chat": {"id": "-1001234567890"},
      "text": "/baslat"
    }
  }'

Beklenen: "Bot aktif ✅"
```

#### Test 2: Pano Listesi (4 bölüm)
```bash
curl -X POST http://localhost:8000/api/webhooks/telegram \
  -d '{"message": {"chat": {"id": "-1001234567890"}, "text": "/pano"}}'

Beklenen:
  🟢 Tamamlandı (5)
  🟡 Beklemede (3)
  🔴 Bloke (1)
  🟣 Plan (2)
```

#### Test 3: Chat Özeti
```bash
curl -X POST http://localhost:8000/api/webhooks/telegram \
  -d '{"message": {"chat": {"id": "-1001234567890"}, "text": "/chat"}}'

Beklenen:
  1️⃣ utku → yasu | API-12: "Token expire sorunu" (acik)
  2️⃣ salih → ihsan | UI-5: "Tema rengini değiştir" (acik)
  ...
```

#### Test 4: Tetik Listesi
```bash
curl -X POST http://localhost:8000/api/webhooks/telegram \
  -d '{"message": {"chat": {"id": "-1001234567890"}, "text": "/tetikler utku"}}'

Beklenen:
  utku'nun bekleyen tetikleri:
  - T-1 (2026-09-25 15:30) → chat_acik_sorular: 2
  - T-2 (2026-09-25 14:00) → chat_acik_sorular: 0
```

#### Test 5: Mesaj Gönderme (KAHİN)
```bash
curl -X POST http://localhost:8000/api/webhooks/telegram \
  -d '{"message": {"chat": {"id": "-1001234567890"}, "text": "/mesaj Yarın maintenance yapılacak"}}'

Beklenen:
  ✅ Mesaj gönderildi! (task_id: genel)
  Telegram'da: 🟡 KAHİN Mesajı - "Yarın maintenance yapılacak"
```

#### Test 6: Tüm Chat Geçmişi (Filtreleme)
```bash
curl -X POST http://localhost:8000/api/webhooks/telegram \
  -d '{"message": {"chat": {"id": "-1001234567890"}, "text": "/chat acik"}}'

Beklenen: Sadece açık sorunlar (durum=acik)
```

### 3.3 Entegrasyon Testi
```bash
# Admin panelden mesaj gönder
# Telegram'da anında görünsün
# Telegram'dan rapor isteme
# Admin panelde görünsün
```

---

## 4. Komut Referansı (Detaylı)

### `/baslat`
- Çıkış: "Bot aktif ✅ | Token: [last4] | Chat: [chat_id]"
- Hata: "Token yok veya geçersiz"

### `/pano [filtre]`
- Filtre: `all` (default), `done`, `active`, `blocked`, `plan`
- Tablo: Task ID | Sahip | Durum | Tarih
- Örnek: `/pano blocked` → sadece bloke görevler

### `/chat [durum]`
- Durum: `all`, `acik`, `cokundurmus`, `cozuldu`
- Çıkış: JSON-style liste veya Markdown tablo
- Sıralama: timestamp DESC (yeni ilk)

### `/tetikler [ajan]`
- Ajan: kanonik ad (utku, salih, yasu, ihsan, mimir)
- Çıkış: Tetik listesi + `chat_acik_sorular` sayısı
- Hata: "Ajan bulunamadı"

### `/mesaj <metin>`
- Metin: max 500 char
- Gönderen: kahin (sabit)
- Önem: orta (default)
- Yanıt: ✅ + task_id + Telegram'a kopyası

### `/rapor [hafta/ay]`
- Varsayılan: geçen hafta
- Metriker: açık/çözüm_bekleniyor/çözüldü sayıları
- Format: Markdown tablo
- Dosya: HTML raporu indirilebilir

### `/ayarlar`
- Çıkış: Mevcut yapılandırma
- Şu an yalnızca okuma (env var)

---

## 5. Veri Akışı Diyagramı

```
Admin Panel                 Telegram Bot                  Chat Log
     │                           │                            │
     ├─ /mesaj gönder ─────────────────────────────────────────┤
     │  kahin_gonder()          webhook alır               chat_acik_sorular
     │                           │                            │
     │                    Telegram'a gönder ◄─────────────────┘
     │                   (push notification)
     │                           │
     └─ /pano iste ◄───────────── komut parse
                        │ 
                   pano çek (task_board.json)
                        │
                   Markdown tablo yap
                        │
                   Telegram'a gönder ──→ Admin telefonda gördü
```

---

## 6. Dosya Düzeni

```
src/company_master/
├── chat.py                    # kahin_gonder() zaten var
│   └─ _gonder_telegram_kahin() # D-212 (var)
│
├── telegram_bot.py            # YENİ (D-216)
│   ├─ TelegramBot class
│   ├─ komut işlemciler
│   └─ tablo formatter
│
└── orchestrator/
    └─ trigger.py              # chat_acik_sorular alanı (D-211, var)

web_app.py                      # webhook endpoint
└─ POST /api/webhooks/telegram  # YENİ (D-216)
```

---

## 7. İmplementasyon Checklist

- [ ] `telegram_bot.py` yaz (TelegramBot class)
- [ ] `/baslat`, `/pano`, `/chat` komutları
- [ ] `/tetikler`, `/mesaj`, `/rapor` komutları
- [ ] `web_app.py` webhook endpoint ekle
- [ ] Test script yaz (6 test adımı)
- [ ] Hata handling (token hatası, API timeout)
- [ ] Markdown formatting (tablo, emoji)
- [ ] Production deployment (env var kontrol)

---

## 8. Sonraki Aşamalar

**D-217**: Telegram → Admin geri bildirim (ajan raporları)
**D-218**: Scheduled reports (haftalık Telegram digest)
**D-219**: Telegram slash command autocomplete

---

## Commit
```bash
git commit -m "D-216: Telegram Bot mimarisi & test protokolü (plan)"
```
