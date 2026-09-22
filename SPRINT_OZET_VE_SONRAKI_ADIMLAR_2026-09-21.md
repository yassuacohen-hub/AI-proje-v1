# SPRINT ÖZET VE SONRAKI ADIMLAR
**Tarih:** 2026-09-21 22:13 UTC+3 | **Hazırlık Durumu:** ✅ TAM

---

## NELER HAZIRLANDII

### 3 STRATEJIK BELGE OLUŞTURULDU

1. **`SPRINT_GRAPH_STRATEGISI_2026-09-21.md`**
   - 4 fazlı uygulama planı (Temizlik → Hub Genişletme → Backlink → Ölçüm)
   - 40–54 saatlik takvim
   - Script şablonları ve kategoriler
   - Risk analizi

2. **`PO_KARAR_FORMU_SPRINT_2026-09-21.md`**
   - 5 kritik karar (Emoji, Hub Stratejisi, Supabase, Canonical, Kırık Link)
   - Her kararın 2–3 seçeneği, etki analizi
   - PO onayı için imza satırları
   - Trade-off açıklaması

3. **`SPRINT_BASLATMA_BELGESI_2026-09-21.md`**
   - WBS (Work Breakdown Structure) — 8 görev × 3–5 saatlik alt görevler
   - RACI matrix (Sorumlu, Muhasebeci, Danışman, Bilgilendirilen)
   - Başarı kriterleri (Done definition)
   - Blokajlar, riskler, kaynaklar

### SORUN ÖZETI

| Metrik | Değer | Hedef |
|--------|-------|-------|
| **Dosya Sayısı** | 389 (exclude: tur, .kilo, _ARSIV) | — |
| **Orphan Dosya** | 261 (%67.1) | %30–40 |
| **Emoji Başlık İçeren Dosya** | 62 | 0 |
| **Hub Backlink'leri** | 7 (PROJECT_ROADMAP'te) | 45–60 |
| **İkiz Dosya Çatışması** | 415 (3 branch) | 0 (1 canonical) |
| **Supabase İzole Nod** | 5 | 0 (ignore) |

### 5 KRİTİK KARAR — ÖNERİLEN SEÇENEKLER

| # | Konu | Seçenek | Takvim | Etki |
|---|------|---------|--------|------|
| 1️⃣ | Emoji Temizliği | B: Script+Review | 1.5–2 saat | %99 doğruluk |
| 2️⃣ | Hub Stratejisi | A: Genişletme | 24–32 saat | %67→%40 orphan |
| 3️⃣ | Supabase | A: Ignore | 20 dakika | %67→%66 |
| 4️⃣ | Canonical | A: data/ | 1–2 saat | 415 ikiz→0 |
| 5️⃣ | Kırık Link | A: 2 dosya (VAULT + OP) | 3 saat | 6→4 beklemeye |

---

## PO'DAN GEREKLİ ADIM

### ⏸ BLOKAJ: PO Onayı Gerekli

**`Huginn Data Insights/PO_KARAR_FORMU_SPRINT_2026-09-21.md`** dosyasını aç ve:

1. **Bölüm I — KARAR 1–5:** Her karar altında seçeneği işaretle
   ```
   [✓] A seçildi  ← Boşluğa işaret koy
   ```

2. **Bölüm VI — ONAY & İMZA:** 
   - Karar Tarihi: bugün
   - İmza: PO ismi/tarihi

3. **Dosyayı kaydet ve Slack/email'de onayla**

**Gerekçe:** Bunlar ürün kararları, PO onayısız sprint başlamayacak.

---

## SONRAKI ADIMLAR (PO ONAYINDAN SONRA)

### ADIM 0: HAZIRLIK (30 dakika)

```bash
# 1. Sprint board güncellensin
python scripts/gorev_ekle "GRAPH-HUB-GENISLEME-01" --proje=graph --durumu=baslamaya_hazir

# 2. Git branch (opsiyonel)
git checkout -b sprint/graph-hub-genisleme-2026-09-21
```

### ADIM 1: TEMİZLİK (4–6 saat)

**1.1 Emoji Başlık Temizliği**
```bash
python data/_tmp/_emoji_baslik_temizle.py --mode=suggest > /tmp/emoji_oneri.txt
# Manual review ilk 20 dosya, sonra batch apply
```

**1.2 Canonical & Exclude Güncelleme**
```json
// .obsidian/app.json — userIgnoreFilters'a ekle:
"data_worktree/",
"Huginn Data Insights/AI proje v1/",
"data/skills/supabase/"
```

**1.3 Kontrol**
```bash
# Graph refresh — Obsidian'da "Bağlantısızlar" filtresi çalıştır
# Orphan sayısı % görülmeli (hedef: 66–67)
```

### ADIM 2: HUB GENIŞLETME (12–16 saat)

**2.1 README Hub Oluştur**
```bash
# Huginn Data Insights/README.md — Bölüm ekle:
## İlgili Belgeler

### Teknik Mimari
- [[Huginn Data Insights/src/company_master/orchestrator/README.md]]
- [[scripts/osint_engine.py]]
...
```

**2.2 AGENTS Hub Oluştur**
```bash
# Huginn Data Insights/AGENTS.md — Bölüm ekle (line 450+ sonrası):
## İlgili Belgeler ve Görevler

### İhsan (Orkestratör) Kanal
- [[data/orchestrator/]]
- [[data/orchestrator/task_board.json]]
...
```

**2.3 PROJECT_ROADMAP Hub Genişlet**
```bash
# Huginn Data Insights/PROJECT_ROADMAP.md — Faz 4 ekle:
## 🎯 FAZ 4: Hub Genişletme Görevleri
- [[Huginn Data Insights/docs/MUNINN_STREAMLIT_PLAN_2026-09-18]]
...
```

### ADIM 3: BACKLINK UYGULAMA (16–24 saat)

**3.1 Backlink Generator Script Çalıştır**
```bash
python data/_tmp/_hub_backlink_generator.py --output=/tmp/backlink_kategoriler.csv
```

**3.2 Hub'lara Kategorileri Ekle**
```bash
# README / AGENTS / PROJECT_ROADMAP'ta:
# - Kategoriler (Teknik, Veri, Planlama, vb.)
# - Her kategoride 3–5 dosyaya backlink
# İşlem: 12–18 saat (paralel işlemle 8–10 saate çekilebilir)
```

**3.3 Doğrulama**
```bash
python data/_tmp/_backlink_validator.py --hubs=README,AGENTS,PROJECT_ROADMAP
# Çıktı: valid link'ler, broken link'ler (varsa)
```

### ADIM 4: ÖLÇÜM & RAPORLAMA (8 saat)

**4.1 Orphan Yeniden Ölçüm**
```bash
python data/_tmp/_emoji_baslik_tara.py
# Beklenen: %67.1 → %35–45
```

**4.2 Hub İstatistikleri**
```
README: 20+ backlink, 5+ kategori
AGENTS: 15+ backlink, 4 ajan kanalı
PROJECT_ROADMAP: 15+ backlink, 4 faz
```

**4.3 Sprint Raporu Yazma**
```bash
# Dosya: data/orchestrator/GRAPH-SPRINT-HUB-GENISLEME_RAPOR_2026-09-21.md
# İçerik:
# - Başlama metriği
# - 4 adım & zamanlar
# - Son metrik
# - Kalan görevler (Faz 2: Tür-Index, Faz 3: Durum takibi)
# - Öneriler
```

---

## BAŞARI KRİTERLERİ (DONEFULNESS)

Sprint bittiğinde kontrol et:

- [ ] **Orphan oranı %35–45** (başlangıç: %67.1)
- [ ] **62 dosya emoji başlığı temiz**
- [ ] **3 hub 45+ backlink'le genişletildi**
- [ ] **Tüm backlink'ler %99+ doğru**
- [ ] **Sprint raporu yazılmış** (`GRAPH-SPRINT-HUB-GENISLEME_RAPOR_2026-09-21.md`)
- [ ] **Git commit** (git push sonrası)

---

## SONRAKI SPRİNTLER (BACKLOG)

### Sprint 2: Tür-Index (FAS 2)
- Yeni dokümantasyon: API.md, Tools.md, Data.md, vb.
- Beklenen takvim: 32–40 saat
- Beklenen orphan: %30–35

### Sprint 3: Durum Takibi & Ölçüm
- Graph health raporları
- Backlink kalitesi audit'i
- Sürdürülebilirlik metrikleri

---

## KRİTİK ÇIKMAZA DÜŞTÜYSE

**Q: Emoji script hataları veriyorsa?**
A: Manuel mode'a geç — 62 dosya × 3 dakika = 3 saat ek

**Q: Backlink'leme taşıyorsa?**
A: Hub'a sadece "top 20" dosya ekle (REST sonraki sprint'e)

**Q: Canonical karar yanlışsa?**
A: Git stash, `.obsidian/app.json` revert, redo (30 dakika)

**Q: PO karar vermez?**
A: Default strateji (A seçenekleri) kullan, rapor yazıp sunuş yap

---

## İLETİŞİM & İZLEME

**Sprint Board:** `data/orchestrator/task_board.json`  
**Günlük Senkron:** 09:00 UTC+3 (15 dakika, standup)  
**Rapor Güncelleme:** Günde 1 (akşam 18:00)

**Sorumlu Ajan:** [Agent/İsim]  
**PO Görüşü:** [PO/İsim]  
**Denetçi:** [yasu]

---

## BELGELER & REFERANSLAR

| Belge | Konum | Amaç |
|-------|-------|------|
| Sprint Stratejisi | `SPRINT_GRAPH_STRATEGISI_2026-09-21.md` | Detaylı uygulama planı |
| PO Karar Formu | `PO_KARAR_FORMU_SPRINT_2026-09-21.md` | 5 karar + onay |
| Sprint Başlama | `SPRINT_BASLATMA_BELGESI_2026-09-21.md` | WBS + RACI |
| **Bu Belge** | `SPRINT_OZET_VE_SONRAKI_ADIMLAR_2026-09-21.md` | Hızlı başlama rehberi |
| Ölçüm Script | `data/_tmp/_emoji_baslik_tara.py` | Orphan % ölçümü |
| Temizlik Script | `data/_tmp/_emoji_baslik_temizle.py` | Emoji başlık temizliği |
| Backlink Generator | `data/_tmp/_hub_backlink_generator.py` | Kategori mapping |
| Validator | `data/_tmp/_backlink_validator.py` | Link doğrulaması |

---

## ⏰ TAKVIM (PO ONAYINDAN SONRAKİ SAATLER)

| Faz | Görev | Başlama | Bitiş | Saatler |
|-----|-------|---------|-------|---------|
| 1 | Temizlik & Canonical | T+0 | T+6 | 6 saat |
| 2 | Hub Genişletme | T+6 | T+22 | 16 saat |
| 3 | Backlink & Doğrulama | T+22 | T+46 | 24 saat |
| 4 | Ölçüm & Rapor | T+46 | T+54 | 8 saat |
| **TOPLAM** | — | — | — | **54 saat** |

**Gerçek takvim:** 22 Eylül 22:00 UTC+3 → 25 Eylül 04:00 UTC+3 (≈ 2.5 gün paralel işlemle)

---

## BAŞLATMADAN ÖNCE

Lütfen kontrol et:

- [ ] 3 belge okundu (SPRINT_GRAPH_STRATEGISI, PO_KARAR_FORMU, SPRINT_BASLATMA)
- [ ] PO 5 kararı onayladı ve imza attı
- [ ] `PO_KARAR_FORMU_SPRINT_2026-09-21.md` kaydedildi
- [ ] Script şablonları hazır (emoji_temizle, backlink_generator, validator)
- [ ] Git branch oluşturuldu (opsiyonel)
- [ ] Sprint board panosu güncellenmiş

**Sonra:** ADIM 0 başlat (hazırlık)

---

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]]

**Sprint Durumu:** 🟡 PO ONAYINA BEKLEMEDE  
**Hazırlık Tamamlanması:** ✅ 100%  
**Tahmini Başlama:** 2026-09-21 23:00 UTC+3 (PO onayı alındıktan sonra)

