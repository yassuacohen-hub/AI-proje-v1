# SPRINT: GRAPH HUB'LAŞTIRMA STRATEJİSİ — 2026-09-21

**Sorun:** 389 dosyada 261 orphan (%67.1), ağ "bağlantısızlar" filtresiyle izole nod yığını.

**Hedef:** %67 → %30–40 orphan oranı (Hub genişletme + backlink stratejisi)

---

## I. BAŞLAMA ÖNCESİ: PO KARARLARI (P0 — KRİTİK)

**Durum:** 5 kararı gerek, sprint başlamaması için.

| Karar | Seçenek | İşe Etkisi | PO Not |
|-------|---------|-----------|--------|
| **1. Emoji başlık temizliği** | A: Manuel (62 dosya) vs B: Script + inceleme | 4 saat vs 1.5 saat | **Seç: B** — Script yaz, başlıkları `##` → `## ` + emoji kaldır |
| **2. Hub strateji** | A: Hub genişletme (README/AGENTS/PROJECT_ROADMAP backlink'le) vs B: Tür-index (API.md, Tools.md, vb.) vs C: Kombo | A: %85→%40, B: %85→%30, C: %85→%15 | **Seç: A** — En düşük risk, 16–24 saat |
| **3. Supabase 5 orphan** | Ignore mı hub nodu mu? | Kapsam belirlenir | **Seç:** Ignore ekle `.obsidian/app.json` → 2 satır |
| **4. HDI iç-ikiz (415 kopya)** | Canonical seç: `data/` vs `data_worktree/` vs `AI proje v1/data/` | 80 grup → 1 kanonical | **Seç:** `Huginn Data Insights/data/` canonical |
| **5. 6 kırık link** | Hangisini çöz: VAULT_HARITA, OPERASYON_KILAVUZU, vb.? | 2–6 saat | **Seç:** VAULT_HARITA + OPERASYON_KILAVUZU; kalan beklemeye al |

**Bekleniyor:** PO onayı. Sprint bu 5 karar olmadan başlamıyor.

---

## II. SPRINT FAZA (Karar Alındıktan Sonra)

### **FAS 1: Temizlik (4–6 saat)**

#### 1.1 Emoji Başlık Standardizasyonu
- **Dosya:** 62 dosya, 197 satır emoji başlık
- **İşlem:** Başlıklardan emoji kaldır, format `## ` tutarak
- **Script:** `data/_tmp/_emoji_baslik_temizle.py` → Otomatik öneri üret
- **Doğrulama:** Manual review (ilk 20 dosya), sonra batch
- **Tahmini:** 2–3 saat

```python
# Örnek: "# 🚀 Huginn Data Insights" → "# Huginn Data Insights"
```

#### 1.2 HDI İç-İkiz Canonical Seçimi
- **Durum:** `data/` vs `data_worktree/` vs `AI proje v1/data/`
- **Karar:** `Huginn Data Insights/data/` = canonical
- **İşlem:** Diğer iki branch'i `.obsidian/app.json` exclude'a ekle
- **Etki:** İkiz dosya çatışması %80 azalır
- **Tahmini:** 1–2 saat

#### 1.3 Supabase Vendor Kararı
- **5 izole nod:** Supabase skill/docs içeriği
- **Karar:** `.obsidian/app.json` → `data/skills/supabase/` exclude'a ekle
- **Tahmini:** 20 dakika

### **FAS 2: Hub Genişletme (16–24 saat)**

#### 2.1 README Hub Genişletme
**Hedef:** `Huginn Data Insights/README.md` → 10–15 backlink ekle

**Kategoriler:**
- **Teknik:** orchestrator, engine, scripts
- **Veri:** data/, models/
- **Doküman:** docs/, plans/
- **Test:** tests/

```markdown
## İlgili Belgeler

### Teknik Mimari
- [[scripts/osint_engine.py]]
- [[src/company_master/orchestrator/README.md]]

### Veri & Modeller
- [[data/]]
- [[Huginn Data Insights/docs/ADMIN_UI_SISTEMI.md]]

### Planlama & Stratejik
- [[Huginn Data Insights/plans/P7-27_ai_cost_dashboard_architecture.md]]
- [[Huginn Data Insights/docs/plans/NAV-PLAN-01_v4.md]]
```

**Tahmini:** 4–6 saat (araştırma + yazma)

#### 2.2 AGENTS Hub Genişletme
**Hedef:** `Huginn Data Insights/AGENTS.md` → Agent başkanları/roller → ilgili bölümlere backlink

**Kategoriler:**
- **İhsan (Orkestratör):** `data/orchestrator/`, task board
- **Utku (Üretim):** `src/`, scripts/
- **Salih (Test):** tests/, quality/
- **Yasu (Review):** docs/review/, raporlar/

**Tahmini:** 4–6 saat

#### 2.3 PROJECT_ROADMAP Hub Genişletme
**Hedef:** Tek satır redirect → tam hub dokümenti

**Yapı:**
- Faz 1–3 görevleri
- FAZ4: **Hub Genişletme Görevler** (backlink'leme strateji + backlink listesi)
- İlgili Nodlar: 55 satırdan 30+ satıra genişlet

**Tahmini:** 3–4 saat

### **FAS 3: Backlink Oluşturma (20–32 saat)**

#### 3.1 Hub Index Oluşturma (Otomatik)
**Script:** `data/_tmp/_hub_backlink_generator.py`

```
giriş: README, AGENTS, PROJECT_ROADMAP
çıkış: kategori → dosya listesi
```

**Kategoriler:**
1. **Teknik Mimari** (15–20 dosya)
2. **Veri & Modeller** (12–18 dosya)
3. **Planlama** (10–15 dosya)
4. **Test & QA** (8–12 dosya)
5. **Doküman & Raporlar** (20–30 dosya)
6. **Ajanlar & Görevler** (5–10 dosya)

**Tahmini:** 2–4 saat (script yazma + test)

#### 3.2 Hub Backlink Uygulama
**İşlem:** Her hub'a kategori başlıkları + backlink'ler ekle

**Örnek:**

```markdown
## Teknik Mimari

- [[Huginn Data Insights/src/company_master/orchestrator/README.md]] — Orkestratör mimari
- [[Huginn Data Insights/scripts/osint_engine.py]] — OSINT motoru
- [[Huginn Data Insights/docs/ADMIN_UI_SISTEMI.md]] — Admin UI sistemi
```

**Tahmini:** 12–20 saat (kategoriler × hub'lar × 3–5 saat)

#### 3.3 Backlink Doğrulama
- **Kontrol:** Her link hedef dosyaya varsa (`[[ ]]` syntax valid mi)
- **Script:** `data/_tmp/_backlink_validator.py`
- **Tahmini:** 2–3 saat

### **FAS 4: Orphan Ölçümü & Raporlama (8 saat)**

#### 4.1 Orphan Yeniden Ölçüm
```bash
python data/_tmp/_emoji_baslik_tara.py  # sozdizimi yok oranı
# Beklenen: %67 → %35–45
```

#### 4.2 Hub Backlink Sayısı
- README: 20+ backlink
- AGENTS: 15+ backlink
- PROJECT_ROADMAP: 10+ backlink

#### 4.3 Rapor Yazma
- **Dosya:** `data/orchestrator/GRAPH-SPRINT-HUB-GENISLEME_RAPOR_2026-09-21.md`
- **İçerik:**
  - Başlama ölçümü (389 dosya, 261 orphan %67)
  - Adımlar & zamanlar
  - Son ölçüm (orphan hedefi %35–45)
  - Kalan görevler (tür-index, durum takibi)

---

## III. RİSK VE TRADE-OFF

| Risk | Çözüm | Kabullenme |
|------|-------|-----------|
| Hub backlink'leri "generic" kalabilir (fazla geniş) | Kategori başlıkları + Türkçe açıklamalar ekle | Evet |
| İkiz canonical karar yanlış olabilir | Karar test edilmeli, hızlı geri dönebilmeli | Evet |
| Emoji kaldırma hataları | Manual review ilk 20 dosya | Evet |
| Backlink'leme zamanı %30 taşabilir | Paralel iş (emoji + hub 1.1 paralel) | Evet |
| Supabase ignore'u yanlışsa graph kapsamı daralır | İgnore yerine hub node + minimal backlink'ler alternatif | Evet |

---

## IV. BAŞARI KRİTERLERİ

- [ ] **Orphan oranı %67 → %35–45** (Plan A hedefi)
- [ ] **62 dosya emoji başlığı temiz** (başlık = başlık + emoji yok)
- [ ] **3 hub dokümantasyonu genişletilmiş** (README, AGENTS, PROJECT_ROADMAP ≥20 backlink'ler)
- [ ] **Backlink'ler doğrulanmış** (script tüm link'leri test)
- [ ] **Rapor yazılmış** (başlama → son durumu, kalan görevler listelenmiş)

---

## V. TAKVIM (Tahmini — Karar Alındıktan Sonra)

| Faz | Görev | Tahmini | Bitişi |
|-----|-------|---------|--------|
| **1** | Temizlik (emoji, ikiz, supabase) | 4–6 saat | Gün 1 saat 12 |
| **2** | Hub Genişletme (3 hub) | 12–16 saat | Gün 2 saat 10 |
| **3** | Backlink Uygulama & Doğrulama | 16–24 saat | Gün 3 saat 15 |
| **4** | Ölçüm & Raporlama | 8 saat | Gün 4 |
| **TOPLAM** | — | **40–54 saat** | — |

---

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]]

## VI. İŞE HAZIRLIK

- [ ] PO bu 5 kararı onaylasın
- [ ] Sprint başlatılacak sprint board'a eklensin (gorev_panosu.md)
- [ ] Script şablonları oluşturulsun (`data/_tmp/`)
- [ ] Hub dosyaları backup'lanacak (git commit)

