> **YENİ OTURUMDA İLK OKUNACAK DOSYA** — orkestratör kimliği ve kalıcı hafıza. Her oturum başında önce bunu oku.
> Şablon: [[Huginn Data Insights/_ajan_context_sablon]] (D-219) · Tavan 400 satır (D-219 Ek, 2026-10-02). §Öz-eleştiri bölümü tavana dahil değil, silinmez.

## KALDIĞIM YER

> D-219: tek blok, **üzerine yazılır**. Pano ile çelişirse pano üstündür.

- **Konum (2026-10-03 16:45):** Mimir tıkanması + simülasyon blokajı turu.
  **Simülasyon blokajı ÇÖZÜLDÜ** (commit `7baf16a0`): `gorev_kutusu.py` B-01 döngüsü `for t in acik`
  (105 sahte HATA → 0), `gorev_at.py _brief_bul` pano `brief` alanını 3. aday okur, pano
  `ALTYAPI-PANO-ARSIV-CAKISMA-02` done. Simülasyon exit **2 → 1** (yalnız B-14/B-17 uyarı);
  `basla` tüm ajanlara tekrar açık. ajan-chat `ORCH-SIMULASYON-BLOK-01` index 0 kapatıldı.
- **Mimir:** `src/company_master/odin_ai/mimir_servis.py` **YOK**, kilit salih'te
  (`file_locks.json`). salih chat'e **hiç yazmamış** (`"kimden": "salih"` 0 kayıt); tetik
  `alindi` 2026-10-01T20:52. Revize bağlam = `prompts/mimir_sistem_promptu.md` **v4 taslak**
  (commitler `4f0c69e9` şapka tablosu/36 senaryo, `7d038b12` ARA/GETIR araç döngüsü,
  `b41a532c` GETIR izin listesi/özel ağ yasağı — hepsi 2026-10-03). Brief
  `plans/brief_salih_ALTYAPI-MIMIR-BAGLAM-01.md` DEĞİŞMEDİ, hâlâ geçerli.
  salih'e D-210 chat (16:43:39, önem yuksek): revize prompt hazır, **24 saat içinde
  teslim/engel yoksa ihsan devralır** (kilit devri `gorev_kutusu.py devret`).
- **N7 koşusu YAPILMIŞ (chat kayıt 1-2, 02 23:56 / 03 00:29):** `qwen3.8-flash-next` 503
  (offline); `mimo-v2.6-pro` çalışıyor ama **güvenlik NO-GO** (inj-12 kararsız sızdırdı,
  mesru-07 İngilizce düşünme sızıntısı, 3 senaryo dil uyumsuz). v4 prompt bu NO-GO'ya cevap;
  `mimir_servis.py` ucu olmadan yeniden ölçülemez (`ODIN_CUSTOMER_API_URL` tanımsız).
- **Açık borç adayı (değişmedi):** `karar_ver()` `hata` senaryosunu `dil_uyumlu=false`
  sayıyor → `erisilemedi` kovası + hata varsa SKIP (NO-GO değil).
- **Review bekleyen:** `SCRAPE-005` (utku) 3 karar — DATABASE_URL env_file /
  `refresh_pipeline.py:67` import yolu / restart `no` → `gorev_kutusu.py onayla|reddet`;
  chat 62/64 kapat.
- **Commit edilmedi:** `data/orchestrator/ajan-chat.jsonl` + bu dosya (bu turda commit).
- **Sonraki adım:** SCRAPE-005 3 kararı işle → P2 toplu devir (`gorev_at.py at --baslik-b64`:
  9Router anahtar betiği, `continue_haftalik_bildir.py` kalıcı, ostim href filtresi, Apify
  ≤10 $, `sync_paket_fiyatlari.py`) → salih 24 saat dolunca Mimir'i devral.
- **Görev:** `ALTYAPI-MIMIR-BAGLAM-01` (salih, bekleme) · **Son okunan karar:** `D-322`

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
| `UnicodeEncodeError: charmap ... '\u2192'` | Konsol cp1254; `print()` ile `→` yazılamaz | Türkçe başlık `--baslik-b64` ile geçirilir; stdout'a yalnız ASCII yaz (`print(f[6:20], b64)`) |
| regex `\*\*Basl.k:\*\*` → `NoneType.group` | `Başlık`ta **iki** Türkçe karakter var (`ş`+`ı`), tek `.` yetmez | `\*\*Ba\w+k:\*\*` |
| `gorev_at.py ata` → argparse `invalid choice` | Alt komutun adı `at`, "ata" değil (`gorev_at.py:483`) | Komut adını uydurma, `main()`'den oku |
| Commit çıktısı `[chore/monorepo-merge]`, `git status` `## master` | Teşhis edilmedi — borç #48, 8. görünüm | Açık |
| `git add` → `paths are ignored by .gitignore: Huginn Data Insights` | **İki ayrı repo var** (D-255); dış kök vault'u yok sayar | Vault dosyası vault içinden commit edilir: `cd "Huginn Data Insights" && git add ...` |
| `gorev_at.py guncelle <ID>` → `required: --task-id` | Görev kimliği pozisyonel değil, zorunlu bayrak | `guncelle --task-id <ID> --durum done --sonuc "..." --cagiran ihsan` |
| `ajan_chat.py ac ihsan ...` kaydı ihsan→ihsan çıktı | İlk pozisyonel = **HEDEF** ajan; gönderen `--kimden` | `ac <hedef> <task_id> "<sorun>" --kimden ihsan --onem yuksek`; yazmadan önce `-h` oku, yazdıktan sonra `oku --task_id` ile geri oku |
| Simülasyon B-01 105 HATA, hiçbir ajan `basla` yapamıyor | B-01 arşiv dosyasında da olan `done` görevleri tarıyordu (`arsivle` idempotent) | `for t in acik` (`7baf16a0`); kök neden düzeltilir, `--simulasyonsuz` kaçış kapısı açılmaz |

## Öz-eleştiri (KALICI — SİLİNMEZ, arşive taşınmaz)

> Ürün Sahibi kararı (2026-10-02): "tüm ajanlar öz eleştirilerini cortex dosyasında sabit tutsun
> silmesinler" — bu bölüm 400 satır tavanına dahil değil, archive rotasyonunda asla taşınmaz.
> En yeni madde en üstte, biriktirilir.

- **2026-10-03 — Kritik bildirim ~12 saat okunmadı:** utku `ORCH-SIMULASYON-BLOK-01`'i 01:44'te
  kritik açtı; ben ~13:30'a kadar görmedim, bu arada hiçbir ajan `basla` yapamadı. Orkestratörün
  gelen kutusunu oturum başında açmaması = tüm takımın boşa beklemesi. **Öğrendiğim:** blokaj
  bildirimi, cortex'ten bile önce gelir. **Bundan sonra:** oturumun ilk komutu
  `ajan_chat.py ozet --durum acik`; kritik varsa cortex okumayı bile sonraya bırak.
- **2026-10-03 — Mimir tıkanması geç ölçüldü:** `ALTYAPI-MIMIR-BAGLAM-01` 2 gün teslimsizdi;
  "salih çalışıyordur" varsayımıyla bekledim, ölçmedim. Ölçünce: `mimir_servis.py` yok, salih
  chat'e hiç yazmamış, tetik 10-01'den beri `alindi`. **Öğrendiğim:** sessizlik ilerleme değil,
  D-260 burada da geçerli. **Bundan sonra:** 24 saati geçen her `alindi`/`aktif` görev için
  dosya + chat + commit üçlüsünü ölç; ikisi boşsa aynı gün süre ver, dolunca devral.
- **2026-10-03 — Komutu `-h` okumadan çalıştırdım, yanlış kayıt yazdım:** `ajan_chat.py ac ihsan ...`
  ilk pozisyoneli hedef sanmadım; ihsan→ihsan kaydı doğdu, kapatmak için ek tur yedim. Aynı gün
  `gorev_at.py guncelle` pozisyonel ID ile de argparse hatası aldım. **Öğrendiğim:** sözdizimi
  tahmini iki kez üst üste yanlış çıktı; tuzak tablosundaki `ata` dersi (gorev_at.py:483)
  bana yetmemiş. **Bundan sonra:** ilk kez kullandığım her alt komutta önce `-h`, yazdıktan
  sonra `oku` ile geri okuma (D-260 beyan kanıt değil).
- **2026-10-03 — Tasarım önce, ölçüm sonra:** `docs/PAKET_KOTA_TASARIMI.md`'yi mevcut
  `packages.features` şemasını ve gerçek paket sayısını ölçmeden yazmaya başladım; ölçüm
  sonradan geldi, bölüm başlıkları değişti. **Öğrendiğim:** "§1 Mevcut (ölçüldü)" başlığı
  dokümanın ilk yazılan bölümü olmalı, son eklenen değil. **Bundan sonra:** tasarım dosyası
  açmadan önce tek bir ölçüm betiği (`scripts/` altında kalıcı) çalıştır, çıktısını §1'e yapıştır.
- **2026-10-03 — Geçici ölçüm betiklerini silme refleksi:** `data/tmp_*` ve tek seferlik `.py`
  dosyalarını iş bitince silmeye yöneldim; kullanıcı kuralı tam tersi (ölçüm betikleri
  `scripts/` altına kalıcı, `data/tmp_*` silinmez — sonraki oturumun kanıtı). **Öğrendiğim:**
  "temizlik" ile "kanıt yok etme" aynı hareket. **Bundan sonra:** silme yerine adlandır ve
  commit et; iz bırakmayan ölçüm yapılmamış sayılır.
- **2026-10-02 — D-320/D-321/D-322 sırayla iddia:** `karar_no.py --al` idempotent değil; aynı konuyu
  3 kez çağırınca 3 ayrı numara (D-320, D-321, D-322) rezerve oldu ama bulgu_defteri.md'de sadece
  2 ayrı konu vardı (SCOR/SKOR+bypass kapısı, regex-virgül satır-bazlı tarama). **Öğrendiğim:**
  numara talep etmeden önce kaç AYRI karar konusu olduğunu netleştir, sonra o sayıda al — tahminle
  fazla almak orphan numara (D-322) doğurur. **Bundan sonra:** `--al` çağrısı sayısı = kanıtlanmış
  konu sayısı; fazlaysa dürüstçe "kullanılmadı" diye işaretle, sessizce yok sayma.
- **2026-10-02 — D-193'te yazılmayan dosya "yapılacak" diye durmuş:** `git_stash_guard.py` ve
  `git_safety_check.py` 2026-09-23'ten beri AGENTS.md'de "yazılacak" diye duruyordu, 3 ayrı
  oturumda da hiç yazılmadığı fark edilmeden kaldı. **Öğrendiğim:** "yapılacak" notu süresiz açık
  kalırsa fiilen "yapılmış" gibi okunuyor — bu D-309/1 deseninin (yazılmayanı yazılmış gibi
  bırakma) kendi başıma düştüğüm örneği. **Bundan sonra:** her oturum açılışında AGENTS.md'de
  kendi attığım "yazılacak" notlarını grep'leyip hâlâ yazılmamışsa ya yaz ya da metni düzelt.

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
| 5 | Vendor due diligence | 🔴 yok | EVET — P3, **kapsam araştırması** (SSOT:867-869 yalnız başlık) |
| 6 | Global corporate intelligence | 🔴 yok | EVET — P3, **kapsam araştırması** ("P4" diye öncelik YOK: P0-P3) |

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

**Dağıtılanlar (2026-10-01 — hepsi panoda, tetik ajan postasına düştü):**

| # | İş | Kime | Öncelik | Durum |
|---|---|---|---|---|
| G-0a | Faz 2 risk motoru (8 skor; adlar SSOT:791-822'den okundu, D-260) | utku | P1 | ATANDI |
| G-0b | Faz 3 entity graph v0 (yalnız `same_osb` + `nace_complementary`) | yasu | P1 | ATANDI |
| G-0c | Faz 5 vendor DD **kapsam araştırması** (kod değil) | yasu | P3 | ATANDI |
| G-0d | Faz 6 küresel istihbarat **kapsam araştırması** (kod değil) | utku | P3 | ATANDI |
| 12 | ~~A senaryosu: 2 `iptal` → `plan`~~ | — | — | **DÜŞTÜ** — `task_board.json:2271,2296`: ikisi de D-310 ile bilinçli iptal; yerine `VERI-RAG-KORPUS-01` + `ALTYAPI-MIMIR-BAGLAM-01` zaten panoda |
| 14 | ~~N8 kalan: OSB temizlik~~ | — | — | **DÜŞTÜ** — `task_board.json:2347`: `VERI-OSB-TEMIZLIK-01` zaten `plan`, brifi var |
| 11 | AGENTS.md 5 karar + numara tahsisi (D-227) | ihsan (devredilemez) | P2 | açık |
| 9/10 | salih brifi + chat (D-210) | ihsan (devredilemez) | P1 | açık |

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
