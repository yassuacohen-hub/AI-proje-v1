# [UI] Sekme rehberini tek kapıya taşı → TabTanimi.rehber + app.py tek çizim (2s)

**Tarih:** 2026-10-04 · **Ajan:** Üretim/Hacim UTKU · **Görev:** `UI-ADMIN-REHBER-ALAN-38` (P2)
**Hub:** [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]] · **SSOT:** `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md` v2.11 → **v2.12**

## Ne yapıldı

Sekme rehberi **yedi sayfada gömülü `_hg_rehber` okumasından** tek bir veri
kaynağına taşındı.

| Ölçüt | Önce | Sonra |
|---|---|---|
| Rehber metnini okuyan kod | 7 sayfa (gömülü) | 1 yer (`app.py`) |
| Metin kaynağı | 7 dosya içinde dağınık | `TabTanimi.rehber` (tek alan) |
| Çizim noktası | her sayfa kendi `st.info`'sunu basıyordu | `app.py:714-715` tek `st.info(tanim.rehber)` |
| Rehberli bölüm | 7 (bölüm bazında gömülü) | **12 / 37** kayıt |
| Rehberli kök | 7 dağınık sayfa | **7 kökün tamamı** |
| Toggle | `app.py:758` `REHBER_KEY` | değişmedi |

**Taşınan 7 metin** ilgili `TabTanimi` kayıtlarına girdi: `kaynaklar`,
`musteriler`, `ayarlar`, `canli_veri`, `ana_kontrol`, `musteri_onizleme`,
`pazarlama`.

**Yeni yazılan 5 kök rehberi** — hepsi **ölçülmüş kaynaktan** türetildi
(brifteki "kendin yaz" yerine kanıt):
`sistem`, `denetim`, `musteri_yonetimi`, `proje_yonetimi`, `veri_kalite`.

**Korunanlar:** toggle (`app.py:758`), 7 metnin içeriği, `min_rol`/sıralama,
`ESLI_URL`, `D-217` Liderlik tablosu, D-259 değişiklikleri.

## Değişen dosyalar

| Dosya | Değişiklik |
|---|---|
| `web_dashboard/tabs/__init__.py` | `TabTanimi.rehber` alanı; 12 bölümün metni buraya taşındı/yazıldı; yedi whitespace-only satır temizlendi |
| `app.py` | `REHBER_KEY` sabiti, `st.info(tanim.rehber)` merkezî çizimi, footer toggle |
| `admin_musteriler.py` · `admin_panel.py` · `admin_realtime.py` · `ana_kontrol.py` · `paketler.py` · `pazarlama.py` | gömülü `_hg_rehber` okuması **kaldırıldı** |
| `admin_sistem.py` · `admin_audit.py` · `musteri_yonetimi.py` · `proje_yonetimi.py` · `admin_kpi.py` | yeni kök rehberlerinin **ölçülen** kaynağı (okundu, yazılmadı) |
| `tests/test_tabs_ia.py` | **7 yeni mandal** (11 → 18) |
| `tests/test_admin_export_excel.py` | eski mandal tek kaynağa bağlandı + yeni dört-başık ratchet testi |
| `utku_project_context.md` | 443 → **363** satır (D-219 rotasyonu; §Öz-eleştiri taşınmadı, 5. madde eklendi) |
| `archive/utku_context_202609.md` / `202610.md` | arşiv rotasyonu + yanlış ay düzeltmesi |
| `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md` | v2.12 · §7 matris satırı · §14 revizyon satırı |
| `hubs/ADMIN_DASHBOARD_HUB.md` | B-14 kapanış satırı + 38 numaralı brif öncul güncellemesi |
| `data/orchestrator/bulgu_defteri.md` | 3 bulgu (aşağıda) |

**Dokunulmayanlar:** `admin_kaynaklar.py` untracked (D-259 kaynağı olduğu için
korundu, dokunulmadı); `proje_yonetimi.py` içindeki satır içi denetim çağrısı;
`AGENTS.md` D-196 kit tablosu (SSOT sürümü yazıldı, AGENTS.md orchestrator alanı —
bildirim yapıldı).

## Test sonuçları

### Hedefli kabul seti

| Komut | Sonuç |
|---|---|
| `pytest tests/test_tabs_ia.py tests/test_dashboard_nav.py tests/test_sekme_kapsama.py tests/test_musteri_yonetimi.py -q` | **220 passed, 3 skipped** |
| `pytest tests/test_admin_export_excel.py tests/test_tabs_ia.py -q` | **39 passed** |
| `python -X utf8 scripts/kodlama_denetim.py --kapsam git` | bu görev dosyalarında **0** ihlal (88 dosya tarandı) |

### Yeni mandallar (7, ölçüldü: HEAD 11 → şimdi 18)

1. `test_rehber_alani_tanimli` — alan sınıf üzerinde tanımlı
2. `test_her_kok_sayfanin_rehberi_var` — 7 kökün tamamı dolu
3. `test_rehberli_bolum_sayisi` — ≥ 12 ratchet
4. `test_okuyucularda_rehber_kodu_kalmadi` — okuyucularda `_hg_rehber`/`REHBER_KEY` **yok**
5. `test_rehber_metni_ikiz_degil` — iki bölüm aynı metni taşımıyor
6. `test_rehber_metni_kaynaksiz_sembol_icermez` — `{...}` / `CACHE_TTL` kalıntısı yok
7. `test_rehber_tek_cizim_noktasi` — AST: `st.info(tanim.rehber)` **1**, `REHBER_KEY` metin sayısı **3**; okuyucu bağımlılıkları AST ile reddedilir (docstring yanlış pozitif üretmez)

### Negatif kontrol (mandal gerçekten kırılıyor mu?)

`data/_tmp/rehber_mandal_kirma.py` → `admin_musteriler.py` içine geçici
`# _hg_rehber` satırı eklendi:

```
1 failed, 17 passed   rc=1
```

Dosya **bayt bayt** geri kondu (4715 bayt). Kanıt rapora taşındı, script silindi.

### Tam süreç (5315 test toplandı)

| Ölçüm | Sonuç |
|---|---|
| İlk koşu | 36 kırmızı — **6'sı bu görevden** (`test_admin_export_excel.py`) |
| Bu göreve ait kırılma düzeltildi | kural gövdesi tek kaynağa bağlandı |
| **Final koşu** | **30 failed · 5285 passed · 12 skipped** (299 sn) |

**Bu göreve ait kırmızı: 0.** Kalan 30 kırmızının dağılımı:

| Kaynak | Adet | Not |
|---|---|---|
| `test_kok_politikasi.py` + `test_kok_izin_listesi.py` | 4 | `data/` kökünü izinsiz sayıyor |
| `test_brief_sablon_denetim.py` | 6 | `brief_*_VERI-SEMA-DOGRULA-0*` D-312 bloğu taşımıyor (D-312/5 açık borç) |
| `test_dokuman_politikasi.py` | 3 | aşağıdaki bulgular |
| `test_pano_d57_kalici.py` + `test_naming_audit.py` | 3 | panoda yeni D-57 ihlali |
| `test_mimir_baglam.py` | 3 | boş bağlam model çağrısı |
| `test_gorev_kutusu_*` + `test_kilit_zorla.py` + `test_dusurulen_kolon.py` | 6 | ortak pano/alan yazımı |
| `test_schema_validation.py` + `test_migration_down_standardi.py` | 2 | göç down dosyası standardı |
| `test_vector/test_embedder.py` | 1 | embedder istemcisi |
| `test_marka_denetim_muafiyet.py` + `test_bulgu_defteri.py` + `test_d309_ders_kapisi.py` | 3 | aşağıdaki bulgular |

`tests/test_ui_search_gap.py` iki kez standalone `2 passed`; süitteki durumu
order/state kaynaklı görünüyor (bu koşuda listede yok).

## Bulgular

| # | Renk | Bulgu | Nasıl çözülecek | Kime |
|---|---|---|---|---|
| 1 | 🟡 | **Refactor kırılan eski mandal.** `test_admin_export_excel.py::test_sekme_rehberi_...` 12 parametreli kural gövdesi **modül dosyasını okuyordu**. Rehber metni 7 sayfadan `TabTanimi`'ye taşınınca **6 parametre kırmızı** verdi. Kural, varlığını kanıtlamak için kaynak dosyayı tarıyordu — yani **D-246'nın tam tersini** yapıyordu. | ✅ **Çözüldü:** kural gövdesi tek kaynağa (`TabTanimi.rehber`) bağlandı; dört-başık ratchet'i ayrı teste taşındı. Ders: **refactor sonrası tam süreç bir kez** (hedefli yeşizlik yetmez). | kapandı |
| 2 | 🟡 | **Davranış farkı:** denetim paneli `proje_yonetimi.py` içinde **satır içi** çağrıldığı için merkezî yaklaşımda **denetim rehberi yalnız `denetim` kökünde** görünür; proje_yonetimi sayfasında görünmez. | 3 seçenek: (a) aynı metni iki yerde göstermek — **D-211 ikiz riski**; (b) kabul et, rehber yalnız kökte; (c) denetim panelini ayrı bölüm yapmak. | **İHSAN** UX kararı |
| 3 | 🟡 | **Ortak mandal hatası:** `tests/test_dokuman_politikasi.py:180` `§Öz-eleştiri` **işaretini** arıyor; kanonik `_ajan_context_sablon.md` başlığı `## Öz-eleştiri` ve `§` içermiyor. Ajan hafızası kuralı **bastan uygulanamaz** hâlde. | Testi şablonla hizalamak (işaret değil) ya da zorunlu muafiyet tanımlamak. Ölçüm: `utku_project_context.md` 363 satıra inince test utku'yu geçti, **`salih_project_context.md`'de kaldı**. | **İHSAN / KAHİN** |
| 4 | 🟡 | `bulgu_defteri.md`'de **2026-10-03 tarihli kendi satırım** 7 alanlı (kural 6 diyor) → `test_bulgu_defteri::test_gercek_defter_kurallara_uyuyor` kırık. Defterde "tek yazıcı `scripts/bulgu_defteri.py`" kuralı var,betikte `düzelt` komutu **yok**. | Ya `düzelt` komutu eklenir ya da geçmiş satır `\|` kaçışıyla onarılır. **Elle düzeltmedim** (D-191: geçmiş yeniden yazılmaz). | **İHSAN** |
| 5 | 🔵 | `test_d309_ders_kapisi.py::test_hafiza_tavani_asmiyor` **200** satır tavanı arıyor; D-219 tavanı **400**'e çıkardı. İhsan'ın dosyası 267 satır → kırık. Mandal karardan geride kalmış (D-265/2 deseni). | Testin tavanı 400'e çekilmeli. | **SALİH / İHSAN** |
| 6 | 🟢 | Arşiv betiğim tarihi değiştirip **hedef dosya adını değiştirmedi** → 2026-10-02 bloğu 2026-09 arşivine yazıldı. Düzeltildi; kalıcı ders context §Öz-eleştiri #5. | Yapıldı. | kapandı |

## Eksik / erteleme

- **Görsel tarayıcı doğrulaması yapılmadı.** Metinler birebir korunduğu ve
  çizim noktası sayısı AST ile sabitlendiği için risk düşük; yine de 8501'de
  gözle doğrulanmadı.
- **`admin_kaynaklar.py` untracked.** D-259 (`%` gösterimi, `saglik_rozet_metni()`)
  bu dosyada duruyor ve commit'e giremiyor. Ajan commit atmaz; dosyanın tamamı
  KAHİN/sabah tarafından commit'lenmeli.
- **Denetim rehberi görünürlüğü** bulgu 2 için İHSAN kararını bekliyor.
- **30 kırmızı** kirli çalışma ağacının önceki turlardan kalan borçları; bu
  görevle ilgisi yok (yukarıdaki dağılım).
- **AGENTS.md D-196 kit tablosu** `ADMIN-KİT v2.11` diyor; SSOT v2.12 oldu.
  Kural gereği AGENTS.md orchestrator alanı — teslim mesajında bildirildi.

## Öz-eleştiri

`utku_project_context.md` §Öz-eleştiri'ye kalıcı 5. madde eklendi: **arşiv
betiğinde tarih değişti ama hedef dosya adı değişmedi; script "başarılı" çıktı,
hiçbir assert kırmızı vermedi.** Ders: yazılı betik hedef dosya adını
tarihten **türetmeli** ve kendi çıktısını doğrulamalı (ay uyuşmazlığı →
`RuntimeError`).

## İlgili Nodlar

- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
- [[Huginn Data Insights/AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-REHBER-ALAN-38]]
- [[Huginn Data Insights/web_dashboard/tabs/__init__]]
- [[Huginn Data Insights/tests/test_tabs_ia]]
- [[Huginn Data Insights/data/orchestrator/bulgu_defteri]]
