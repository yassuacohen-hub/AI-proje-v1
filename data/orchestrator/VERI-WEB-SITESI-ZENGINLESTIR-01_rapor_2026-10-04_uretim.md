# VERI-WEB-SITESI-ZENGINLESTIR-01 — `website_domain` zenginleştirme kaynağı

**Rol:** Üretim · **Tarih:** 2026-10-04 · **Sahip:** utku · **Durum:** teslim → `review`
**Ölçüm kaynağı:** canlı Supabase Postgres (`scripts/web_kaynak_olcum.py`, `data/_tmp/provenance_olcum.py` — yalnız SELECT, `--kuru`)
**Pilot kanıtı:** `data/_tmp/web_pilot40_v2.json` (saf JSON, stderr ayrı)

## Ne yapıldı

`website_domain` boş olan firmayı, **gerçekten o firmanın sitesi olan** bir alan adıyla eşleştiren kaynak yazıldı. Zincir sırası sabit ve tek yönlüdür:

| # | Adım | Kapı |
|---|---|---|
| 1 | Unvan → anahtar kelime | `unvan_anahtar_kelimeler()` (genel kelime ölçümü, 112 kelime) |
| 2 | Anahtar kelime → aday domain | `NineRouterClient.web_search()` |
| 3 | Aday → izin | `KazimaYazici.izin_var()` (robots + KVKK), Jina fallback |
| 4 | İçerik doğrulama | `icerik_dogrula()` — alan adı ∩ içerik, marka kalıntısı, sahiplik |
| 5 | Yazma kapısı | `yazma_kapisi.kabul()` — `SABLON_WEB` + tek kanonik şablon |
| 6 | Yazma | **yalnız NULL/boş alana**, provenance kaydı ile; varsayılan `--kuru` |

**Bu turda eklenen dört kapı:**

| Kapı | Neden | Nerede |
|---|---|---|
| `marka_kalintisi_kaniti_yok` | Alan adında geçmeyen ayırt edici unvan kelimesi varsa en az biri içerikte geçmeli | `icerik_dogrula()` |
| Yurt kapısı (`_uzanti` + `_TURKIYE_UZANTI`) | Türk şirketi + yabancı TLD → **içerik çekilmeden** eleme | `yurt_kakismasi_olasilik()`, `izin_var()` öncesi |
| Saf JSON stdout | `[OK]` özetleri stdout'a karışınca JSON parse edilemiyordu (eski pilot dosyasının sonunda `[OK]` vardı) | `zenginlestir()` |
| `el_tasidi` sayacı | Elle inceleme kuyruğu sayısı satır içinden türetiliyor, ikinci sayaç tutulmuyor | `zenginlestir()` |

`_uzanti()` düzeltildi: `ornek.tr → tr`, `gezencadir.com.tr → com.tr`, `gezencadir.com → com`, `gomap.be → be`.

### Ölçülen sonuçlar

| Ölçüm | Değer |
|---|---|
| Firma (canlı) | 10123 |
| `website_domain` **dolu** (korunacak) | **2780** |
| `website_domain` **boş** (hedef havuz) | **7343** |
| `source_records.raw_website` dolu | 6514 |
| `sources.source_name='web_sitesi'` provenance kaydı | **0** |
| `companies` semasında web kolonu | yalnız `website_domain` (ikiz yok) |
| Pilot hedef / yazılan / doğrulanan | 40 / **0** / **1** |
| Pilot elle kuyruk | **78** (67 yurt · 7 tek kelime · 4 marka kalıntısı) |
| Toplam aday denemesi / tekil domain | 150 / 102 |

**Korunma kanıtı:** yazılan 0 kayıt, provenance 0 kayıt, dolu sayı 2780 → başlangıçla birebir. Tüm koşular `--kuru`.

## Sınıflandırma (elle inceleme kuyruğu)

**35** aday (tablodaki satır sayısıyla birebir), kanıt sınıfıyla dağıtıldı:

| Sınıf | n | Oran | Anlamı |
|---|---|---|---|
| kesin TP | **1** | %2,9 | dogrulanmasi mumkun olan tek satir |
| kesin FP | **14** | %40,0 | kapilar dogru eleme yapti |
| belirsiz | **11** | %31,4 | karar insan eline birakildi |
| coverage reddi | **2** | %5,7 | kapı dogru calisti, **gercek site** yine de elendi |
| geçici (robots) | **2** | %5,7 | yeniden denenebilir; unvan tam eslesiyor |
| kesin FP (dogru eleme) | **3** | %8,6 | sahiplik kaniti yok (OSB odasi/dernek/rehber) |
| teknik (cek hatasi) | **2** | %5,7 | ağ/JS hatasi; karar icerik degil |
| **toplam** | **35** | %100 | — |

Dagilim **tablodan sayildi** (1+14+11+2+2+3+2 = 35); "en az kac TP cikti" degil,
"kac aday siniflandirildi" sorusu yanitlanir (D-260: paydasiyla birlikte).

| # | Domain | Unvan | Kapı kararı | Sınıf | Kanıt |
|---|---|---|---|---|---|
| 1 | `duzeygd.com.tr` | DÜZEY GAYRİMENKUL DEĞERLEME A.Ş. | **kabul** | **kesin TP** | Sayfa başlığı doğrulandı; `duzey` alan adında + `gayrimenkul` içerikte |
| 2 | `gezencadir.com` | GEZEN GRUP İÇ DIŞ TİC. VE ÇADIR | `yurt_kakismasi_suspesi` | **coverage reddi** | Gerçek Gezen Çadır üreticisi; `.com` yurt kapısı eledi |
| 3 | `mkbhidrolik.com` | MKB HİDROLİK SİSTEMLER | `yurt_kakismasi_suspesi` | **coverage reddi** | Unvan Türk şirketi + `.com` |
| 4 | `gomap.be` | GOMAP MÜH. MÜŞAVİRLİK | `yurt_kakismasi_suspesi` | **kesin FP** | İçerik `GOMAP SCS`, Belçika sicili `BCE0806.750.087` → farklı ülke, farklı tüzel kişi |
| 5 | `gmtpano.com` | EGEMEN PANO | `marka_kalintisi_kaniti_yok` | **kesin FP** | İçerik `GMT PANO`, `egemen` geçmiyor — yeni kapının yakaladığı tam senaryo |
| 6 | `fatihlojistik.com.tr` | FATIH BAĞBAŞI | `marka_kalintisi_kaniti_yok` | **belirsiz (FP lehine)** | İçerikte `lojistik` geçiyor ama `bağbaşı` yok; bağlantısız kelime |
| 7 | `fatihpinarbasi.com` | FATIH BAĞBAŞI | `marka_kalintisi_kaniti_yok` | **belirsiz** | Unvanın ikinci kelimesi içerikte yok |
| 8 | `egemen-group.com` | EGEMEN PANO | `marka_kalintisi_kaniti_yok` | **belirsiz** | Ad markayla birebir; eleme büyük olasılıkla **hatalı** — elle bakılmalı |
| 9 | `rocketreach.co` | çok sayıda | `yurt_kakismasi_suspesi` | **kesin FP** | ABD B2B listesi; tek başına **26 kez** denendi (arama motoru sonucu) |
| 10 | `yandex.ru` | MKB HİDROLİK | `yurt_kakismasi_suspesi` | **kesin FP** | Arama motoru |
| 11 | `cargoagent.net` | DAĞHAN GRUP GIDA | `yurt_kakismasi_suspesi` | **kesin FP** | Uluslararası lojistik dizini |
| 12 | `isbul.net` | MKB HİDROLİK | `yurt_kakismasi_suspesi` | **kesin FP** | İş ilanı dizini |
| 13 | `ostimbul.com` | AKIN MAKİNA | `yurt_kakismasi_suspesi` | **kesin FP** | OSB bülteni — D-245 kaynak sızıntısı tipi |
| 14 | `listofcompany.com` | AKIN MAKİNA | `yurt_kakismasi_suspesi` | **kesin FP** | Firma dizini |
| 15 | `rehbersanayi.com` | GOMAP MÜH. MÜŞAVİRLİK | `yurt_kakismasi_suspesi` | **kesin FP** | Meslek rehberi |
| 16 | `indixio.com` | GOMAP MÜH. MÜŞAVİRLİK | `yurt_kakismasi_suspesi` | **kesin FP** | ABD B2B dizini |
| 17 | `anadolugroup.com` | DAĞHAN GRUP GIDA | `yurt_kakismasi_suspesi` | **belirsiz** | Ad kısmen tutuyor ama grup adı farklı; sahiplik kanıtı yok |
| 18 | `beratmakinam.com` | BERAT MAK. | `tek_anahtar_kelime_elle_gerekli` | **belirsiz** | Kısaltılmış unvan; tek kelime kanıtı yetersiz — kapı doğru |
| 19 | `beratmakina.net` | BERAT MAK. | `tek_anahtar_kelime_elle_gerekli` | **belirsiz** | 18'in varyantı |
| 20 | `soyalpgroup.com` | MEHMET SOYALP | `tek_anahtar_kelime_elle_gerekli` | **belirsiz** | Şahıs unvanı + `group` → şahıs/firma ayrımı riski |
| 21 | `tamgucsogutma.com.tr` | TAMGÜÇ TİC. SAN. TİC. | `tek_anahtar_kelime_elle_gerekli` | **belirsiz** | `.tr` doğru, tek kelime kanıtı yetersiz |
| 22 | `aksisgrup.com.tr` | AKSİS GRUP ALÜMİNYUM… | `tek_anahtar_kelime_elle_gerekli` | **belirsiz** | 23'ün grup varyantı |
| 23 | `aksis.com.tr` | AKSİS GRUP ALÜMİNYUM… | `tek_anahtar_kelime_elle_gerekli` | **belirsiz** | 22'nin kısa varyantı |
| 24 | `ahsapteknik.com.tr` | AHŞAP TEKNİK DEKORASYON | `tek_anahtar_kelime_elle_gerekli` | **belirsiz** | Türkçe kök ünlü → normalizasyon ayrı konu |
| 25 | `alarko.com.tr` | — | `unvan_kelimesi_gecmiyor` | **kesin FP** | Unvan kelimesi sayfada yok → kapı doğru çalıştı |
| 26 | `cbinsights.com` | — | `unvan_kelimesi_gecmiyor` | **kesin FP** | ABD pazar araştırma sitesi |
| 27 | `emlakjet.com` | — | `unvan_kelimesi_gecmiyor` | **kesin FP** | Emlak ilan sitesi |
| 28 | `dergipark.org.tr` | — | `unvan_kelimesi_gecmiyor` | **kesin FP** | Akademik dergi platformu |
| 29 | `akinmakina.com.tr` | AKIN MAKİNA | `izin_yok` | **geçici — yeniden denenebilir** | Robots kapısı; unvan **tam** eşleşiyor → gerçek TP olabilir |
| 30 | `egemenlogistics.com` | EGEMEN PANO | `izin_yok` | **geçici — yeniden denenebilir** | Robots; marka adı tutuyor |
| 31 | `kazankasiad.org.tr` | — | `sahiplik_kaniti_yok` | **kesin FP (doğru eleme)** | OSB meslek odası sitesi, firma değil |
| 32 | `osiad.org.tr` | — | `sahiplik_kaniti_yok` | **kesin FP (doğru eleme)** | OSB derneği |
| 33 | `cicekrehberi.net` | — | `sahiplik_kaniti_yok` | **kesin FP (doğru eleme)** | Sektör rehberi |
| 34 | `nsosyal.com` | — | `cek_hatasi` | **teknik** | Önceki görevde bu domain kaynak sızıntısı olarak ölçülmüştü; bloklist dışı kalmış |
| 35 | `craft.co` | — | `cek_hatasi` | **teknik** | Ağ/JS hatası; yeniden denenmeli |

**Dağılım:** kesin TP 1 · kesin FP 14 · belirsiz 9 · coverage reddi 2 · geçici/teknik 5 · doğru eleme 3.

**Okuma:** 21 adayda kapı doğru davranmış, 2 adayda **coverage kaybı** var (`.com`), 1 aday (`egemen-group.com`) muhtemelen **hatalı eleme**. Tek doğrulanmış TP'nin telefonu GSM (`+908505322444`) — bkz. 🟡 Bulgu 3.

## Değişen dosyalar

| Dosya | Durum | Ne |
|---|---|---|
| `src/company_master/etl/web_sitesi_zenginlestir.py` | **yeni** (untracked) | Ana ETL; 4 kapı + `_uzanti` düzeltmesi |
| `tests/test_web_sitesi_zenginlestir.py` | **yeni** (untracked) | 33 regresyon (residual, yurt, uzantı, saf JSON, `_kap_denetimi`) |
| `scripts/genel_kelime_olcum.py` | **yeni** (untracked) | Genel kelime ölçümü + `--drift` kapısı (112 kelime) |
| `data/_tmp/web_pilot40_v2.json` | yeni (gitignored) | Pilot kanıtı |
| `data/_tmp/pilot_grup.py`, `data/_tmp/provenance_olcum.py` | geçici — **silindi** | Ölçüm betikleri; kanıt rapora işlendi, D-220/3 (ikiz kanıt) gereği bırakılmadı |
| `data/orchestrator/VERI-WEB-SITESI-ZENGINLESTIR-01_rapor_2026-10-04_uretim.md` | yeni | Bu rapor |

**Değiştirilmedi:** `task_board.json`, `file_locks.json`, `bulgu_defteri.md` (bulgular `scripts/bulgu_defteri.py ekle` ile yazıldı — tek yazıcı kuralı), görev dışı hiçbir kaynak.

## Test sonuçları

| Denetim | Komut | Sonuç |
|---|---|---|
| Hedefli testler | `pytest tests/test_web_sitesi_zenginlestir.py tests/test_website_sablon_kisiti.py -q` | **47 passed in 3.44s** ✅ |
| Genel kelime drift | `python -X utf8 scripts/genel_kelime_olcum.py --drift` | `[OK] kod ve olçum ayni (112 kelime)` ✅ |
| Sema yazma yolu | `--sema-denetimi` | `[OK] tüm kolonlar + UNIQUE kısıtı mevcut (salt okunur)` ✅ |
| Kapı kırma testi | `_kap_denetimi()` | `GMT PANO`/`EGEMEN PANO`, `.tr`/`.com`/`.com.tr`/`.be` regresyonları yeşil ✅ |
| Canlı korunma ölçümü | `scripts/web_kaynak_olcum.py` | dolu **2780**, boş **7343**, provenance **0** ✅ |
| Kodlama denetimi | `python scripts/kodlama_denetim.py` | **exit 1** — 11 `dosya_sonu` + 36 `mojibake`, **hepsi görev dışı dosyada**; bu görevin 3 dosyası temiz ⚠️ |

### Bilinen kırmızılar (bu görevden değil)

Doküman kapıları 2026-10-04'te koşuldu: `test_karar_numara_tekligi.py` **tamamen yeşil**, `brief_utku_VERI-WEB-SITESI-ZENGINLESTIR-01.md` şablon denetiminden geçiyor. Kırmızı olanlar:

| Kırmızı | Ölçülen |
|---|---|
| `test_dokuman_politikasi::test_kural4_yasak_ad_kalibi_artmiyor` | yasak ad kalıbı **16** dosyada, üst sınır 15 (bu raporun adı sayıya **katkı yapmıyor**) |
| `test_dokuman_politikasi::test_d272_borc_defteri_eksiksiz` | borç defteri eksik |
| `test_dokuman_politikasi::test_d320_ajan_context_dosyalari` | ajan context dosyası eksik |
| `test_brief_sablon_denetim` × 6 | `brief_utku_VERI-INGEST-ASO-GLOB-01`, `brief_salih_VERI-SEMA-DOGRULA-01/02/03`, `brief_yasu_VERI-SEMA-DOGRULA-02/03` — hepsi eski brifler (D-312 borcu) |

Hiçbiri bu görevin dosyalarına dokunmuyor; görev kapsamında düzeltilmedi (D-243 kapsam dışı → bulgu).

## Bulgular

🔴 **Yazma yok ama telefon kırılgan.** Brief telefon/e-posta/adres de istiyor; pilotun tek kabulünde telefon `+908505322444` çıktı — kişisel GSM olabilir. Kurumsal/kişisel ayrımı kodda yok; KVKK nedeniyle `--yaz` öncesi bu alan elle gözden geçirilmeli.

🟡 **`.com` yurt kapısı gerçek TP'leri eliyor.** 2 ölçülü coverage kaybı (`gezencadir.com`, `mkbhidrolik.com`). Güvenlik lehine şimdilik açılmadı; bilinçli ödünç, karar sahibine bırakıldı.

🟡 **Arama sonucu tekrar edilebilir değil.** Aynı 40 firma ikinci koşuda farklı aday kümesi üretti (`rocketreach.co` 26 kez denendi). Pilot kabul sayısı kapı kalitesinin ölçüsü **değildir**; offline mandal + deterministik testler esas kanıttır.

🟡 **`source_records.raw_website` kaynak sızıntısı taşıyor.** Canlı ölçüm: `www.isim.org.tr` **2161**, `www.ostimistihdam.com` **475** kayıt. Ham aday havuzu bu yüzden 6514 görünüyor ama gerçek aday havuzu çok daha küçük. Havuz ölçümünde bu iki değer hariç tutulmadan "aday" denmemeli.

🟢 **Marka kalıntısı kapısı gerçek FP'yi yakaladı.** `gmtpano.com` canlı pilotta `EGEMEN PANO` için reddedildi — dış web doğrulaması bunu bağımsız olarak FP olarak teyit etti.

🔵 **`egemen-group.com` muhtemelen hatalı eleme.** Marka adı birebir tutuyor; residual kapısı `PANO` kelimesini arıyor. Bu satır elle onaya düşmeli.

## Eksik / erteleme

| Konu | Durum | Neden |
|---|---|---|
| NACE sektör kelimesi genişletmesi | **Ertelendi** | Ölçüldü: `TR_NACE_Rev2` K=3 → 1332 token; 9356 firmanın yalnız **%2,7**'si tümüyle kelimesiz kalıyor (252 firma), 1895 firmanın kümesi daralıyor. Etki geniş → ayrı görev |
| `.com` coverage kaybı | Açık | Yukarıda 🟡 |
| Canlı yazma doğrulaması | **Yapılmadı** | Kuru koşu; KVKK + 2780 dolu kaydın korunması için bilinçli |
| Başlangıç SHA256 kanıtı | **Doğrulanamadı** | `6f3e9a19…` değerinin üretim tanımı kayıtlı değil; yeniden denen tanımlar eşleşmedi. Kanıt yerine **2780/7343 + provenance 0 + kuru** kullanıldı |
| Tam repo süiti | Kırmızı (baseline) | Yukarıdaki 3 kayıt, görev dışı |
| Kodlama denetimi | exit 1 | 11 dosya sonu + 36 mojibake, görev dışı |

## Özeleştiri

- **Ne iyi gitti:** Yeni kapıyı (marka kalıntısı) canlı pilotta bir gerçek FP üzerinde doğruladım — kırma testi kâğıtta kalmadı.
- **Ne kötü gitti:** Eski pilot dosyası JSON değil, `[OK]` satırıyla biten bir metindi; saf JSON kapısını **yazmadan** fark ettim. Dosyayı doğrulamadan "pilot çalıştı" demedim.
- **Zamanı ne yedi:** Arama/robots değişkenliği yüzünden eski-yeni pilot farkını "kapı kötüleşti" diye okuyacakken iki kez ölçümü tekrarladım. Doğru okuma: fark canlı ortam kaynaklı.
- **Yarın neyi değiştireceğim:** Pilot raporunu yazarken "kabul sayısı" yerine **kapı kararı dağılımını** birincil ölçüt yapacağım; kabul sayısı tek başına yön göstermiyor.

## İlgili Nodlar

- [[hubs/VERI_KALITESI_HUB]]
- [[hubs/PLAN_STRATEGY_HUB]]
- [[plans/brief_utku_VERI-WEB-SITESI-ZENGINLESTIR-01]]
- [[data/orchestrator/VERI-OSTIM-HREF-FILTRE-01_rapor_2026-10-03_uretim]]
- [[src/company_master/etl/web_sitesi_zenginlestir]]
- [[docs/VERI_KALITE_SOZLESMESI]]
