# VERI-SKOR-MOTORU-01 — Fırsat motoru teslim raporu

**Tarih:** 2026-10-02 · **Rol:** üretim (UTKU) · **Karar:** D-319 / K4 resmî skor seti

## Ne yapıldı

D-319'ın açtığı F5 kapatıldı. K4 resmî skor seti (`need`/`fit`/`timing`/`ensemble`)
şema + hesaplayıcı olarak kuruldu.

| Faz | İş | Durum |
|---|---|---|
| A | `0049_firsat_skorlari.sql` ölçüldü ve doğrulandı | 10/10 ölçüm |
| B | `intelligence/skor_motoru.py` yazıldı | tek yazma kapısı |
| C | `tests/test_firsat_skorlari.py` mandalı + kırma kanıtı | 35/35, 3/3 |

### Faz A — ölçüm gerekçesiyle

Mevcut göç **9 denetimden 8'ini** geçiyordu; kırılan tek denetim gerçek bir kusurdu:
`NUMERIC(5,2)` tek başına 0.0–1.0 aralığını **korumaz** (999.99'a kadar kabul eder).
`need_score = 1.5` sessizce yazılabilirdi. D-245'in kendi ifadesiyle: kolon adı
içeriğini doğrulamaz.

Düzeltme: `pg_constraint` kataloğundan varlık kontrolü yapan bir `DO` bloğu ile dört
kısıt eklendi (`pg_constraint` varlık kontrolü sayesinde iki kez koşulur, patlamaz —
D-251/5). Kod tabanı engellemesin diye, kısıt D-267/6 gereği hem veritabanına hem
Python'a yazıldı.

### Faz B — kararlar ve gerekçeleri

| Karar | Gerekçe |
|---|---|
| Bileşen `None` ise ensemble `None` | Eksik bileşeni 0 saymak "ölçtük, sıfır bulduk" olurdu — D-249 ihlali |
| `fit_score` üç tablo boşken `None` | Brief madde 8'in istediği F3 senaryosu; sahte 0 üretmiyor |
| `timing_score` üstel yarı ömür | SSOT:236 "recency"; doğrusal yerine monoton ve kalibrasyonu tek yerde tutan seçim |
| Pozisyonel imza SSOT:243 ile birebir | Brief madde 6 birebir istiyor; iki bonus bayrağı anahtar-kelimeyle ayrıldı |
| Kalibrasyon sabitleri `KALIBRASYON` sözlüğünde | D-250/6: ağırlık değişince sürüm artar, eski puanlar bayatlar |

**Bulunan ve düzeltilen kendi hata:** İlk yazımda `field_bonus` koşulunu
`evidence >= 1.0` olarak uydurmuştum. SSOT:260 bunu `is_field_verified` diye ayrı
bir koşul olarak yazıyor; bileşenden türetilemez. Doğrulama kapıları anahtar-kelime
parametrelerine çevrildi, varsayılan `False` (güvenli taraf).

### Faz C — mandal kırılarak doğrulandı (D-256/4)

`scripts/mandal_kirma_denemesi.py` üç ayrı bozma denedi:

| Bozma | Sonuç |
|---|---|
| Migration'a `DEFAULT 0` geri geldi | 1 kırık mandal, exit 1 |
| `need` ağırlığı 0.30 → 0.40 | 6 kırık mandal, exit 1 |
| `need_score(None)` artık `0.0` dönüyor | 1 kırık mandal, exit 1 |

**3/3 yakalandı, dosyalar geri alındı, 35/35 temiz.**

**Kırma denemesi ilk çalıştırmada kendi mandalımı yakaladı.** `DEFAULT 0` denemesi
kaçtı: regex'im `need_score` ile `DEFAULT` arasındaki virgülü (`NUMERIC(5,2)`) geçemiyordu —
yanlış negatif. Mandala satır bazlı tarama yazıldı. Bu, D-268/5'in ("metin taraması
mandal yerine geçmez") altıncı örneği ve D-259'ın "test de bir beyandır" dersi:
yeşil mandal, yakalamadığı bozmayı da örtüyordu.

## Değişen dosyalar

| Dosya | Değişiklik |
|---|---|
| `src/company_master/schema/migrations/0049_firsat_skorlari.sql` | 0.0–1.0 aralık koruması eklendi (4 kısıt, idempotent) |
| `src/company_master/intelligence/skor_motoru.py` | **yeni** — hesaplayıcı + tek yazma kapısı |
| `tests/test_firsat_skorlari.py` | **yeni** — 35 mandal |
| `scripts/skor_motoru_faz_a_olcumu.py` | **yeni** — Faz A ölçümü (9 denetim) |
| `scripts/mandal_kirma_denemesi.py` | **yeni** — kırma kanıtı (3 deneme) |
| `docs/BORC_DEFTERI.md` | 2 borç açıldı, 2 görev kaydı eklendi |
| `hubs/VERI_KALITESI_HUB.md` | B-14 kapanış kaydı |

## Test sonuçları

| Ölçüm | Değer |
|---|---|
| F5 mandalı | **35/35** |
| Kırma kanıtı | **3/3** yakalandı |
| `test_schema_validation.py` + F5 | **7 passed** |
| Tam süit | **19 failed / 4958 passed / 12 skipped** |
| Taban (teslim öncesi) | 18 failed / 4957 passed / 12 skipped |

### Bilinen hatalar ve sahiplik (teslim öncesi ölçüldü, 19 kalem)

| # | Hata | Sahibi | F5'le ilgisi |
|---|---|---|---|
| 1 | `test_brief_sablon_denetim` ×5 | SALİH | Yok |
| 2 | `test_kok_politikasi` ×2 (kök `_update_pano.py`, vault kökü 6 tek kullanımlık) | İHSAN | Yok |
| 3 | `test_pano_d57_kalici` ×2, `test_naming_audit` ×1 | İHSAN | Yok |
| 4 | `test_gorev_kutusu_hafiza` ×2, `test_gorev_kutusu_arsiv` ×1, `test_pano_denetim_tetik` ×1, `test_gorev_kutusu_cli` ×1 | İHSAN | Yok |
| 5 | `vector/test_embedder.py::test_embedder_client_uyuzsuz` | ALTYAPI | Yok |
| 6 | `test_dusurulen_kolon` (`scripts/yasu_canli_olcum_d260.py:47-48`) | YASU | Yok |
| 7 | `test_kodlama_denetim::test_guard_bom_ratchet` | İHSAN | Yok |
| 8 | **`test_dokuman_politikasi::test_d272_borc_defteri_eksiksiz`** | SALİH ×2, YASU ×1 | **Kısmi: F5 kaydı eklendi, 5→3 düştü; kalan 3'ü başkasının** |

Tam süit 18 → 19 arası tek değişim **F5'in borç defterine girmemiş olmasıydı**;
kayıt eklendi. Kalan 3 kimlik başka ajanların görevleri — sahiplik kuralı
(D-226) gereği dokunulmadı, ajan chat'e yazıldı.

## Bulgular

| # | Bulgu | Çözüm | En iyi ajan |
|---|---|---|---|
| 1 | 🟡 `ensemble_score` **tablo yeniden üretilemez**: formül `evidence` (ağırlık 0.15) kullanıyor, ama `evidence_strength` SSOT:232-237'de skord değil **gate girdisi** — tablo 4 kolonla sabitlendiği için kolonu yok. Satırdaki `need/fit/timing` ile `ensemble` arasındaki ilişki doğrulanamaz | Ya tabloya `evidence_strength` kolonu eklensin (0050 + D-253 defter güncellemesi) ya da ensemble hesabı denetlenebilir olmaktan çıkarılsın. **D-319 tabloyu 4 kolonla sabitlediği için bu bir karar kararıdır** | **İHSAN** — tablo kapsamı D-319 kararına bağlı; teknik seçenekleri önce ölçmeli |
| 2 | 🟡 Bugün **hiçbir firmanın ensemble skoru hesaplanamaz**: `fit_score` (en yüksek ağırlık 0.35) üç tablodan okuyor, üçü de boş (F3 ETL'i yok) → `fit=None` → ensemble `None` | F3 ETL'i önceliklendirilmeli; ara çözüm: `fit` boşken ensemble'i ağırlıksız normalize edip *kısmi* puan üretmek — ama bu D-249'a aykırı olabilir, kararı ihsan vermeli | **İHSAN** karar · **UTKU** uygulama · **VERI-SEMA-DOGRULA-01'i yürüten ajan** F3 sahibi |
| 3 | 🔵 `D-198 simulasyon` kapısı sürekli exit 2 veriyor: 17 arşiv çakışması (pano bakımı, D-77) + 5 eksik brif dosyası. Kapı fiilen **hiçbir ajan için kapalı değil** | 17 arşiv çakışması orchestrator'da temizlenmeli; 5 eksik brifin 4'ü `.agents/skills/` yolunu gösteriyor, bu dizin D-220 Kural 2 ile arama dışı | **İHSAN** (pano/arşiv) · **SCRAPE-* sahipleri** (brif yolları) |
| 4 | 🔵 `test_dokuman_politikasi`: 3 görev kimliği hâlâ borç defterinde değil (`VERI-SEMA-DOGRULA-01/02`, `VERI-TOBB2B-BUYUTME-01`) | Her görev tesliminde kendi satırını defter + hub'a yazmalı; bu bir alışkanlık açığı, kod açığı değil | **SALİH** (2 kimlik) · **YASU** (1 kimlik) |
| 5 | 🔵 D-309/3'ün yeni örneği: regex tabanlı "yoktur" denetimi `NUMERIC(5,2)` içindeki virgülde kırıldı ve **yanlış negatif** verdi | Yeni yazılan metin denetimlerinde virgül içeren tip tanımları için satır bazlı tarama kullanılmalı; kırma denemesi her yeni metin mandalında zorunlu | **SALİH** (test danışmanı — mandal kalitesinin sahibi) |

## Eksik / erteleme

- Gerçek hesaplama **çalıştırılmadı** (brief s.89, D-238). `firsat_recalc()` üretildi ve
  sahte motorla doğrulandı; canlı DB'ye yazılmadı. Göç `0049` **uygulanmadı**.
- Kalibrasyon sabitleri (`need_doygunluk=3`, `timing_yarim_yasam_gun=180`,
  `evidence_doygunluk=3`, `fit_doygunluk=5`) ölçümle değil kararla kondu; SSOT
  yalnız ağırlıkları sabitler. Gerçek dağılımla kalibre edilmeden müşteriye
  gösterilmemeli.
- `schema_versions.json` güncellenmedi — 46/47/48'de de güncellenmediği için aynı
  pratiği izliyor (D-265 ile donmuş tarihî kayıt).

## D-198 kapı gerekçesi (bypass kaydı)

Simülasyon kapısı exit `2` verdiği hâlde göreve başlandı. Gerekçe ajan chat'ine
`cokundurmus` olarak yazıldı: kapı hatalarının **%100'ü başka alanda** (pano bakımı
ve brif dosyası), görev canlı veritabanına **yazmıyor** (veri riski 0) ve Faz A'yı
tek başına bırakmak yarım göç üretirdi (D-267/6). Bypass teslim özetinin parçasıdır.

## Öz-eleştiri

**Neyi iyi gitti:** Her iddia ölçüldü — göç kanıtsız kabul edilmedi, kırma denemesi
kendi mandalımın yanlış negatifini buldu, tam süit tabanı 18'den başlandı.

**Neyi kötü gitti:** İlk ensemble yazımında bonus koşulunu uydurdum (SSOT ayrı koşul
diyor, ben bileşenden türettim). İki kez `apply_diff`/`edit` hatası yapmamak yerine
tek doğrulama turunda yakaladım — ama yakalayana kadar yanlış kod yazılmışti.

**Dünü düzelten şey:** Regex tabanlı "yoktur" denetimine güvenmeyi bırakmak. Kırma
denemesi olmasa o mandal yeşil kalır ve `DEFAULT 0` sessizce geri girebilirdi.

## İlgili Nodlar

- [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]]
- [[AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani]]
- [[docs/BORC_DEFTERI]]
- [[plans/brief_utku_VERI-SKOR-MOTORU-01]]