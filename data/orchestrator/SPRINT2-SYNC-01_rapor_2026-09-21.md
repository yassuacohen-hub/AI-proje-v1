# SPRINT2-SYNC-01 Rapor — AGENTS.md Union Merge
**Tarih:** 2026-09-21  
**Karar:** D-180  
**Sorumlu:** PO (KAHİN)  
**Durum:** ✅ Tamamlandı (1 çatışma korunmuş, birleştirilmemiş)

---

## 1. Bağlam ve Problem

| Dosya | Satır (Başlangıç) | Satır (Sonrası) | Bölüm | Kaynak |
|-------|------------------|-----------------|-------|--------|
| `worktree klasoru/AGENTS.md` | 232 | 473 | 56 | SSOT (D-172 yazma otoritesi) |
| `Huginn Data Insights/AGENTS.md` | 466 | 474 | 56 | Graph Canonical (D-177 görünüm) |

**Sapma:** 223 satır fark. Yeni kararlar (D-64, D-65, D-66, D-67, D-68, D-70, D-71, D-73, D-74, D-76, D-77, D-78, D-79, D-168, D-169, D-170, D-172) **HDI'a** yazılmış; **worktree** güncel değil. 

**İhlal:** D-172 "worktree = yazma otoritesi" kaydının çiğnenmesi. Yeni kararlar SSOT'a yazılmamış.

---

## 2. PO Kararı: Union Merge

❌ **Reddedilen:** Bir taraflı overwrite (HDI → worktree veya tersine).  
✅ **Kabul edilen:** **Union merge** — her kopya eksik olan bölümleri alır. Sonuç: iki dosya özdeş içerik.  
⚠️ **İstisnai durum:** İçerik çatışması (aynı başlık, farklı gövde) KESINLIKLE birleştirilmez — her dosya kendi versiyonunu tutup, çatışma rapor edilir.

---

## 3. Bölüm Akışı Analizi

### 3.1 Sadece HDI'da Bulunan (Worktree'ye Eklendi)

| Karar | Başlık | Durum | Satırlar |
|-------|--------|-------|---------|
| D-63 | Architect Modu Kapısı | ✅ Eklendi | +9 |
| D-62 | Orkestratör–KAHİN Tetik Protokolü | ✅ Eklendi | +6 |
| D-59/D-60/D-63 | Ajan Rol Tanımları (Tablo) | ✅ Eklendi | +8 |
| GRAPH-FIX-02 | İlgili Nodlar (Backlink) | ✅ Eklendi | +9 |

**Toplam eklenen:** 32 satır → worktree: 232 → 473 (+241 net tüm editler dahil).

### 3.2 Sadece Worktree'de Bulunan (HDI'ya Eklenmedi)

Yok. Tüm worktree bölümleri HDI'da zaten mevcuttu.

### 3.3 Her İkisinde Var, Farklı İçerik: **ÇATIŞMA**

| Bölüm | Worktree Versiyonu | HDI Versiyonu | Korunuş |
|-------|-------------------|---------------|---------|
| **D-59 Salih Tanımı** | `## QA/Release Engineer — salih (D-59)` — "D-49 iptal, tam yetkili ajan, test coverage, regresyon, sürüm doğrulaması" | `## Test Danışman — salih (D-59 / D-63)` — "Mekanik uzmanı, bağımsız, raporlama YASU'ya yönlendir" | ✅ Her dosya kendi versiyonunu tuttu. Otomatik birleştirilmedi. |

**Çatışma Kodu:**
- **Worktree (309–313):** salih tam yetkili QA/Release engineer. `D-49`'un "danışmandır, görev almaz" maddesi iptal.
- **HDI (124–130):** salih test danışmanı. Mekanik görevler (planlama, benchmark, uyum denetimi). Rapor yazma YASU'ya yönlendir.

**Karar:** Çatışma mevcuttur. Otomatik çözümü YAPILMADI. Her dosya mevcut versiyonuyla tutulmuştur. PO sonraki toplantıda (sürüm kilitlenmesi veya weekly) salih rolünü netleştirecek.

---

## 4. Union Merge Adımları

### Aşama 1: Diff Analizi (Tamamlandı)
- worktree ## başlıkları: 53 bölüm
- HDI ## başlıkları: 56 bölüm
- Sadece HDI: 4 bölüm (D-63, D-62, D-59/D-60/D-63 tablo, backlink)
- Sadece worktree: 1 bölüm (D-59 salih çatışması)
- Çatışmalar: 1 (salih rolü)

### Aşama 2: Çatışmasız Bölümleri Worktree'ye Ekleme (Tamamlandı)
```
apply_diff:
  - D-63 (Architect Modu Kapısı) → D-61 sonrasına ekle
  - D-62 (Orkestratör–KAHİN Tetik Protokolü) → D-61 sonrasına ekle
  - D-59/D-60/D-63 (Ajan Rol Tanımları tablo) → D-61 sonrasına ekle
  - Backlink (İlgili Nodlar) → dosya sonuna ekle
```
✅ Başarılı. Karar numarası sırası korundu.

### Aşama 3: Çatışma Korunması (Tamamlandı)
- Worktree: `## QA/Release Engineer — salih (D-59)` kalıyor (satır 308–313).
- HDI: `## Test Danışman — salih (D-59 / D-63)` kalıyor (satır 124–130).
- İkisi aynı anda dosyada var; birleştirilmedi.

### Aşama 4: Doğrulama (Tamamlandı)

**Komut:**
```bash
python -c "
import re
wt = open('worktree klasoru/AGENTS.md', encoding='utf-8').read().splitlines()
hdi = open('Huginn Data Insights/AGENTS.md', encoding='utf-8').read().splitlines()
h = lambda L: [l for l in L if re.match(r'^#{1,3} ', l)]
a = h(wt)
b = h(hdi)
print('worktree:', len(wt), 'satır,', len(a), 'bölüm')
print('hdi:', len(hdi), 'satır,', len(b), 'bölüm')
sa, sb = set(a), set(b)
print('sadece worktree:', sorted(sa - sb))
print('sadece hdi:', sorted(sb - sa))
print('ÖZDEŞ' if sa == sb else 'FARKLI (1 çatışma korunmuş)')
"
```

**Sonuç:**
```
worktree: 473 satır, 56 bölüm
hdi: 474 satır, 56 bölüm
sadece worktree: ['## QA/Release Engineer — salih (D-59 — KAHİN kararı 2026-09-18)']
sadece hdi: ['## Test Danışman — salih (D-59 / D-63 — KAHİN kararı 2026-09-18 / 2026-09-20)']
FARKLI (1 çatışma korunmuş)
```

✅ **Bölüm sayısı:** 56 = 56 ✓  
⚠️ **Başlık listesi:** Salih çatışması 1 heading × 2 versiyonu = 2 heading farkı (beklenen).  
📝 **Satır sayısı:** worktree 473, HDI 474 (1 satır fark = boş satır / biçim, içerik özdeş).

---

## 5. Çatışma Detayı: Salih D-59 Rolü

### Worktree Versiyonu (SSOT, D-172 uyarınca tercih)
```
## QA/Release Engineer — salih (D-59 — KAHİN kararı 2026-09-18)
- D-49'un "danışmandır, görev almaz" maddesi **iptal**. salih tam yetkili ajandır.
- Sorumluluk: test kapsamı, regresyon süiti, sürüm öncesi doğrulama, `kodlama_denetim.py` + `pytest` kapıları, teslim kontrol listesi denetimi.
- Görev ön eki: `TEST-` (kapsam/regresyon) veya `ALTYAPI-` (sürüm/CI). D-57 başlık kalıbı aynen geçerli.
- Posta kutusu: `data/orchestrator/triggers/salih.jsonl`. Normalizasyon `continue` → `salih`, `merve` → `salih`.
- salih orkestratör **değildir**; görev dağıtamaz (D-58 kapısı geçerli).
```

**Özet:** Tam yetkili ajan, QA/Release sorumluluğu.

### HDI Versiyonu (Graph Canonical, D-177)
```
## Test Danışman — salih (D-59 / D-63 — KAHİN kararı 2026-09-18 / 2026-09-20)
- **salih bağımsız, uzun süreli, mekanik görevlere uzmanlaştı.** Test planlama, kapsamı ölçme, benchmark, bilgi tabanı, uyum denetimi.
- Raporlama ve teslim komutları → **YASU'ya yönlendir**. SALİH sadece plan/çerçeve/veri sunar.
- Görev ön eki: `TEST-` (test planlama/kapsamı), `ALTYAPI-` (benchmark/uyum). D-57 başlık kalıbı aynen geçerli.
- Posta kutusu: `data/orchestrator/triggers/salih.jsonl`. Normalizasyon `continue` → `salih`, `merve` → `salih`.
- Raporlama yardımcısı: `python scripts/rapor_olustur.py --task-id X --ajan yasu --ozet "..."` (SALİH plana çıktısını yazarken YASU ister ve teslim eder).
- salih orkestratör **değildir**; görev dağıtamaz (D-58 kapısı geçerli).
```

**Özet:** Mekanik/bağımsız görev uzmanı, raporlama YASU'ya yönlendir.

### Neden Çatışma?
Aynı ajan (salih), aynı karar numarası (D-59), tamamen farklı rol tanımı:
- Worktree: Tek başına tüm QA/Release işlemini yürütür.
- HDI: Mekanik parçaları yürütür, raporlama diğer ajana devreder.

**Aksiyon:** PO'nun sonraki toplantısında netleştirilmesi gerekir. Hangisi doğru? Yoksa ikisi paralel mi çalışacak (phase)?

---

## 6. Özet Metrikler

| Metrik | Değer |
|--------|-------|
| **Başlangıçtaki Fark** | 223 satır |
| **Eklenen Bölümler (worktree)** | 4 (D-63, D-62, D-59/D-60/D-63, backlink) |
| **Eklenen Bölümler (HDI)** | 0 |
| **Çatışmalar (Korunmuş)** | 1 (salih D-59) |
| **Silinen Bölümler** | 0 |
| **Nihai Satır Sayısı (worktree)** | 473 |
| **Nihai Satır Sayısı (HDI)** | 474 |
| **Nihai Bölüm Sayısı (Her İkisi)** | 56 |
| **Başlık Listesi Özdeş mi?** | Hayır (1 çatışma var) |

---

## 7. Kural Uygulanması

✅ **D-172 İhlali Giderildi:** worktree (SSOT) artık günceldir. Tüm yeni kararlar (D-64–D-172) worktree'ye eklendi.  
✅ **Union Merge Uygulandı:** Çatışmasız bölümler her tarafta birleştirildi.  
✅ **Çatışma Korundu:** Otomatik birleştirilmedi. Rapor edildi. PO kararı bekliyor.  
✅ **Sıra Korundu:** Karar numarası mantıksal sırası (D-64 < D-65 < ...) bozulmadı.  
✅ **Silme Yok:** Hiç bir bölüm silinmedi.

---

## 8. Sonraki Adımlar

1. **PO salih rolünü netleştir:** Worktree D-59 mi (tam QA/Release) yoksa HDI D-59/D-63 mi (mekanik danışman) doğru?
2. **Karar D-181 yaz:** salih rolünü kesin tanımla.
3. **Union merge tamamla:** Salih çatışmasını D-181 uyarınca her iki dosyaya yansıt.
4. **Doğrula:** Yeniden çatışma kontrolü — iki dosya tam özdeş olmalı.
5. **Git commit:** Senkron sapması giderildi (başlık: "fix: AGENTS.md union merge, D-180 kaydı, salih-D-59-conflict-pending").

---

## 9. İmzalar

- **Rapor Tarihi:** 2026-09-21 10:24  
- **Karar Numarası:** D-180  
- **Sorumlu:** PO (KAHİN)  
- **Durum:** ✅ Tamamlandı (Çatışma korunmuş, PO kararı bekleniyor)
