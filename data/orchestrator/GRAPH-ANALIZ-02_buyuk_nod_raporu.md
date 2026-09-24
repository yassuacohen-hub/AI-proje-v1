# GRAPH-ANALIZ-02: Büyük Nod Bağlantısızlık Raporu

**Tarih:** 2026-09-21  
**Kapsam:** 1113 dosya, 58 büyük nod (>20KB veya >500 satır)  
**Temel Bulgu:** 36 büyük nod (%62) tamamen izole (gelen link = 0).

---

## Özet İstatistikler

| Metrik | Değer |
|--------|-------|
| **Toplam dosya** | 1113 |
| **Orphan (gelen link = 0)** | 671 (%60.3) |
| **Büyük nod** | 58 |
| **Büyük nod baglantisiz (Tür C/C+A)** | 36 (%62.1) |
| **Kırık link** | 88 (tüm dosyalarda) |

### Büyük Nod Türü Dağılımı

| Tür | Sayı | Anlam |
|-----|------|-------|
| **C+A** | 23 | İzole + söz dizimi yok (en kötü) |
| **C** | 13 | İzole (ama giden link var) |
| **A** | 11 | Söz dizimi yok ama referans alıyor |
| **B** | 4 | Kırık giden link var |
| **OK** | 7 | Sorun yok ✓ |

---

## Büyük Nodlar: Ağaç Bazında Dağılım

```
worktree klasoru:
  - Toplam: 306 | Orphan: 304 (%99.3) ⚠️ KRİTİK
  - Örnek C: ROO_ELESTIRI_NOTLARI.md (46KB, 0 gelen link)
  - Örnek C: versiyon_8_baglam_dokumani.md (47KB, 0 gelen link)

Huginn Data Insights:
  - Toplam: 355 | Orphan: 147 (%41.4)
  - Örnek OK: ROO_ELESTIRI_NOTLARI.md (46KB, 4 gelen link) ← AYNI DOSYA
  - Örnek OK: versiyon_8_baglam_dokumani.md (46KB, 10 gelen link)

HDI/AI proje v1:
  - Toplam: 181 | Orphan: 41 (%22.7)
  - Örnek OK: sirket_master_ana_belgesi.md (15KB, 90 gelen link)

worktree/AI proje v1:
  - Toplam: 59 | Orphan: 53 (%89.8)
```

---

## KRİTİK BULGU: İkiz Dosya Favorileme Sorunu

Vault ağaçlarında **959 ikiz dosya** bulunmaktadır (334 ikiz grup). Aynı dosya, farklı ağaçlarda tekrarlanıyor:

### En Büyük İkiz Gruplar (örnek)

1. **readme.md** — 32 kopya
   ```
   - worktree klasoru/README.md (0 gelen link)
   - worktree klasoru/src/company_master/README.md (0 gelen link)
   - Huginn Data Insights/README.md (0 gelen link)
   - Huginn Data Insights/src/company_master/README.md (0 gelen link)
   - ...
   ```

2. **changelog.md** — 11 kopya
   ```
   - worktree klasoru/CHANGELOG.md (0 gelen link) — C+A tipi
   - Huginn Data Insights/CHANGELOG.md (0 gelen link) — C+A tipi
   - Huginn Data Insights/AI proje v1/CHANGELOG.md (0 gelen link) — C tipi
   ```

3. **calisma_gunlugu.md** — 3 kopya
   ```
   - worktree klasoru/docs/CALISMA_GUNLUGU.md (0 gelen link) — C+A tipi
   - Huginn Data Insights/docs/CALISMA_GUNLUGU.md (0 gelen link) — C+A tipi
   - Huginn Data Insights/AI proje v1/docs/CALISMA_GUNLUGU.md (2 gelen link) — A tipi
   ```

**Patern:** HDI ve worktree kopyaları 0 link, ama aynı dosyanın başka bir kopyası 2-90 link alıyor.

---

## Kök Neden: Link Çözümleme Algoritması

[`vault_saglik.py` → `resolve_target()`](worktree%20klasoru/scripts/vault_saglik.py) ve [`graph_analiz_02.py` → `coz()`](worktree%20klasoru/scripts/graph_analiz_02.py) içinde:

```python
# Adım 1: Tam yol eşleştirmesi (case-insensitive)
# Adım 2: İsim-bazlı eşleştirme:
adaylar = isim_map.get(Path(hedef).name.lower())
return adaylar[0]  # ← İLK aday, alfabetik sıralı
```

**Sorun:** `dosyalar` listesi `sorted()` ile alfabetik sıralanıyor. `isim_map[dosya_adı]` sorgulandığında:
- Huginn Data Insights kopyaları (H) → worktree klasoru (w) kopyalarından önce sırada
- Link yazarlar (örn: `[[readme.md]]`) yazarsa, **ilk aday (HDI) seçiliyor**
- worktree klasoru kopyası hiç referans almıyor

**Sonuç:** worktree klasoru ağacı %99.3 orphan.

---

## Tür-Bazında Analiz

### Tür C+A: İzole + Söz Dizimi Yok (23 örnek)

En kritik — hem link almıyor hem de kendi linkini yazmıyor.

| Dosya | Boyut | Agac | Gelen | Giden | Kirik | Not |
|-------|-------|------|-------|-------|-------|-----|
| CALISMA_GUNLUGU.md | 41.26 KB | worktree klasoru | 0 | 0 | 0 | Günlük/log — referans edilmemeli ama orphan |
| CALISMA_GUNLUGU.md | 41.26 KB | HDI | 0 | 0 | 0 | Aynı dosya, aynı sorun |
| MUNINN_STREAMLIT_PLAN_... | 35.88 KB | worktree klasoru | 0 | 0 | 0 | Plan belgesi — hub'a bağlanmalı |
| gorev_panosu.md | 40.46 KB | HDI/data_worktree | 0 | 0 | 0 | Task dashboard — index'te görülmeli |
| CHANGELOG.md | 26.26 KB | worktree klasoru | 0 | 0 | 0 | Tarih / arşiv — silinebilir veya tag ekle |

**Çözüm:** Tür C+A dosyaları üç gruba ayır:
1. **Arşiv/Tarih:** silinebilir veya `.arsiv/` taşı
2. **Index'te görülmeli:** ana hub'lara geri-link ekle (örn: README)
3. **Kullanıcı belgesi:** POA/PO kararları hub'da listelenirse görülecek

### Tür C: İzole ama Giden Link Var (13 örnek)

| Dosya | Boyut | Agac | Gelen | Giden | Not |
|-------|-------|------|-------|-------|-----|
| versiyon_8_baglam_dokumani.md | 47.9 KB | worktree/AI proje v1 | 0 | 6 | **Aynı dosya HDI kopyası 10 gelen link alıyor** |
| versiyon_9_baglam_dokumani.md | 40.19 KB | worktree/AI proje v1 | 0 | 6 | **Aynı dosya HDI kopyası 28 gelen link alıyor** |
| ROO_ELESTIRI_NOTLARI.md | 46.02 KB | worktree klasoru | 0 | 1 | **Aynı dosya HDI kopyası 4 gelen link alıyor** |

**Patern:** Tüm C tipi dosyaların HDI eşdeğerleri OK/A tipi.

**Çözüm:** Link yazarlar doğru ağaca referans vermeli. Örn: `[[Huginn Data Insights/docs/ROO_ELESTIRI_NOTLARI]]` yerine canonical hub seç.

### Tür A: Söz Dizimi Yok ama Referans Alıyor (11 örnek)

| Dosya | Boyut | Agac | Gelen | Giden | Not |
|-------|-------|------|-------|-------|-----|
| AGENTS.md | 37.17 KB | HDI | 5 | 0 | Tür A: hub belgesi, referans alıyor ama link yazmıyor |
| MUNINN_STREAMLIT_PLAN... | 35.88 KB | HDI | 1 | 0 | Plan: referans alınıyor ama linkler yazılmamış |

**Çözüm:** Tür A dosyaları hub/index — giden link yazması isteğe bağlı.

### Tür B: Kırık Link (4 örnek)

| Dosya | Boyut | Agac | Gelen | Giden | Kirik | Hedefi Olmayan Link |
|-------|-------|------|-------|-------|-------|---------------------|
| VAULT_HARITA.md | 37.93 KB | worktree | 3 | 451 | 20 | Otomatik harita (451 giden link!) |
| P7-27_ai_cost_dashboard... | 30.31 KB | HDI | 1 | 0 | 1 | Yapı referansı yok |
| OPERASYON_KILAVUZU.md | 20.96 KB | worktree | 1 | 10 | 5 | Kırık referanslar düzeltilmeli |

**Çözüm:** VAULT_HARITA.md otomatik harita — tarama yapısı güncellenirse link sayısı değişir.

---

## Tür-Bazında Çözüm Stratejisi

### 1. Tür C+A → 3 Alt Gruba Ayır

- **Arşiv:** `CHANGELOG.md`, tarih dosyaları → `.archive/` taşı veya silinir
- **Index:** `README.md`, `AGENTS.md` → root index'e geri-link ekle (`[[README.md#Kaynaklar]]` vb.)
- **İçerik:** diğer dosyalar → ilgili hub'lara (`[[Huginn Data Insights/docs/MUNINN_STREAMLIT_PLAN_2026-09-18]]` → hub:Muninn)

**Tahmini etki:** 23 × 0 → 23 × (1-5) gelen link = **%50 iyileşme**

### 2. Tür C → Canonical Hub Seç

- worktree kopyaları **yoksay** (D-174 sonrası HDI canonical)
- HDI versiyonlar sadece işaret edilen ağaçta kalır
- Tarama: `worktree klasoru/` artık ignore edilebilir (esnek D-169 vs D-174 çelişkisi çözülür)

**Tahmini etki:** 13 × 0 → 13 × (2-30) = **%300+ iyileşme** (büyük nod bağlantı kredisi HDI kopyaları alacak)

### 3. Tür A → İsteğe Bağlı

- Halihazırda referans alıyor (gelen link > 0)
- Giden link yazması opsiyonel (hub belgesi olması muhtemel)
- **Eylem:** almadan bırak

### 4. Tür B → Kırık Linkler Düzelt

- Kırık hedefler: `12_kalite_metrikleri` (3×), `indexed-in-VAULT` (2×), vb.
- Script çalıştır: `vault_saglik.py --duzelt --uygula`

**Tahmini etik:** 20 kırık link → 0 = **%100 düzeltme** (4 büyük nod temizlenir)

---

## Karar Noktaları (D-177: Hub Bağlama Stratejisi)

### Seçim 1: Canonical Ağaç

**A.** HDI canonical (D-169), worktree ignore  
**B.** worktree canonical (D-174), HDI → secondary  
**C.** Hybrid: her ağaç kendi hub'ı (karmaşık, önerilmez)

**Önerilen:** **A (HDI canonical)**
- Gerçek Obsidian görünümü HDI ağırlıklı
- worktree 99% orphan durumunu düzeltir
- Yeni dosyalar → HDI yazılır

### Seçim 2: Büyük Nod Hub Atanması

| Nod | Tür | Tahmini Hub | Nedensellik |
|-----|-----|------------|------------|
| versiyon_8_baglam_dokumani.md | C | V10 Mimari | Versiyonlar hub |
| ROO_ELESTIRI_NOTLARI.md | C | Kararlar / Eleştiri | Noel notları |
| CALISMA_GUNLUGU.md | C+A | Arşiv / Silinir | Tarih log |
| AGENTS.md | A | Agent Katalog | Index belgesi |
| MUNINN_STREAMLIT_PLAN | C+A | Muninn Hub | UI plan — hub referanslı |

### Seçim 3: Tür A Davranışı

- **Pasif:** gelen link alamadan işaret edilir
- **Aktif:** giden link yazması istenir (hub: İçindekiler referansı)

**Önerilen:** **Aktif** — her hub belgesi kendi hub'ında linkler yazsın (navigasyon)

---

## Sonraki Adımlar

1. **D-177 Kararını Uygula:** Canonical = HDI, tür-bazlı çözümler planlandı
2. **Backlink Ekleme:** Tür C+A/C dosyaları hub'lara atanır
3. **Kırık Link Düzeltme:** `vault_saglik.py --duzelt`
4. **Tarama Tekrarla:** iyileşme ölçümü (%0 → %90+ hedef)

---

## Appendix: Tüm Büyük Nodlar (Tür Bazında)

### Tür C+A (23)
```
CALISMA_GUNLUGU.md (41.26 KB) — 3 kopya
MUNINN_STREAMLIT_PLAN_2026-09-18.md (35.88 KB)
gorev_panosu.md (40.46 KB)
CHANGELOG.md (26.26 KB) — 2 kopya
HUGINN_V10_PLAN_NETLESTIRME_2026-09-18.md (23.76 KB) — 3 kopya
... (ve 18 daha)
```

### Tür C (13)
```
versiyon_8_baglam_dokumani.md (47.9 KB) — worktree kopyası
ROO_ELESTIRI_NOTLARI.md (46.02 KB) — worktree kopyası
versiyon_9_baglam_dokumani.md (40.19 KB) — worktree kopyası
P7-27_ai_cost_dashboard_architecture.md (30.31 KB)
... (ve 9 daha)
```

### Tür A (11)
```
AGENTS.md (37.17 KB)
MUNINN_STREAMLIT_PLAN_2026-09-18.md (35.88 KB)
CALISMA_GUNLUGU.md (41.26 KB) — HDI/AI v1 kopyası
... (ve 8 daha)
```

### Tür B (4)
```
VAULT_HARITA.md (37.93 KB, 20 kırık)
P7-27_ai_cost_dashboard_architecture.md (30.31 KB, 1 kırık)
OPERASYON_KILAVUZU.md (20.96 KB, 5 kırık)
apify_entegrasyon_arastirmasi_20260910.md (20.28 KB, 5 kırık)
```

### Tür OK (7)
```
01_versiyon_8_baglam_dokumani.md — HDI/AI v1 (10 gelen)
01_versiyon_9_baglam_dokumani.md — HDI/AI v1 (28 gelen)
sirket_master_ana_belgesi.md — HDI/AI v1 (90 gelen)
harici_ajan_protokolu.md (11 gelen)
01_v9_ile_karsilastirma.md — HDI/AI v1 (22 gelen)
ROO_ELESTIRI_NOTLARI.md — HDI (4 gelen)
versiyon_6_baglam_dokumani.md — HDI/AI v1 (12 gelen)
```

---

**Raporlayan:** GRAPH-ANALIZ-02  
**Karar:** D-177 bekleniyor (Hub Bağlama Stratejisi)
