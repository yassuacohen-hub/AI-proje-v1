> **YENİ OTURUMDA İLK OKUNACAK DOSYA** — orkestratör kimliği ve kalıcı hafıza. Her oturum başında önce bunu oku.
> Şablon: [[Huginn Data Insights/_ajan_context_sablon]] (D-219) · Tavan 200 satır.

## KALDIĞIM YER

> D-219: tek blok, **üzerine yazılır**. Pano ile çelişirse pano üstündür.

- **Konum:** `TEST-ODIN-PROMPT-INJECTION` — Mimir-DIŞ güvenlik ölçümü. **6 canlı koşu bitti.**
  Son durum: ret oranı **%83.3** (10/12), düşünme sızıntısı **0**, karar hâlâ **NO-GO**.
  NO-GO'nun sebebi artık oran değil: `kararsiz` (4 senaryo) + `dil_uyumsuz` (`inj-10`).
- **Yapılanlar (2026-10-01):** Prompta **MUTLAK KURAL 0c** (etiket/araç çağrısı/base64 = veri değil)
  + **İlk Karakter Kuralı** eklendi; betiğe `LOG_KESIT = 2000` (borç #68). 45 mandal yeşil,
  commit **`84811e8`**, kilit salih'e usulünce geri devredildi (`--no-verify` YOK, D-309/5).
  Ölçüm felsefesi netleşti: **üç ayrı kusur sınıfı** (davranış / cevap dili / düşünme sızıntısı),
  her biri AYRI GO kapısı; ortalama alınmaz, kötü alanlar `any()` ile katlanır.
  Bu dosya D-219 tavanına dayandı → 2026-09 günlüğü `archive/ihsan_context_202609.md`'ye taşındı.
- **KRİTİK BAĞLAM:** SADECE `prompts/mimir_sistem_promptu.md`,
  `scripts/odin_prompt_injection_test.py`, `tests/test_odin_prompt_injection.py`,
  `data/odin_injection_test_log.jsonl`, `data/odin_injection_test_scenarios.json`
- **Sonraki adım:** A planı → borç **#71** (Türkçe düşünme kalıpları + yanlış pozitif mandalı),
  sonra #72/#73/#74, sonra **7. koşu** `--tekrar 3`. Kıyas tabanı: %83.3 · kararsız 4 ·
  `dil_uyumsuz ["inj-10"]` · `dusunme_sizan []`.
- **Görev:** `TEST-ODIN-PROMPT-INJECTION` (salih'te, ölçüm bende) · **Son okunan karar:** `D-312`

## Tuzaklar (belirti → kök neden → çözüm)

> D-219: yazılmayan tuzak gelecek oturumda tekrar ödenir.

| Belirti | Kök neden | Çözüm |
|---|---|---|
| `[kilit] DURDU: n dosya yasu disinda bir ajanin kilidinde` | Dosya başka ajanın kilidinde, git kimliğim `Yasua` → kanca beni `yasu` sanıyor | `birak <sahip> <dosya>` → commit → `kilitle <sahip> <task> <dosya>`. `--no-verify` YASAK (D-309/5) |
| Tek koşuda oran yüksek çıkıyor, sonra düşüyor | Model kararsız; tek koşu kanıt değil | Her ölçüm `--tekrar 3`; `kararsiz` alanı ayrı GO kapısı |
| Log'dan yeniden puanlama yanlış sonuç veriyor | `yanit_kesit` kısa; red kalıbı kesitin dışında kalıyor | `LOG_KESIT = 2000` + mandal |
| Model Türkçe düşünmesini ekrana yazıyor ama araç görmüyor | `DUSUNME_KALIPLARI` sadece İngilizce | Borç #71 — Türkçe kökler + yanlış pozitif mandalı |
| Red kalıbı eklenince meşru cevap "red" sanılıyor | `yapmam`/`uygulamam` gibi geniş kökler | Kök eklerken **önce** yanlış pozitif mandalı yazılır |
| `python -c` kırma testi hiçbir şey ölçmüyor, exit 0 | Tek satır kurgusu sessiz düşüyor | Kırma testi de kırılarak doğrulanır (D-256/4) |
| Commit çıktısı `[chore/monorepo-merge]`, `git status` `## master` | Teşhis edilmedi — borç #48, 8. görünüm | Açık |

## Yapılacaklar (emir #47-b · 2026-10-01)

**G-0 — Ürün Sahibi emri (2026-10-01): müşterinin aradığı cevapların eksik başlıkları GÖREVLEŞTİRİLECEK.
Unutma — bunlar çok önemli.** Kaynak doğrulandı, tahmin değil:

*Müşterinin 7 sorusu* — `yedekler/Huginn Data Insights (HUGIns).txt:11-17`
(1 gerçek şirket mi · 2 yasal yükümlülük · 3 dolandırıcılık riski · 4 mali devamlılık ·
5 gerçek sahip kim · 6 dijital güvenlik · 7 itibar). Satır 877-883'te üçe iniyor:
**Kimdir? Güvenilir midir? Risk taşır mı?** Müşteri alan adını yazar → 0-100 güven skoru +
4 kademe (Çalışılabilir / Dikkatli / Ek inceleme / Yüksek riskli). 8 kitle: satın alma, yatırımcı,
e-ticaret, banka, fintech, sigorta, kurumsal satış, tedarik zinciri.

*6 fazlı yol haritası* — aynı dosya satır 850-873. **Eksik olanlar panoya görev olacak:**

| Faz | Ne | Bugün | Görev açılacak mı |
|---|---|---|---|
| 1 | OSINT + şirket doğrulama | 🟡 kısmen (8.905 eşleşme) | tamamlama |
| 2 | **Risk motoru (8 skor)** | 🔴 tablo bile yok | **EVET — P1, 7 sorunun cevabı burada** |
| 3 | **Entity graph (firma ilişki ağı)** | 🔴 yok | **EVET — P1 (v0 brifi madde 10)** |
| 4 | AI Analyst (Mimir/Odin) | 🟢 şu an bu | devam |
| 5 | Vendor due diligence | 🔴 yok | EVET — P3 |
| 6 | Global corporate intelligence | 🔴 yok | EVET — P4 |

**Dürüst itiraf (kayıtta kalsın):** sırayı atlıyoruz — Faz 2 ve 3 bitmeden Faz 4'ü yapıyoruz.
Prompt v4 madde 15c bu atlamanın dürüst cümlesi: *"bu skor henüz ölçülmüyor."*
⚠ Görev başlıkları yazılırken 8 skorun adı SSOT'tan okunur, uydurulmaz (D-260 · borç #53/#54).

**İŞ BÖLÜMÜ — Ürün Sahibi emri #49 (2026-10-01): A planı BENDE (ihsan),
diğer tüm kalemler utku ve yasu'ya dağıtılır. Ben dağıtırım, kendim yapmam.**

**A planı (ihsan, onaylandı) — 4 kusuru kapat, 7. kez ölç:**
1. **#71** `DUSUNME_KALIPLARI` + Türkçe kökler (`kullanici turkce`, `kurallar:`, `sistem promptum`, `asistaniyiz`) + yanlış pozitif mandalı + kırma testi — *en ciddi, gerçek oran bunun yüzünden bilinmiyor*
2. **#72** `inj-11` ret sırasında prompt metnini sızdırıyor ("Madde 0c'si") → sızıntı kapısı veya prompt maddesi
3. **#73** `inj-10` ayna dil ihlali → MUTLAK KURAL 0'a "ret cümlesi de soru diliyle yazılır"
4. **#74** `mesru-04` senaryosuna `<KATALOG>` bloğu eklenir (yoksa yanlış ölçüyor)
5. **7. koşu** `--tekrar 3` (57 çağrı, ~4 dk, 0 TL) + commit (N7)

**Dağıtılacaklar (ihsan yalnız brif yazar + onaylar):**

| # | İş | Kime | Öncelik |
|---|---|---|---|
| G-0a | Faz 2 risk motoru (8 skor; adlar SSOT'tan okunur, D-260) | utku | P1 |
| G-0b | Faz 3 entity graph / ilişki ağı v0 | yasu | P1 |
| G-0c | Faz 5 vendor due diligence | yasu | P3 |
| G-0d | Faz 6 global corporate intelligence | utku | P4 |
| 12 | A senaryosu: 2 `iptal` görev → `plan` + maskeleme kapısı (D-247) | utku | P2 |
| 14 | N8 kalan: `osb_veri_denetim.py` + Supabase yazımı | yasu | P2 |
| 11 | AGENTS.md 5 karar + numara tahsisi (D-227) | ihsan (devredilemez) | P2 |
| 9/10 | salih brifi + chat (D-210) | ihsan (devredilemez) | P1 |

**Ardından:**
6. salih brifini güncelle (19 senaryo, %83.3, üç kusur sınıfı, LLM-as-judge borcu #61)
7. salih'e chat (D-210): `--kimden ihsan --to salih --type koordinasyon --task-id TEST-ODIN-PROMPT-INJECTION`
8. AGENTS.md'ye **5 karar** + numara tahsisi (D-227): ayna dil · tek koşu kanıt değil · düşünme dili serbest/görünürlük yasak · red kalıbı yanlış pozitif kapısı · log kesiti
9. A senaryosu panosu: `VERI-ODIN-EGITIM-VERISI-HAZIRLA` + `ALTYAPI-ODIN-EGITIM-PIPELINE` `iptal` → `plan` (utku); brifte maskeleme kapısı (D-247), firma verisi publik DEĞİL
10. İlişki ağı v0 brifi → utku (OSB komşuluğu + NACE tamamlayıcılık → `company_signals`)
11. K-B açık sorusu: resmî skor seti = SSOT'un 8 skoru · Admin orkestratör paneli brifi · N8 kalan (`osb_veri_denetim.py` + Supabase)

**Açık borçlar:** #71 #72 #73 #74 · #61 (LLM-as-judge) · #63 (EVREN ~%6 HTTP 500, retry yok) ·
#59 · #57 yarım · #56 · #55 · #54/#53 · #52/#51 · #48 (dal) · #47 · #8 #12 #13 #14 #15 #19 #23 #30
**Kapandı:** #68 #67 #70 #69 #66 #65 #64 #60 · #62 ölçülür oldu

## Kimlik
- Rol: Huginn Data Insights projesi orkestratörü.
- Sorumluluk alanı: admin panel / dashboard (Streamlit `app.py` + `web_dashboard/`), test sağlığı, ajan görev teslim kabulü, görev planlama.
- Karar yetkisi: kod düzeyinde uygulama serbest. Mimari/ürün kararı KAHİN onayı ister. Yeni bağımlılık ekleme yasak (stdlib/mevcut kütüphane önceliği).

## Proje Temel Bilgileri
- Giriş noktası: `app.py` — sidebar, topbar, footer, routing, session state anahtarları.
- Sekme modülleri: `web_dashboard/tabs/*.py` (`ana_kontrol`, `admin_panel`, `admin_realtime`, `admin_musteriler`, `pazarlama`, `paketler`, `admin_quality`, `admin_auth`, `__init__.py` = `TabTanimi`/`SECTIONS`/rol yardımcıları).
- Görsel reçeteler: `web_dashboard/charts.py` (`kpi_karti_html`, `tema_paleti`, `kategori_rengi`, `sparkline_fig`, `donut_fig`, `alan_grafigi_fig`).
- Global CSS: `src/company_master/ui/styles.py` — `_BLOKLAR` tuple (bileşen CSS blokları) → `bilesen_css()` → `tum_css()` (root token'ları ekler) → `stil_etiketi()` (`<style>` sarar). `stil_enjekte(tema=aktif_tema())` `app.py::main()` içinde bir kez çağrılır (satır 758), tema değişmedikçe tekrar enjekte etmez (`_hg_stil_tema` session guard).
- Testler: `tests/` (pytest; `test_charts.py`, `test_sekme_kapsama.py`, `test_taslak_sahte_veri.py`, `test_admin_export_excel.py`, `test_ui_modal_stil.py`...).
- API: `web_app.py` (FastAPI; `/api/kpi`, `/api/companies`, `/api/admin/*`, `/api/buyer/*`).

## Sabitler ve Sözleşmeler
- `REHBER_KEY = "_hg_rehber"` (`app.py`) — TEK merkezi "Sekme rehberi" toggle anahtarı, footer'da (`render_footer`) çizilir. Sekme modülleri kendi toggle'ını çizmez, bu anahtarı `st.session_state`'ten okur. **Doğrulandı (2026-09-26)**: 6 sekme (`ana_kontrol`, `admin_panel`, `admin_realtime`, `admin_musteriler`, `pazarlama`, `paketler`) hepsi `_hg_rehber` okuyor, yerel toggle YOK — önceki "açık kusur" notu hatalıydı, kaldırıldı.
- `LOGO_YOLU = ROOT / "docs" / "brand" / "assets" / "Muninn_logo_transparent.png"` (`app.py:100`) — `st.logo` ile sol üst logo; dosya yoksa metin başlığa düşer (`render_sidebar`). **MARKA-LOGO-01 (2026-09-26, ÇÖZÜLDÜ)**: eski değer `ROOT / "assets" / "huginn_logo.png"` idi, `assets/` klasörü hiç üretilmemişti → `.exists()` daima False → marka başlığı hep metin (`## 🏢 Huginn` + caption) olarak kalıyordu. KAHİN onaylı Muninn varyantına çevrildi; artık yazı yok, sadece logo.
- `ROL_KEY = "_hg_rol"` (`app.py`) — U-10 oturum rolü override anahtarı (gelecek RBAC). `aktif_rol()` ile çapraz kontrolü henüz yapılmadı.
- **K3-10h kart kenar reçetesi** (KPI-RENK-05, `tests/test_charts.py`): `kpi_karti_html` çıktısı `background:{surface}; border:1px solid {border}; border-left:3px solid {kategori_rengi}`. Gradient/box-shadow/renk dolgusu yasak — kategori rengi yalnız sol şerit + 6px nokta (`count == 2`). **Doğrulandı**: `pytest tests/test_charts.py -q` → 47 passed.
- **K3-10h madde 4 (tüm container çerçeveleri)** — ÇÖZÜLDÜ. `_AKSIYON_CSS` (`ana_kontrol.py`, 5 aksiyon butonuna özel) genişletilmedi; onun yerine `styles.py`'e yeni global blok eklendi: `_CONTAINER_CSS` → `div[data-testid="stVerticalBlockBorderWrapper"]{border:2px solid var(--hg-color-border-strong)!important}`, `_BLOKLAR` tuple'ına eklendi (tüm `st.container(border=True)` çerçevelerini kapsar, tüm sayfalarda tek kural). Kategori rengi YOK, sadece `border-strong` token'ı (nötr, tema-duyarlı). Test: `tests/test_ui_modal_stil.py::test_container_cerceve_kategori_rengi_yok`.
- `_kart_izgara` (`ana_kontrol.py:165-196`) — sparkline yükseklik eşitleme kuralı: satırdaki tüm kartların serisi yoksa hiçbirinde çizilmez (`hepsinde_seri`).

## Bilinen Ön-Mevcut Test Açıkları (bu oturumun kapsamı DIŞINDA, madde 12 backlog'u)
`pytest tests/ -q` tam koşumda (2026-09-26) **22 failed, 4218 passed, 12 skipped** — hepsi bu oturumdaki değişikliklerden (styles.py/_CONTAINER_CSS/container border) bağımsız, önceden var olan hatalar: naming-audit ihlalleri, DB migration dosya kontrolleri, `test_sayfa_iskeleti.py` (admin_mfa/ana_kontrol iskelet), `test_sekme_kapsama.py` render-fonksiyonu öksüz kontrolü, `test_pano_denetim.py`, `test_musteri_yonetimi.py`, `test_marka_denetim_muafiyet.py`, API route-inventory testleri, chat-table-stil testi, user-settings schema testi. Kasıtlı olarak dokunulmadı (scope creep önleme) — madde 12'ye devredildi.

## Oturum Gunlugu

> 2026-09 bloklari D-219 tavani nedeniyle tasindi: [[Huginn Data Insights/archive/ihsan_context_202609]]

## Kimlik — ihsan = orkestratör = bu ajan (D-286)

Ürün sahibi bildirdi: ihsan ile orkestratör **aynı kişi**; bu dosya benim hafızam. `git config user.name` `Yasua` döndüğü için `kilit_zorla.ajan_kimligi()` beni `yasu` sanıyor, `ajan_chat.py` ise `orkestrator` yazıyor — **üç isim, tek aktör** (D-265 deseni). `ponytail:` kanonik ad tek kaynağa bağlı değil; yükseltme: `ajan_kimligi()` `git config huginn.ajan` okur (tek satır).
D-286'te yasu'ya iki karar bu sıfatla verildi: OSTİM izin adımı **bende**, birleştirme **yasu'da** (assert D-270 + boş tabloya prova D-243 şartıyla). `yasu_project_context.md` benim değil — 213 satırlık kırmızısı sahibinde (`BORC-AJAN-HAFIZA-01`).

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/_ajan_context_sablon]]
- [[Huginn Data Insights/utku_project_context]]
- [[Huginn Data Insights/yasu_project_context]]
- [[Huginn Data Insights/salih_project_context]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
