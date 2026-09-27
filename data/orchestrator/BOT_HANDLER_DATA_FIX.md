# Bot Handler Veri Akışı Taşıması — task_board.json SSOT

> Karar referansı: D-223 (Tek Otorite: Vault) — bkz. `AGENTS.md`. Bu rapor karar
> numarası **sahiplenmez**, yalnızca uygulamayı belgeler (D-227).

**Tarih:** 2026-09-25 12:37 UTC+3  
**Sorun:** "bot yanıt veiyor amam handel eksik olabilir mi doğru veri akışları gözükmüyor tüm menülerde"  
**Kök Sebep:** Handler'lar iki ayrı veri kaynağı arasında bölünmüş; tetik sistem boş "bekliyor" listesi döndürüyor  
**Çözüm:** Handler'ları task_board.json (SSOT) okumasına taşı

---

## 1. Veri Akışı Sorunu Analizi

### Sistem Mimarisi (Kopya)
- **task_board.json** = SSOT (32 görev, karışık durum: done/aktif/bloke/plan/iptal)
- **triggers/*.jsonl** = Legacy polling sistem (tamamlanmış görevler, durum: done)
- **Bot handler'ları** = Eski sistem okuyordu (boş "bekliyor" filtresi)

### Tetik Sisteminin Durumu
| Dosya | İçerik | Durum |
|-------|--------|-------|
| `data/orchestrator/triggers/utku.jsonl` | 103 satır görev geçmişi | Tümü "done" |
| `data/orchestrator/triggers/yasu.jsonl` | 98 satır görev geçmişi | Tümü "done" |
| `data/orchestrator/triggers/salih.jsonl` | 87 satır görev geçmişi | Tümü "done" |

**Sonuç:** `bekleyen_tetikler(ajan)` filtresi `durum=="bekliyor"` → boş liste döner

---

## 2. Düzeltilen Handler'lar

### A. `show_pano_status()` — Pano Menüsü (Satır 135-195)

**Eski kod:**
```python
from src.company_master.orchestrator.trigger import bekleyen_tetikler
tasks = bekleyen_tetikler("*")  # ← Boş liste
```

**Yeni kod:**
```python
import json
from pathlib import Path

task_board_path = Path("data/orchestrator/task_board.json")
with open(task_board_path, "r", encoding="utf-8") as f:
    tasks = json.load(f)  # ← SSOT oku
```

**Durum Mapping:**
```python
status_map = {
    "done": "done",
    "active": "aktif",        # triggers.jsonl → task_board durum isimleri
    "blocked": "bloke",       # triggers.jsonl → task_board durum isimleri
    "plan": "plan",
    "all": None
}
```

**Test:** Pano menüsü şimdi 32 görevle filtreleme yapabilecek.

---

### B. `_show_tetikler_ajan_detay()` — Tetikler Menüsü (Satır 331-370)

**Eski kod:**
```python
from src.company_master.orchestrator.trigger import bekleyen_tetikler
tetikler = bekleyen_tetikler(ajan)  # ← Boş (legacy status)
```

**Yeni kod:**
```python
task_board_path = Path("data/orchestrator/task_board.json")
with open(task_board_path, "r", encoding="utf-8") as f:
    gorevler = json.load(f)

# Ajanın aktif/plan görevlerini filtrele
tetikler = [g for g in gorevler if g.get("sahip", "").lower() == ajan.lower() 
           and g.get("durum", "").lower() in ["aktif", "plan"]]
```

**Test:** Tetikler menüsü şimdi ajan başına aktif görevleri gösterecek.

---

## 3. Doğrulanmış Handler'lar (Değişiklik Yok)

| Handler | Kaynak | Durum |
|---------|--------|-------|
| `show_chat_status()` | `chat.oku()` | ✅ OK |
| `show_rapor_pano_ozeti()` | `task_board.json` | ✅ OK |
| `show_gorev_takibi_durum()` | `task_board.json` | ✅ OK |
| `show_gorev_sahib_goster()` | `task_board.json` | ✅ OK |

---

## 4. Durum Mapping Referans

### task_board.json Durum Değerleri
```json
{
  "durum": "done" | "aktif" | "bloke" | "plan" | "iptal"
}
```

### Triggers/*.jsonl Eski Durum Değerleri (Uyumlu kılındı)
```json
{
  "durum": "bekliyor" | "alindi" | "teslim" | "done"
}
```

**Mapping Kuralları:**
- `bekliyor` → `aktif` (görev hazır, henüz başlanmamış)
- `alindi` → `aktif` (görev başladı)
- `teslim` → `bloke` (teslim onay bekliyor)
- `done` → `done` (tamamlandı)

---

## 5. Bot Instance Çakışması (D-220 Sonrası)

**Sorun:** Polling mode + webhook mode çakışması
```
ERROR: Conflict: terminated by other getUpdates request
```

**Çözüm:** Terminal 1 eski instance'ı, Terminal 3 yeni instance'ı çalıştırıyor.

**Temizleme Adımları:**
1. Terminal 1 kapatılacak (eski bot instance)
2. Terminal 3 üzerinden yeni instance yürütülecek
3. `TELEGRAM_WEBHOOK_URL` env var kontrol edilecek (prod/dev mod)

---

## 6. Commit

```
0f423b4: D-223 Bot handler veri akışı taşıması — task_board.json SSOT oku
- show_pano_status(): bekleyen_tetikler() → task_board.json (aktif/bloke/plan/done)
- _show_tetikler_ajan_detay(): bekleyen_tetikler() → task_board.json (ajan görevleri)
- Durum mapping düzeltildi: aktif, bloke (triggers isimlendirmesinden)
- Diğer handler'lar (chat, rapor, takibi) zaten doğru kaynaktan okuyor
```

---

## 7. Sonraki Adımlar

- [ ] Bot instance (Terminal 3) manuel test: `/pano`, `« Pano` butonları kontrol et
- [ ] Telegram client'ta Pano menüsü → görevler listelenmeli (32 toplam)
- [ ] Tetikler menüsü (ajan başına aktif/plan görevleri)
- [ ] Hata log'larını kontrol et (data path, JSON parse)
- [ ] Diğer menüler (Chat, Rapor, Takibi) doğrulamak

---

## 8. Teknik Detaylar

### Path Handling
```python
# Eski (relative path sorunu):
task_board_path = Path(__file__).parent.parent.parent / "data" / "orchestrator" / "task_board.json"

# Yeni (basit, CWD tabanlı):
task_board_path = Path("data/orchestrator/task_board.json")
```

### JSON Decode Error Handling
```python
try:
    with open(task_board_path, "r", encoding="utf-8") as f:
        tasks = json.load(f)
except Exception as e:
    logger.error(f"[PANO] task_board.json read error: {e}")
    tasks = []  # Graceful fallback
```

---

## Ilgili Nodlar

- D-219: Debug handler greedy matching
- D-220: Hybrid polling/webhook mode
- D-222: Bot operasyon durumu
- [[Huginn Data Insights/data/orchestrator/task_board.json]]
- [[Huginn Data Insights/src/company_master/telegram_bot.py:135]]
