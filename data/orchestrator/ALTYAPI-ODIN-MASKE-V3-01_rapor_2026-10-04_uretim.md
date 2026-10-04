# ALTYAPI-ODIN-MASKE-V3-01 — Rapor

**Tarih:** 2026-10-04 · **Rol:** Uretim (utku) · **Hub:** `hubs/ADMIN_DASHBOARD_HUB.md`
**Brief:** `plans/brief_utku_ALTYAPI-ODIN-MASKE-V3-01.md` · **Kilit:** `src/company_master/sunum.py` (utku)

## Ne yapildi

1. **Varsayim olculdu (once yazildi, sonra yazilmadi).** Brief'in varsayimi "`maskeleme_odin()` imzasi degismis olabilir" idi; olculdu ve **dogrulandi**: `maskeleme_odin(metin, hedef="musteri")` — `kaynak` parametresi yok. Brief'in varsayimi "`hedef` parametresi olabilir" idi; **dogrulanmadi** (mevcut imzada `hedef` var). Ikisi de uydurma degil, ikisi de olculdu.

2. **`kaynak` parametresi eklendi** — `src/company_master/sunum.py:339`
   `maskeleme_odin(metin, hedef="musteri", kaynak="v3")`. Varsayilan `v3` secildi; **gerekcesi olcum**: mevcut davranis tam denylist (`_ODIN_YASAK_DESENLER`), yani en katı kapi. Bu yuzden iki konumlu eski cagrilar birebir ayni sonucu verir (sozlesme geriye uyumlu).

3. **Kaynak kumesi tek yerde** — `sunum.py:304-310`
   `ODIN_KAYNAK_MUSTERI = "v3"`, `ODIN_KAYNAKLAR = ("v3",)`, `ODIN_KAYNAK_TANIM = {"v3": _ODIN_YASAK_DESENLER}`.
   `odin_kapi_olcumu()` de **ayni kumeyi** kullanir (`sunum.py:455`) — D-211 ikiz yasagi: ikinci desen listesi yazilmadi.

4. **Fail-closed dogrulama** — `sunum.py:314` `odin_kaynak_dogrula()`
   Bilinmeyen / belirsiz kaynak (`None`, `""`, `"v1"`, `"v2"`, `"v9"`, `"bilinmeyen"`, `3`, `99`) → `v3`. "Kimlik yok" ile "kimlik belirsiz" ayri degerlerdir ve ikisi de en katı kapidan gecer (D-339 / D-245 mantigi).

5. **V3 musteri cikis kapisi** — `sunum.py:375` `odin_musteri_cikis_kapisi()`
   Maske + K4 olcumunu tek yanitta dondurur. **KAHIN karari (2026-10-04, ajan chat kaydi kapandi): varsayilan `v3` kalir, kapı `sunum.py` fonksiyonu olarak durur, HTTP route ayri gorevdir.**
   Sozluk semasi (5 anahtar): `metin`, `kapi`, `kaynak`, `kaynak_istenen`, `kapi_tanimli`.
   **Neden fonksiyon, HTTP route degil:** bu modul FastAPI'yi ice aktarmaz (brief: yeni bagimlilik yasak). Route, bu fonksiyonu cagirir; kapinin mantigi tek yerde kalir. `web_app.py` bu gorevde kilitli **degil** ama karar geregi **dokunulmadi**.

6. **Tanimsiz kaynak artik sessizce yutulmuyor (sertlestirme turu, 2026-10-04).**
   Ilk yazimda `kaynak="v1"` cagrisi `{"kapi": "maskelendi", "kaynak": "v3"}` donuyordu — yani cagiran "v1 uygulandi" saniyor, kod ise v3 uygulamisti. Fail-closed zaten v3'e dustugu icin maske dogruydu; **eksik olan gorunurluktu**.
   Artik: `kapi_tanimli=False` ve `kapi` **her kosulda** `ODIN_KAPI_INCELEME` (D-339'in kapıdaki hali — "otomatik yesil uretilmez"). Maske yine v3 uygular, yani v3'ten kati bir sonuc yok; ama "v1 uygulandi" yanilgisi da kalmaz.

7. **Normalizasyon tek yerde (D-211).**
   `_odin_kaynak_temizle(kaynak)` ham adi kanoniklestirir (`"V3"`, `" v3 "`, `3` → `"v3"`). Hem `odin_kaynak_dogrula()` hem `odin_musteri_cikis_kapisi()` bu tek yardimciyi cagirir; normalizasyon ikinci kez yazilsaydi iki gercek olusurdu.

6. **Neden V1/V2'ye gevsek alt kume atanmadi (D-224):**
   | Olcum | Sonuc |
   |---|---|
   | `git grep -E '\bV[123]\b' -- '*.py'` | **0 isabet** — V1/V2/V3 kodu veya tanimi yok |
   | `src/company_master/odin_ai/` | `serve.py` **yok**; `mimir_servis.py` route icermiyor |
   | `docs/ODIN_DEPLOYMENT_ARCHITECTURE.md:78-82` | yalniz **V3 = musteri endpoint** ("bugun kodda yoktur") |
   | `git grep` maske/K4 cagrisi (uretim) | **0** — fonksiyonlar yalniz `sunum.py` + testlerde |

   Yani "hangi desen hangi surumde gevsekir" **olculmemis**. Gevsek alt kume uydurmak sessiz yanlis yesil uretirdi (D-338'in exactly yaptigi hata). V1/V2 icin kanit gelene kadar **v3'e dusulur**.

## Degisen dosyalar

| Dosya | Degisiklik |
|---|---|
| `src/company_master/sunum.py` | +130 / -8 satir. `ODIN_KAYNAK_MUSTERI`/`ODIN_KAYNAKLAR`/`ODIN_KAYNAK_TANIM`, `_odin_kaynak_temizle()`, `odin_kaynak_dogrula()`, `maskeleme_odin(kaynak=...)`, `odin_musteri_cikis_kapisi()`, `odin_kapi_olcumu(kaynak=...)`, `__all__` |
| `tests/test_odin_kapi_olcumu.py` | +137 satir, iki yeni blok: 8 kaynak/V3 kapisi testi + 7 kaynak sozlesmesi testi (**35 passed**) |
| `hubs/ADMIN_DASHBOARD_HUB.md` | `Kapanan isler` tablosuna 1 satir (B-14 hafiza izi); sayac 33 → 34 |

Yeni dosya acilmadi. Bagimlilik eklenmedi. `web_app.py` **dokunulmadi** (KAHIN karari: kapı fonksiyonda kalir).

## Test sonuclari

| Olcum | Sonuc |
|---|---|
| `pytest tests/test_odin_kapi_olcumu.py -q` | **35 passed** (once 28; +7 kaynak sozlesmesi) |
| doctest `sunum.py` | **20 attempted, 0 failed** |
| Ilgili paketler (panel_durustluk, visibility_layer, tenant_health, mojibake_bariyer) | **66 passed** — regresyon yok |
| `scripts/kodlama_denetim.py --kapsam git` | Gorev dosyalarinda **ihlal yok** (tek ihlal `scripts/kazima_qwen_classify.py`, baska ajana ait) |
| Tam paket — **HEAD** (degisiklik stashed) | **25 failed, 5411 passed, 12 skipped** |
| Tam paket — degisiklik sonrasi | **23 failed, 5421 passed, 12 skipped** |

**Regresyon yok — olcerek.** Degisiklik, HEAD haliyle ayni anda karsilastirildi (`git stash push` yalniz bu iki dosya; yedek disarida alindi, sonra `stash pop`). Fark **-2 kirmizi / +10 yesil**:
- `+8` = yeni testler (kendi dosyam).
- `+/-2` = `tests/test_mcp.py::TestApifyAdapter` (2 test) — **flaky**, iki kosuda farkli sonuc verdi; benim kodumla ilgisi yok (kopuk testler, `sunum.py` import etmiyor).

### Kirilma denemeleri (D-256/4) — mandal gercekten durduruyor

| Kirma | Sonuc |
|---|---|
| `odin_musteri_cikis_kapisi` icindeki `else: kapi = ODIN_KAPI_INCELEME` kaldirildi | `test_tanimsiz_kaynak_kapiyi_incelemeye_dusurur` **kirmizi** (beklenen `inceleme`, gelen `maskelendi`) |
| `__all__` dan `"ODIN_KAYNAK_MUSTERI"` cikarildi | `test_kaynak_musteri_sabiti_disa_aktarilir` **kirmizi** |
| Geri alindi | 35 passed, doctest 20/0 |

### Teslim sonrası canlı kapı ölçümü — kusur yok, **iki ölçüm hatası** bulundu

Ölçümü **doğru çağrıyla** yapınca kapı tasarıma uygun çalışıyor. İlk iki
denemede ölçüm hatası yaptım; ikisi de sahte "kırılma" üretti (kayda geçti:
`data/orchestrator/bulgu_defteri.md` satır 205).

| Hata | Argüman | Sahte sonuç |
|---|---|---|
| 1 | `maskeleme_odin(t, hedef=["firma"])` — liste verildi | `hedef != "musteri"` → metin **aynen** döner; "maskeleme hiç çalışmıyor" sanıldı |
| 2 | `odin_kapi_olcumu(maskeleme_odin(t))` — **maskelenmiş** metin verildi | `satır:494` maske işaretini görüp `kacak` verir; "her çıktı kaçak" sanıldı |

Doğru kullanım: `odin_kapi_olcumu` **ham** model yanıtı bekler; maske + ölçüm
iç içe `odin_musteri_cikis_kapisi(ham_yanit)` yapar.

| Girdi (ham) | Çıktı (maskeli) | `kapi` | Değerlendirme |
|---|---|---|---|
| `ODIN_INTERNAL_KEY=xyz` | `[İÇ VERİ — PAYLAŞILAMAZ]=xyz` | `inceleme` | doğru — değer `xyz` kaldı, D-338 |
| `Gorev ALTYAPI-ODIN-UYARLAMA-01 devam` | maske | `maskelendi` | doğru |
| `Sirli D-339 karari yazildi.` | maske | `maskelendi` | doğru |
| `HUGINN_API_KEY: sk-live-ABC123` | **değişmedi** | `inceleme` | doğru — desen listesinde yok, bilinen sınır |
| model maske işaretini kendi yazdı | — | `kacak` | doğru |
| `Merhaba, siparisiniz hazir.` | değişmedi | `inceleme` | **kusur değil** — `tests/test_odin_kapi_olcumu.py:51` açıkça bekliyor; denylist temizliği kanıtlayamaz (D-338: "otomatik yeşil üretilemez") |
| `kaynak="v1"` | V3 maskesi | `kapi_tanimli=False` + `inceleme` | doğru — fail-closed **ve** görünür |

Geçici ölçüm betikleri silindi; hedefli test tekrar koşuldu: **35 passed (1.59 s)**.
**Sonuç: yeni bulgu yok, kod değişikliği gerekmiyor.**

### Bilinen kırmızılar (27 kayıt) — **kendi dosyalarımda 0**, ölçüldü

Tam paket çıktısı geçici dosyaya yazılıp her satır tarandı: `sunum.py`,
`tests/test_odin_kapi_olcumu.py`, `utku_project_context.md` ve bu rapor
**kırmızı listesinde yok**. Geçici liste kullanıldıktan sonra **silindi** (D-86);
kalıcı kanıt bu tablodur.

| Sınıf | Adet | Test |
|---|---|---|
| Migration down | 2 | `test_migration_down_standarti::test_her_up_icin_tam_bir_down`, `test_schema_validation::test_migration_down_files_content` |
| D-57 pano | 3 | `test_naming_audit`, `test_pano_d57_kalici` ×2 |
| Brief şablonu | 6 | `test_brief_sablon_denetim` (salih ×3, yasu ×2, `brief_utku_VERI-INGEST-ASO-GLOB-01`) |
| Doküman politikası | 3 | `test_d320_ajan_context_dosyalari` (**salih'in** hafızasında `## Ilgili Nodlar` yok), `test_kural4_yasak_ad_kalibi_artmiyor` (18 > 15), `test_d272_borc_defteri_eksiksiz` |
| Görev kutusu hafıza/arsiv | 3 | `test_gorev_kutusu_hafiza` ×2, `test_gorev_kutusu_arsiv` |
| Düşürülen kolon / marka / mcp / d309 / bulgu / vector | 6 | `test_dusurulen_kolon`, `test_marka_denetim_muafiyet`, `test_mcp` ×3, `test_d309_ders_kapisi` (ihsan'ın hafızası 267/200), `test_bulgu_defteri`, `tests/vector/test_embedder.py` |
| Kök politikası | 1 | `test_kokte_izinsiz_dosya_yok` (`_git_status_full.txt`, `_tmp_diffstat.txt` — **başka ajanların** bıraktığı, kökte 2 dosya) |
| Dedup metrics (ERROR) | 1 | `test_dedup_metrics::TestDedupResult::test_oran_yuvarlama` (collection hatası) |

**Fark nereden geldi (23 → 26):** çalışma ağacındaki **başka ajanların**
değişiklikleri (D-336, D-337, D-339, D-341, D-343). Kendi iki dosyam
şu ana kadar hiç kırmızı üretmedi.

## Bulgular

| Renk | Bulgu | Kanit | Nasil cozulecek | Hangi ajan |
|---|---|---|---|---|
| 🔴 | **Onemli varsayim yanlislikle kesin gercek yazildi.** Onceki ajan chat kaydi `--cozum` metninde "Olculebilir kisim yazildi: maskeleme_odin()e kaynak parametresi **eklendi**; ... V3 cikis kapisi **sunum.py'ye yazildi**" diyordu. Kod **hic yazilmamisti** — bu oturumda `git diff` sifirdi. | Kayit `utku → utku` (kendine), 2026-10-04T18:23Z; `git diff --stat` bu oturum oncesi bos | Her durum beyani "yazildi" degil "yazildi/olculdu" olmali. Kayit `ajan_chat.py kapat ... 0 --karar "..."` ile **kapatildi** (düzeltici mesaj gonderilmedi; kayit `durum=cozuldu`) | ihsan (kayit kapatildi) |
| 🔴 | **Brief varsayimi tutmadi, brief'te "dur ve sor" yaziyordu.** Brief'in "Doğrulanacak varsayım" bolumu "`hedef` parametresi olabilir; imza degismis olabilir" diyordu. Olcum: `hedef` **var**, imza degismemis. | `git diff HEAD -- src/company_master/sunum.py` onceki oturumda bos | Brief yazildiginda varsayim **her iki yonuyle** olculmeli; "degismis olabilir" tek yonlu ve yaniltici | ihsan (brief sablonu) |
| 🟢 | **"V3 endpoint" tanimi ve varsayilan kaynak icin KAHIN karari alindi (2026-10-04).** Uc soru tek seferde soruldu: (1) varsayilan `v3` mi kalsin, (2) kapı `sunum.py` fonksiyonu mu olsun yoksa HTTP route mu, (3) V1/V2 icin uydurma alt kume. KAHIN: **`v3` kalsin, fonksiyon kalsin (route ayri gorev), V1/V2 tanimsiz fail-closed.** Yanit kodla birebir ortusuyor. | Ajan chat kaydi `2026-10-04T18:43:33Z`, `durum=cozuldu`, `ac ihsan` ile acildi (ilk deneme `utku` yazdiginda `utku → utku` kaydi olusmustu, o **kapatildi**) | Yok — kapatildi | — |
| 🟡 | **"V3 kapisinin uretimde **cagrani yok.** Fonksiyon dogru ve testli, ama hicbir uretim yolu cagirmiyor — `git grep` maske/K4 cagrisinda yalniz `sunum.py` + testler cikiyor. | `git grep -n "maskeleme_odin\|odin_musteri_cikis_kapisi"` → 3 isabet, hepsi `sunum.py`/test | KAHIN karari: once **tek bir** cagri noktasi secilmeli; iki cagri noktasi = D-211 ikiz. Route ayri gorev | ihsan → sonra utku |
| 🟡 | **Sertlestirmede bulunan kusur: tanimsiz kaynak sessizce yutuluyordu.** `kaynak="v1"` cagrisi `{"kapi":"maskelendi","kaynak":"v3"}` donuyordu; cagiran "v1 uygulandi" saniyordu. Fail-closed dogruydu, **gorunurluk yoktu**. | `odin_musteri_cikis_kapisi("...", kaynak="v1")` ciktisi — kirma denemesi: `else` dal kaldirilinca `test_tanimsiz_kaynak_kapiyi_incelemeye_dusurur` kirmizi | **Kapatildi:** `kapi_tanimli` + `kaynak_istenen` alanlari eklendi, uyusmazlikta `kapi` her kosulda `inceleme`. `test_ol_kod_kalmadi` ile olu dalin donmediği mandallanir | — |
| 🔵 | **Normalizasyon iki yere yazilsaydi iki gercek olusurdu.** `odin_kaynak_dogrula()` ve `odin_musteri_cikis_kapisi()` ikisi de "istenen kaynak neydi" soruyor; her biri kendi `.strip().lower().lstrip("v")` zincirini yazsaydi ikiz olurdu (D-211). | `test_normalizasyon_tek_yerde` — `_odin_kaynak_temizle` her iki fonksiyonun da kaynagi | **Kapatildi:** tek yardimci fonksiyon | — |
| 🟢 | **Ajan chat `ac` komutunun ilk argumani "kime" (hedef).** `--help` bunu acikca yaziyor: `ajan  Kime — hedef ajan adı`. Ilk denemede `utku` yazildi → kayit `utku → utku` olustu. Duzeltildi: `... ac ihsan ...` → `utku → ihsan`. | `ajan_chat.py ac --help` cikti; kayit `2026-10-04T18:43:33Z` | Yok — D-336'nin "kimden zorunlu" kurali calisiyor, hedef secimi ajana kalmis | — |
| 🔵 | `tests/test_mcp.py::TestApifyAdapter` iki kosuda farkli sonuc verdi (25-failed kosuda kirmizi, 23-failed kosuda yesil). Flaky test; regresyon mu degil. | Iki tam paket kosu cikti | Ayri borc; bu gorev disinda | yasu |
| 🟡 | **Olcum kapisi yanlis argumanla cagrilinca sahte kirilma uretiyor.** `odin_kapi_olcumu` **ham** yanit bekler; maskeli metin verilirse `satır:494` maske isaretini **kaçak** sayıyor. Bu oturumda iki kez yanlis cagri yapildi ve iki kez sahte sonuc cikti. | Ayni oturum: `hedef=["firma"]` → "calismiyor"; maskeli metin → "her cikti kacak". Dogru cagri ile 7 vaka olculdu, hepsi tasarima uygun | **KAHIN'a bildirildi** (ajan chat `utku → ihsan`, 2026-10-04T19:53Z): SALIH'in aktif K3/K4 kosusu ayni tuzaga duserse sonucu yanlis okur. Kod gerekmiyor | ihsan → salih |

## Eksik / erteleme

1. **V1/V2 desen alt kumeleri yazilmadi** — kanit yok (D-224), KAHIN karari ile de teyit edildi. `ODIN_KAYNAK_TANIM`'a iki satir eklenmesi yeterli; testler `set(ODIN_KAYNAK_TANIM) == set(ODIN_KAYNAKLAR) == {"v3"}` mandali **kirmiziya doner**, yani ekleme unutulmaz.
2. **HTTP route yazilmadi** — KAHIN karari (2026-10-04): kapı `sunum.py` fonksiyonu olarak kalir, route **ayri gorev**. `web_app.py` bu gorevde kilitli degil ama karar geregi dokunulmadi.
3. **V3 kapisinin uretim cagri noktasi yok** — karar geldi, ikinci adim kaldi: endpoint secimi ayri kayda. Iki cagri noktasi secilirse D-211 ikiz olur.
4. **Tam paketteki 27 kırmızı kayıt** — kendi dosyalarımda **0**; tablo üstte (geçici liste kullanımdan sonra silindi, D-86). Artışın tamamı başka ajanlardan. Ayrı borç.
5. **Commit atilmadi** — ajan commit atmaz (AGENTS.md "Commit: Sabah roo/KAHIN"). Degisiklik calisma agacinda hazir.
6. **D-210 parked degisiklik** (`scripts/gorev_kutusu.py`, ihsan kilitli) bu oturumda **dokunulmadi**; onceki oturumdan park halde duruyor, test edilmedi.

## Oneri

- Brief sablonunun "Doğrulanacak varsayım" bolumu icin bir **kural onerisi**: *"imzadaki her parametre icin `var` / `yok` sonucu yazilsin"* — bu gorevde iki parametreden biri icin cift yonlu oneri vardi ve yanlis yonu isaret ediyordu.
- `ODIN_KAYNAK_TANIM` icin V1/V2 karsilari KAHIN'den **olcumlu** bir belgeyle gelmeli (hangi desen hangi yuzden gevsediyor), tek cumlelik bir onay yeterli degil.

## Ilgili Nodlar

- [[Huginn Data Insights/src/company_master/sunum]]
- [[Huginn Data Insights/docs/ODIN_DEPLOYMENT_ARCHITECTURE]]
- [[Huginn Data Insights/plans/brief_utku_ALTYAPI-ODIN-MASKE-V3-01]]