# GRAPH-FIX-01 — D-169 Enforce Raporu (Graph Canonical = Huginn Data Insights)

**Tarih:** 2026-09-21
**Görev:** GRAPH-FIX-01
**Karar dayanağı:** D-169, D-177, D-178
**Kapsam:** Scope filtreleme + yeniden ölçüm. **SİLME/TAŞIMA/BİRLEŞTİRME YOK.**

---

## 1. KRİTİK NOT — D-172 vs D-177 Ayrımı (yanlış okunmayı önle)

Bu iki karar **çelişmiyor**, farklı katmanlara ait:

| Karar | Ne der | Katman | Anlamı |
|---|---|---|---|
| **D-172** | `worktree klasoru/` = otorite kaynak | **YAZMA / SSOT** | Kod ve doküman **buraya yazılır**. Değişiklik burada yapılır. Git ağacı burada. |
| **D-177** | Graph canonical = `Huginn Data Insights/` | **GRAPH / GÖRÜNÜM** | Obsidian graph, link kredisi, backlink sayımı **burayı** temel alır. |

**Kural:** `worktree klasoru/` = **YAZMA otoritesi (SSOT)**. `Huginn Data Insights/` = **GRAPH görünümü**.
Bir dosyayı düzenlerken `worktree klasoru/` altındaki kopya değiştirilir; graph metriği okunurken `Huginn Data Insights/` altındaki kopya sayılır.

> **Bu görevde `worktree klasoru/` SİLİNMEDİ, TAŞINMADI.** Sadece graph taramasının dışına alındı (filtreleme). Dosyalar yerinde ve yazma otoritesi değişmedi.

---

## 2. Yapılan Değişiklikler (dosya + satır)

### 2.1 Obsidian ignore filtreleri

| Dosya | Satır | Değişiklik | Durum |
|---|---|---|---|
| [`Huginn Data Insights/.obsidian/app.json`](Huginn%20Data%20Insights/.obsidian/app.json:17) | 17 | `"worktree klasoru/"` | **Zaten mevcuttu** — değişiklik gerekmedi |
| [`.obsidian/app.json`](.obsidian/app.json:13) | 13–17 | `".roo/"`, `".obsidian/"`, `".github/"`, `"worktree klasoru/"` eklendi | **Eklendi** |

Kök `.obsidian/app.json` son hali (mevcut girdiler korundu, JSON geçerli):

```json
{
  "userIgnoreFilters": [
    ".venv/", ".kilo/", ".agents/", ".claude/", ".cursor/",
    ".continue/", ".kombai/", ".vscode/", ".pytest_cache/",
    "node_modules/", ".git/", ".roo/", ".obsidian/", ".github/",
    "worktree klasoru/", "AI proje v1/", "data_worktree/"
  ]
}
```

### 2.2 Tarama scope'u (D-169 hizalama)

Her iki scriptte de **mevcut `IGNORE` set'ine tek girdi eklendi**. Yeni parametre / abstraction / config dosyası eklenmedi.

| Dosya | Satır | Değişiklik |
|---|---|---|
| [`worktree klasoru/scripts/graph_analiz_02.py`](worktree%20klasoru/scripts/graph_analiz_02.py:16) | 16–19 | `# ponytail: worktree klasoru/ canonical = Huginn Data Insights (D-177)` + `IGNORE`'a `'worktree klasoru'` |
| [`worktree klasoru/scripts/vault_saglik_genis.py`](worktree%20klasoru/scripts/vault_saglik_genis.py:27) | 27–33 | `# ponytail: worktree klasoru/ canonical = Huginn Data Insights (D-177)` + `IGNORE`'a `'worktree klasoru'` |

`ROOT` **değiştirilmedi** — her iki scriptte de `c:\Huginn Data Projesi` olarak kaldı. Filtreleme `IGNORE` üzerinden yapıldı (minimum diff).

---

## 3. ÖNCE / SONRA Metrik Tablosu

| Metrik | ÖNCE (GRAPH-ANALIZ-02/03) | SONRA (GRAPH-FIX-01) | Δ |
|---|---:|---:|---|
| **Toplam dosya** | 1113 | **750** | −363 (−32.6%) |
| **Orphan sayısı** | 671 | **661** | −10 |
| **Orphan yüzdesi** | %60.3 | **%88.1** | **+27.8 pp** ⚠ |
| **İkiz grup** | 334 | **156** | −178 (−53.3%) |
| **İkiz dosya** | 959 | **426** | −533 (−55.6%) |
| **Kırık link** | 88 | **55** | −33 (−37.5%) |
| **Büyük nod (toplam)** | 58 | **36** | −22 |
| **İzole büyük nod** | 36 | **24** | −12 (−33.3%) |
| **Söz dizimi yok** | — | 646 | — |
| **Case çatışma** | — | 1 | — |

> `vault_saglik_genis.py` orphan sayısı **641** (README/AGENTS/VAULT_HARITA muafiyeti nedeniyle 20 fark). `graph_analiz_02.py` muafiyetsiz sayar → **661**.

### Ağaç dağılımı (SONRA)

| Ağaç | Toplam | Orphan | Orphan % |
|---|---:|---:|---:|
| Huginn Data Insights | 355 | 336 | %94.6 |
| HDI/data_worktree | 200 | 198 | %99.0 |
| HDI/AI proje v1 | 181 | 113 | %62.4 |
| kök | 14 | 14 | %100 |
| **worktree klasoru** | **0** (ignore) | — | — |

---

## 4. Hedefe Ulaşıldı mı? — **HAYIR (kısmen)**

D-178 tahmini: **671 → 146 orphan (%60 → %13)**.
Gerçekleşen: **671 → 661 orphan (%60.3 → %88.1)**.

### Neden tahmin tutmadı — kök neden analizi

Tahmin, "worktree'nin 304 orphan'ı yok olacak, kalan HDI kopyaları link kredisini devralacak" varsayımına dayanıyordu. **Bu varsayım hatalı.** Gerçekte:

1. **Orphan mutlak sayısı neredeyse hiç düşmedi (−10).** Filtrelenen 363 dosyanın neredeyse tamamı zaten orphan'dı. Onları silmek paydayı (1113→750) küçülttü ama payı (671→661) küçültmedi. **Sonuç: orphan yüzdesi düştü değil, YÜKSELDİ (%60.3 → %88.1).**

2. **Asıl sorun ikizlik değil, söz dizimi eksikliği.** 750 dosyanın **646'sında (%86.1)** hiç `[[wikilink]]` veya `[markdown](link.md)` yok. Link vermeyen bir vault'ta link almayan dosya olması matematiksel zorunluluk. İkiz filtreleme bu sorunu çözemez.

3. **HDI ağacı zaten kendi içinde ikizli.** `Huginn Data Insights/` altında hâlâ 156 ikiz grup / 426 ikiz dosya var (`data/` vs `data_worktree/` vs `AI proje v1/data/`). Alfabetik favorileme problemi **HDI içinde devam ediyor** — 415 kopya hâlâ kredi kaybediyor.

### Doğru yorum

D-169 enforce'u **başarıyla uygulandı** ve şu gerçek kazanımları sağladı:
- İkiz gürültü **yarıya indi** (334→156 grup)
- Kırık link **%37.5 azaldı** (88→55)
- İzole büyük nod **üçte bir azaldı** (36→24)
- Graph artık tek bir canonical ağacı yansıtıyor (worktree çift-sayım yok)

Ama **orphan problemi scope filtresiyle çözülmez** — çözümü GRAPH-FIX-02 (backlink/index ekleme) işidir. D-178'in %13 tahmini, "ignore = orphan düşer" varsayımı yanlış olduğu için **revize edilmeli**.

---

## 5. Kalan İzole Büyük Nod Listesi (24 adet)

Tür: **C** = izole (kimse referans vermiyor) · **C+A** = izole + söz dizimi yok (en kötü)

| # | Tür | KB | Dosya |
|---:|---|---:|---|
| 1 | C+A | 41.26 | `Huginn Data Insights/AI proje v1/docs/CALISMA_GUNLUGU.md` |
| 2 | C+A | 41.26 | `Huginn Data Insights/docs/CALISMA_GUNLUGU.md` |
| 3 | C+A | 40.46 | `Huginn Data Insights/data_worktree/orchestrator/gorev_panosu.md` |
| 4 | C+A | 35.88 | `Huginn Data Insights/docs/MUNINN_STREAMLIT_PLAN_2026-09-18.md` |
| 5 | C+A | 32.84 | `Huginn Data Insights/data/orchestrator/gorev_panosu.md` |
| 6 | C | 30.31 | `Huginn Data Insights/plans/P7-27_ai_cost_dashboard_architecture.md` |
| 7 | C+A | 27.29 | `Huginn Data Insights/data/orchestrator/VAULT-TARAMA-02_analiz_2026-09-20_orkestrator.md` |
| 8 | C+A | 26.26 | `Huginn Data Insights/CHANGELOG.md` |
| 9 | C+A | 25.52 | `Huginn Data Insights/scripts/_tavily_skill_incele.md` |
| 10 | C | 24.95 | `VAULT_AUTOMATION_TEMPLATE.md` (kök) |
| 11 | C+A | 23.76 | `Huginn Data Insights/docs/HUGINN_V10_PLAN_NETLESTIRME_2026-09-18.md` |
| 12 | C+A | 22.30 | `Huginn Data Insights/docs/UX_MENU_AGACI_WIREFRAME_2026-09-18.md` |
| 13 | C+A | 22.07 | `Huginn Data Insights/docs/MUNINN_PLAN_UC_TUR_DEGERLENDIRME_2026-09-18.md` |
| 14 | C+A | 21.38 | `Huginn Data Insights/data/orchestrator/PO-BACK-08_kritik_bulgular_20260915_cline.md` |
| 15 | C+A | 21.14 | `Huginn Data Insights/data_worktree/orchestrator/PO-BACK-08_kritik_bulgular_20260915_cline.md` |
| 16 | C | 20.28 | `Huginn Data Insights/AI proje v1/V10/CHANGELOG.md` |
| 17 | C | 13.26 | `Huginn Data Insights/data/skills/supabase/skills/supabase/SKILL.md` |
| 18 | C | 7.81 | `Huginn Data Insights/data/skills/supabase/AGENTS.md` |
| 19 | C | 6.27 | `Huginn Data Insights/data/skills/supabase/CONTRIBUTING.md` |
| 20 | C+A | 5.09 | `Huginn Data Insights/data/skills/supabase/README.md` |
| 21 | C+A | 4.85 | `Huginn Data Insights/data/skills/supabase/skills/supabase-postgres-best-practices/references/_contributing.md` |
| 22 | C+A | 4.85 | `Huginn Data Insights/data/skills/supabase-postgres-best-practices/references/_contributing.md` |
| 23 | C+A | 4.68 | `Huginn Data Insights/AI proje v1/data/skills/supabase-postgres-best-practices/references/_contributing.md` |
| 24 | C+A | 4.68 | `Huginn Data Insights/data_worktree/skills/supabase-postgres-best-practices/references/_contributing.md` |

**Gözlem:** #1/#2, #3/#5, #14/#15, #21/#22/#23/#24 → hâlâ **HDI içi ikiz**. Scope filtresi worktree'yi çıkardı ama HDI'nin kendi iç ikizliğini çözmedi. #17–24 `data/skills/supabase/` vendor içeriği — muhtemelen graph'a hiç girmemeli (ignore adayı).

---

## 6. Kalan Kırık Link Listesi (55 adet) — **UYGULAMA YOK**

> ⚠ Otomatik düzeltme **ÇALIŞTIRILMADI**. Aşağıdaki liste sadece envanterdir. Uygulama ayrı görevde, ürün sahibi onayıyla.

### 6.1 Gerçek kırık iç link (düzeltme adayı)

| Kaynak dosya | Kırık hedef | Tahmini doğru hedef |
|---|---|---|
| `Huginn Data Insights/AI proje v1/V10/00-Home.md` | `02_huginn_master_kaynak_dokumani` | `AI proje v1/V10/02_huginn_master_kaynak_dokumani.md` — dosya adı/yol doğrula |
| `.../V10/06_arsiv/kilo_sitemap_taslaklari_2026_09_14/14_po_panel_haritasi.md` | `12_kalite_metrikleri` (2x) | Arşiv taslağı — hedef hiç oluşturulmamış olabilir |
| `.../V10/06_arsiv/kilo_sitemap_taslaklari_2026_09_14/14_po_panel_haritasi.md` | `product_owner_kararlari` (2x) | `decision_log.jsonl` karşılığı? |
| `Huginn Data Insights/AI proje v1/V10/13_po_karar_analizi.md` | `12_kalite_metrikleri` | Aynı eksik hedef |
| `data/orchestrator/GRAPH-ANALIZ-02_buyuk_nod_raporu.md` | `MUNINN_STREAMLIT_PLAN` | `Huginn Data Insights/docs/MUNINN_STREAMLIT_PLAN_2026-09-18.md` (tarih eki eksik) |
| `data/orchestrator/GRAPH-REFACTOR-01_rapor_2026-09-21.md` | `VAULT_HARITA` (2x) | `VAULT_HARITA.md` — dosya mevcut değil, oluşturulmalı |
| `data/orchestrator/GRAPH-REFACTOR-01_rapor_2026-09-21.md` | `OPERASYON_KILAVUZU` | Hedef dosya yok |
| `data/orchestrator/VAULT-XREF-DUBLO-RAPOR-FINAL_...md` | `data/orchestrator/decision_log` | `data/orchestrator/decision_log.jsonl` (`.md` değil → çözümlenemiyor) |

### 6.2 Yanlış pozitif — düzeltilmemeli

| Tip | Örnek | Neden yanlış pozitif |
|---|---|---|
| Doküman içi **placeholder** | `...`, `file#section`, `dosya#Başlık`, `K1`, `K2`, `data/orchestrator/...`, `data/orchestrator/x` | Rapor metninde **örnek sözdizimi**, gerçek link değil |
| `indexed-in-VAULT` (2x) | `GRAPH-REFACTOR-01_rapor...md` | Etiket/durum belirteci, dosya hedefi değil |
| **Harici URL `.md` ile biten** (≈14x) | `https://docs.apify.com/integrations/mcp.md`, `https://supabase.com/docs/guides/api/securing-your-api.md` | Dış web adresi. `MDLINK` regex'i `.md` uzantısı gördüğü için iç link sanıyor. **Script false-positive'i.** |

> **Öneri:** `resolve_target` / `coz` fonksiyonlarına `http://` `https://` ön-ek kontrolü eklenirse kırık link sayısı **55 → ~35** düşer. Bu bir ölçüm hatası düzeltmesi, içerik değişikliği değil. Ayrı görev.

### 6.3 Case çatışması (1 adet)

`osint_scraper_motoru.md` → iki farklı yazım mevcut: `OSINT_SCRAPER_MOTORU.md` ve `OSINT_Scraper_Motoru.md`. Windows'ta aynı dosya, Obsidian'da ayrı nod riski.

---

## 7. Ham Ölçüm Çıktısı

### 7.1 `graph_analiz_02.py`

```
=== OZET ===
  toplam_dosya: 750
  orphan_gelen_link_0: 661
  sozdizimi_yok: 646
  kirik_link_toplam: 55
  buyuk_nod_sayisi: 36
  buyuk_nod_baglantisiz: 24
  ikiz_grup: 156
  ikiz_dosya: 426
  ikiz_kayip_kopya: 415
  case_catisma: 1
  ai_v1_kirik_hedef: 4

=== BUYUK NOD TUR DAGILIMI ===
  Tur A: 4
  Tur B: 1
  Tur C: 6
  Tur C+A: 18
  Tur OK: 7

=== AGAC DAGILIMI (toplam / orphan) ===
  HDI/AI proje v1: 181 / 113 orphan
  HDI/data_worktree: 200 / 198 orphan
  Huginn Data Insights: 355 / 336 orphan
  kok: 14 / 14 orphan

=== CASE CATISMA: 1 ===
  osint_scraper_motoru.md: ['OSINT_SCRAPER_MOTORU.md', 'OSINT_Scraper_Motoru.md']

=== EN COK KIRIK HEDEF (ilk 15) ===
  3x  ...
  3x  12_kalite_metrikleri
  2x  indexed-in-VAULT
  2x  VAULT_HARITA
  2x  K1
  2x  K2
  2x  product_owner_kararlari
  2x  https://supabase.com/docs/guides/api/securing-your-api.md
  1x  MUNINN_STREAMLIT_PLAN
  1x  OPERASYON_KILAVUZU
  1x  file
  1x  data/orchestrator/...
  1x  data/orchestrator/decision_log
  1x  data/orchestrator/x
  1x  dosya

[OK] self-check gecti
```

`[OK] self-check gecti` → scriptin 3 assert'i (dosya sayısı > 0, büyük nod tutarlılığı, tür dağılımı toplamı) geçti.

### 7.2 `vault_saglik_genis.py`

```
Vault taraniyor (workspace kapsamı)...
   750 dosya bulundu
Referanslar analiz ediliyor...
Büyük nodlar tespit ediliyor (>20KB veya >500 satır)...
   36 büyük nod bulundu
OK Rapor (genişletilmiş): c:\Huginn Data Projesi\data\orchestrator\VAULT-SAGLIK-GENIS_2026-09-21_orkestrator.json
   Toplam dosya: 750
   Büyük nod: 36
   Kırık link: 55
   Orphan: 641
OK CSV: c:\Huginn Data Projesi\data\orchestrator\buyuk_nodlar_2026-09-21.csv
```

**Her iki script exit code 0 ile tamamlandı.**

### Üretilen çıktı dosyaları
- `data/orchestrator/GRAPH-ANALIZ-02_analiz.json` (güncellendi)
- `data/orchestrator/GRAPH-ANALIZ-02_buyuk_nodlar.csv` (güncellendi)
- `data/orchestrator/VAULT-SAGLIK-GENIS_2026-09-21_orkestrator.json` (güncellendi)
- `data/orchestrator/buyuk_nodlar_2026-09-21.csv` (güncellendi)

---

## 8. Sonraki Adım Önerileri

Öncelik sırasına göre:

1. **[YÜKSEK] GRAPH-FIX-02 — Backlink/index ekleme.**
   Asıl darboğaz bu: 646 dosyada (%86.1) hiç link sözdizimi yok. Orphan sorunu **ancak** içeriğe backlink eklenerek çözülür. Hedef: `VAULT_HARITA.md` + tür bazlı hub belgeleri oluştur, 24 izole büyük nodu hub'lara bağla. Beklenen kazanım: orphan %88 → %30 aralığı.

2. **[YÜKSEK] D-178'in %13 tahminini revize et.**
   "Ignore → orphan düşer" varsayımı ölçümle çürüdü. Karar kaydına düzeltme notu eklenmeli, aksi halde sonraki görevler yanlış baseline ile planlanır.

3. **[ORTA] Ölçüm false-positive'ini gider.**
   `resolve_target` / `coz` içine `http://` `https://` ön-ek kontrolü ekle. Kırık link 55 → ~35. Tek satırlık değişiklik, içerik dokunmaz.

4. **[ORTA] HDI içi ikizlik (156 grup / 415 kayıp kopya).**
   `data/` vs `data_worktree/` vs `AI proje v1/data/` üçlüsü aynı sorunu HDI **içinde** tekrar üretiyor. Ürün sahibi kararı gerekli: hangisi HDI-içi canonical?

5. **[DÜŞÜK] `data/skills/` vendor içeriğini ignore et.**
   İzole büyük nodların 8'i (#17–24) supabase vendor dokümanı. Graph'a ait değil, `userIgnoreFilters`'a eklenmeli.

6. **[DÜŞÜK] Case çatışmasını çöz.**
   `OSINT_SCRAPER_MOTORU.md` / `OSINT_Scraper_Motoru.md` tek yazıma indirilmeli.

7. **[DÜŞÜK] Kırık link düzeltmesi.**
   Bölüm 6.1'deki 8 gerçek kırık link, **ürün sahibi onayından sonra** elle veya `--duzelt --uygula` ile giderilir.

---

## 9. Yasak Uyumu

| Yasak | Durum |
|---|---|
| Dosya silme | ✅ Yapılmadı |
| Taşıma | ✅ Yapılmadı |
| İkiz birleştirme | ✅ Yapılmadı |
| Markdown içeriğine backlink/satır ekleme | ✅ Yapılmadı |
| Kırık link otomatik düzeltmesi | ✅ Çalıştırılmadı |
| Git commit/push | ✅ Yapılmadı |
| Yeni bağımlılık | ✅ Eklenmedi |
| Yeni script dosyası | ✅ Oluşturulmadı (mevcut scriptler kullanıldı) |
| Yeni parametre/abstraction/config | ✅ Eklenmedi (tek `IGNORE` girdisi) |
