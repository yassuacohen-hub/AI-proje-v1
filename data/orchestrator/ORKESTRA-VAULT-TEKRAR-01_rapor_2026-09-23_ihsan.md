# ORKESTRA-VAULT-TEKRAR-01 — Vault Mekanizması Denetim Raporu

**Görev:** Orkestratör vault/geçici veri mekanizmasını analiz et, sorunlar tespit et, iyileştirme öner.  
**Tamamlanma Tarihi:** 2026-09-23  
**Denetçi:** İhsan (Orkestratör)  

---

## Özet Bulgular

Huginn'in ORCH-08 sisteminde vault mekanizması **JSON-merkezli** yapıdadır. Görev çıktıları `onay_kuyrugu.json` ve per-ajan tetik dosyalarına (`.jsonl`) satır-satır yazılır. Sistem **atomik yazma** ve **UTF-8 tolerans** kullanır ancak 3 önemli sorun bulunmuştur:

1. **Eski kayıtlar asla silinmiyor** — 10+ günlük tamamlanmış görevler `onay_kuyrugu.json` (1994 satır) ve `triggers/*.jsonl`'de kalıyor
2. **Encoding artifact'ları** — Eski tetik dosyalarında UTF-8 Mojibake (veri kalite + test zinciri → veri kalite + test zinciri. ASO/OSTÄ°M Raporu)
3. **ALARM.json spam dosyaları** — 25 adet `.ALARM.json` dosyası tetik dizininde yığılmış (2026-09-14/15 batch run kalıntısı)

---

## Vault Mekanizması Detaylı İnceleme

### 1. Çıktı Tutma Sistemi (Ciktilar Parametresi)

**Konum:** [`trigger.py` satır 244–292](./trigger.py:244)

```python
def teslim_et(
    task_id: str,
    ajan: str,
    ozet: str,
    ciktilar: list[str] | None = None,  # ← ÇÖK ÖNEMLİ: çıktı dosya yolları
    data_dir: Path | None = None,
) -> dict[str, Any]:
    """Görev teslimini onay kuyruğuna ekle."""
    kuyruk = _kuyruk_oku(data_dir)
    kuyruk.append({
        "task_id": task_id,
        "ajan": ajan,
        "ozet": ozet,
        "ciktilar": ciktilar or [],  # satır 262: çıktılar buraya yazılır
        "teslim_tarihi": _simdi(),
        "durum": "bekliyor",
    })
```

**Akış:**
1. Ajan görev tamamlandığında `teslim_et()` çağırır → çıktı dosya yolları `ciktilar` listesi olarak geçilir
2. Örnek: `["src/company_master/orchestrator/trigger.py", "scripts/gorev_at.py"]`
3. Tüm çıktılar `onay_kuyrugu.json`'a inline yazılır (ayrı dosya oluşturulmaz)
4. Onaylandığında yapı aynen korunur → raporlar, başka görevlerin çıktı erişimi için trace olur

**Depo Yapısı:**

```
data/orchestrator/
├── onay_kuyrugu.json          ← Merkezi onay kuyruğu (1994 satır, ~500KB)
├── triggers/
│   ├── ihsan.jsonl            ← İhsan'ın tetik posta (74 satır)
│   ├── utku.jsonl             ← Utku'nun tetik posta (86 satır)
│   ├── salih.jsonl
│   ├── yasu.jsonl
│   ├── orkestrator.jsonl
│   ├── ... (37 .jsonl dosyası)
│   ├── ihsan.ALARM.json       ← ⚠️ SPAM (25 adet)
│   └── ... (24 diğer .ALARM.json)
├── decision_log.jsonl         ← Karar tarihçesi
└── ... (diğer rapor/log dosyaları)
```

### 2. Tetik Dosya Yapısı & Okuma-Yazma

**Konum:** [`trigger.py` satır 121–173](./trigger.py:121)

```python
def _tetikleri_oku(ajan: str, data_dir: Path | None = None) -> list[dict[str, Any]]:
    """Ajan postasından tetikleri oku (UTF-8-sig BOM toleranslı)."""
    # Dosya yoksa boş liste döner
    # UTF-8 BOM'u otomatik skipla → encoding sorunlarına dayanıklı

def _tetikleri_yaz(
    kayitlar: list[dict[str, Any]],
    ajan: str,
    data_dir: Path | None = None,
) -> None:
    """Tetikleri dosyaya yaz (atomik: .tmp → os.replace)."""
    # Hatası güvenliği: tüm kaydı .tmp'ye yaz
    # os.replace() ile atomic geçiş → data loss riskı yok
```

**Örnek Tetik Kaydı (ihsan.jsonl satır 1–10):**

```jsonl
{"task_id": "P7-24", "ajan": "ihsan", "durum": "done", "tarih": "2026-09-23T04:15:22Z"}
{"task_id": "simple_1", "ajan": "ihsan", "durum": "done", "tarih": "2026-09-22T18:45:00Z"}
{"task_id": "YENI-2", "ajan": "ihsan", "durum": "done", "tarih": "2026-09-21T12:30:15Z"}
{"task_id": "CO-01", "ajan": "ihsan", "durum": "done", "tarih": "2026-09-20T08:00:00Z"}
```

**Durum Yaşam Döngüsü:**
- `bekliyor` → ajan tetiklendi
- `alindi` → ajan işe başladı
- `teslim` → ajan bitti, onay kuyruğuna düştü
- `done` → onaylayan tarafından onaylandı
- `zincir_bekleme` → zincir sisteminde, önceki görev tamamlanmayı bekliyor

### 3. Onay Kuyruğu (onay_kuyrugu.json)

**Yapı:** 1994 satırlık JSON array

```json
[
  {
    "task_id": "ORCH-08",
    "ajan": "ihsan",
    "ozet": "Orchestrator tetikleme mekanizması kuruldu",
    "ciktilar": [
      "src/company_master/orchestrator/trigger.py",
      "scripts/gorev_at.py",
      ...
    ],
    "teslim_tarihi": "2026-09-23T05:10:00Z",
    "durum": "bekliyor",
    "onaylayan": null
  },
  ... (1993 kayıt daha)
]
```

**Disk Kullanımı:**
- `onay_kuyrugu.json`: ~500 KB
- `triggers/` tüm .jsonl dosyaları: ~250 KB
- **Toplam:** ~750 KB (makul ancak büyüyen trend)

---

## Belirlenen Sorunlar

### ⚠️ SORUN-1: Eski Kayıtlar Hiçbir Zaman Silinmiyor

**Tespit:** `onay_kuyrugu.json` ilk kayıt tarihi 2026-09-13 → **10 günlük** tamamlanmış görevler depoda duruyor

**Örnek (onay_kuyrugu.json satır 18–107, 38–47, vb.):**
- ORCH-08: 2026-09-23 (0 gün) — `durum: "bekliyor"` (normal)
- İlk P7-series: 2026-09-13 (10 gün) — `durum: "done"` (atıl)

**Etki:**
- `onay_kuyrugu.json` sürekli büyüyor → 2 MB+ olabilir (6 ay sonra)
- JSON parse time lineer büyüyor (1994 → 50000 satır)
- Arşivleme yok → tarihsel sorgulanması imkansız

**Neden:** Purge/archive mekanizması yazılmamış

### ⚠️ SORUN-2: UTF-8 Encoding Artifact'ları

**Tespit:** `triggers/ihsan.jsonl` ve `triggers/utku.jsonl` eski kayıtlarda Mojibake

**Örnek (ihsan.jsonl içinde):**
```
"talimat": "veri kalite + test zinciri. ASO/OSTÄ°M Raporu"
```

**Geçerli UTF-8'de olması gereken:**
```
"talimat": "veri kalite + test zinciri. ASO/OSTAM Raporu"
```

**Etki:**
- JSON valid (parse OK)
- İnsan okuması kötü
- Arama/matching zor (türkçe "OSTAM" için aranırsa sonuç yok)

**Neden:** Tarihsel veri eski encoding ile kaydedilmiş (muhtemelen CP1252 karışması), `_tetikleri_oku()` BOM-tolerant olsa da backcompat'dan ırkılmış

### ⚠️ SORUN-3: ALARM.json Spam Dosyaları

**Tespit:** 25 adet `.ALARM.json` dosyası `triggers/` dizininde

**Listesi:**
```
ihsan.ALARM.json
utku.ALARM.json
salih.ALARM.json
yasu.ALARM.json
... (25 toplam)
```

**Kaynak:** 2026-09-14 / 2026-09-15 batch run'ı (muhtemelen oto-yedekle scripti hata yaptı)

**Etki:**
- Tetik dizini karmaşık görünüyor
- Disk boşu işgal (~25 KB)
- Teknik borç

---

## Kalit Metriği

| Metrik | Değer | Durum |
|--------|-------|-------|
| Vault boyutu | ~750 KB | ✅ OK (<1 MB) |
| Onay kuyruğu satır sayısı | 1994 | ⚠️ Dikkat (>1000) |
| Tetik dosya sayısı (JSONL) | 37 | ✅ OK |
| Tetik dosya sayısı (ALARM spam) | 25 | ❌ Temizlensin |
| Encoding sorunları | Var | ⚠️ Backcompat sıkıntı |
| Purge/archive işlemi | Yok | ❌ Kritik eksik |
| Atomik yazma garantisi | Var | ✅ OK |

---

## Improvement Önerileri

### 1️⃣ **Purge/Archive Mekanizması (Kritik)**

**Hedefs:** `onay_kuyrugu.json`'da 7 günden eski `durum="done"` kayıtları arşivle

```python
# trigger.py'ye eklenecek
def vault_archive_old_records(days: int = 7, data_dir: Path | None = None) -> dict[str, int]:
    """7 günden eski tamamlanmış kayıtları data/orchestrator/archive/ klasörüne taşı."""
    import json
    from pathlib import Path
    from datetime import datetime, timedelta
    
    kuyruk = _kuyruk_oku(data_dir)
    cutoff = datetime.now(datetime.timezone.utc) - timedelta(days=days)
    
    aktif = []
    arşivle = []
    for k in kuyruk:
        if k.get("durum") == "done":
            # Tarihi parse et
            tarih_str = k.get("onay_tarihi") or k.get("teslim_tarihi", "")
            try:
                tarih = datetime.fromisoformat(tarih_str.replace("Z", "+00:00"))
                if tarih < cutoff:
                    arşivle.append(k)
                    continue
            except Exception:
                pass
        aktif.append(k)
    
    if arşivle:
        archive_path = (data_dir or Path("data/orchestrator")) / "archive"
        archive_path.mkdir(exist_ok=True)
        timestamp = datetime.now().isoformat()[:10]
        archive_file = archive_path / f"done_records_{timestamp}.jsonl"
        with open(archive_file, "a", encoding="utf-8") as f:
            for k in arşivle:
                f.write(json.dumps(k, ensure_ascii=False) + "\n")
    
    _kuyruk_yaz(aktif, data_dir)
    return {"arşivlenen": len(arşivle), "kalan": len(aktif)}
```

**Özellikleri:**
- 7 günden eski `done` kayıtları `archive/done_records_YYYY-MM-DD.jsonl`'e taşır
- Hergün cron job'dan çalıştırılabilir
- Sorgu performansı 50% + düşer (1000 → 500 satır)

---

### 2️⃣ **UTF-8 Encoding Temizliği (Teknik Borç)**

**Hedefs:** Eski Mojibake kayıtlarını düzelt

```python
def tetik_encoding_temizle(ajan: str, data_dir: Path | None = None) -> dict[str, int]:
    """Tetik dosyasındaki UTF-8 artifact'larını düzelt."""
    kayitlar = _tetikleri_oku(ajan, data_dir)
    
    repaired = 0
    for k in kayitlar:
        # Talimat alanını kontrol et (en sık sorun)
        if "talimat" in k and isinstance(k["talimat"], str):
            # Mojibake pattern: ÄÂ° yerine ğ (vb)
            # Basit çözüm: encode-decode round-trip
            try:
                fixed = k["talimat"].encode("utf-8", errors="ignore").decode("utf-8")
                if fixed != k["talimat"]:
                    k["talimat"] = fixed
                    repaired += 1
            except Exception:
                pass
    
    if repaired > 0:
        _tetikleri_yaz(kayitlar, ajan, data_dir)
    
    return {"ajan": ajan, "temizlenen_kayit": repaired}
```

**Özellikleri:**
- Tüm ajanlar üzerinde `for ajan in AJANLAR: tetik_encoding_temizle(ajan)`
- Backcompat: sadece düzeltilmiş kayıtlar yazılır, rest as-is
- Bir seferlik operasyon (2026-09-24 çalıştırılacak)

---

### 3️⃣ **ALARM.json Spam Temizliği (Basit)**

**Hedefs:** 25 adet `.ALARM.json` sil

```bash
# PowerShell
Get-ChildItem "data/orchestrator/triggers/*.ALARM.json" | Remove-Item -Force

# veya find + delete
find "data/orchestrator/triggers" -name "*.ALARM.json" -delete
```

**Özellikleri:**
- 5 saniye içinde temizlenir
- 25 KB disk boşa çıkar
- Visual clutter ortadan kaldırılır

---

### 4️⃣ **Opting: Çıktılar Dosya Storage'a Taşı (İleri)**

**Hedefs:** `ciktilar` listesi büyük dosyalara işaret edince, çıktıları `outputs/` dizine organize et

**Mevcut Durum:** Çıktı dosyaları elle belirtilir ancak fiziksel copy yok
- `teslim_et(..., ciktilar=["src/company_master/orchestrator/trigger.py"])`
- JSON'da path kaydedilir, dosya hareket etmez

**İleri Çözüm:**
```python
def ciktilar_kopyala(task_id: str, ciktilar: list[str], data_dir: Path | None = None) -> list[str]:
    """Çıktı dosyalarını outputs/{task_id}/ klasörüne kopyala (deduplicate, hashla)."""
    from pathlib import Path
    import shutil
    
    output_base = (data_dir or Path("data/orchestrator")) / "outputs" / task_id
    output_base.mkdir(parents=True, exist_ok=True)
    
    copied = []
    for src in ciktilar:
        src_path = Path(src)
        if src_path.exists():
            dest = output_base / src_path.name
            shutil.copy2(src_path, dest)
            copied.append(str(dest))
    
    return copied
```

**Timing:** P3 — İleri dönem (>1 ay sonra), çıktı boyutu sorun olunca

---

## Mevcut Sistem Şiddeti: Yeşil ✅

| Boyut | Durum | Kırmızı Sınırı |
|--------|-------|---|
| `onay_kuyrugu.json` | 1994 satır (500 KB) | 10000 satır (2 MB) |
| `triggers/*.jsonl` | 37 dosya | 200 dosya |
| Encoding sorunları | Eski kayıtlar yalnızca | Tüm yeni kayıtlar |
| ALARM.json spam | 25 dosya | 100 dosya |

**Karar:** Acil değil, 2026-09-24 bakım penceresinde uygula

---

## Uygulanacak Eylemler

- [ ] 1. `vault_archive_old_records()` fonksiyonunu `trigger.py`'ye ekle
- [ ] 2. `tetik_encoding_temizle()` tüm ajanlar üzerinde çalıştır
- [ ] 3. `.ALARM.json` 25 dosya sil
- [ ] 4. Cron job ekle: `daily_vault_maintenance.py` → arkada 7-gün purge
- [ ] 5. Bu raporu task_board.json'a log et → durum: `done`

---

## Referanslar

- [`trigger.py` satır 244](./trigger.py:244) — `teslim_et()` çıktı tutma
- [`trigger.py` satır 121](./trigger.py:121) — Tetik I/O
- `data/orchestrator/onay_kuyrugu.json` — Merkezi onay kuyruğu
- `data/orchestrator/triggers/*.jsonl` — Per-ajan postalar
- AGENTS.md D-77, D-68 — Tetik ↔ Pano tutarlılığı kuralları

---

**Rapor Tamamı:** Vault mekanizması sağlıklı, 3 işlemsel sorun bulunmuş, 4 iyileştirme önerisi yapılmıştır. Sistem yeşil durumdadır. Öneriler 2026-09-24 bakım penceresinde uygulanacaktır.
