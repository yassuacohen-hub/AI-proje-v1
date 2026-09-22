# SPRINT BAŞLATMA BELGESİ — GRAPH HUB'LAŞTIRMA SPRINTI
**Tarih:** 2026-09-21 | **Sprint Adı:** GRAPH-HUB-GENİŞLEME-01

---

## KARAR ÖZETI (PO ONAYLANDI)

### 5 KRİTİK KARAR — ÖNERİLEN SEÇENEKLER

| # | Konu | Karar | Gerekçe |
|---|------|-------|---------|
| 1️⃣ | Emoji Başlık Temizliği | **B: Script + Manual Review** | 4–5 saat → 1.5–2 saat, %99 doğruluk |
| 2️⃣ | Hub Strateji | **A: Hub Genişletme (README/AGENTS/PROJECT_ROADMAP)** | %67 → %40 orphan, 24–32 saat, en düşük risk |
| 3️⃣ | Supabase 5 Orphan | **A: Ignore Ekle (.obsidian/app.json)** | Vendor içeriği, 2 satır değişiklik |
| 4️⃣ | HDI Canonical | **A: Huginn Data Insights/data/ = Canonical** | Üretim doğruluğu, exclude: data_worktree + AI proje v1 |
| 5️⃣ | Kırık Link Çözümü | **A: VAULT_HARITA + OPERASYON_KILAVUZU (1. sprint)** | Kalan 4 sonraki sprint'e (3 saat + 4–6 saat = bu sprint: +3 saat) |

**PO Onayı:** ___________  
**İmza Tarihi:** ___________

---

## SPRINT BAŞLAMA ÖNCESİ KONTROL LİSTESİ

- [x] Sorun tanımlı (389 dosya, 261 orphan %67.1)
- [x] Stratejik belgeler oluşturuldu (SPRINT_GRAPH_STRATEGISI, PO_KARAR_FORMU)
- [x] 5 karar önerildi ve hazırlandı
- [ ] **PO bu belgede checkboxları doldurdu ve imzaladı** ← GEREKLI
- [ ] Sprint board oluşturuldu (`data/orchestrator/task_board.json` güncellendi)
- [ ] Script şablonları oluşturulsun
- [ ] Git branch oluşturuldu (opsiyonel)

**DURDUR:** PO bu kontrol listesini tamamlayana kadar sprint başlamaz.

---

## SPRINT KAPSAMI (WBS — Work Breakdown Structure)

### FAS 1: HAZIRLIK & TEMİZLİK (4–6 saat)

**1.1 Emoji Başlık Temizliği**
- Input: 62 dosya, 197 emoji başlık
- İşlem: Script → öneriler, manual review (ilk 20), batch
- Output: 62 dosya temiz, emoji yok, başlık format tutarlı
- Tahmini: 1.5–2 saat
- Sorumlu: [Agent/İsim]
- Durum: Beklemede

**1.2 HDI Canonical Seçim & Exclude Güncelleme**
- Input: 415 ikiz dosya, 3 branch
- İşlem: `.obsidian/app.json` → `data_worktree/` + `AI proje v1/` exclude'a ekle
- Output: Graph kapsamı clean, canonical = `Huginn Data Insights/data/`
- Tahmini: 1–2 saat
- Sorumlu: [Agent/İsim]
- Durum: Beklemede

**1.3 Supabase Vendor Ignore Ekle**
- Input: 5 izole nod (`data/skills/supabase/`)
- İşlem: `.obsidian/app.json` → `data/skills/supabase/` exclude'a ekle
- Output: 5 orphan → ignore, graph %67 → %66
- Tahmini: 20 dakika
- Sorumlu: [Agent/İsim]
- Durum: Beklemede

### FAS 2: HUB DOKÜMANTASYONU GENİŞLETME (12–16 saat)

**2.1 README Hub Genişletme**
- Input: `Huginn Data Insights/README.md` (30 satır minimal)
- İşlem: 
  - Bölüm ekle: "İlgili Belgeler"
  - Kategori: Teknik Mimari, Veri & Modeller, Planlama, Doküman
  - 15–20 backlink ekle
- Output: README ≥60 satır, ≥15 backlink
- Tahmini: 4–5 saat
- Sorumlu: [Agent/İsim]
- Durum: Beklemede

**2.2 AGENTS Hub Genişletme**
- Input: `Huginn Data Insights/AGENTS.md` (501 satır)
- İşlem:
  - Bölüm ekle: "İlgili Belgeler" (kanal ve rolle eşleştirilmiş)
  - Kategori: İhsan (Orkestratör), Utku (Üretim), Salih (Test), Yasu (Review)
  - 12–15 backlink ekle (ajanlar → görevler/raporlar)
- Output: AGENTS ≥550 satır, ≥12 backlink
- Tahmini: 4–5 saat
- Sorumlu: [Agent/İsim]
- Durum: Beklemede

**2.3 PROJECT_ROADMAP Hub Genişletme**
- Input: `Huginn Data Insights/PROJECT_ROADMAP.md` (1 satır redirect + 64 satır içerik)
- İşlem:
  - Bölüm ekle: "FAZ 4: Hub Genişletme Görevler"
  - Backlink ekle: ilgili sprint raporları, tasarım dokümanları
  - Mevcut backlink'ler → 7 → 15+ backlink
- Output: PROJECT_ROADMAP ≥100 satır, ≥15 backlink
- Tahmini: 3–4 saat
- Sorumlu: [Agent/İsim]
- Durum: Beklemede

### FAS 3: BACKLINK UYGULAMA & DOĞRULAMA (16–24 saat)

**3.1 Hub Index Script Oluştur**
- Input: 389 dosya, exclude listesi
- İşlem: Script `data/_tmp/_hub_backlink_generator.py` → kategoriler ve dosya mapping'i
- Output: CSV/JSON → kategori → dosyalar
- Tahmini: 2–3 saat
- Sorumlu: [Agent/İsim]
- Durum: Beklemede

**3.2 Backlink'leri Hub'lara Uygula**
- Input: 389 dosya, kategori mapping
- İşlem:
  - README: teknik 15–20 dosyaya backlink
  - AGENTS: ajan görevleri 12–15 dosyaya backlink
  - PROJECT_ROADMAP: ilgili raporlar/tasarımlar 10–15 dosyaya backlink
- Output: 40–50 backlink uygulanmış, hub'lar bağlantılı
- Tahmini: 12–18 saat
- Sorumlu: [Agent/İsim]
- Durum: Beklemede

**3.3 Backlink Doğrulama**
- Input: 40–50 backlink, hub'lar
- İşlem: Script `data/_tmp/_backlink_validator.py` → tüm link'ler valid mi?
- Output: Rapor → geçersiz link'ler (varsa) ve düzeltmeler
- Tahmini: 2–3 saat
- Sorumlu: [Agent/İsim]
- Durum: Beklemede

### FAS 4: ÖLÇÜM & RAPORLAMA (8 saat)

**4.1 Orphan Yeniden Ölçüm**
- Input: 389 dosya, yeni backlink'ler
- İşlem: `data/_tmp/_emoji_baslik_tara.py` → orphan % hesapla
- Output: %67.1 → [Beklenen: %35–45]
- Tahmini: 1 saat
- Sorumlu: [Agent/İsim]
- Durum: Beklemede

**4.2 Hub Backlink İstatistikleri**
- Input: 3 hub dokümantasyonu
- İşlem: 
  - README backlink sayısı
  - AGENTS backlink sayısı
  - PROJECT_ROADMAP backlink sayısı
  - Kategori dağılımı
- Output: Tablo/Rapor
- Tahmini: 1 saat
- Sorumlu: [Agent/İsim]
- Durum: Beklemede

**4.3 Sprint Raporu Yazma**
- Input: Tüm ölçümler, adımlar, sonuçlar
- İşlem: `data/orchestrator/GRAPH-SPRINT-HUB-GENISLEME_RAPOR_2026-09-21.md`
- Output:
  - Başlama ölçümü (389 dosya, 261 orphan %67)
  - Adımlar & zamanlar
  - Son ölçüm (orphan hedefi vs gerçek sonuç)
  - Kalan görevler (Faz 2: Tür-Index, Faz 3: Durum takibi)
  - Öneriler & İleri adımlar
- Tahmini: 5–6 saat
- Sorumlu: [Agent/İsim]
- Durum: Beklemede

---

## BAŞARI KRİTERLERİ (DONEFULNESS)

Sprint başarılı sayılır eğer:

- [x] **Strateji belgesi oluşturuldu** ✅ DONE
- [x] **PO karar formu oluşturuldu** ✅ DONE
- [ ] **PO 5 kararı onayladı** ← BLOKAJ
- [ ] **Emoji başlıkları %95+ temiz** (hedef: 62 dosya, %60 temiz = başarı)
- [ ] **Orphan oranı %67 → %35–45** (hedef: ±5 puan)
- [ ] **3 hub 45+ backlink'le genişletildi** (hedef: ≥40)
- [ ] **Backlink'ler %99+ doğrulanmış**
- [ ] **Sprint raporu yazılmış**

---

## BLOKAJLAR VE RİSKLER

| Risk | Olasılık | Etki | Çözüm |
|------|----------|------|-------|
| PO 5 kararı onaylamaz | Orta | Sprint başlamaz | Alternatif stratejiler sunulsun |
| Emoji script hataları | Düşük | 5 dosya manual düzeltme gerekir | Manual review sonrası batch |
| Backlink'leme zamanı taşar | Orta | 2–4 saat delay | Paralel iş (emoji + hub 2.1 paralel) |
| Canonical seçim yanlış | Düşük | Graph kapsamı değişir, redo gerek | Karar hızlı test edilmeli, git branch geri dönebilmeli |
| Hub'lar "generic" backlink'ler ekler | Orta | Graph düşük kaliteli olabilir | Kategori başlıkları + Türkçe açıklamalar |

---

## KAYNAKLAR & REFERANSLAR

- `Huginn Data Insights/SPRINT_GRAPH_STRATEGISI_2026-09-21.md` — Detaylı strateji
- `Huginn Data Insights/PO_KARAR_FORMU_SPRINT_2026-09-21.md` — Karar formu
- `data/orchestrator/GRAPH-SPRINT-OZET_2026-09-21.md` — Önceki sprint raporu
- `.obsidian/app.json` — Graph exclude ayarları
- `data/_tmp/_emoji_baslik_tara.py` — Ölçüm script'i

---

## SONRAKI ADIMLAR

1. **PO bu belgede checkboxları doldurur ve imzalar** (20 dakika)
2. **Sprint board güncellensin** (10 dakika)
3. **Script'ler oluşturulsun** (30 dakika)
4. **Faz 1 başlat** — Temizlik (4–6 saat)
5. **Günlük raporlar** (sprint board'da güncelleme)

---

## SPRINT SAHIBI & İLETİŞİM

- **Sprint Yöneticisi:** [İhsan / Orkestratör]
- **PO:** [Ürün Sahibi]
- **Teknik Lead:** [Agent/İsim]
- **Denetim:** [yasu / Denetim]

**Günlük Senkron:** 09:00 UTC+3 (15 dakika standup)

---

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]]

**Sprint Başlama Tarihi:** ___________ (PO onayı sonrası)  
**Tahmini Bitiş:** ___________ (Başlama + 40–54 saat)

