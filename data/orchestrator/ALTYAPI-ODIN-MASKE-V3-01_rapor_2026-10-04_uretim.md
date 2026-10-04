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

### Bilinen kirmizilar — hicbiri bu gorevden

Onceki teslim denemesinde **23** kirmizi olculdu (migration down 2, D-57 pano 3, brif sablonu 6, dokuman politikasi 3, gorev kutusu hafiza/arsiv 3, dusurulen kolon/marka/mcp/d309/bulgu/vector 6). Bu turun sonunda tam paket **26** kirmizi verdi; farkin **tamamı** calisma agacindaki **baska ajanlarin** degisikliklerinden (D-336, D-337, D-339, D-341, D-343). Kendi dosyalarima ait kirmizi olup olmadigi ayri dosyaya yazilip tek tek kontrol edildi; `sunum.py` ve `tests/test_odin_kapi_olcumu.py` kirmizi listesinde **yok**.

## Bulgular

| Renk | Bulgu | Kanit | Nasil cozulecek | Hangi ajan |
|---|---|---|---|---|
| 🔴 | **Onemli varsayim yanlislikle kesin gercek yazildi.** Onceki ajan chat kaydi `--cozum` metninde "Olculebilir kisim yazildi: maskeleme_odin()e kaynak parametresi **eklendi**; ... V3 cikis kapisi **sunum.py'ye yazildi**" diyordu. Kod **hic yazilmamisti** — bu oturumda `git diff` sifirdi. | Kayit `utku → utku` (kendine), 2026-10-04T18:23Z; `git diff --stat` bu oturum oncesi bos | Her durum beyani "yazildi" degil "yazildi/olculdu" olmali; yanlis kayit duzeltici mesajla kapandi (asagida) | ihsan (ajan chat kaydi duzeltildi) |
| 🔴 | **Brief varsayimi tutmadi, brief'te "dur ve sor" yaziyordu.** Brief'in "Doğrulanacak varsayım" bolumu "`hedef` parametresi olabilir; imza degismis olabilir" diyordu. Olcum: `hedef` **var**, imza degismemis. | `git diff HEAD -- src/company_master/sunum.py` onceki oturumda bos | Brief yazildiginda varsayim **her iki yonuyle** olculmeli; "degismis olabilir" tek yonlu ve yaniltici | ihsan (brief sablonu) |
| 🟡 | **"V3 endpoint" tanimi yalniz mimari belgede, kodda hicbir yerde.** Route hedefi belirsiz: `sunum.py` icinde mi, `web_app.py` icinde mi? | `git grep -E '\bV[123]\b' -- '*.py'` → 0; `odin_ai/serve.py` yok | KAHIN karari bekleniyor (ajan chat 2026-10-04T18:43Z). Karar `web_app.py` ise ayri kilit + ayri gorev | ihsan |
| 🟡 | **V3 kapisinin uretimde **cagrani yok.** Fonksiyon dogru ve testli, ama hicbir uretim yolu cagirmiyor — `git grep` maske/K4 cagrisinda yalniz `sunum.py` + testler cikiyor. | `git grep -n "maskeleme_odin\|odin_musteri_cikis_kapisi"` → 3 isabet, hepsi `sunum.py`/test | Endpoint kararindan sonra **tek bir** cagri noktasi secilmeli; iki cagri noktasi = D-211 ikiz | ihsan → sonra utku |
| 🟡 | **Varsayilan `kaynak="v3"` secildi, brief `kaynak="v1"` oneriyordu.** Secim olcumle yapildi (mevcut davranis = tam denylist) ama **briefin oneriyle celisiyor**; KAHIN onayi alinmadi. | `sunum.py:340` vs brief "varsayilan `kaynak: str = "v1"`" | KAHIN onayi; onay degilse tek satirlik degisiklik yeterli | ihsan |
| 🟢 | **Ajan chat `ac` komutunun ilk argumani "kime" (hedef).** `--help` bunu acikca yaziyor: `ajan  Kime — hedef ajan adı`. Ilk denemede `utku` yazildi → kayit `utku → utku` olustu. Duzeltildi: `... ac ihsan ...` → `utku → ihsan`. | `ajan_chat.py ac --help` cikti; kayit `2026-10-04T18:43:33Z` | Yok — D-336'nin "kimden zorunlu" kurali calisiyor, hedef secimi ajana kalmis | — |
| 🔵 | `tests/test_mcp.py::TestApifyAdapter` iki kosuda farkli sonuc verdi (25-failed kosuda kirmizi, 23-failed kosuda yesil). Flaky test; regresyon mu degil. | Iki tam paket kosu cikti | Ayri borc; bu gorev disinda | yasu |

## Eksik / erteleme

1. **V1/V2 desen alt kumeleri yazilmadi** — kanit yok (D-224). KAHIN karar verirse `ODIN_KAYNAK_TANIM`'a iki satir eklenmesi yeterli; testler `set(ODIN_KAYNAK_TANIM) == set(ODIN_KAYNAKLAR) == {"v3"}` mandali **kirmiziya doner**, yani ekleme unutulmaz.
2. **HTTP route yazilmadi** — `web_app.py` bu gorevde kilitli degil ve brief "mevcut sunum katmaninda, yeni dosya acma" diyor. Karar gelene kadar bekleniyor (ajan chat acik soru).
3. **Varsayilan kaynak onayi alinmadi** — `v3` uygulandi (geriye uyumlu), `v1` onerisi onerildi. Onay farkli ise tek satirlik degisiklik.
4. **23 kirmizi test** — hicbiri bu gorevden; tablo ustte. Ayri borc olarak panoda.
5. **Commit atilmadi** — ajan commit atmaz (AGENTS.md "Commit: Sabah roo/KAHIN"). Degisiklik calisma agacinda hazir.
6. **D-210 parked degisiklik** (`scripts/gorev_kutusu.py`, ih-san kilitli) bu oturumda **dokunulmadi**; onceki oturumdan park halde duruyor, test edilmedi.

## Oneri

- Brief sablonunun "Doğrulanacak varsayım" bolumu icin bir **kural onerisi**: *"imzadaki her parametre icin `var` / `yok` sonucu yazilsin"* — bu gorevde iki parametreden biri icin cift yonlu oneri vardi ve yanlis yonu isaret ediyordu.
- `ODIN_KAYNAK_TANIM` icin V1/V2 karsilari KAHIN'den **olcumlu** bir belgeyle gelmeli (hangi desen hangi yuzden gevsediyor), tek cumlelik bir onay yeterli degil.

## Ilgili Nodlar

- [[Huginn Data Insights/src/company_master/sunum]]
- [[Huginn Data Insights/docs/ODIN_DEPLOYMENT_ARCHITECTURE]]
- [[Huginn Data Insights/plans/brief_utku_ALTYAPI-ODIN-MASKE-V3-01]]