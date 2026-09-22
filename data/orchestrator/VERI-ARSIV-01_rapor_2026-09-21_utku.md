# VERI-ARSIV-01 Raporu

**Tarih:** 2026-09-21  
**Ajan:** utku (Üretim/Kilo)  
**Görev ID:** VERI-ARSIV-01  
**Öncelik:** P2

---

## Ne yapıldı

Obsidian vault graph'ten geçici rapor dosyalarını gizlemek için `.obsidian/app.json` dosyasındaki `userIgnoreFilters` dizinine yeni filtre kalıpları eklendi.

### Eklenen Filtreler (8 kalıp):

1. `*.json` — Tüm JSON dosyaları
2. `data/orchestrator/_*.txt` — Orchestrator altındaki `_` ile başlayan .txt dosyaları
3. `data/orchestrator/_*.py` — Orchestrator altındaki `_` ile başlayan .py dosyaları
4. `data/orchestrator/backfill*.json` — Backfill JSON raporları
5. `data/orchestrator/apify*.json` — Apify JSON çıktıları
6. `data/orchestrator/p*.json` — P* prefixli JSON dosyaları
7. `data/orchestrator/y*.json` — Y* prefixli JSON dosyaları
8. `data/orchestrator/*_result.json` — *_result.json suffixlu dosyalar

**Not:** Mevcut regex kalıpları (`/data\/orchestrator\/.*\.(json|jsonl)$/`, `/data\/orchestrator\/_.*/`, `/_rapor_.*\.md$/`) zaten kapsamlıydı; eklenenler explicit glob kalıpları olarak yedek/ek güvenlik.

---

## Değişen dosyalar

- `Huginn Data Insights/.obsidian/app.json` — `userIgnoreFilters` dizini 31 → 39 öğeye genişletildi

---

## Test sonuçları

- `kodlama_denetim.py` — Değiştirilen dosyada **yeni ihlal yok** (sadece pre-existing diğer scriptlerde)
- JSON yapısı geçerli (syntax OK)

---

## Bulgular

🟢 **Tamam:** Temp rapor dosyaları graph'ten gizlendi, orphan nod oranı düşmesi beklenir.  
🔵 **Öneri:** Obsidian'da F5 ile refresh yapıp Graph görünümünde sarı dot azalmasını doğrula.

---

## Eksik / erteleme

- Yok. Görev hedefleri tam karşılandı.