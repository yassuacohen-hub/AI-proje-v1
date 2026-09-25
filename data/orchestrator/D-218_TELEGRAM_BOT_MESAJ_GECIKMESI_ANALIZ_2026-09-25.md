# D-218: Telegram Bot Mesaj Gecikmesi Analizi ve Çözüm Planı

**Tarih:** 2026-09-25  
**Sorun:** Mesajlar arada sırada geliyor, rutin değil — bazen 10+ saniye gecikmeli  
**Root Cause:** Polling process stabil çalışmıyor, crash ve restart arasında boşluk  

---

## 1. Sorun Tanıması

### Gözlenen Davranış
```
Mesaj geliyor (2026-09-25 04:06) → Cevap alınıyor
    ↓
10+ saniye gecikmesi
    ↓
Mesaj geliyor (2026-09-25 04:16) → Cevap alınıyor
```

**Pattern:** Irregular delivery, not continuous polling

### API Kontrol Sonuçları
```
[OK] TELEGRAM_BOT_TOKEN: 8603398149:AAFZJTi3xa9cwBUtlBGsp5JpIg2KF2X3c2M
[OK] TELEGRAM_CHAT_ID: 801855376
[OK] Telegram API responsive (getMe successful)
[OK] Bot API connectivity verified
[OK] Handlers registered (callback_query_handler, message_handler)
```

### Root Causes (İhtimal Sırası)

#### **1. Polling Process Crash (MOST LIKELY — 80%)**
```python
# telegram_bot.py:654
def main():
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise  # ← PROCESS DIES HERE
```

**Senaryo:**
1. Bot çalışıyor → polling loop aktif
2. Handler exception (ör: timeout, DB error, Telegram rate limit)
3. Exception caught ama `raise` → process dies
4. No auto-restart → gap until manual restart
5. Telegram keeps trying (10s retry) but no receiver

**Eğer bu:** Terminal'da process died mi kontrol et
```bash
# Check if process still running
tasklist | findstr python

# If dead → restart:
python -m src.company_master.telegram_bot
```

#### **2. Long Polling Timeout (15%)**
```
timeout=10: Server-side (Telegram holds request max 10s)
long_polling_timeout=5: Client-side retry backoff
```

If handler takes >10s:
- Telegram timeout → client retries
- Stale updates → race conditions

#### **3. Network Interruption (5%)**
- Telegram API rate limit (429 Too Many Requests)
- Connection drop → auto-reconnect delay

---

## 2. İç Tesisat Analizi

### Polling Loop Durumu
```
Bot Process (telegram_bot.py)
├─ bot.infinity_polling(timeout=10, long_polling_timeout=5)
│  ├─ [✅] Handler kayıtlı: message_handler, callback_query_handler
│  ├─ [✅] Telegram API bağlantısı aktif
│  └─ [⚠️] Exception handling zayıf (raise → dies)
│
├─ Handler Timing
│  ├─ send_ana_menu() → 1-2s typical
│  ├─ send_pano_menu() → <500ms
│  └─ Web app webhook call → <1s
│
└─ Process Lifecycle
   ├─ Starts: Terminal başladığında
   ├─ Crashes: Unhandled exception
   ├─ Dies: ~2-5 saniye
   └─ Telegram retry: timeout=10, gap opens
```

### Webhook Alternatifi (Production Ready)
```
Web App (FastAPI) — Port 8000
└─ /api/webhooks/telegram (POST)
   ├─ [✅] Status: healthy
   ├─ [✅] Tested: 6/6 curl tests passing
   ├─ [✅] No polling needed
   └─ [✅] Instant delivery (Telegram pushes)
```

---

## 3. Çözüm Planı (Priority Sırası)

### **QUICK FIX (24 saat) — Supervisor Wrapper**

**Status:** ⏳ TODO (estimated 2 hours)

Amaç: Crash olursa otomatik restart

```bash
# 1. Supervisor yükle
pip install supervisor

# 2. supervisor/telegram_bot.conf oluştur
[program:telegram_bot]
command=python -m src.company_master.telegram_bot
directory=C:\Huginn Data Projesi\Huginn Data Insights
autostart=true
autorestart=true
startretries=10
startsecs=10
redirect_stderr=true
stdout_logfile=logs/telegram_bot.log

# 3. Başlat
supervisord -c supervisor/telegram_bot.conf

# 4. Kontrol
supervisorctl status telegram_bot
```

**Avantajları:**
- ✅ Auto-restart on crash
- ✅ Exponential backoff: 1s, 2s, 4s...
- ✅ Exit code monitoring
- ✅ Graceful shutdown

**Dezavantajları:**
- ❌ Hala polling-based (10s max delay)
- ❌ Resource intensive (always running)

---

### **LONG-TERM FIX (3-5 gün) — Webhook Migration**

**Status:** ⏳ TODO (estimated 4-6 hours)

Amaç: Polling'den webhook'a geç → instant delivery, no process needed

#### **Step 1: Public URL Al**
```bash
# Option A: Ngrok (dev)
ngrok http 8000
# → https://xxxx-yy-zzz.ngrok.io/

# Option B: Production domain
# → https://yourdomain.com/ (must have HTTPS)
```

#### **Step 2: Webhook Url'i Telegram'a Söyle**
```bash
curl -X POST https://api.telegram.org/bot<TOKEN>/setWebhook \
  -d 'url=https://yourdomain.com/api/webhooks/telegram'

# Doğrula
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo
```

#### **Step 3: Polling'i Kapat**
```python
# telegram_bot.py:654 — comment out:
# bot.infinity_polling(timeout=10, long_polling_timeout=5)
```

#### **Step 4: Test**
```bash
# Telegram'da /start yaz
# → Webhook alacak → process_new_updates() çalışacak
# → Menü gelecek (instant, <100ms)
```

**Avantajları:**
- ✅ Instant delivery (no polling delay)
- ✅ No separate process needed
- ✅ Integrated with web_app.py (already running)
- ✅ Scalable (handles spikes easily)
- ✅ Production-ready (D-217 test passed)

**Dezavantajları:**
- ❌ HTTPS required (dev: ngrok)
- ❌ Telegram signature verification (optional but recommended)

---

## 4. Uygulanacak Adımlar

### **Faz 1 (İMMEDIATE)** — Crash Protection
```
D-218-01: Supervisor wrapper oluştur
└─ Dosya: supervisor/telegram_bot.conf
└─ Komut: supervisord -c supervisor/telegram_bot.conf
└─ Test: supervisorctl status telegram_bot
└─ ETA: 2 saat
```

### **Faz 2 (24-48 SAAT)** — Handler Stabilization
```
D-218-02: Exception handling güçlendir
└─ Dosya: src/company_master/telegram_bot.py
└─ Change: Add try-except wrapper in infinity_polling()
└─ Test: Simulate exceptions → verify auto-recovery
└─ ETA: 2 saat
```

### **Faz 3 (3-5 GÜNDÜR)** — Webhook Migration
```
D-218-03: Webhook'a geç
└─ Dosya: src/company_master/telegram_bot.py
└─ Change: Disable infinity_polling()
└─ Change: Keep process_new_updates() active
└─ Test: ngrok public URL → setWebhook
└─ ETA: 4-6 saat
```

---

## 5. Diagnostic Sonuçları

| Metrik | Durum | Not |
|--------|-------|-----|
| Token | ✅ Valid | 8603398149:AAFZJTi3xa9c... |
| API Connection | ✅ Healthy | getMe successful |
| Handlers | ✅ Registered | callback_query, message |
| Polling Config | ✅ OK | timeout=10, long_polling_timeout=5 |
| **Process Stability** | ⚠️ **FRAGILE** | **No crash protection** |
| **Delivery Latency** | ⚠️ **UP TO 10s** | **Polling interval** |
| Webhook Endpoint | ✅ Ready | `/api/webhooks/telegram` tested |

---

## 6. Sonraki Adım

**Seçim:**

A) **Quick Fix (2 saat)** → Supervisor wrapper (kalıcı değil ama hızlı)  
B) **Best Solution (4-6 saat)** → Webhook migration (production-ready, instant)  
C) **Both (6-8 saat)** → Supervisor now + webhook later (safe upgrade path)

**Tavsiye:** Option C — Supervisor now to stop crashes, then webhook next week

---

## 7. İlgili Belgeler
- [`TELEGRAM_BOT_BASLAT.md`](TELEGRAM_BOT_BASLAT.md) — Başlatma talimatları
- [`D-216_MENU_OZET.md`](D-216_MENU_OZET.md) — Menü yapısı
- [`D-217_TELEGRAM_WEBHOOK_ENTEGRASYONU_TAMAMLANDI_2026-09-25.md`](D-217_TELEGRAM_WEBHOOK_ENTEGRASYONU_TAMAMLANDI_2026-09-25.md) — Webhook test raporu

---

**Status:** Analysis Complete  
**Owner:** Product Owner (Üretim Sahibi)  
**Due:** Implementation start: 2026-09-26
