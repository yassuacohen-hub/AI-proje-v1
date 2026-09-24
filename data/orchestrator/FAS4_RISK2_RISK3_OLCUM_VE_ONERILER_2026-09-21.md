# FAS 4 — Risk 2 & 3 Ölçüm ve PO Kararları (2026-09-21)

**Amaç:** Risk 2 (ikiz dosya senkron) ve Risk 3 (kapsam eksikliği) için veri-driven öneriler sunmak.

---

## Risk 2: İkiz Dosya Senkron — Yaşayan Problemi Harita

### Genel Bulgu
- **Toplam MD dosya:** 2388
- **İkiz grup:** 220 (223 farklı ad)
- **İkiz dosya:** 1224 (toplam %51)

### Sorun Kaynağı
**99% sebebi:** `.agents/marketplace/` klasöründeki 264 `SKILL.md` dosyası — her skill bir SKILL.md kopyası taşıyor.
Bu hafif sayılabilir (.agents/, .roo/ içi kopya = beklenen yapı).

### Ana Vault İçinde Gerçek İkizler (Vault-level)
Canonical olmayan, senkronize edilmeyen **11 tespit edilen ikiz:**

```
PROJECT_ROADMAP.md
├─ Huginn Data Insights/PROJECT_ROADMAP.md  (✓ canonical, hub linkli, backlink alıyor)
└─ Huginn Data Insights/AI proje v1/PROJECT_ROADMAP.md  (✗ emoji başlıklı, orphan, backlink yok)

ADMIN_UI_SISTEMI.md
├─ Huginn Data Insights/docs/ADMIN_UI_SISTEMI.md  (✓ canonical, backlink eklenmiş)
└─ Huginn Data Insights/AI proje v1/V10/...ADMIN_UI_SISTEMI.md  (✗ orphan, backlink yok)

[+ 9 diğer ikiz grup, benzer patern]
```

### Risk 2 Sonucu — 3 Seçenek

| Seçenek | Aksyon | Maliyet | Risk | PO Tercih |
|---------|--------|--------|------|----------|
| **A: Temiz Sil** | `AI proje v1/` ikizlerini sil, `Huginn Data Insights/` kalan kalıp | Düşük | `AI proje v1/` erişim kaybı | ✓ Önerilen |
| **B: Birleştir** | Tüm ikizleri canonical'a merge et | Yüksek | Manual çatışma çözüm | |
| **C: Görmezden Gel** | Hub stratejisini canonical'a kısıtla, ikizler varolsun | Orta | Graph saçılması devam | |

**Tavsiye:** Seçenek A — `AI proje v1/` klasörü eğer "eski proje snapshot" ise `.arsiv/` taşı; aksi takdirde 11 ikizi sil.

---

## Risk 3: Kapsam Eksikliği — İkinci Dalga Hub Adayları

### Ölçüm Tablosu — Orphan Noktalar Konu Başına

| Konu | Orphan | Hub Adayı | Dosya Örneği |
|------|--------|-----------|--------------|
| **Müşteri Paneli/Huginn** | 1107 | ✓ Kuvvetli | `system_prompt.md`, `SPRINT_*.md` (sprint doklar) |
| **Veritabanı/Sema** | 225 | ✓ Kuvvetli | `schema.md`, `dlt-migration.md` (migration yönergeler) |
| **Güvenlik/Auth** | 31 | ○ Orta | `auth-flows.md`, `security.md` (auth belgeler) |
| **Deploy/Altyapi** | 16 | ○ Orta | `ci/cd-deployment.md`, `config-files.md` |
| **n8n/Workflow** | 10 | ○ Orta | `n8n-architect.agent.md`, workflow referans |
| **Marka/Brand** | 2 | ✗ Zayıf | Pek az orphan |
| **Konusuz** | 12 | – | Planda/rapor dokular (intentional orphan) |

### Bulgu
- **Müşteri Paneli**: FAS 5'in **kore adayı** — 1107 orphan, çoğunlukla sprint/arayüz dokümanı.
  Orphan'lar: `PO_KARAR_FORMU_SPRINT_2026-09-21`, `SPRINT_BASLATMA_BELGESI_2026-09-21`, system_prompt vb.
  → Bu belgeler koordinasyon/görünürlük hub'ında kullanıcı hikayesi/gereksinim toplaması ister.

- **Veritabanı/Sema**: **İkinci öncelik** — 225 orphan, teknik derin referanslar.
  → Ayrı "Teknik Derinlik" hub'ında yer alması, TECHNICAL_DOCS_HUB'dan bağlanarak faydalı.

- **Güvenlik/Auth**: **Üçüncü** — küçük ama kritik (Auth mimarisi, RBAC yönergeler).
  Mevcut `ORKESTRASYON_AJANLAR_HUB` kapsıyor; ayrı hub yerine bu hub'da "Güvenlik & Yetki" bölümü yeterli olabilir.

---

## PO Kararı Gerekli — 2 Senaryo

### Senaryo 1: Minimal (Bu Sprint Bitiş)
1. **Risk 2 Seç:** Seçenek A — `AI proje v1/` ikizlerini `.arsiv/` taşı (git history kayıt).
2. **Risk 3 Seç:** Yalnız **Müşteri Paneli HUB** FAS 5'de oluştur (1107 orphan çözüm, ROI yüksek).
3. **Veritabanı/Sema:** FAS 6'da değerlendir.

**Tahmin:** Risk 2 +2h, Risk 3 FAS5 +4h.

### Senaryo 2: Kapsamlı (Iki Dalga)
1. Risk 2: Seçenek A
2. Risk 3: Üç hub FAS 5'de — Müşteri Paneli, Veritabanı, Güvenlik.

**Tahmin:** Risk 2 +2h, Risk 3 (3 hub) +8h.

---

## Tavsiye

| Adım | İş | Sorumlu | Bağlı Risk |
|------|-----|---------|-----------|
| **Hemen** | Risk 2 Seç: A veya B | PO | Project discovery |
| **FAS 5** | Risk 3 Müşteri Paneli HUB | TBD | Sprint planning |
| **FAS 5+ gerekli** | Veritabanı/Sema HUB | TBD | Teknik derinlik yönü |

---

## Dosya Bulguları (Doğrulama)

Ölçüm scripti: `data/_tmp/_graph_olc.py`
```
TARANAN_MD      2388
IKIZ_GRUP       220
IKIZ_DOSYA      1224
ORPHAN          1120
```

Backlink doğrulama (FAS 3 sonrası):
```
HUB_ICI_LINK    315   (hub dosyalarındaki yönler)
HEDEF_BACKLINK  112   (vault'taki backlink yönleri)
TOPLAM_LINK     427
KIRIK_LINK      0
```

---

## Aksiyon Önerisi PO'ya

1. Risk 2 — Karar Formu: Seçenek A (Sil) veya B (Birleştir)?
   - Seçim: _______________
   - PO İmza: _____________

2. Risk 3 — FAS 5 Kapsam:
   - [ ] Müşteri Paneli HUB (TED = tavsiye edilen)
   - [ ] Veritabanı/Sema HUB (FAS 6'ya ertele)
   - [ ] Güvenlik/Auth (ORKESTRASYON_HUB içinde konuşmalı bölüm + Future HUB)

   PO İmza: _____________
   Tarih: 2026-09-21
