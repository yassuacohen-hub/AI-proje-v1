# Özel Görev Delegasyonu — 2026-09-20

**Saatlık yoğunluk nedeniyle aşağıdaki 2 P2 görev doğrudan havuza devredilmiştir.**

## 1. ALTYAPI-DECISION-LOG-ENCODE-01 (P2)

**Görev:** `data/orchestrator/decision_log.jsonl` dosyasının UTF-8 kodlama denetimi + kategori backfill

**Bağlam:**
- Dosya: `worktree klasoru/data/orchestrator/decision_log.jsonl` (98 satır)
- İlgili P1 raporu: [`ORKESTRA-DECISION-LOG-FORMAT-01_rapor_2026-09-20_orkestrator.md`](ORKESTRA-DECISION-LOG-FORMAT-01_rapor_2026-09-20_orkestrator.md)
- Bulgu: 97/98 kaydın `kategori` alanı boş
- Mevcut çerçeve: [`src/company_master/orchestrator/decision_log.py`](../src/company_master/orchestrator/decision_log.py:1) → `DecisionRecord` + `denetle()` metodu
- CLI: [`scripts/karar_ekle.py`](../scripts/karar_ekle.py:1) → `listele`, `ara`, `degistir` subkomutları

**İş maddeleri:**
1. `decision_log.jsonl` satırlarını parse et (UTF-8 BOM denetle)
2. Satır 46, konum ~46494'te mojibake var mı kontrol et
3. 97 satırın `kategori` alanını backfill et (müş. ön dönem kategorisi tahmin edebilirse)
4. `DecisionLog.denetle()` çalıştırıp 98/98'in geçerli olduğunu doğrula

**Ön koşul:** `scripts/karar_ekle.py` fonksiyonel (tamamlanmış)

---

## 2. ALTYAPI-KILIT-TEMIZLIK-V10-01 (P2)

**Görev:** V10-HIJYEN sürecinin stale dosya kilitlerini serbest bırak

**Bağlam:**
- `data/orchestrator/file_locks.json` (13 kilit toplam)
- 3 V10-HIJYEN dosyası stale (2.1 gün yaşında, roo/cline tarafından kilitli):
  - `src/company_master/search/engine.py` (V10-HIJYEN-01)
  - `tests/test_search_engine_where.py` (V10-HIJYEN-01)
  - `src/company_master/search/fulltext.py` (V10-HIJYEN-02)
- İlgili P2 raporu: [`TEST-D77-01_rapor_2026-09-20_orkestrator.md`](TEST-D77-01_rapor_2026-09-20_orkestrator.md) → Bulgu 1

**İş maddeleri:**
1. 3 dosyayı `file_locks.json` dari kaldır
2. Dosya izinleri doğrula (modifiable state)
3. Atomik yazma ile `file_locks.json` güncelle (tempfile+replace)

**Script Şablonu:**
```python
import json
from pathlib import Path

locks_path = Path("worktree klasoru/data/orchestrator/file_locks.json")
locks = json.loads(locks_path.read_text(encoding="utf-8"))

stale_v10 = [
    "src/company_master/search/engine.py",
    "tests/test_search_engine_where.py",
    "src/company_master/search/fulltext.py",
]

for f in stale_v10:
    if f in locks:
        del locks[f]
        print(f"Kaldırıldı: {f}")

tmp = locks_path.with_suffix(".tmp")
tmp.write_text(json.dumps(locks, ensure_ascii=False, indent=2), encoding="utf-8")
tmp.replace(locks_path)
print(f"Güncellendi: {locks_path}")
```

---

## Özel Not

Bu iki görev **P1 + P2 setinin geri kalanını tamamlama** kısıtlamalarına rağmen doğru şekilde tanımlanıp havuza devredilmiştir. Hangisi tarafından ele alınırsa alınsın:

- ALTYAPI-DECISION-LOG-ENCODE-01 için [`scripts/karar_ekle.py`](../scripts/karar_ekle.py:1) zaten fonksiyonel
- ALTYAPI-KILIT-TEMIZLIK-V10-01 için `file_locks.json` yapısı basit ve atomik yazma şablonu hazır

Pano(görev_panosu.md) bu iki görev için tetiklerden beklemeye işaretlenmiş.

---

**Delegasyon Tarihi:** 2026-09-20T18:58:32Z  
**Orkestrator İmzası:** ihsan
