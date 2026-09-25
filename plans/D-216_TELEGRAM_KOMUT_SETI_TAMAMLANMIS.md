# D-216: Telegram Komut Seti — Tüm Operasyonlar (Seçili)

## 1. Telegram Komut Kategorileri

### **A. YÖNETİM KOMUTLARI** (Admin panel → Telegram)

| Komut | Parametreler | Yanıt | Kullanım |
|-------|--------------|-------|----------|
| `/baslat` | — | "Bot aktif ✅ \| Token: [***] \| Chat: [ID]" | Bot sağlık kontrolü |
| `/ayarlar` | — | Mevcut yapılandırma (token, chat_id, webhook) | Setup kontrol |
| `/help` | — | Tüm komutlar + örnekler | Yardım |

---

### **B. PANO & TASK KOMUTLARI** (Görev takibi)

| Komut | Parametreler | Yanıt | Kullanım |
|-------|--------------|-------|----------|
| `/pano` | `[filtre]` | 4 bölüm tablo (tamamlandi/beklemede/bloke/plan) | Pano genel görünüm |
| `/pano done` | — | ✅ Tamamlanan görevler (son 10) | Review edilen işler |
| `/pano active` | — | 🟡 Aktif görevler (sahip dahil) | Şu an yapılanlar |
| `/pano blocked` | — | 🔴 Bloke görevler + neden | Engellenenler |
| `/pano plan` | — | 🟣 Planlı görevler (başlamayan) | Gelecek işler |
| `/task <ID>` | `task_id` | Görev detayı (sahip, durum, talimat, deadline) | Tek görev sorgusu |
| `/tasklar <ajan>` | `ajan_adı` | O ajan'ın tüm görevleri (aktif + done) | Ajan workload |

---

### **C. CHAT & SORUN KOMUTLARI** (Ajan iletişim)

| Komut | Parametreler | Yanıt | Kullanım |
|-------|--------------|-------|----------|
| `/chat` | `[durum]` | Son 5 açık sorun (task, gönderen, metin) | Chat özeti |
| `/chat acik` | — | Sadece açık sorunlar (durum=acik) | Bekleyen sorunlar |
| `/chat cokundurmus` | — | Çözüm bekleniyor (durum=cokundurmus) | Yanıt bekleyenler |
| `/chat cozuldu` | — | Çözüldü sorunlar (durum=cozuldu) | Kapalı sorunlar |
| `/sorun <task_id>` | — | O task ile ilgili tüm chat mesajları | Task-specific chat |
| `/sorun <ajan>` | — | O ajan'a yöneltilmiş açık sorunlar | Ajan-specific sorular |
| `/mesaj <metin>` | `<metin>` | ✅ Broadcast (kahin_gonder) → chat + Telegram | KAHİN bildirimi |
| `/mesaj-ajan <ajan> <metin>` | — | Özel mesaj (sadece bir ajana) | Targeted message |

---

### **D. TETIK KOMUTLARI** (Posta kutusu)

| Komut | Parametreler | Yanıt | Kullanım |
|-------|--------------|-------|----------|
| `/tetikler <ajan>` | `ajan_adı` | Bekleyen tetikler + chat_acik_sorular sayısı | Ajan postası |
| `/tetikler` | — | Tüm ajanlar (ajan: tetik_sayısı) | Global postalar |
| `/tetik-ac <ajan>` | — | Detaylı tetik listesi (task_id, talimat, tarih) | Tetik detayları |

---

### **E. RAPOR KOMUTLARI** (Analitik & özet)

| Komut | Parametreler | Yanıt | Kullanım |
|-------|--------------|-------|----------|
| `/rapor` | `[hafta/ay]` | Haftalık özet (açık/çözüm_bekl/çözüldü metrikleri) | Haftalık özet |
| `/rapor hafta` | — | Geçen haftanın chat + pano özeti | 1 haftalık özet |
| `/rapor ay` | — | Geçen ayın chat + pano özeti | 1 aylık özet |
| `/metrik` | — | KPI özeti (toplam görev, tamamlanma oranı, avg tepki zamanı) | Performans metrikleri |
| `/ajan-rapor <ajan>` | — | Ajan özeti (görev sayısı, açık sorun, son aktivite) | Ajan performansı |

---

### **F. ARAMA & FİLTRE KOMUTLARI** (Sorgu)

| Komut | Parametreler | Yanıt | Kullanım |
|-------|--------------|-------|----------|
| `/ara <arama_terimi>` | `keyword` | Task board + chat'te eşleşen sonuçlar | Tam metin arama |
| `/ara-task <durum>` | `done/aktif/plan/bloke` | Filtreli görev listesi | Task duruma göre |
| `/ara-chat <ajan>` | `ajan_adı` | O ajan'ın tüm chat mesajları (gönderen/alıcı) | Ajan chat geçmişi |

---

### **G. HİZLİ KOMUTLAR** (Kısayol)

| Komut | Parametreler | Yanıt | Kullanım |
|-------|--------------|-------|----------|
| `/q` | — | Quick status (bloke sayısı + acik_sorunlar) | 1 satırlık durum |
| `/acil` | — | Tüm kritik işler (pano + chat) | Emergency filter |
| `/ozet` | — | 1 min özet (pano + chat + tetik metrikleri) | Dashboard quick view |

---

## 2. Komut Kullanım Örnekleri

```
Kullanıcı: /pano
Bot: 
  🟢 Tamamlandı: 12 görev
  🟡 Beklemede: 5 görev (davulcu, yasu, utku çalışıyor)
  🔴 Bloke: 2 görev (API-12 bekleniyor)
  🟣 Plan: 3 görev (Sonraki sprint)

---

Kullanıcı: /chat acik
Bot:
  1. utku → yasu (API-12): "Token expire hatası" [15:30]
  2. salih → ihsan (UI-5): "Tema renklerini ayarla" [14:15]
  3. yasu → mimir (DOC-8): "Dökümanları güncelle" [13:00]

---

Kullanıcı: /tetikler utku
Bot:
  utku'nun bekleyen tetikleri:
  • T-1 (API-12) — 2 açık soru
  • T-2 (UI-3) — 0 açık soru
  Toplam: 2 tetik, 2 açık soru

---

Kullanıcı: /mesaj Yarın 14:00'de maintenance
Bot:
  ✅ Broadcast mesajı gönderildi!
  Chat logu: kahin → * (genel)
  Telegram: 🟡 KAHİN Mesajı - "Yarın 14:00'de maintenance"

---

Kullanıcı: /rapor hafta
Bot:
  📊 Haftalık Özet (2026-09-19 → 2026-09-25)
  
  Chat:
  • Açık: 8 sorun
  • Çözüm Bekleniyor: 3 sorun
  • Çözüldü: 12 sorun
  
  Pano:
  • Tamamlandi: 8 görev
  • Aktif: 5 görev
  • Bloke: 2 görev
```

---

## 3. Komut Seçimi — İş Gücüne Göre

### **MİNİMAL SETUP** (Sadece gerekli)
```
/baslat        → Kontrol
/pano          → Pano özeti
/chat          → Açık sorunlar
/tetikler      → Ajan postası
/mesaj         → Broadcast
```
**5 komut — MVP**

---

### **STANDART SETUP** (Haftalık iş akışı)
```
+ /pano done        → Review görevleri
+ /pano blocked     → Engellenenler
+ /task             → Task detayı
+ /sorun            → Task-specific chat
+ /rapor hafta      → Haftalık özet
+ /ajan-rapor       → Ajan performansı
```
**11 komut — Standard**

---

### **FULL SETUP** (Detaylı operasyonlar)
```
+ /ara-task         → Görev sorgular
+ /ara-chat         → Chat geçmişi
+ /mesaj-ajan       → Targeted message
+ /tetik-ac         → Tetik detayları
+ /metrik           → KPI
+ /q                → Quick status
+ /ozet             → 1 min view
```
**18 komut — Advanced**

---

## 4. Implementasyon Katmanları

### **Katman 1: Webhook (web_app.py)**
```python
@app.post("/api/webhooks/telegram")
def telegram_webhook(update: dict) -> dict:
    message_text = update["message"]["text"]
    chat_id = update["message"]["chat"]["id"]
    
    if message_text.startswith("/"):
        komut, *args = message_text.split()
        yanit = router(komut, args, chat_id)
        send_telegram(yanit, chat_id)
    
    return {"ok": True}
```

### **Katman 2: Router (telegram_bot.py)**
```python
router = {
    "/baslat": cmd_baslat,
    "/pano": cmd_pano,
    "/chat": cmd_chat,
    "/tetikler": cmd_tetikler,
    "/mesaj": cmd_mesaj,
    "/rapor": cmd_rapor,
    "/task": cmd_task,
    "/tasklar": cmd_tasklar,
    "/sorun": cmd_sorun,
    "/ajan-rapor": cmd_ajan_rapor,
    "/ara": cmd_ara,
    "/metrik": cmd_metrik,
    "/q": cmd_quick_status,
    "/ozet": cmd_ozet,
    ...
}
```

### **Katman 3: Komut İşlemciler**
```python
def cmd_pano(args, chat_id):
    filtre = args[0] if args else "all"
    pano = read_task_board()
    if filtre != "all":
        pano = [t for t in pano if t["durum"] == filtre]
    return format_pano_table(pano)

def cmd_chat(args, chat_id):
    durum = args[0] if args else "all"
    chat = read_chat_log()
    if durum != "all":
        chat = [s for s in chat if s["durum"] == durum]
    return format_chat_table(chat[:5])
```

---

## 5. Test Protokolü (Seçili komutlar)

### **Test 1: Pano Komutları**
```bash
/pano           # 4 bölüm
/pano done      # Tamamlanmışlar
/pano blocked   # Engellenenler
```

### **Test 2: Chat Komutları**
```bash
/chat           # Son 5 açık
/chat acik      # Nur açık
/sorun API-12   # Task-specific
```

### **Test 3: Tetik Komutları**
```bash
/tetikler utku      # Utku'nun postası
/tetikler           # Global postalar
```

### **Test 4: Mesaj Komutları**
```bash
/mesaj Maintenance başlıyor      # Broadcast
/mesaj-ajan utku "Urgente"       # Targeted
```

### **Test 5: Rapor Komutları**
```bash
/rapor hafta       # Haftalık
/rapor ay          # Aylık
/metrik            # KPI
```

---

## 6. Dosya Düzeni & Geliştirilecek

```
src/company_master/
├── telegram_bot.py              # YENİ (18 komut işlemcisi)
│   ├─ class TelegramBot
│   ├─ def router(komut, args, chat_id) → işlemci mapping
│   └─ 18 komut fonksiyonu (cmd_*)
│
├── chat.py                      # VAR (kahin_gonder var)
├── orchestrator/
│   ├─ trigger.py               # VAR (chat_acik_sorular var)
│   └─ task_board.py            # VAR (task_board.json oku)
│
web_app.py                       # UPDATE
└─ @app.post("/api/webhooks/telegram")  # YENİ endpoint
```

---

## 7. Veri Kaynakları

| Komut Grubu | Veri Kaynağı | Dosya |
|-------------|--------------|-------|
| Pano | task_board.json | `data/orchestrator/task_board.json` |
| Chat | JSONL log | `data/orchestrator/ajan-chat.jsonl` |
| Tetik | JSONL posta | `data/orchestrator/{ajan}-tetikler.jsonl` |
| Rapor | Task + Chat | Kombinasyon |

---

## 8. İmplementasyon Checklist

### **Faz 1: Minimal (MVP)**
- [ ] `/baslat` — bot sağlık
- [ ] `/pano` — 4 bölüm tablo
- [ ] `/chat` — son 5 açık
- [ ] `/tetikler` — ajan postası
- [ ] `/mesaj` — KAHİN broadcast

### **Faz 2: Standard**
- [ ] `/pano done`, `/pano blocked` — filtreler
- [ ] `/task` — task detayı
- [ ] `/sorun` — task-specific chat
- [ ] `/rapor hafta` — haftalık özet
- [ ] `/ajan-rapor` — ajan performansı

### **Faz 3: Advanced**
- [ ] `/ara-task`, `/ara-chat` — arama
- [ ] `/mesaj-ajan` — targeted
- [ ] `/tetik-ac` — tetik detayları
- [ ] `/metrik` — KPI
- [ ] `/q`, `/ozet` — kısayollar

---

## 9. Seçim: Hangileri Başlayalım?

**Sizin için önerim:**

1. **MVP** (Faz 1) başlatın — 5 komut, 2 gün
2. **Standard** (Faz 2) ekleyin — 5 komut, 1 gün
3. **Advanced** (Faz 3) optional — ihtiyaç olursa

**Sonuç**: 15 komut, tam iş akışı senkronizasyonu.

---

## Commit
```bash
git commit -m "D-216: Telegram komut seti tasarımı (18 komut, 3 faz)"
```
