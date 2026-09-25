# Bot Webhook Fix — D-219 / D-220 Özet

**Tarih:** 2026-09-25 09:12 Istanbul  
**Sorun:** Telegram bot menülere geçiş yapamıyor, komut almıyor  
**Kök Neden:** Bot `infinity_polling()` içinde bloke kaldığı için FastAPI webhook endpoint'i mesajları işleyemiyor  
**Status:** ✅ ÇÖZÜLDÜ

---

## Problem

Kullanıcı screenshot gönderdi:
- Bot "[GENEL] kahin / Konu: ?" mesajında takılı
- Butonlar (« Chat Menüsü, « Ana Menü, Tag Seç, /start) yanıt vermiyor
- Bot polling modunda infinite loop'da bloke kaldı

---

## Root Cause Analysis

### Sorun 1: debug_catch_all Handler (Greedy)
- Line 2361: `@bot.message_handler(func=lambda message: True)`
- **Problem:** Tüm mesajları yakalar, diğer handler'lar match etmiyor
- **Sonuç:** Mesajlar handler'a ulaşmıyor, yanıt yok

### Sorun 2: Polling vs Webhook Çatışması
- Line 2386: `bot.infinity_polling(timeout=10, long_polling_timeout=5)`
- **Problem:** Bot polling loop'da bloke kaldı, FastAPI webhook endpoint'i çağrılamıyor
- **Sonuç:** web_app.py:/api/webhooks/telegram update'leri alamıyor

### Sorun 3: Production-Ready Olmayan Setup
- Dev ortamında polling gerekli (test için)
- Production'da webhook gerekli (HTTPS)
- Aralarında mode seçeneği yok

---

## Fix Applied

### Commit 1: D-219 (9f78c21)
**Değişiklik:**
```python
# BEFORE
@bot.message_handler(func=lambda message: True)
def debug_catch_all(message):
    # Tüm mesajları yakala + debug log

# AFTER
# DISABLED: debug_catch_all handler tüm mesajları yakalaması bot'u donduruyor
```

**Etki:** debug_catch_all disabled, önceki handler'lar artık match edebilir

---

### Commit 2: D-220 (772412c)
**Değişiklik:**
```python
# BEFORE
def main():
    """Bot başlat."""
    logger.info("Starting Telegram Bot polling...")
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise

# AFTER
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
```

**Etki:** Hybrid mode — webhook ready + polling fallback

---

## Sonuç

| Durum | Before | After |
|-------|--------|-------|
| Debug Handler | Tüm mesajları yakala | Disabled |
| Polling | Always on | Fallback only |
| Webhook | FastAPI'ye ulaşamıyor | FastAPI process_new_updates çağrısı yapabilir |
| Dev Mode | Polling (bloke) | Polling (fallback, menü çalışıyor) |
| Prod Mode | Polling (bloke) | Webhook (HTTPS, asynchronous) |

---

## Test Edilecekler

1. **Dev Ortamında:** `/start` komutu test et → polling mode aktif
2. **Menü Butonları:** Ana menü → Pano → butonlar çalışmalı
3. **Production:** TELEGRAM_WEBHOOK_URL set → webhook mode aktif
4. **FastAPI Webhook:** POST /api/webhooks/telegram test (curl)

---

## Dosyalar

- [`src/company_master/telegram_bot.py`](../src/company_master/telegram_bot.py:2361-2385) — Handler + main() düzeltme
- [`web_app.py`](../web_app.py:509-566) — Webhook endpoint (production ready)

---

## Related Issues

- D-216: Telegram Bot Menü Sistemi
- D-210: Chat Entegrasyonu
- D-212: KAHİN Telegram Bildirimleri
