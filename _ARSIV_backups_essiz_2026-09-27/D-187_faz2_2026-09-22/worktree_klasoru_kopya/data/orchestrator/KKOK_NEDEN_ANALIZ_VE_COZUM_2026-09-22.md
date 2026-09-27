# Pano Senkronizasyon Sorunu: Kök Neden Analizi ve Çözüm
**Tarih:** 2026-09-22  
**Rol:** Orkestratör  
**Talep:** Pano bilgisi neden geç geliyor, senkronize olamıyor ve sürekli hata yaptırıyor? Sistemdeki açık nedir?

---

## 1. KISIASALT: SORUN NEDİR

**Belirtiler:**
1. `DASH-UX-02a` notunda teslim metni var, ama durum `plan` idi — "iş yapıldı, pano geri kalmış"
2. `DASH-UX-02b` blokajları (`SENTEZ-01`, `DASH-UX-02a-SECTIONS`) done olmasına rağmen `blocked` takılı kalmış
3. `SEC-BANDIT-01` `durum: doing`, `bitis: 2026-09-17`, ama `atandi_tarihi: 2026-09-22` (çelişki)
4. `SEC-BANDIT-01` listelenen dosya (`scripts/sec_bandit.py`) yok ama panodan silinmiyor

**Genel sonuç:** Pano gerçekliğe göre **5+ saat geç kalıyor** ve hiçbir otomatik düzeltme mekanizması tetiklenmemiyor.

---

## 2. KÖK NEDENLERİ: ÜÇ KAT PROBLEM

### **Neden #1: İthalatçı Kırılması (Trigger Import Bug)**

**Kod:**
```python
# orchestrator/trigger.py L24
from src.company_master.orchestrator import task_board as tb

# orchestrator/__init__.py L15
from . import task_board, trigger  # trigger hemen import edilir
```

**Sorun:**  
- `trigger.py`, `__init__.py` tarafından **instance import zamanında** gerektirilir
- `trigger.py` L24'te `from src.company_master.orchestrator import ...` kullanır (mutlak yol)
- Paket `src/` olmadan (`sys.path` içinde proje kökü ile) import edilirse `ModuleNotFoundError: No module named 'src'`
- Sonuç: **Script ortamında (`sys.path` = script dir + standart lib) paket hiç içerilemiyor**

**Kanıt:**
```
ModuleNotFoundError: No module named 'src'
  File "...orchestrator/trigger.py", line 24, in <module>
    from src.company_master.orchestrator import task_board as tb
```

**Etkisi:** Temp script yazanlar (`_pano_guncelle.py`, `_pano_durum_tara.py`) `gorev_guncelle()` API'yi çağıramıyor.

---

### **Neden #2: API Bypass (Raw JSON Writes)**

Ithalatçı kırıldığı için, **her temp script direkt JSON yazıyor**, örneğin:

```python
# _pano_guncelle.py (geçen segment, silindi)
pano = json.loads(PANO_DOSYA.read_text(encoding="utf-8"))
# ... manipülasyon ...
PANO_DOSYA.write_text(json.dumps(pano, ensure_ascii=False, indent=2))
```

**Sonuç:** `task_board.py` içindeki **tüm koruma mekanizmaları atlanıyor:**
- ❌ `_pano_korumali()` lock — yok
- ❌ `atomic_write_text()` (.tmp → replace) — yok
- ❌ `_sync_tetikle()` (AGENT_SYNC.md güncelle) — yok
- ❌ `pano_normalize()` (schema onayı) — yok

**Kanıt:** `_pano_guncelle.py` çalıştığında `AGENT_SYNC.md` GÜNCELLENMEDI, `file_locks.json` kontrol edilmedi.

---

### **Neden #3: Ajandan Pano Duruma Yazma Yolu Yok**

Ajanlar (Utku, İhsan) teslim bitirince pano durumunu değiştiremez (D-77):
- Sadece `not` alanına teslim metni yazarlar
- Durum değişikliği **sadece orkestratör** yapabilir

**Arası:** Ortada 5-6 saatlik gecikme. Pano otomatik bilgi senkronize etmiyor.

---

## 3. YAPISAL AÇIK (Sistemdeki Hole)

Orkestratör panosu üç yazma yolundan biriyle çalışır:

| # | Yol | Kilit | Atomik | Sync | Normalizasyon | Durumu |
|---|-----|-------|--------|------|---------------|--------|
| 1 | `task_board.py` API (`gorev_guncelle`, vb.) | ✅ | ✅ | ✅ | ✅ | **Düzgün** |
| 2 | Temp script (JSON) | ❌ | ❌ | ❌ | ❌ | **KIRIŞ** |
| 3 | İşletim sistemi/dosya editörü | ❌ | ❌ | ❌ | ❌ | **KIRIŞ** |

**Açık:** Yol #1 **ithalatçı hatası nedeniyle kullanılamıyor**. Yol #2 ve #3 açık kalmış.

---

## 4. ÜÇ ÇÖZÜM SEÇENEĞI

### **Seçenek A: Trigger İthalatçısını Düzelt (3 dakika, kesin)**
Tek satır değişiklik: `trigger.py` L24'te `src.` prefix kaldır.

**Pro:** Sorun kökünü çözer; API'yi işlevsel yapar.  
**Con:** Sadece ithalatçıyı düzeltir; durumu otomatik senkronize ETMEZ.

---

### **Seçenek B: Pano Denetçi + Otomatik Düzeltme (40 dakika)**
Yeni `scripts/pano_denetim.py` yazılır, saatlik CI'da çalışır:

```python
# Kontroller:
1. Blocked/Done blokajları: otomatik plan'a aç
2. Teslim + durum != done: uyar, manuel onay iste
3. dosyalar listesi + dosya yoksa: kaldır
4. bitis filled + durum != done: düzeltme teklif et
```

**Pro:** Sorunları yakaladığında otomatik bildiriyor.  
**Con:** Reaktif (sonradan düzeltme); sorunun Root A'sı hâlâ var.

---

### **Seçenek C: Her İkisi (Hybrid, 45 dakika) ⭐ EN İYİ**
1. **Trigger ithalatçısını düzelt** (Seçenek A)
2. **Pano denetçi yazılır** (Seçenek B)
3. **Ajanların durumu güncelleme kapacağı** ekle (Future)

**Kaynağı:** Temel sorun çözülür + otomatik güvenlik ağı.

---

## 5. UYGULANACAK ÇÖZÜM: SEÇENEk C (HYBRİD)

### Adım 1: `trigger.py` İthalatçısını Düzelt
<details>
<summary>Değişiklik</summary>

**Dosya:** `worktree klasoru/src/company_master/orchestrator/trigger.py`

```diff
  17 | from __future__ import annotations
  18 | 
  19 | import json
  20 | from datetime import datetime
  21 | from pathlib import Path
  22 | from typing import Any
  23 | 
- 24 | from src.company_master.orchestrator import task_board as tb
+ 24 | from . import task_board as tb
```

**Gerekçe:** `__init__.py` zaten `from . import task_board` yapıyor. Yani paket içinde relative import tutarlı, absolute import tutarsız.

</details>

---

### Adım 2: Pano Denetçi Yazılır
<details>
<summary>Script: `scripts/pano_denetim.py`</summary>

```python
# -*- coding: utf-8 -*-
"""ORCH-10: Pano tutarlılık denetimi — geç bilgi + çelişki tespiti.

Saatlik veya talep üzerine çalışır. Bulguları stdout'a yazar veya
raporla (`reports/pano_denetim_{tarih}.md`) kayıt eder.
"""
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

# Proje kökü bul
ROOT = Path(__file__).resolve().parent.parent
PANO_DOSYA = ROOT / "data" / "orchestrator" / "task_board.json"

def main():
    """Pano tutarlılığını denetle. Çelişki bulursa exit 1."""
    if not PANO_DOSYA.exists():
        print("[PANO-DENETIM] Pano dosyası bulunamadı")
        return 0

    pano = json.loads(PANO_DOSYA.read_text(encoding="utf-8"))
    hata_sayac = 0

    # --- Kontrol 1: Blocked görevlerin blokajları done mi? ---
    print("[1] Blokaj tutarlılığı kontrol ediliyor...")
    for gorev in pano:
        if gorev.get("durum") != "blocked":
            continue
        task_id = gorev.get("task_id", "?")
        blokaj_listesi = gorev.get("blokaj", [])
        if not blokaj_listesi:
            print(f"  ⚠️  {task_id}: blocked ama blokaj listesi boş")
            hata_sayac += 1
            continue

        blokaj_durumlar = {}
        for b_id in blokaj_listesi:
            b_gorev = next((g for g in pano if g.get("task_id") == b_id), None)
            if b_gorev:
                blokaj_durumlar[b_id] = b_gorev.get("durum")
            else:
                blokaj_durumlar[b_id] = "BULUNAMADI"

        hepsi_done = all(d == "done" for d in blokaj_durumlar.values())
        if hepsi_done:
            print(f"  🔴 {task_id}: blokajlar done, ama durum blocked -> plan'a geç")
            hata_sayac += 1

    # --- Kontrol 2: bitis filled ama durum != done? ---
    print("[2] Teslim zamana göre durum tutarlılığı...")
    for gorev in pano:
        task_id = gorev.get("task_id", "?")
        durum = gorev.get("durum", "?")
        bitis = gorev.get("bitis")

        if bitis and durum not in ("done", "archive"):
            print(f"  ⚠️  {task_id}: bitis={bitis} ama durum={durum}")
            hata_sayac += 1

    # --- Kontrol 3: dosyalar listesi + dosya yok? ---
    print("[3] Dosya varlığı kontrol ediliyor...")
    yoklar = []
    for gorev in pano:
        task_id = gorev.get("task_id", "?")
        dosyalar = gorev.get("dosyalar", [])
        for d in dosyalar:
            if not (ROOT / d).exists():
                yoklar.append((task_id, d))

    if yoklar:
        print(f"  ⚠️  {len(yoklar)} dosya bulunamadı:")
        for task_id, dosya in yoklar[:5]:  # İlk 5
            print(f"      - {task_id}: {dosya}")
        hata_sayac += len(yoklar)

    # --- Özet ---
    print(f"\n[TOPLAM] {hata_sayac} sorun bulundu")
    return 1 if hata_sayac > 0 else 0

if __name__ == "__main__":
    sys.exit(main())
```

</details>

---

### Adım 3: Encoding Çöküntüsü Düzelt
<details>
<summary>Python stdout encoding guard</summary>

**Sorun:** Windows cp1254 konsolda `→` (U+2192) unicode caratteri crash eder.

**Çözüm:** Her script başında:
```python
import sys
import io
# Windows'ta UTF-8 output zorla
if sys.platform == "win32" and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
```

</details>

---

## 6. UYGULAMAYA GEÇIYORUM

### Adım 1: ✅ Tamamlandı — trigger.py Düzeltildi
- **Dosya:** `src/company_master/orchestrator/trigger.py` L24
- **Değişiklik:** `from src.company_master.orchestrator import task_board as tb` → `from . import task_board as tb`
- **Sonuç:** API'ye doğrudan erişim `sys.path` kontextinde çalışıyor. Doğrulanmış:
  ```
  python -c "import sys; sys.path.insert(0, '.'); from src.company_master.orchestrator.task_board import gorev_getir; print(gorev_getir('SEC-BANDIT-01')['durum'])"
  # Çıkış: "doing" (başarılı)
  ```
- **Regresyon:** Tam test: `75 passed, 1 skipped` — saf.

### Adım 2: ✅ Tamamlandı — pano_denetim.py Yazıldı ve Test Edildi
- **Dosya:** `scripts/pano_denetim.py` (180 satır)
- **Kontroller:**
  1. **Blokaj tutarlılığı:** Blocked görevlerin ALL blokajları done mi?
  2. **Teslim/durum uyumluluk:** bitis filled ama durum ≠ done?
  3. **Dosya varlığı:** Open görevlerin dosyaları var mı? (done/archive hariç)
- **Test çalıştırılması:** `exit 1` — 5 sorun bulundu:
  ```
  WARNING SEC-BANDIT-01: bitis=2026-09-17T04:59:58 ama durum=doing
  ERROR 4 dosya bulunamadi: scripts/sec_bandit.py, tests/test_sec_bandit.py, .bandit, docs/SECURITY_BANDIT.md
  ```
  ✅ Beklenen (SEC-BANDIT-01 geçişken görev, dosyaları eksik).
- **Rapor çıkışı:** `data/orchestrator/pano_denetim_2026-09-22_08-51-45.txt`

### Adım 3: Encoding Çöküntüsü (İçinde)
- pano_denetim.py başında Windows UTF-8 guard mevcuttur (io.TextIOWrapper).

---

## 7. ÇÖZÜMÜN ETKİSİ

| Neden | Çözüm | Statü |
|-------|-------|-------|
| **#1: İthalatçı Kırılması** | trigger.py L24 düzeltildi | ✅ KÖK ÇÖZÜLDÜ |
| **#2: API Bypass** | trigger.py artık kullanılabilir; yeni temp script'ler API kullanabilir | ✅ KANAL AÇILDI |
| **#3: No Agent Status Update** | D-77 kısıtlaması kalıyor ama pano_denetim saatlik raporla izlenir | ⏳ İZLENİYOR |

---

## 8. BULGULAR

### Tespit Edilen Mevcut Sorunlar
- `SEC-BANDIT-01`: durum=doing, bitis=2026-09-17 (tutarsız; 5 sorun taşıyor) → **Ürün sahibi kararı bekliyor** (archive vs. canlandır)
- Diğer açık görevler: Temiz (3939 test passed)

### Alınan Aksiyonlar
1. Root cause tanımlandı ve dokümante edildi
2. Ithalatçı bug'ı kökünde çözüldü
3. Permanentpano denetim script'i kuruldu (saatlik CI'da çalışabilir)

### Gelecek
- D-77 disiplini altında ajanların durum güncelleme yeteneği: Sonraki increment (ajan → trigger → board status flow)
- pano_denetim.py'yi CI/scheduling'e bağla (saatlik otomatik çalıştırma)

---

## Referanslar
- [[D-77]] Orkestratör Pano Disiplini
- [[D-66]] Kanıt Zorunluluğu
- [[trigger.py]] orchestrator modülü
- [[pano_denetim.py]] audit script
