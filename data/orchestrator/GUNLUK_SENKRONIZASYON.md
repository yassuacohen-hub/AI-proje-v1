# Günlük Senkronizasyon Planı (2026-09-25)

**Başlangıç:** 2026-09-25 08:54:53 UTC  
**Zaman Dilimi:** Europe/Istanbul (UTC+3)  
**Tetik Saatleri:** 09:00, 14:00, 19:00 Istanbul  

---

## 1. Senkronizasyon Döngüsü

### 1.1 Sabah Süresi (09:00 Istanbul / 06:00 UTC)
- [ ] task_board.json durum kontrol (30 saniye)
- [ ] Bekleyen görevler tespit et (todo → in_progress geçişler)
- [ ] Chat kanalı açık sorular kontrol
- [ ] Tetikle: UTKU-01, YASU-01, ORCH-01 başlangıç
- [ ] Rapor: Günün hedefi + risk özeti

### 1.2 Öğleden Sonra (14:00 Istanbul / 11:00 UTC)
- [ ] Midway progress kontrol (aktif görevlerin % tamamlanma)
- [ ] Bloke görevler tespit (in_progress → done geçişler)
- [ ] Chat bulgular oku (Telegram: @KAHİN grubu)
- [ ] Yenileme trigger (eğer P0/P1 blokaj varsa)

### 1.3 Akşam (19:00 Istanbul / 16:00 UTC)
- [ ] Günlük kapanış kontrol (done görevler doğrula)
- [ ] Teslim raporları topla (chat bulgularından)
- [ ] Ertesi gün hedefi set et
- [ ] Haftasonu inceleme hazırlık (Perşembe akşamı)

---

## 2. Görev Tetikleme Matrisi

| Saat | UTKU | YASU | ORKESTRATOR | Hedef |
|------|------|------|-------------|-------|
| 09:00 | UTKU-01 başla | YASU-01 başla | ORCH-01 başla | İlk 3 görev başlangıç |
| 14:00 | UTKU-02 hazırla | YASU-02 hazırla | ORCH-02 hazırla | Paralel iş başlat |
| 19:00 | UTKU-01 kontrol | YASU-01 kontrol | ORCH-01 kontrol | Teslim doğrulama |

**Görev Siradaki Sira (Dependency):**
```
UTKU-01 (VERI-ADMIN-AKTIVITE-LOG-13) ✅ done
  ↓
UTKU-02 (API-ADMIN-AKTIVITE-YAZ-14) ✅ done [depend: UTKU-01]
  ↓
UTKU-03 (API-ADMIN-CHURN-3SINYAL-16) ✅ done [depend: UTKU-02]
  ↓
UTKU-04 (UI-ADMIN-LTV-CAC-27) ⏳ aktif [depend: UTKU-03]
  ↓
UTKU-05 (API-ADMIN-MFA-26) 🔴 review [depend: UTKU-04]
```

---

## 3. Chat Entegrasyonu & Bulguları Belgeleme

### 3.1 Chat Kanal Kurgusu
- **KAHİN Grubu (Telegram):** @KAHİN, @Utku, @Yasu, @Orkestrator, @İhsan, @Mimir
- **İçerik:** Tetik uyarıları, bloke bildirimleri, teslim onayları
- **Format:** Standart `chat_brief_template.md`

### 3.2 Bulguları Kaydetme Süreci

Her görev teslimi sonrası:

1. **Chat Kontrol** (15 dakika)
   - Ajan tarafından bulgular yazdı mı? (Telegram @KAHİN mesajı)
   - Açık sorular var mı? (Blocking issues?)

2. **Bulgular Dosyası Oluştur**
   ```
   data/orchestrator/{task_id}_bulgular_{date}_{ajan}.md
   ```
   
   İçerik:
   - Çalışma özeti (2-3 cümle)
   - Kabul kriterleri durumu (✅/❌)
   - Açık sorular varsa listeyle
   - Tavsiye edilen sonraki adım

3. **Raporlar Dosyası Oluştur**
   ```
   data/orchestrator/{task_id}_rapor_{date}_{ajan}.md
   ```
   
   İçerik:
   - Yapılan değişiklikleri listele
   - Test sonuçları (pytest/doctest geçişler)
   - Kod örneği (kritik satır numaraları)
   - Proof-of-Work linki

---

## 4. Senkronizasyon Otomasyonu

### 4.1 Python Tetik Script
```python
# scripts/sync_gunluk.py
import json
from datetime import datetime
from pathlib import Path

def sync_task_board():
    """Günlük senkronizasyon: durum kontrol + tetikleme."""
    board_path = Path("data/orchestrator/task_board.json")
    data = json.load(board_path.open())
    
    # Durum özetin
    todo = [t for t in data if t["durum"] == "todo"]
    aktif = [t for t in data if t["durum"] in ["in_progress", "aktif"]]
    done = [t for t in data if t["durum"] == "done"]
    
    print(f"Görev Durumu: {len(todo)} TODO, {len(aktif)} Aktif, {len(done)} Tamamlandı")
    
    # Tetik P0/P1 görevleri
    untuk_tetikle = [t for t in todo if t["oncelik"] in ["P0", "P1"]][:3]
    for task in untuk_tetikle:
        print(f"Tetik: {task['task_id']} ({task['sahip']})")

if __name__ == "__main__":
    sync_task_board()
```

### 4.2 Cron Job (Linux/macOS)
```bash
# /etc/cron.d/huginn-sync
0 6,11,16 * * * cd /app && python scripts/sync_gunluk.py >> logs/sync.log 2>&1
```

### 4.3 Windows Task Scheduler
```powershell
$action = New-ScheduledTaskAction -Execute "python" -Argument "scripts/sync_gunluk.py"
$trigger = New-ScheduledTaskTrigger -At 09:00, 14:00, 19:00 -Daily
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "HuginnSync"
```

---

## 5. Bloke Görevler & Escalation

### 5.1 Risk Tetikler (Otomatik)
- **P0 + 2h timeout:** KAHİN'e uyarı gönder
- **P1 + 4h timeout:** Ajan değiştir (fallback)
- **Dependency missing:** Rapor yaz, schedule çek

### 5.2 Manuel Intervention
- API-ADMIN-MFA-26: 5 kabul kriteri eksik → Utku'ya geri ata (review → todo)
- UI-ADMIN-KVKK-MODU-26: KAHİN elle onay → Bekle signal

---

## 6. Haftalık Özet (Perşembe 19:00)

Hedef Tarih: **2026-10-02 19:00 Istanbul**

İçerik:
- 15 görevin durumu (özetlenmiş tablo)
- Geçiş oranları (%)
- Risk kayıt (Açık sorular, tekrar testler)
- Ertesi hafta planı

---

## 7. İletişim Şablonları

### 7.1 Tetik Bildirimi (Telegram)
```
🚀 Görev Tetiklendi
├─ Task: {task_id}
├─ Sahip: @{ajan}
├─ Hedef: {baslik}
├─ Deadline: {deadline}
└─ Brief: {brief_path}
```

### 7.2 Bloke Bildirimi
```
⚠️ Görev Blokajı
├─ Task: {task_id}
├─ Bloke Süresi: {saat}h
├─ Neden: {bloke_sebebi}
├─ İhtiyaç: {gerekli_input}
└─ Eskalasyon: KAHİN
```

### 7.3 Teslim Bildirimi
```
✅ Görev Teslim Alındı
├─ Task: {task_id}
├─ Teslim: @{ajan}
├─ Durum: done / review
├─ Bulgular: {bulgular_path}
└─ Sonraki: {next_task_id}
```

---

## 8. Kontrol Listesi (Günlük)

### Sabah (09:00)
- [ ] task_board.json açıldı
- [ ] Tetik script çalıştı
- [ ] Telegram bildirimi gönderildi
- [ ] Günün hedefi belgelendi

### Öğleden Sonra (14:00)
- [ ] Aktif görevler kontrol edildi
- [ ] Chat kanalı okundu
- [ ] Midway raporlar yazıldı

### Akşam (19:00)
- [ ] Teslim görevleri doğrulandı
- [ ] Bulgular dosyaları oluşturuldu
- [ ] Raporlar özetlendi
- [ ] Ertesi gün hazırlanması tamamlandı

---

**Güncellenme:** 2026-09-25 08:56 UTC  
**Sorumlu:** Orkestrator (Bot)  
**Onay:** KAHİN (Ürün Sahibi)
