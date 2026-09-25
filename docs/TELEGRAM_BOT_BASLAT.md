# Telegram Bot Başlatma Rehberi

## Durum
- ✅ Web App: Çalışıyor (Port 8000)
- ✅ Webhook Endpoint: `/api/webhooks/telegram` hazır
- ⏳ Bot Süreci: Başlatılması gerekli
- ⚠️ Eksik: `telebot` kütüphanesi (kurulmak üzere)

---

## Adım 1: Token Hazırlama

### BotFather'dan Token Al
1. Telegram'da `@BotFather` bulunuz
2. `/newbot` yazınız
3. Bot adı ve kullanıcı adı belirtiniz
4. **Token al** (format: `123456:ABCDEFghijk-xyz...`)

### Token'ı Kaydet
```bash
# Kopya yap → Token alanına yapıştır
set TELEGRAM_BOT_TOKEN=<TOKEN_BURAYA>
```

---

## Adım 2: Bot Başlatma

### Terminal 2'yi Aç (Web app'ın yanında)

**CMD:**
```bash
cd "c:\Huginn Data Projesi\Huginn Data Insights"
set TELEGRAM_BOT_TOKEN=<TOKEN_BURAYA>
python -m src.company_master.telegram_bot
```

**PowerShell:**
```powershell
cd "c:\Huginn Data Projesi\Huginn Data Insights"
$env:TELEGRAM_BOT_TOKEN="<TOKEN_BURAYA>"
python -m src.company_master.telegram_bot
```

### Başarılı Başlatma İşareti
```
[✓] Bot başlangıç yapıldı
[✓] Polling aktif: Telegram mesajlarını bekliyor...
```

---

## Adım 3: Bot'u Test Et

### Telegram'da Bot'a Git
1. Token'den elde edilen **bot kullanıcı adı**'nı bul
2. Sohbet aç: `/start` yazınız

### Beklenen Menü
```
┌──────────────────────────┐
│   📊 HUGINN ANA MENU     │
├──────────────────────────┤
│  [🎯 Pano]    [💬 Chat]  │
│  [⚡ Tetikler] [📨 Mesaj] │
│  [📈 Rapor]  [⚙️ Ayarlar]│
└──────────────────────────┘
```

### API Test (curl)
```bash
curl -X GET http://localhost:8000/api/webhooks/telegram/health
```

**Beklenen Yanıt:**
```json
{
  "status": "healthy",
  "bot_token_configured": true,
  "polling_mode": true,
  "endpoint": "/api/webhooks/telegram"
}
```

---

## Adım 4: Webhook Test (İsteğe Bağlı)

Callback routing'i test etmek için:

```bash
curl -X POST http://localhost:8000/api/webhooks/telegram ^
  -H "Content-Type: application/json" ^
  -d "{\"update_id\": 12345, \"callback_query\": {\"from\": {\"id\": 999, \"first_name\": \"Test\"}, \"data\": \"menu:pano\"}}"
```

**Beklenen Yanıt:**
```json
{"ok": true, "message": "Update processed", "update_id": 12345}
```

---

## Durum Kontrolü

| Bileşen | Komutu | Beklenen |
|---------|--------|----------|
| Web App | `curl http://localhost:8000/` | 200 OK |
| Telegram Health | `curl http://localhost:8000/api/webhooks/telegram/health` | `"status": "healthy"` |
| Bot Process | Terminal'da koşu | `Polling aktif` |

---

## Sorun Giderme

### "ModuleNotFoundError: No module named 'telebot'"
```bash
pip install pytelegrambotapi
```

### "Connection refused" (Port 8000)
Web app çalışıyor mu kontrol et:
```bash
netstat -ano | findstr ":8000"
```

### Bot mesaj almıyor
1. Token doğru mu kontrol et (BotFather'dan kopyala)
2. Terminal'da polling başlatılmış mı gözle
3. Telegram'da `/start` bir kez daha gönder

### Webhook 404 "Not Found"
Web app'ı yeniden başlat:
```bash
# Terminal 1'de Ctrl+C
python web_app.py
```

---

## İlgili Belgeler
- `D-216_MENU_OZET.md` — Menü yapısı özeti
- `D-216_CALLBACK_ROUTING_TEST.md` — Callback test protokolü
- `D-217_TELEGRAM_WEBHOOK_ENTEGRASYONU_TAMAMLANDI_2026-09-25.md` — Webhook entegrasyon raporu

---

## Faz Planlama

- **Faz 1 (MVP)** ✅: Ana menü + callback routing
- **Faz 2** (Gelecek): Input handler (broadcast, targeted, alert)
- **Faz 3** (Gelecek): Slash commands (/pano done, /task, /sorun, vb.)
- **Faz 4** (Gelecek): Webhook signature verification + rate limiting
