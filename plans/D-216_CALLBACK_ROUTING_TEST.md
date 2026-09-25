# D-216: Telegram Callback Routing — Test Protokolü

## 🧪 Test Ortamı Setup

### 1. Bot Başlat (Local)

```bash
# .env dosyasına ekle
TELEGRAM_BOT_TOKEN=<bot-token>
TELEGRAM_CHAT_ID=<your-chat-id>
TELEGRAM_WEBHOOK_URL=http://localhost:8000/api/webhooks/telegram

# telegram_bot.py çalıştır
python src/company_master/telegram_bot.py
```

### 2. Telegram Bot'a Yazı Gönder

```
/start
```

Bot yanıt verir: Ana Menü (6 buton + 3 hızlı)

---

## 📋 Callback Routing Test Matrisi

### TEST 1: Ana Menü → Submenüler (6 Test)

| # | Buton | callback_data | Beklenen | HTTP Simülasyon |
|---|-------|---------------|----------|-----------------|
| 1.1 | 📊 Pano | `menu:pano` | Pano Menüsü | POST /webhook ← pano:pano_menu |
| 1.2 | 💬 Chat | `menu:chat` | Chat Menüsü | POST /webhook ← menu:chat_menu |
| 1.3 | ✉️ Tetikler | `menu:tetikler` | Tetikler Menüsü | POST /webhook ← menu:tetikler_menu |
| 1.4 | 📝 Mesaj | `menu:mesaj` | Mesaj Menüsü | POST /webhook ← menu:mesaj_menu |
| 1.5 | 📈 Rapor | `menu:rapor` | Rapor Menüsü | POST /webhook ← menu:rapor_menu |
| 1.6 | ⚙️ Ayarlar | `menu:ayarlar` | Ayarlar Menüsü | POST /webhook ← menu:ayarlar_menu |

### TEST 2: Hızlı Erişim (3 Test)

| # | Buton | callback_data | Beklenen | HTTP Simülasyon |
|---|-------|---------------|----------|-----------------|
| 2.1 | 🚨 ACİL | `quick:urgent` | Bloke Görevler | POST /webhook ← quick:urgent_tasks |
| 2.2 | ⚡ Q | `quick:q` | Soru Özeti | POST /webhook ← quick:q_summary |
| 2.3 | 📌 ÖZET | `quick:summary` | Günlük Özet | POST /webhook ← quick:daily_summary |

### TEST 3: Pano Menüsü (7 Test)

| # | Buton | callback_data | Beklenen | Veri |
|---|-------|---------------|----------|------|
| 3.1 | ✅ Tamamlandı | `pano:done` | Görevler (durum=done) | 5-10 kayıt |
| 3.2 | ✔️ Aktif | `pano:active` | Görevler (durum=working) | 3-5 kayıt |
| 3.3 | 🔴 Bloke | `pano:blocked` | Görevler (durum=blocked) | 1-3 kayıt |
| 3.4 | 📋 Plan | `pano:plan` | Görevler (durum=plan) | 2-4 kayıt |
| 3.5 | 🔍 Tümü | `pano:all` | Tüm Görevler | 20+ kayıt |
| 3.6 | 👤 Ajan Ara | `pano:ajan_input` | Input Prompt | "Ajan adını girin" |
| 3.7 | « Ana Menü | `menu:ana` | Ana Menü | 6 buton + 3 hızlı |

### TEST 4: Chat Menüsü (8 Test)

| # | Buton | callback_data | Beklenen | Veri |
|---|-------|---------------|----------|------|
| 4.1 | 🔴 Açık | `chat:acik` | Sorunlar (durum=açık) | 3-8 kayıt |
| 4.2 | 🟡 Çözüm Bekl. | `chat:cokundurmus` | Sorunlar (durum=cokundurmus) | 2-5 kayıt |
| 4.3 | 🟢 Çözüldü | `chat:cozuldu` | Sorunlar (durum=cozuldu) | 20+ kayıt |
| 4.4 | 🔍 Tümü | `chat:all` | Tüm Sorunlar | 25+ kayıt |
| 4.5 | 🔎 Arama | `chat:ara_input` | Input Prompt | "Arama terimini girin" |
| 4.6 | 👤 Ajan Sorusu | `chat:ajan_input` | Input Prompt | "Ajan adını girin" |
| 4.7 | 📢 Broadcast | `chat:broadcast` | Input Prompt | "Mesajınızı yazın" |
| 4.8 | « Ana Menü | `menu:ana` | Ana Menü | 6 buton + 3 hızlı |

### TEST 5: Tetikler Menüsü (7 Test)

| # | Buton | callback_data | Beklenen | Veri |
|---|-------|---------------|----------|------|
| 5.1 | 👨 Utku | `tetikler:utku` | Tetikler (ajan=utku) | 1-3 kayıt |
| 5.2 | 👨 Salih | `tetikler:salih` | Tetikler (ajan=salih) | 1-2 kayıt |
| 5.3 | 👨 Yasu | `tetikler:yasu` | Tetikler (ajan=yasu) | 0-2 kayıt |
| 5.4 | 👨 İhsan | `tetikler:ihsan` | Tetikler (ajan=ihsan) | 0-1 kayıt |
| 5.5 | 👨 Mimir | `tetikler:mimir` | Tetikler (ajan=mimir) | 0-1 kayıt |
| 5.6 | 🔍 Tümü | `tetikler:all` | Tüm Tetikler (Özet) | Ajan × Tetik sayısı |
| 5.7 | « Ana Menü | `menu:ana` | Ana Menü | 6 buton + 3 hızlı |

### TEST 6: Mesaj Menüsü (5 Test)

| # | Buton | callback_data | Beklenen | Akış |
|---|-------|---------------|----------|------|
| 6.1 | 📢 Broadcast | `mesaj:broadcast` | Input Prompt | Mesaj yaz → chat.kahin_gonder() |
| 6.2 | 👤 Targeted | `mesaj:targeted` | Ajan Seçim Menüsü | 5 ajan buton |
| 6.3 | 🎯 Tag Seç | `mesaj:tag` | [Henüz Aktif Değil] | Placeholder |
| 6.4 | 🔔 Uyarı | `mesaj:alert` | Uyarı Şablonları | 4 şablon buton |
| 6.5 | « Ana Menü | `menu:ana` | Ana Menü | 6 buton + 3 hızlı |

**Targeted Akış:**
```
Tıkla: 👤 Targeted
  ↓ [mesaj:targeted]
Menü: 5 Ajan Seçim
  ↓ [Tıkla: 👨 Utku]
  ↓ [mesaj_targeted:utku]
Input: Mesaj Prompt
  ↓ [Yaz: "API-12 hakkında..."]
Sonuç: chat.ac() → Mesaj kaydedildi
```

**Uyarı Akışı:**
```
Tıkla: 🔔 Uyarı
  ↓ [mesaj:alert]
Menü: 4 Şablon
  ↓ [Tıkla: 🚨 Sistem Hatası]
  ↓ [mesaj_alert:sistem_hatasi]
Input: Ek Not Prompt
  ↓ [Yaz: "DB bağlantısı koptu"]
Sonuç: chat.kahin_gonder(onem=kritik) → Uyarı gönderildi
```

### TEST 7: Rapor Menüsü (7 Test)

| # | Buton | callback_data | Beklenen | Veri |
|---|-------|---------------|----------|------|
| 7.1 | 📅 Hafta | `rapor:hafta` | Haftalık Rapor | Metrikler + Trend |
| 7.2 | 📅 Ay | `rapor:ay` | [Henüz Aktif Değil] | Placeholder |
| 7.3 | 📅 YTD | `rapor:ytd` | [Henüz Aktif Değil] | Placeholder |
| 7.4 | 👤 Ajan Bazlı | `rapor_detail:ajan` | [Henüz Aktif Değil] | Placeholder |
| 7.5 | 📊 KPI | `rapor_detail:kpi` | KPI Raporu | Performance, Quality, Agent KPI |
| 7.6 | 📈 Trend | `rapor_detail:trend` | Trend Raporu | 4 haftalık trend grafikleri |
| 7.7 | 📋 Özet | `rapor_detail:ozet` | Özet Raporu | Günlük hedefler + Gerçekleşme |

### TEST 8: Ayarlar Menüsü (10 Test)

| # | Buton | callback_data | Beklenen | Veri |
|---|-------|---------------|----------|------|
| 8.1 | 🔌 Bağlantı Kontrol | `ayarlar:baglanti` | Health Check | API latency, DB status, uptime |
| 8.2 | 🔑 Token Doğrula | `ayarlar:token` | Token Status | Permissions, validity, bot info |
| 8.3 | 📋 Bot Bilgisi | `ayarlar:info` | Bot Info | Version, stats, features, integrations |
| 8.4 | 🔔 Bildirimler | `ayarlar:bildirim` | [Henüz Aktif Değil] | Placeholder |
| 8.5 | 📧 E-posta Ayarı | `ayarlar:email` | [Henüz Aktif Değil] | Placeholder |
| 8.6 | 🎯 Tercihler | `ayarlar:tercih` | [Henüz Aktif Değil] | Placeholder |
| 8.7 | ❓ Yardım | `ayarlar:yardim` | Yardım & Komutlar | Komut referansı |
| 8.8 | 📝 Changelog | `ayarlar:changelog` | [Henüz Aktif Değil] | Placeholder |
| 8.9 | 📞 Destek | `ayarlar:destek` | Destek İletişimi | E-posta adresleri |
| 8.10 | « Ana Menü | `menu:ana` | Ana Menü | 6 buton + 3 hızlı |

---

## 🧬 HTTP Simülasyon (Webhook Test)

### Mock Update JSON (Callback)

```json
{
  "update_id": 123456789,
  "callback_query": {
    "id": "callback_query_1",
    "from": {
      "id": 987654321,
      "is_bot": false,
      "first_name": "Admin",
      "username": "admin_user"
    },
    "chat_instance": "1234567890",
    "data": "menu:pano",
    "message": {
      "message_id": 100,
      "date": 1695700000,
      "chat": {
        "id": 987654321,
        "type": "private"
      }
    }
  }
}
```

### Webhook POST Testi (curl)

**1. Ana Menü → Pano**

```bash
curl -X POST http://localhost:8000/api/webhooks/telegram \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123456789,
    "callback_query": {
      "id": "callback_1",
      "from": {"id": 987654321, "first_name": "Admin"},
      "chat_instance": "1234567890",
      "data": "menu:pano",
      "message": {"message_id": 100, "chat": {"id": 987654321}}
    }
  }'
```

**Beklenen Yanıt:**
```
✅ Pano Menüsü mesajı gönder
   [✅ Tamamlandı] [✔️ Aktif]
   [🔴 Bloke] [📋 Plan]
   [👤 Ajan Ara] [« Ana Menü]
```

---

**2. Pano → Tamamlanan Görevler**

```bash
curl -X POST http://localhost:8000/api/webhooks/telegram \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123456790,
    "callback_query": {
      "id": "callback_2",
      "from": {"id": 987654321, "first_name": "Admin"},
      "chat_instance": "1234567890",
      "data": "pano:done",
      "message": {"message_id": 101, "chat": {"id": 987654321}}
    }
  }'
```

**Beklenen Yanıt:**
```
✅ Tamamlandı Görevler (12)

1. API-15 [utku]
2. UI-8 [salih]
...
```

---

**3. Chat → Açık Sorunlar + Broadcast Input**

```bash
curl -X POST http://localhost:8000/api/webhooks/telegram \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123456791,
    "callback_query": {
      "id": "callback_3",
      "from": {"id": 987654321, "first_name": "Admin"},
      "chat_instance": "1234567890",
      "data": "chat:broadcast",
      "message": {"message_id": 102, "chat": {"id": 987654321}}
    }
  }'
```

**Beklenen Yanıt:**
```
📢 **KAHİN Mesajı Gönder**

Mesajınızı yazın (max 500 karakter):
(İpucu: /cancel yazarak iptal edebilirsiniz)
```

---

**4. Tetikler → Utku**

```bash
curl -X POST http://localhost:8000/api/webhooks/telegram \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123456792,
    "callback_query": {
      "id": "callback_4",
      "from": {"id": 987654321, "first_name": "Admin"},
      "chat_instance": "1234567890",
      "data": "tetikler:utku",
      "message": {"message_id": 103, "chat": {"id": 987654321}}
    }
  }'
```

**Beklenen Yanıt:**
```
📬 Utku Posta Kutusu (2)

1. 📬 T-1 (API-12)
   Talimat: "API v2 uyumlu hale getir"
   ⚠️ 2 açık soru
   
2. 📬 T-2 (UI-3)
   Talimat: "Dark theme ekle"
   ✅ 0 açık soru
```

---

**5. Rapor → KPI**

```bash
curl -X POST http://localhost:8000/api/webhooks/telegram \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123456793,
    "callback_query": {
      "id": "callback_5",
      "from": {"id": 987654321, "first_name": "Admin"},
      "chat_instance": "1234567890",
      "data": "rapor_detail:kpi",
      "message": {"message_id": 104, "chat": {"id": 987654321}}
    }
  }'
```

**Beklenen Yanıt:**
```
📊 **KPI Analizi**

├─ ⚡ **Performans KPI**
│  • Ortalama Tamamlama: 2.3 gün
│  • Ortalama Cevap: 4.2 saat
...
```

---

**6. Ayarlar → Bağlantı Kontrol**

```bash
curl -X POST http://localhost:8000/api/webhooks/telegram \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123456794,
    "callback_query": {
      "id": "callback_6",
      "from": {"id": 987654321, "first_name": "Admin"},
      "chat_instance": "1234567890",
      "data": "ayarlar:baglanti",
      "message": {"message_id": 105, "chat": {"id": 987654321}}
    }
  }'
```

**Beklenen Yanıt:**
```
🔌 **Bot Bağlantı Durumu**

✅ **Sistem Bağlantıları**
├─ Telegram Bot API: ✅ Aktif (268ms)
├─ Chat Sistemi: ✅ Aktif (45ms)
...
```

---

## ✅ Test Kontrol Listesi

- [ ] TEST 1: Ana Menü → 6 Submenü (tüm menüler açılıyor)
- [ ] TEST 2: Hızlı Erişim → 3 Sonuç (urgent, Q, summary)
- [ ] TEST 3: Pano → Durum Filtreleri (done, active, blocked, plan, all)
- [ ] TEST 4: Chat → Sorun Filtreleri + Broadcast (açık, bekleyen, çözüldü, broadcast input)
- [ ] TEST 5: Tetikler → Ajan Seçimi (5 ajan + all)
- [ ] TEST 6: Mesaj → Broadcast + Targeted + Uyarı (3 akış)
- [ ] TEST 7: Rapor → Hafta + KPI + Trend + Özet (4 tip)
- [ ] TEST 8: Ayarlar → Durum + Token + Info + Yardım (4 aktif)
- [ ] Geri Dön: « Ana Menü → Ana Menü (tüm menülerden loop)
- [ ] Input Handling: /start → Ana Menü (başlangıç)
- [ ] Timeout: 5dk sonra menüye dön
- [ ] Error Handling: Invalid callback → Hatanız var mesajı

---

## 🎯 Test Sonucu Kriterleri

✅ **PASS:**
- Tüm callback'ler doğru handler'a gidiyor
- Veri doğru şekilde DB'den okunuyor
- Menü navigasyonu loop'suz ve akıcı
- Geri dön butonları çalışıyor

❌ **FAIL:**
- Callback timeout (5s+)
- Yanlış menü açılıyor
- Veri eksik/hatalı
- Geri dön butonları çalışmıyor
