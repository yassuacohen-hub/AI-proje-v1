# Borç Defteri — tek kanonik kayıt (D-272)

**Bu dosya borç listesinin tek kaynağıdır.** Devir notu buradan okunur, hafızadan değil.
`AGENTS.md` kararın *gerekçesini* tutar; bu defter *durumunu* tutar.

**Neden ayrı dosya:** `AGENTS.md` içindeki D-kayıtları kronolojik değil (ölçüm D-272/1:
`[…263, 266, 265, 264, 267, 268, 270, 269, 271]`). Bu yüzden bir borcun son durumu dosyada
**aşağıda** değil, **en büyük D numarasında** yazılıdır. Satır sırasıyla okuyan her tur
yanlış okudu — altı tur üst üste (D-265, D-266, D-267/1, D-268/1, D-271/1).

**Kural (D-272):**
1. Bir D-kaydı borç kapatıyor/iptal ediyorsa **aynı turda** bu defter güncellenir.
2. Durum alanı yalnız şu değerleri alır: `ACIK` · `KAPANDI` · `IPTAL` · `KURAL` (borç değil, kural/görev kimliği).
3. `AGENTS.md`'de adı geçip bu defterde olmayan kimlik testi düşürür:
   [`tests/test_dokuman_politikasi.py::test_d272_borc_defteri_eksiksiz()`](../tests/test_dokuman_politikasi.py).
4. Başlık fiil taşımaz (D-271).

---

## Borçlar

| Kimlik | Ölçülen sapma | Durum | Kaynak D | Kapanış D |
|---|---|---|---|---|
| `BORC-NACE-DOGRULAMA-01` | `nace_validity` alanı kaynaksız | KAPANDI | D-258 | D-287: doğrulama **yapılamaz değil, anlamsız** — sözlük var (3319) ama yetim kod **0**, hiçbir şeyi ayırt etmiyor; `verified` değeri hiç üretilmiyor, kolon `src/`de hiç **okunmuyor**. Ağırlık çekilmedi (kilit dürüst), puan kapısı iki mandalla korundu |
| `BORC-PANO-BORC-00` | borç listesinin kanonik kaydı yok | KAPANDI | D-271 | D-272 |
| `BORC-SCRIPTS-01` | `scripts/` altında 41 `_*` girdi (29 `.py` hepsi derlenir, **0 çürük**, üretim çağıranı **0**); kökte ayrıca **76 index hayaleti** tek kullanımlık betik. D-281'de ölçüldü ve **tavanlandı** (76/2), kesme ürün sahibinde. **D-288 eki:** `_ARSIV_tek_kullanimlik/` altında ayrıca **~160 izlenen dosya** var — aynı sapmanın ikinci yuvası, otomasyonun `git add -A`'sı ile büyümüştü; kapı kapatıldı, mevcut dosyalar **kesilmedi** (sahiplik belirsiz) | ACIK | D-255 | — |
| `BORC-KARAR-NUMARA-01` | karar numarası **iki ayrı dosyadan** tahsis ediliyordu (`AGENTS.md` max D-281, bu defter max D-282); çakışma: **D-281 iki karara birden** verilmiş. D-227 mandalı yalnız `AGENTS.md`'yi ve yalnız `(D-NNN — KAH` biçimini tarıdığı için çatışma görünmezdi | KAPANDI | D-281 | D-286: `scripts/karar_no.py` tek havuz + `TAVAN_CATISMA=1` mandalı (kırılarak doğrulandı; D-283 eşzamanlı ajan yarışında çakıştı, **mandal yakaladı**, kayıt D-286'e taşındı — tavan yükseltilmedi) |
| `BORC-AJAN-HAFIZA-01` | `yasu_project_context.md` **213 satır > 200** (D-219 tavanı); mandal kırmızı: `tests/test_dokuman_politikasi.py::test_d219_ajan_context_dosyalari`. **SAHİBİNDE** — başka ajanın hafıza dosyası, D-299'da kesilmedi (D-226/sahiplik) | KAPANDI | D-286 | D-301: **ölçüldü, sahibi kapatmış** — dosya **149 satır** (tavan 200). Devir notu hâlâ "213" diyordu; not bayattı, borç değil |
| `BORC-KIMLIK-ANAHTAR-01` | `config/certs/selfsigned.key` (gerçek RSA özel anahtar) `90c4702` ile elle commit edilmiş; blob `216cfdd…` hâlâ ulaşılabilir. **D-293 ölçümü:** commit **hiçbir dalda/etikette/uzakta yok** (`for-each-ref --contains` boş; uzaktaki dal ebeveyn `993ce8a`'da) — yalnız yerel cline checkpoint ref'leri yaşatıyor. Sertifika `CN=localhost`/`SAN=DNS:localhost`, tek tüketicisi `config/nginx.conf` ve o da hiçbir serviste mount edilmiyor. Tarih **temizlenmedi**; A (rotasyon) / B (filter-repo, 421 commit) kararı ürün sahibinde | ACIK | D-288 | D-293'te kapsam ölçüldü; mandal `tests/test_kimlik_dosyalari.py` (kırılarak doğrulandı) — kesme kararı bekliyor |
| `BORC-SICIL-DAIRE-01` | 619 firmada sicil no var, sicil dairesi yok. **D-295 ölçümü:** eksik olan tam **594**; bu alan puan kapısında `number AND office` istediği için 619 sicilin **25'i** puan alıyor, 594'ü **kayıp**. Daire tamamlanırsa ortalama +0.06 (ağırlık 1.0 × 594/9412) | ACIK | D-260 | — · **Kaynak bulundu (D-306 hattı):** TSG ilanı Katman 0 alanları arasında `mudurluk` var (`skills/services/ticaret_sicili_kanit.py::KATMAN_0`) — eksik daire bilgisinin bedava kanalı budur. **Kapsam ölçülmedi**: 594 firmanın kaçında TSG ilanı bulunabildiği `TSG-PILOT-20` ölçümüne bağlı; tahmin yazılmadı (D-268) |
| `BORC-PANEL-ADRES-01` | `web_dashboard/tabs/admin_executive.py::_firma_kayitlari()` **var olmayan kolonu** okuyor: `SELECT … address_line … FROM companies` → canlı `psycopg.errors.UndefinedColumn`. Veri `companies.address`'te (5798 dolu). `address_line` yalnız `company_locations`'ta var, o tablo **0 satır**. Test `tests/test_admin_executive.py::test_firma_kayitlari_30_gun_esigi` **sahte engine** ile hazır satır döndürdüğü için yeşil — D-288'in "yeşil test de beyandır" kuralının canlı örneği | ACIK | D-295 | — |
| `BORC-SITE-COP-01` | `website_domain` 5446 dolu görünüyor ama **2779 kayıt yalnız 58 adresi paylaşıyor**: `http://www.isim.org.tr` **2142** kez, `ostimistihdam.com` 474 kez. Ayrıca 3799 kayıtta (%69.8) alan adı ile unvan arasında **tek ortak sözcük yok**. Dizin/portal bağlantısı firma sitesi sayılıyor (D-292: doluluk ≠ bilgi). **D-303 düzeltmesi:** şablon/yer-tutucu sayılan toplam **2666** (devir notu "2142" diyordu — o yalnız tek desenin sayısıydı); hepsi tek yazma yolundan (`ostim.org.tr` / `web_scrape`) girmiş, kök sebep kaynak değil **kapısız yazma** (`BORC-YAZMA-KAPISI-01`) | ACIK | D-295 | — |
| `BORC-ILETISIM-ORTAK-01` | `primary_phone`: 1057 kayıt 498 yinelenen numarayı paylaşıyor (tepe `905344018261` ×10); 913 numara ne cep ne sabit biçiminde. `primary_email`: 444 kayıt 196 yinelenen adresi paylaşıyor, tepe değer **yer tutucu** `bilinmeyen@bilinmeyen.com` ×17. Bu kayıtlar puan alıyor ama firmaya ait olduğu doğrulanmadı | ACIK | D-295 | — |
| `BORC-ADRES-KALITE-01` | `address` 5798 dolu (%61.6) ve tamamı puan alıyor; ama 4795'inde (%82.7) "ankara" **geçmiyor**, 626'sı (%10.8) 20 karakterden kısa, **0'ında** posta kodu var. Adres ağırlığı 1.5 — puanın en pahalı ikinci alanı doğrulanmamış metinle besleniyor | ACIK | D-295 | — |
| `BORC-ESLESME-KAPSAM-01` | `entity_resolution` 8905 satır tutuyor ama **8820 firmanın** (9412'nin %93.7'si) hiç eşleşme kaydı yok. Tablo dolu görünüyor, kapsamı yok. `source_records` tarafında yalnız 12 yetim var — sorun kaynak bağında değil, çözümleme kapsamında | ACIK | D-295 | — |
| `BORC-KAPI-KURULUM-01` | `MANDAL-SAHNE-01` yazılıydı ama **koşmuyordu**: kapı yalnız `.pre-commit-config.yaml`'a yazılmıştı, oysa `git config core.hooksPath` = `scripts/hooks` ve `pre_commit` modülü kurulu değil. Kanıt: `8a25798` commit'i **24 dosyayla** (kendi eşiğim 20) kapıdan geçti ve **dört mandalımın hepsini** içine aldı — kapının önlemek için kurulduğu olay, kapıya rağmen, kapının kendi dosyasına oldu | KAPANDI | D-302 | D-302: `scripts/hooks/pre-commit`'e eklendi + `tests/test_sahne_kapisi_kurulu.py` mandalı (kanca satırı silindi → `1 failed`, geri yüklendi → `8 passed`) |
| `BORC-KARAR-ESZAMAN-01` | `karar_no.py` eşzamanlı tahsiste çakışmayı **önlemiyor**, yalnız sonradan haber veriyor. Ölçüm: `data/karar_tahsis/D-301.txt` = `bilinmeyen` — başka bir ajan D-301'i benimle aynı anda aldı (`8a25798` başlığı da "D-301" diyor). **İkinci çift numara vakası**; birincisi D-281, o da hâlâ `CATISMA` veriyor. Hakemlik ürün sahibinde (D-226) | KAPANDI | D-302 | D-303: iki kök sebep ayrı ayrı kesildi — (1) `al()` zaten atomikti, çatal **kimlikteydi**: `karar_no.py` yalnız `HUGINN_AJAN`'a bakıyordu, `kilit_zorla.ajan_kimligi()` tek kaynak yapıldı (`bilinmeyen` → `yasu`); (2) kilit sahipsiz kalıyordu → `bayat()` + `BAYAT_SAAT=24`. **Hakemlik hâlâ ürün sahibinde**: mevcut D-281/D-301/D-303 çakışmaları çözülmedi |
| `BORC-TAHSIS-ZORLAMA-01` | Tahsis sistemi vardı, **zorlayanı yoktu** (D-261). Ölçüm: iç depo HEAD `ff210e4` "D-303 kapsamli veri denetimi" diyor, **başka bir ajanın** commit'i; ama `data/karar_tahsis/D-303.txt` = `yasu` — o ajan `--al` hiç çalıştırmamış. D-281 ve D-301'den sonra **üçüncü** vaka, aynı tur içinde | KAPANDI | D-303 | D-303: `karar_no.py --dogrula` + `scripts/hooks/commit-msg` kancası; kırarak doğrulandı (`D-303`→exit 0, `D-999`→exit 1). Mandal `tests/test_sahne_kapisi_kurulu.py`, `pre-commit` listesine eklendi (`45 passed`) |
| `BORC-TEK-REPO-01` | `Huginn Data Insights` üst depoda `160000` **gitlink** olarak duruyordu ama `.gitmodules` **yoktu** → yarım submodule. Her iç commit üst depoda ` M` üretiyor, "alt depo isaretcisi guncellendi" gürültü commit'leri doğuyor, commit yanlış depoya düşebiliyordu. Üst depoda kanca da yok (`.git/hooks` sadece `.sample`); tüm koruma iç depoda | KAPANDI | D-303 | D-303 (ürün sahibi kararı): gitlink index'ten kaldırıldı, `/Huginn Data Insights/` ignore'landı, üst depo commit `df82690` (`delete mode 160000`). Kırarak: `git add "Huginn Data Insights"` **reddediliyor**, sızıntı `0` satır. `ponytail:` üst depo hâlâ 64 kök ayar dosyasını izliyor |
| `BORC-YAZMA-KAPISI-01` | Veriye **tek kapı yoktu**: 58 ayrı bağlantı noktası, 79 SQL dosyası, **23 dosyada** aynı temizleme mantığının 5 ayrı kopyası. Kök sebep filtre yokluğu değil, **kanonik liste yokluğu** — herkes kendi listesini yazmış | ACIK | D-303 | D-303: `src/company_master/db/yazma_kapisi.py` (tek kanonik liste + `kabul()`) + `docs/VERI_YAZMA_KURALLARI.md` + `MANDAL-SABLON-01` (`TAVAN_KOPYA=23`, kırılarak doğrulandı: `25>23` kırmızı). **23 kopya birleştirilmedi** — kapsam uyarısı gereği yalnız tavanlandı |
| `BORC-TENDER-ING-01` | `0041_tsg_kolon_adlari_ingilizce.sql` yalnız `companies`/`query_requests` kolonlarını çevirdi; `0039_tender_tracking.sql`'deki `ihale_*` 6 tablo (14 Türkçe kolon: `acilis_tarihi, aday_firma_adi, adres, aktif, durum, duyuru_tarihi, ilce, kaynak_alan_kodu, kaynak_id, kaynak_ilan_id, kaynak_ilan_url, soru_cevap_son_tarihi, teklif_verme_son_tarihi, vergi_no`) unutuldu — `test_sema_dili_ingilizce` kırmızı. Tablolar 6'sı da **0 satır**, tek tüketici `osb_tender_monitor.py` (kaynak taranamaz durumda, VERI-02/VERI-TOBB2B-KESISIM-01 zincirinde kayıtlı) | **KAPANDI** | D-307 | **D-308** (goc `0042_tender_kolonlari_ingilizce.sql`, uygulandi + deftere yazildi): once **olculdu** — 6 tablonun **6'si da 0 satir**, yani RENAME'de veri kaybi riski **sifir**. 4 tabloda **14 kolon** RENAME edildi (`kaynak_id`->`source_id`, `teklif_verme_son_tarihi`->`bid_deadline`, `aday_firma_adi`->`bidder_company_name`, `vergi_no`->`tax_no` ...); 0039'un Turkce kurdugu 3 indeks Ingilizce adla yeniden kuruldu; DO blogu ile idempotent (D-251/5). Kanit: `tests/test_goc_defteri.py` **4 passed**, mandal yesil. |
| `BORC-NACE-OLU-KOLON-01` | `0036_nace_olu_kolon.sql` göçü `companies.nace_name` kolonunu düşürmeyi taahhüt ediyor ama canlı şemada kolon **hâlâ duruyor** — `test_defter_semayla_uyusuyor` kırmızı (`EKSIK`: dusurulmemis kolon) | **KAPANDI** | D-307 | **D-308** (ayni goc `0042`): olculdu — `companies.nace_name` **0 dolu satir**. Veri yokken DROP guvenli; dolu olsaydi bu satir RENAME'a donusurdu. Kolon dusuruldu. **Bonus:** ayni olcum ikinci bir ikiz kalintiyi da ortaya cikardi: `companies.adres` **0 dolu** (gercek veri `address`'te, 5.798 dolu) — 0007 `adres`'i kurmus, 0027 `address`'e cevirmis ama `adres` geride kalmisti. O da dusuruldu. |
| `BORC-VKN-01` | VKN kanalı ölü, kaynak bulunamadı | ACIK | D-253 | — · **Kanal açıldı (D-275, tek kapı D-306):** VKN, MERSİS'in ilk 10 hanesinden türetilir; `kimlik_no.mersis_dogrula()` 17 haneli yeni yazımı kanonik 16'ya indirir ve **VKN sağlamasından geçmezse None döner**. Türetme yalnız bu kapıdan yapılır — çağıran modülde dilim yazmak yasak (K-1). **Kapsam ölçüldü (D-307, `TSG-PILOT-20`):** 20/20 kapanmadı, sebep tek ve sabit — TSG sorgu sonuç tablosunda **VKN sütunu hiç yok**. Yani bu kanaldan doğrudan VKN gelmiyor; MERSİS→VKN türetmesi tek yol olarak kalıyor, ama MERSİS de her ilanda yer almıyor olabilir (65 ilan türü etiketi arasında hangisinin MERSİS taşıdığı ayrıca ölçülmedi) |
| `BORC-GOREV-EKLE-01` | `scripts/gorev_kutusu.py` panoya **görev ekleyemiyor**: `al`/`teslim`/`zincir` var, `ekle` yok. `zincir` yalnız *var olan* görevi tetikler. Sonuç: her yeni görev `data/orchestrator/task_board.json`'a elle veya tek kullanımlık betikle yazılıyor — şema denetimi yok, alan adı uydurma riski var | ACIK | D-306 | D-306: `TSG-PILOT-20` bu yolla eklendi (stdlib `json`, geçici betik, silindi). Kalıcı çözüm: `gorev_kutusu.py ekle --task-id --baslik --sahip --brief --mod` + zorunlu alan denetimi. **Aynı iş bir daha gerekirse önce bu yazılmalı** |
| `BORC-AD-VARYANT-01` | 31 kısaltma varyantı | IPTAL | D-261 | D-263 |
| `BORC-ADLANDIRMA-01` | kimlik hiç açılmamıştı (devir notu uydurdu) | IPTAL | — | D-271 |
| `BORC-DEDUP-KAYNAK-01` | `content_hash` yinelenmeyi durdurmuyor | KAPANDI | D-261 | D-262 |
| `BORC-DEFTER-IKI-SEMA-01` | kimlik hiç açılmamıştı; uyarı gerçek, borç değil | IPTAL | — | D-271 |
| `BORC-EXTID-01` | `baskentosb.org.tr` kazıyıcısı `external_id` üretmiyordu | KAPANDI | D-261 | D-262 |
| `BORC-GOC-IKI-DEFTER-01` | göç defteri iki değil üç, yazan yol dört | KAPANDI | D-264 | D-265 (son yol D-271) |
| `BORC-KOLON-DUSUR-01` | ölü kolon aktif sanılıyordu | KAPANDI | D-258 | D-259 |
| `BORC-PANEL-TAVAN-01` | panel tavanı sabit yazıyordu | KAPANDI | D-253 | D-258 |
| `BORC-PERF-BANT-01` | performans bandı yanlış; yüzeyin çağıranı yoktu | KAPANDI | D-259 | D-266 |
| `BORC-QUALITY-BETIK-01` | adı geçen betik diskte yok | IPTAL | D-255 | D-271 |
| `BORC-TASFIYE-IKIZ-01` | 22 tasfiye önekli firma öneksiziyle ikiz | KAPANDI | D-263 | D-264 |
| `BORC-TEST-SIRA-01` | test sırası bağımlılığı; iki kirleten | KAPANDI | D-267 | D-271 |
| `VERI-KAYNAK-BAG-01` | 5060 yetim firma, kaynak bağı yok | KAPANDI | D-260 | D-263 |

## Borç değil — kural / görev kimlikleri

Mandal `BORC-*` ile `VERI-*` kimliklerini birlikte tarar; aşağıdakiler borç değil, bu
yüzden ayrı bölümde durur. Silinmezler: adları `AGENTS.md`'de geçtiği sürece defterde kalır.

| Kimlik | Ne | Durum | D |
|---|---|---|---|
| `VERI-ETIKET-01` | her blok kaynağını söyler | KURAL | D-213 |
| `VERI-HAYALET-TEMIZ-01` | 9412 firma + UNIQUE indeks, onaylandı | KURAL | D-260 |
| `VERI-KAYNAK-TURU-01` | kaynak türü sözleşmesi | KURAL | D-235 |
| `VERI-KAZIYICI-DONGU-01` | kazıyıcı döngü sözleşmesi | KURAL | D-235 |
| `VERI-KOLON-IKIZ-01` | `companies.vergi_no` ikiz kolon ölçümü | KURAL | D-245 |
| `VERI-NACE-KOLON-01` | 0 kaçak NACE etiketi, onaylandı | KURAL | D-260 |
| `VERI-NACE-SOZLUK-01` | 3319 NACE kodu, onaylandı | KURAL | D-260 |
| `VERI-NACE-TEMIZ-01` | 554 `invalid_cleared`, onaylandı | KURAL | D-260 |
| `VERI-GORUNURLUK-01` | **böyle bir kimlik yok.** D-272/5'in anlattığı hayalet; o metni yazmak hayaleti gerçek bir dizeye çevirdi. Deftere iptal olarak girer, çünkü çıkarmanın yolu kaydı silmek olurdu | IPTAL | D-272 |

## Ölçülmüş sayılar (D-272)

- `AGENTS.md`'de kimlik: **71**. Mandalın gördüğü (`BORC|VERI`): **27**. Dışında kalan: **45**.
- Borç (gerçek): **18** — açık 4, kapandı 10, iptal 4.
- **Kapanmış ama açık/çelişkili sanılan: 2** — `BORC-KOLON-DUSUR-01` ve `BORC-PANEL-TAVAN-01`.
  D-271/6 bunları "çelişki" ilan etti; çelişki yoktu, satır sırası yanlış okundu
  (s2920=D-256 "kapanmadı" → s2945=D-258 "kapandı"; s3037=D-258 → s3121=D-259).
- 45 kimlik mandalın regex kapsamı dışında (`NACE-*`, `KVKK-*`, `GOC-*`, `SEMA-*`…).
  Bu bilinen kör nokta; genişletme ayrı bir tur işi — kapsam büyütmek defteri şişirir,
  fayda ölçülmedi.
- **26 → 27:** D-272/5 metni hayalet kimliği tek başına andığı için mandalın gördüğü kimlik
  bir arttı. Kayıt tutmanın kendisi ölçümü değiştirdi; sayı kılıfına uydurulmadı, gerçeğe
  çekildi (D-271'in tavanı 3 değil 4 yapmasıyla aynı karar).

## Devir — sonraki oturum (D-303 sonrası)

Bu tur **üç kesim + bir düzeltme**. Gerekçe: `AGENTS.md` D-303 (beş bölüm).
Teslim: [`docs/YOL_HARITASI.md`](YOL_HARITASI.md), [`docs/VERI_YAZMA_KURALLARI.md`](VERI_YAZMA_KURALLARI.md).

### Kesilenler — hepsi kırılarak doğrulandı (D-288)

| Ne | Dosya | Kırma kanıtı |
|---|---|---|
| Kimlik çatalı (kilit) | `scripts/karar_no.py` → `kilit_zorla.ajan_kimligi()` | tahsis sahibi `bilinmeyen` → `yasu` |
| Bayat kilit | `scripts/kilit_zorla.py::bayat()`, `BAYAT_SAAT=24` | `2gun=True`, `taze=False`, `zamansiz=False` |
| Veri yazma kapısı | `src/company_master/db/yazma_kapisi.py` | `MANDAL-SABLON-01` `25>23` → kırmızı → `7 passed` |
| Tahsis zorlaması | `scripts/hooks/commit-msg` + `karar_no.py --dogrula` | `D-303`→exit 0, `D-999`→exit 1 |
| Tek repo tek sistem | üst `.gitignore`, commit `df82690` | `git add "Huginn Data Insights"` **reddediliyor**, sızıntı 0 satır |

`pre-commit` listesi beşe çıktı (`test_sahne_kapisi_kurulu.py` eklendi) → `45 passed`.

### Devir notunun yanlış çıkan iddiaları (D-260: beyan kanıt değildir)

| İddia | Ölçüm |
|---|---|
| "tahsis atomik olsun" | `al()` **zaten** `O_CREAT\|O_EXCL`; sorun kimlikteydi |
| "2142 şablon site" | **2666** (2142 yalnız tek desen) |
| "25 ayrı yazma yolu" | **58** bağlantı noktası, **79** SQL dosyası |
| "11 dosyada kopya" | **23** dosya |

### Sonraki turun ilk işleri

1. **Hakemlik ürün sahibinde:** D-281, D-301, **D-303** çift numaralı. Üç kesim de
   bundan sonrasını korur, **mevcut üçünü çözmez**. Numara kaydırmak geçmişi bozar.
2. `BORC-YAZMA-KAPISI-01` açık: 23 kopya birleştirilmedi, yalnız tavanlandı.
   En çok yalan üreten yol kesildi; kalanı sıraya yazıldı.
3. **MERSIS etkisi hiç ölçülmedi** — ürün sahibi A/B kararı bunu bekliyor.
4. Şema gerçeği: `companies` tablosunda `source`, `collected_at`, `postal_code`
   kolonları **yok**. Köken zinciri `companies.source_record_id` →
   `source_records.source_id` → `sources` üzerinden kurulur.

---

## Devir — D-301 turu (tarihî kayıt)

Bu tur **dört mandal** kuruldu. Hepsi kırılarak doğrulandı (D-288: kırmadığın yeşil yeşil değildir).
Teslim: [`docs/YOL_HARITASI.md`](YOL_HARITASI.md). Gerekçe: `AGENTS.md` D-301.

### Kesilenler

| Mandal | Dosya | Kırma kanıtı |
|---|---|---|
| `MANDAL-SAHNE-01` — `git add -A` kapısı | `scripts/sahne_kapisi.py`, `.pre-commit-config.yaml` | `SAHNE_TAVAN=1` → exit 1 |
| `MANDAL-KPI-01` — panel testsizdi | `tests/test_admin_kpi.py` | ilk koşuda **3 kırmızı** (aşağıda) |
| `MANDAL-YUTULAN-01` — yutulan hata "veri yok" diye sunuluyordu | `web_dashboard/tabs/admin_quality.py`, `tests/test_yutulan_hata.py` | patlayan engine → panel nedeni yazıyor |
| `MANDAL-SIRA-01` — CI sabit sırada koşuyordu | `.github/workflows/ci.yml`, `tests/test_ci_rastgele_sira.py` | konfig bozuldu → **2 failed**, geri alındı → **5 passed** |

### Yeni bulgular (mandal kurulur kurulmaz çıkan canlı yalanlar)

`tests/test_admin_kpi.py` ilk koşusunda **üç ayrı canlı kusur** yakalandı. Üçü de yutulan
`except` içinde yıllardır sessizce duruyordu:

| Loader | Ölçülen hata | Kullanıcının gördüğü |
|---|---|---|
| `load_quality_trend` | `operator does not exist: timestamp with time zone - smallint` | kalite trendi grafiği **hiç çalışmamış** |
| `load_admin_kpi_summary` | `column "created_at" does not exist` → doğrusu `olay_zamani` | DAU kartı **hiç dolmamış** |
| `load_source_health` | `column sr.created_at does not exist` → doğrusu `collected_at` | kaynak sağlık tablosu **hep boş** |

Birincinin kök nedeni Postgres **operatör önceliği**: `NOW() - :gun || ' days'` ifadesi
`(NOW() - :gun) || ' days'` diye ayrışıyor. Doğrusu `NOW() - (:gun * INTERVAL '1 day')`.

**Kardeş taraması tahmini yarıya indirdi.** `admin_quality.py`'de 7 loader hata yutuyor ama
yalnız **2'si** (satır 698, 717) yokluğu `st.success` ile **olumluyordu** — D-249'u ihlal eden
bunlar. Diğerleri "bulunamadı"/"DB erişilemiyor" diyor, belirsiz, dokunulmadı. Ölçüm olmasa
6 yere gereksiz kod yazacaktım.

**`pytest-randomly` beyan edilmişti ama kurulmuyordu.** `requirements-dev.txt:8`'de duruyor;
CI'ın `test` job'ı o dosyayı hiç kurmuyor (`pip install -r requirements-dev.txt` yalnız `lint`
job'ında, satır 28). Yazılı olan ile koşan aynı şey değildi.

### Kendi kırmızım / kendi hatam (D-260)

1. **Sahne kapısı eşiğinin ilk gerekçesi yanlıştı.** "Sadece otomasyon 20'yi aşar" demiştim;
   49 commit ölçüldü: medyan 8, **%24'ü 20 üstü**. Eşik ölçümle yeniden seçildi.
2. **Kod tarayan mandal kendi yorumunu kod sandı — aynı turda iki kez.** Hem `test_admin_kpi.py`
   hem `test_ci_rastgele_sira.py` ilk sürümünde kırma denemesi yeşil kaldı, çünkü mandal
   "şu hatayı arıyoruz" diyen *yorum satırını* eşleşme saydı. İkisinde de yorum satırları
   atlanacak şekilde düzeltildi. **Ders: kod tarayan mandal, açıklamayı koddan ayırmadan yazılmaz.**

Test kırmızısı olarak **kendi kırmızım yok**: tam takım **iki sırada da** `4613 passed,
12 skipped, 0 failed` (rastgele 224.89s, sabit 191.60s).

### Yasu'nun üç kırmızısı — varsayılmadı, ölçüldü: **üçü de kapanmış**

Devir notu `3 failed` diyordu; ölçüm `0 failed`. `yasu_project_context.md` **149 satır**
(not "213" diyordu). D-226 tartması gereksiz kaldı — **yasu'nun hiçbir dosyasına dokunulmadı**,
çünkü dokunulacak kırık yoktu. Not beş tur bayatlamıştı.

### Beşinci kusur: kapım yazılıydı, koşmuyordu (D-302) — kendi hatam

Commit aşamasında HEAD'i kendim ölçtüm: `8a25798`. `git show --stat` → **24 dosya**, ve içinde
**dört mandalımın hepsi** var. Başka bir ajanın commit'i benim işimi yuttu — yani
**`MANDAL-SAHNE-01`'in önlemek için kurulduğu olay, kapı kurulduktan sonra, kapıya rağmen oldu.**

Kök neden ölçüldü: `git config core.hooksPath` = `scripts/hooks`. Fiilen koşan kanca
`scripts/hooks/pre-commit` ve o dosya `sahne_kapisi.py`'yi çağırmıyordu. Kapıyı yazdığım
`.pre-commit-config.yaml` ise `pre_commit` modülü kurulu olmadığı için **hiç okunmuyor**.

D-301'de "kırılarak doğrulandı" dediğim şey **betikti**, kurulum değildi. *Yazılı olan ile koşan
aynı şey değildir* — aynı turda **üçüncü kez** aynı kök. Kesim: kanca satırı + mandal
`tests/test_sahne_kapisi_kurulu.py` (silindi → `1 failed`, geri yüklendi → `8 passed`).

### Açık kalan / sıraya yazılan

- **MERSIS etkisi ÖLÇÜLMEDİ.** OSTİM'de ölçüldü (adres +1.427, e-posta +982, telefon +0),
  MERSIS'te ölçülmedi. PO A/B kararı vermeden **önce ölçülmeli**; bu turun işi değil.
- `pytest-timeout` **yerelde kurulu değil** (CI'da kurulu): `--timeout=300` yerelde
  `unrecognized arguments` veriyor. Küçük, `requirements-dev.txt` satırı.
- `karar_no.py` hâlâ **`CATISMA: ['D-281']`**: `AGENTS.md:4484` = index hayaleti kuralı,
  `docs/BORC_DEFTERI.md:856` = OSTİM kaynak araştırması (yasu'nun satırı). İki farklı karar,
  aynı numara. **Ölçüldü, çözülmedi** — hakemlik PO'da (D-226). Tavan yükseltilmedi.

---

## Devir — D-299 turu (tarihî kayıt)

Bu tur **panelin yüzeyi** ölçüldü. Teslim: [`docs/YOL_HARITASI.md`](YOL_HARITASI.md).

### Kesilenler (hepsi kırarak doğrulandı)

- **D-299 — şablon değer yalanı.** `website_domain` kolonundaki 2.142 `http://www.isim.org.tr`
  placeholder'ın kendisiydi (`AD_ICINDE=0/2142`). Dört şablon daha ölçüldü. Tek kapı
  `admin_quality._dolu_kosulu()`; `admin_kpi` import eder, kopyalamaz. **Web Sitesi %57,9 → %29,6.**
  Veri **silinmedi** — silme PO'da.
- **`BORC-PANEL-SAHTE-TEST-01` kapandı.** `admin_executive._firma_kayitlari()` canlıda üç ayrı
  katmanda patlıyordu: kolon adı (`address_line` yok), naive/aware datetime, `Decimal`/`float`.
- `admin_quality` + `admin_kpi`: "hepsi %0 eksik" yalanı (D-249) ve transaction-abort zinciri.
- NACE etiketi export çıkış kapısına bağlandı; `sunum.nace_metni` NaN sızıntısı (D-287).

### Ölçüldü ama kesilmedi

- **Yasu'nun OSTİM zenginleştirmesi panele ulaşmamış.** Yasu **SQLite** (`company_master.db`),
  panel **Postgres**. 3.338 kayıt izole klasörde. Eşleşen 1.577 → **adres +1.427, e-posta +982,
  telefon +0**; canlıda hiç olmayan 1.742. Yazma kararı PO'da (`BORC-D-281`).
- **9 kolon tamamen boş, 54 tablodan 31'i boş.** Devir notu "28 kolon / 8 tablo" diyordu — yanlış.
  D-266 gereği düşürülmedi, haritaya donduruldu.

### Kendi kırmızım (ikisi de kesildi)

1. **BOM (U+FEFF)** — `admin_kpi.py`, `admin_quality.py`, `tests/test_admin_quality.py`.
   `test_panel_durustluk` `ast.parse` ile `SyntaxError`, `test_guard_bom_ratchet` ratchet ihlali.
   Ben açtım, ben ölçtüm, ben sildim.
2. **`test_admin_sistem_quality.py:46`** `assert ...shape[0] == 7` — DB erişilemezken
   `load_missing_field_analysis`'ten "7 alan, hepsi %0 eksik" bekliyordu. D-249 kesimimden sonra
   kırmızıya döndü. **Testi düzelttim, kodu değil**: test yalanı koruyordu, aynı testin diğer üç
   satırı zaten `empty` bekliyor. Yeni hâli `.empty`.

Sonrası: `45 passed` (dört ilgili dosya), tam takım `4592 passed`.

### Açık kalan borçlar

- `admin_quality.load_risky_companies` hâlâ `except` ile hatayı yutuyor → kullanıcı
  "riskli firma yok" sanır (D-249 ihlali).
- **`tests/test_admin_kpi.py` hiç yok.** Panel testsiz.
- `karar_no.py` **`CATISMA: ['D-281']`** bildiriyor: `AGENTS.md` D-281 = index hayaleti,
  bu dosyada D-281 = OSTİM kaynak araştırması. İki farklı karar aynı numarada; yasu'nun satırı
  olduğu için D-226 gereği dokunulmadı.

### Yasu'nun üç kırmızısı — kesilmedi (D-226), beyan edildi

Tam takım, rastgele sıra: `3 failed, 4592 passed, 12 skipped in 203.47s`. Üçü de yasu'nun
dosyasında; ben dokunmadım.

1. `test_brief_sablon_denetim::test_yeni_brif_sablona_uyar[brief_yasu_VERI-OSTIM-TAM-TARAMA-01.md]`
   — brief D-217 şablonunu taşımıyor (`**Başlık:**`, `**Hub:**`, `## Neden` eksik).
2. `test_dokuman_politikasi::test_d219_ajan_context_dosyalari` — `yasu_project_context.md`
   **213 satır**, tavan 200. Eski oturum blokları `archive/`e taşınmalı.
3. `test_ui_search_gap::test_admin_quality_bos_tabloda_hata_vermez` — **sıra bağımlı**, tek başına
   yeşil. Kök sebep ölçüldü ve yeniden üretildi: test `load_freshness_distribution.clear()`
   çağırmıyor, `st.cache_data` bir önceki testin sonucunu döndürüyor. Yani test kendi iddiasını
   değil cache'i okuyor (D-288). Sabit sırada gizlenir, rastgele sırada patlar. Tek satırlık
   düzeltme: fonksiyon çağrısından önce `.clear()`.

## Devir — sonraki oturum (D-295 sonrası, tarihî kayıt)

Bu tur **ürünün kendisi** ölçüldü: altyapı değil, müşteriye satılacak veri.
Sonuç tek cümleyle: **ürün bugün satılabilir durumda değil.** Aşağıdaki bölümler
sayıdır, yorum değil. D-293 ve öncesi başlıklar **tarihî kayıttır**.

### 1 — Dağılım: 9412 firmanın kaç tanesi müşteriye hazır?

`identity_completeness`, azami **10.0**, ortalama **3.72**, en düşük 1.0, en yüksek **6.5**.

| Bant | Firma | Oran |
|---|---|---|
| 8–10 | **0** | %0.0 |
| 6–8 | **5** | %0.1 |
| 4–6 | 5329 | %56.6 |
| 2–4 | 3381 | %35.9 |
| 0–2 | 697 | %7.4 |

**Hiçbir firma 7'ye ulaşmıyor.** D-258'in "ulaşılabilir tavan 7.5" kaydı dürüsttü ama
tavana yaklaşan **yok**: en dolu firma 6.5, ondan sadece 5 tane var. "6+ müşteriye hazır"
dense bile **elde 5 firma** var, 9412 değil.

Veritabanındaki yazılı puanlar yeniden hesaplananla **birebir** aynı, hepsi `score_version=v1`
— bayat puan yok. Puanlama kapısı (D-250) dürüst çalışıyor; kötü olan veri.

### 2 — Temsilî firma kartları (alan alan)

| | EN BOŞ (1.0) | ORTANCA (4.3) | EN DOLU (6.5) |
|---|---|---|---|
| `legal_name` | ✔ puanlı | ✔ puanlı | ✔ puanlı |
| `tax_number` | — | — | ✔ `9380023742` |
| `tax_office` | — | — | — |
| `mersis_number` | — | — | — |
| `trade_registry_number` | — | — | — |
| `nace_code` | `62.01` **puansız** (`title_default`) | `10.11` **puansız** (`sector_default`) | `47.78` **puansız** (`unknown`) |
| `address` | — | ✔ puanlı | ✔ puanlı |
| `primary_phone` | — | ✔ puanlı | ✔ puanlı |
| `primary_email` | — | — | ✔ puanlı |
| `website_domain` | — | ✔ puanlı | ✔ puanlı |

Üç firmanın **üçünde de** NACE dolu ama üçünde de puansız: kaynak tahmin (D-245).
Üçünde de MERSİS ve sicil yok. **En dolu firmanın kartında bile** vergi dairesi,
MERSİS ve sicil boş — yani bir kurumsal kimlik doğrulaması yapılamıyor.

### 3 — Alan doluluğu: puanlı mı, yoksa sadece dolu mu?

`KAYIP` = alan dolu ama puan kapısından geçmiyor.

| Alan | Ağırlık | Puanlı | Ham dolu | KAYIP |
|---|---|---|---|---|
| `legal_name` | 1.0 | 9412 (%100) | 9412 | 0 |
| `tax_number` | 1.5 | **5** (%0.1) | 5 | 0 |
| `tax_office` | 0.5 | **0** | 0 | 0 |
| `mersis_number` | 1.0 | **0** | 0 | 0 |
| `trade_registry_number` | 1.0 | 25 (%0.3) | 619 (%6.6) | **594** |
| `nace_code` | 1.0 | **0** | 8289 (%88.1) | **8289** |
| `address` | 1.5 | 5798 (%61.6) | 5798 | 0 |
| `primary_phone` | 1.5 | 8251 (%87.7) | 8251 | 0 |
| `primary_email` | 0.7 | 4038 (%42.9) | 4038 | 0 |
| `website_domain` | 0.3 | 5446 (%57.9) | 5446 | 0 |

NACE kaynak dağılımı: `sector_default` %60.3, `unknown` %26.6, `fallback` %6.9,
`invalid_cleared` %5.9, `title_default` %0.2 — **kanıta dayalı sıfır**. 8289 firmada
NACE "var" ama tamamı tahmin; puan kapısı doğru davranıp 0 veriyor.

**`HEDEF_VERI_KAPSAMI.md` vaadiyle karşılaştırma:** belgede 35 öbek sayılıyor —
VAR 5, BOŞ 4, KAPALI 4, YOK 22. Yani **vaadin %14'ü** (5/35) veri taşıyor. Bu turda
ölçülen o 5 öbeğin **içeriği** de sorunlu (aşağıda); yani "%14 var" bile iyimser.

### 4 — Doluluk ≠ bilgi (D-292 dersi, bu turda tekrar çıktı)

Puanlanan alanların içeriği ölçüldü:

- **Adres** (ağırlık 1.5, 5798 puanlı): 4795'inde (%82.7) "ankara" geçmiyor; 626'sı (%10.8)
  20 karakterden kısa; **posta kodu olan 0**.
- **Web sitesi** (5446 puanlı): 2779 kayıt yalnız **58** adresi paylaşıyor —
  `http://www.isim.org.tr` **2142** kez, `ostimistihdam.com` 474 kez. 3799 kayıtta (%69.8)
  alan adı ile unvan arasında ortak sözcük yok. Bu kolon büyük ölçüde **dizin bağlantısı**.
- **Telefon** (8251 puanlı): 1057 kayıt 498 yinelenen numarayı paylaşıyor
  (tepe `905344018261` ×10); 913'ü ne cep ne sabit biçiminde.
- **E-posta** (4038 puanlı): 444 kayıt 196 yinelenen adresi paylaşıyor; en sık değer
  **yer tutucu** `bilinmeyen@bilinmeyen.com` (17 firma). Olumlu yan: ücretsiz sağlayıcı
  yalnız %0.6.
- **`entity_resolution`**: 8905 satır var ama **8820 firmanın** hiç eşleşme kaydı yok (%93.7).

### 5 — Panel okuma tarafı (D-288 yazma tarafını ölçmüştü, okuma ölçülmemişti)

- 33 sekme modülünün **33'ü** import ediliyor, kırık import **0**. `SECTIONS` 36 kayıt.
- Panelin okuduğu tablolardan **6'sı dolu**: `source_records` 10601, `companies` 9412,
  `search_events` 379, `users` 7, `sources` 4, `credit_ledger` 3.
- **8'i tamamen boş**: `admin_audit_log`, `api_usage_daily`, `audit_logs`,
  `company_packages`, `company_signals`, `login_events`, `packages`, `user_activity_log`.
  Bu sekmeler çiziliyor ama gösterecek satırları yok.
- Veritabanında **91 tablo**, dolu olan **20**, boş **71**.
- `companies` 49 kolon; **28'i panelde hiç geçmiyor** — aralarında `address`,
  `mersis_number`, `tax_office`, `trade_registry_number`, `trade_registry_office`,
  `osb_id`, `osb_parcel`, `nace_validity`, `score_version` ve tüm `*_score` kolonları.
- **Canlı kırık sorgu** (`BORC-PANEL-ADRES-01`): `admin_executive._firma_kayitlari()`
  `address_line` okuyor, o kolon `companies`'te **yok**:

```
psycopg.errors.UndefinedColumn: column "address_line" does not exist
LINE 1: SELECT address_line AS adres FROM companies LIMIT 1
```

`address_line` yalnız `company_locations`'ta var ve o tablo **0 satır**. Testi
(`test_firma_kayitlari_30_gun_esigi`) sahte engine kullandığı için yeşil —
**D-288 kuralının canlı örneği: yeşil test de beyandır.**

### 6 — En büyük tek kazanç (benzetim)

Alan tamamen doldurulsaydı ortalamanın nereye çıkacağı (3.72'den):

| Alan | Eksik firma | Ortalama kazanç | Sonuç | Kaynak durumu |
|---|---|---|---|---|
| `tax_number` | 9407 | **+1.50** | 5.22 | **KAPALI** (D-257: GİB tek yönlü) |
| `mersis_number` | 9412 | +1.00 | 4.72 | **KAPALI** (MERSİS 404) |
| `nace_code` | 9412 | +1.00 | 4.72 | kanıt kaynağı yok |
| `trade_registry_number` | 9387 | +1.00 | 4.71 | **KAPALI** (TSG captcha) |
| `address` | 3614 | +0.58 | 4.29 | açık |
| `tax_office` | 9412 | +0.50 | 4.22 | KAPALI |
| `primary_email` | 5374 | +0.40 | 4.12 | açık |
| `primary_phone` | 1161 | +0.19 | 3.90 | açık |
| `website_domain` | 3966 | +0.13 | 3.84 | açık |

**Acı gerçek: en büyük dört kazancın dördü de D-257'de kapalı ilan edilen kaynakların
arkasında.** Yani puanı yükseltecek iş, veri toplamak değil **kapalı kapıyı açmak**.

Kaynak gerektirmeyen, ölçülmüş üç iş:

1. **`BORC-PANEL-ADRES-01`** — tek satırlık sorgu düzeltmesi; panelin sağlık sayfası
   şu an ölü. Puana etkisi 0, **ürünün görünürlüğüne etkisi tam**.
2. **`BORC-SICIL-DAIRE-01`** — elde 619 sicil no var, 594'ünde daire eksik.
   Daire tamamlanırsa **+0.06 ortalama**, 594 firma 1.0 puan kazanır. Dış kaynak gerekmez
   (sicil no'dan daire çıkarımı / tek seferlik eşleme).
3. **`BORC-SITE-COP-01` temizliği** — 2779 kayıttaki dizin bağlantısı silinirse ortalama
   **düşer** (−0.09), ama puan **dürüstleşir**. Ürün sahibinin kararı: dürüst düşük puan mı,
   şişik puan mı?

### 🔴 ÜRÜN SAHİBİNE — karar bekleyen üç soru

1. **Ürün bu haliyle satılabilir mi?** Ölçüm: 9412 firmanın **5'i** 6+ puan. Kurumsal
   kimlik (VKN/MERSİS/sicil) **hiçbir firmada tam değil**. Benim okumam: **satılamaz**;
   bugünkü ürün "Ankara'da firma listesi + telefon"dur, "firma istihbaratı" değil.
2. **Şişik puan mı, dürüst düşük puan mı?** `website_domain` ve `address` alanlarındaki
   doğrulanmamış içerik ayıklanırsa ortalama 3.72'den ~3.5'e düşer. D-292'nin dersi
   ayıklamayı söylüyor, ama bu **ürün vitrinini** düşürür.
3. **Kapalı kaynaklar (D-257) yeniden denenecek mi?** Puanın %45'i (4.5/10) o kapıların
   arkasında. Denenmezse tavan pratikte **~5.5**'te kalır; bu turda ölçülen dağılım da
   zaten oraya sıkışmış durumda.

---

## Tarihî kayıt — D-293 ve öncesi

Bu turda anahtarın kapsamı ölçüldü ve D-288'in bir kaydı **çürütüldü**. Aşağıdaki
D-288 ve D-287 bölümleri **tarihî kayıttır**, güncel durum yukarıdaki D-295 başlığındadır.

### ⚠ D-288'İN KAYDI YANLIŞ — düzeltildi

D-288 defterine `Commit HEAD'in atası mı | **EVET**` yazmıştı. **Ölçüm: HAYIR.**

```
git merge-base --is-ancestor 90c4702 HEAD     → çıkış 1  (ATA DEĞİL)
git cat-file -e HEAD:config/certs/selfsigned.key → fatal: does not exist in 'HEAD' (128)
```

Yanlışın sebebi benim de ilk turda düştüğüm tuzak: cmd.exe `%errorlevel%` değişkenini
**satır ayrıştırılırken** genişletir. `komut & echo EXIT=%errorlevel%` biçiminde
zincirlenen her okuma **bayattır**. Komutlar ayrı ayrı koşturulmalı.

### 🔴 ÜRÜN SAHİBİNE — anahtar kararı: **B konusuz, A da muhtemelen konusuz**

Anahtar `90c4702` **hiçbir dalda değil**:

```
git branch -a --contains 90c4702   → boş
git tag --contains 90c4702         → boş
git for-each-ref refs/remotes refs/heads refs/tags --contains 90c4702  → BOŞ
git log --format="%h %p" -1 90c4702 → 90c4702 993ce8a
git ls-remote origin → refs/heads/worktree/…-UX-v2 = 993ce8a
```

Uzaktaki dal anahtar commit'inin **ebeveyninde** duruyor (`993ce8a`). **Anahtar hiç
push edilmedi.** Blob'u yaşatan tek şey yerel cline checkpoint ref'leri
(`refs/cline/checkpoints/1789915554965_dwoi5/{4,5}`; toplam 169 `refs/cline/*`,
fetch refspec `+refs/heads/*` olduğu için asla gönderilmez).

Anahtarın neye bağlı olduğu (ölçüldü):

| Soru | Ölçüm |
|---|---|
| Kim okuyor | **tek tüketici** `config/nginx.conf` (`ssl_certificate_key`) — o dosya da yalnız `90c4702` içinde, diskte/HEAD'de/index'te **yok** |
| Servise bağlı mı | **hayır** — `docker-compose.yml`'de nginx servisi yok, 443 yok, certs mount yok |
| Yerel mi üretim mi | **yerel** — `CN=localhost`, `SAN=DNS:localhost`, issuer==subject, 2026-09-20→2027-09-20 |
| Servis kimliği mi | **hayır** — Supabase/servis hesabı/imza anahtarı değil |
| Üretim HTTPS'i | CI `deploy-staging.yml` `https://staging.huginn.example.com`, iş akışında cert malzemesi **yok** → TLS başka yerde sonlanıyor |
| Başka kimlik dosyası | **yok** — 987 commit'lik tüm nesne veritabanında yalnız 2 nesne: `c0881ee…crt`, `216cfdd…key` |

Bedel:

- **(B) `filter-repo`:** HEAD'de **421 commit** yeniden yazılır, üç ajanın klonu kırılır —
  **yayımlanmamış, hiçbir daldan ulaşılamayan** bir blob için. D-221/1: bedel > fayda.
- **(A) rotasyon:** sertifika `localhost`'a bağlı, onu sunan servis yok, süresi 2027-09-20.
  Döndürülecek bir üretim bağı **ölçülemedi**.

Devir notunun ön değerlendirmesi doğrulandı ve güçlendi. **Hiçbir şey temizlenmedi**, karar sizde.

### Mandal — `tests/test_kimlik_dosyalari.py` (D-293)

`.gitignore:155-156` (`*.key`, `*.pem`) 2026-09-24'te `7a9ff2c` ile zaten vardı ama
**zorlayıcısı yoktu**. Mandal iki ayrı şeyi ölçer: `git ls-files` (gerçek durum) ve
`git check-ignore --no-index` (desen **gerçekten** eşliyor mu). `.crt`/`.cer` kapsam
dışı — açık anahtar, sızması zarar vermez.

**Kırılarak doğrulandı** (D-288 dersi):

```
temiz:  2 passed
kırma1: *.key → /*.key  →  AssertionError: .gitignore bu kimlik yollarini tutmuyor:
        ['config/certs/selfsigned.key']          ← D-288'in tam hatası (köke bağlı desen)
kırma2: git add -f _kirma_denemesi.key  →  AssertionError: izlenen kimlik dosyasi: [...]
geri alındı: 2 passed
```

### Yan bulgu — D-281'in kendi artığı index'te duruyordu

`scripts/_nace_olcum.py` (D-287'nin tek seferlik aracı) diskten silinmiş, **index'te
kalmıştı**. Kural yazıldıktan sonra bir tur daha ihlal edildi. `git rm --cached` ile
kesildi. Ders: silme beyanı `git ls-files` ile doğrulanmadıkça beyandır (D-260).

### Tam takım (D-293 kapanışı)

Sabit sıra `4 failed, 4582 passed, 12 skipped — 209,09 sn`; rastgele sıra **aynı 4 kırmızı**
(`207,63 sn`). **Sıra bağımlılığı yok.** Taban 4580 → +2, ikisi de D-293 mandalı.
**Benim hiçbir kırmızım yok.**

### Kırmızılar — hepsi yasu'da, kesilmedi (D-226)

`ajan_chat.py ac` ile yasu'ya **tek kayıt** açıldı, ölçülmüş eksik listesiyle.

| Kırmızı | Sahibi | Eksik |
|---|---|---|
| `test_naming_audit::test_acik_gorevlerde_yeni_d57_ihlali_yok` | yasu | başlık D-57 kalıbı: `[ALAN] FIIL + NESNE -> CIKTI (SURE)` |
| `test_pano_d57_kalici::test_aktif_gorevler_d57_gecer` | yasu | aynı görev, aynı sebep |
| `test_brief_sablon_denetim::…[brief_yasu_VERI-OSTIM-TAM-TARAMA-01.md]` | yasu | 11 zorunlu bölümün **hepsi**: `**Başlık:**`, `**Hub:**`, `## Neden`, `## Doğrulanacak varsayım`, `## Kabul kriteri`, `## Ajan chat zorunlu`, `## Teslim`, `## Ilgili Nodlar`, `## Adımlar\|## Faz A`, `ajan_chat.py` komut referansı, ≥2 wikilink (D-218) |
| `test_dokuman_politikasi::test_d219_ajan_context_dosyalari` | yasu | `yasu_project_context.md` 213 > 200 (`BORC-AJAN-HAFIZA-01`) |

**Ürün sahibine:** ilk üçü **tek düzeltmeyle** kapanır (başlığı kalıba çek + brief'i
`plans/_brief_sablon.md`'ye uydur). Bu 4 kırmızı her ajanın tam takım beyanını kirletiyor;
gerçek arızalar gürültüye karışıyor. Yanıt gelmezse **devri üreticiye taşıma** kararı sizde.

### Sonraki tura

- Anahtar kararı (A / B / hiçbiri) — **bekliyor**, ölçüm yukarıda tamam.
- Otomasyonun beyaz listesi ilk gerçek koşudan sonra `git log -1 --name-only` ile ölçülmeli.
- `data/` altına sır düşerse otomasyon yine alır — veri sızması kesilmedi.

---

## Devir — D-288 turu (tarihî kayıt)

Bu turda otomasyonun git kapısı daraltıldı. Aşağıdaki D-287 bölümü **tarihî kayıttır**.

### Bu turda bitenler (D-288)

| İş | Sonuç | Kanıt |
|---|---|---|
| Otomasyon nerede yaşıyor | `scripts/git_auto_push.bat`, Zamanlanmış Görev `\Huginn Git Push`, **iki tetik** (00:01 + 12:01, günlük), 2026-09-11'den beri, kuran `EXCALIBUR\yasin` | `schtasks /query /xml ONE` → `<Command>…git_auto_push.bat</Command>`, iki `<StartBoundary>` |
| Kaç yol var | **2** toptan sahneleme: `git_auto_push.bat:33` + `wiki_automation/run_all.py::git_commit` | `git grep -n -E "git add (-A\|--all\|\.)"` |
| Tarih etkisi | **64** otomatik commit, **2150** benzersiz dosya (`src/` 217, `tests/` 143, `scripts/` 233, `_ARSIV…` 160) | `git log --name-only --grep=…` + Counter |
| Kapı daraltıldı | her iki yolda beyaz liste: `data docs hubs plans indexes` | docstring/REM gerekçe (D-267) |
| Mandal | `tests/test_otomasyon_sahneleme.py` (2 test) | **kırarak** doğrulandı, aşağıya bak |
| Yeni kırmızı kesildi | `_ARSIV_tek_kullanimlik/_pytest_rerun.txt` → `git rm --cached` | `test_zaman_damgali_yedek_git_te_izlenmiyor` **1 passed** |
| Kural çelişkisi | `AGENTS.md` D-193 maddesi ajanlara `git add -A` **emrediyordu** → düzeltildi | AGENTS.md:751 |

### ⚠ MANDAL İLK SÜRÜMÜNDE YALANCI YEŞİLDİ — kendi hatam, beyan ediyorum

Mandalın ilk deseni düz `git` arıyordu. `.bat` git'i `"%GIT%"` değişkeniyle çağırdığı için
gerçek `"%GIT%" add -A` satırını **kaçırdı**. İlk koşuda gelen kırmızı, çalışan koddan değil
benim yazdığım **gerekçe yorumundan** geliyordu — yorumu soyunca test yeşile döndü ve
"tamam" görünüyordu. Kırma testi yapılmasaydı bu mandal **hiç çalışmadan** yeşil duracaktı.

**Ders (D-260'ın mandala uygulanışı): yeşil test de bir beyandır, kırılana kadar kanıt değildir.**
Desen `%GIT%` / `$GIT` biçimlerini kapsayacak şekilde düzeltildi; `.bat` ve `.py` yolları
**ayrı ayrı** kırılıp kırmızı görüldü, sonra geri alındı.

### 🔴 ÜRÜN SAHİBİNE — TARİHTE GERÇEK ÖZEL ANAHTAR VAR (temizlik YAPILMADI)

Zorunlu sır araması yapıldı. İki ayrı sonuç:

1. **Otomatik commit'lerin içinde sır YOK.** Çıkan isimler yalnızca sır *aracı*
   (`rotate_secrets.py`, `test_secrets_rotation.py`, bir kurulum raporu). Bu iyi haber.
2. **Ama tarihte elle girmiş gerçek bir anahtar var:** `config/certs/selfsigned.key`,
   içeriği `-----BEGIN RSA PRIVATE KEY-----`.

| Ölçüm | Sonuç |
|---|---|
| Ekleyen commit | `90c4702` (2026-09-20) — **otomasyonun ürünü değil, elle** |
| HEAD ağacında mı | **Hayır** (`git ls-tree -r HEAD` boş) |
| İzleniyor mu | **Hayır** (`git ls-files -- config/certs/` boş) |
| Commit HEAD'in atası mı | **EVET** (`git merge-base --is-ancestor` → 0) |
| Blob ulaşılabilir mi | **EVET** — `216cfdd540712a8c327ceb1cd4bc1ec37c6048fe` |

Yani dosya çalışma ağacından kalkmış ama **tarihten kalkmamış**; depoyu klonlayan herkes
`git show 90c4702:config/certs/selfsigned.key` ile anahtarı okuyabilir.

**Hiçbir şey temizlenmedi.** Tarih yazmak geri dönüşsüzdür, karar sizindir. Seçenekler:
**(A)** anahtarı **döndür** (yenisini üret, eskisini iptal et) — tarihi hiç ellemez, en güvenli,
self-signed sertifika için genelde yeterli. **(B)** `git filter-repo` ile tarihten sök — tüm
commit karmaları değişir, üç ajanın ağacı ve üst depo işaretçisi bozulur, **ağır**.
**Önerim A**, çünkü depo şu an özel ve anahtar self-signed; ama depo bir gün herkese açılırsa
B kaçınılmaz olur.

Ek not: `workspace/external/cursor_grok/.../leak.py` içindeki `API_KEY = 'secret123'`
**kasıtlı sahte fikstürdür**, zarar yok.

### Otomasyon: durdurulmadı, daraltıldı

Ölçülen seçenekler — **(A)** durdur: günlük yedek kaybolur, **sizin kararınız**, yapılmadı.
**(B)** beyaz liste: **uygulandı**. **(C)** `pre-commit`'e bırak: kanca commit anında çalışır,
`add`'i engellemez, yetmez.

Otomasyon artık yalnız `data docs hubs plans indexes` sahneliyor. Kod, test, betik ve
`_ARSIV_tek_kullanimlik` **otomasyonun işi değil** — ajanlar tek tek sahneler.
`data_worktree` bilerek dışarıda: D-228'de tasfiye edildi, diskte yok.

### `.gitignore` neden tutmadı (ölçüldü)

Kural eksikliği değil, **kapsam hatası**: `/_*.txt` baştaki eğik çizgi yüzünden yalnız köke
bağlıydı, alt dizine hiç inmiyordu. `git check-ignore -v` çıkış kodu **1**, çıktı **boş** —
hiçbir desen eşleşmemişti. `_pytest_rerun*` eklendi; tekrar ölçüldü, artık eşleşiyor
(`.gitignore:148`).

**Yan bulgu, kesilmedi:** `_ARSIV_tek_kullanimlik/` altında **~160 izlenen dosya** var.
`BORC-SCRIPTS-01` DONDURULMUŞ; ölçüldü, rapor edildi, dokunulmadı.

### Tam takım (D-288 kapanışı)

Sabit sıra `4 failed, 4580 passed, 12 skipped — 202,13 sn`; rastgele sıra **aynı 4 kırmızı**
(`203,25 sn` koşusunda 5'ti, beşinci benim çöpümdü, aşağıda). **Sıra bağımlılığı yok.**
Taban 4562 → +18 geçen (D-288 mandalı 2, kalan 16 başka ajanların bu turdaki testleri).

| Kırmızı | Sahibi | Bu turda kesildi mi |
|---|---|---|
| `test_kok_izin_listesi::test_zaman_damgali_yedek_git_te_izlenmiyor` | **benim** (`_pytest_rerun.txt`) | **EVET** — `git rm --cached` + `.gitignore` kapsam düzeltmesi |
| `test_kok_politikasi::test_vault_kokte_tek_kullanimlik_yok` | **benim** (`_k.tmp`, `_oc.tmp`, `_oc2.tmp`, `_sir_taramasi.txt`) | **EVET** — D-241, silindi, mandal yeşile döndü |
| `test_dokuman_politikasi::test_d219_ajan_context_dosyalari` | yasu (`yasu_project_context.md` 213>200) | hayır — `BORC-AJAN-HAFIZA-01`, D-226/sahiplik |
| `test_brief_sablon_denetim::…[brief_yasu_VERI-OSTIM-TAM-TARAMA-01.md]` | yasu | hayır — brief 11 zorunlu bölümün **hiçbirini** taşımıyor (D-217) |
| `test_naming_audit::test_acik_gorevlerde_yeni_d57_ihlali_yok` | yasu | hayır — aynı görev, başlık D-57 kalıbına uymuyor |
| `test_pano_d57_kalici::test_aktif_gorevler_d57_gecer` | yasu | hayır — aynı görev, aynı sebep |

**Ölçülen not:** son üç kırmızı **tek kaynak** — `VERI-OSTIM-TAM-TARAMA-01` görevi bu tur
açıldı ve üç ayrı mandalı birden kırdı. Üçü tek düzeltmeyle (başlığı D-57 kalıbına çekip
brief'i `plans/_brief_sablon.md`'ye uydurmak) kapanır; sahibi yasu, kesme bende değil.

### Sonraki tura

- Anahtar kararı (A döndür / B tarih temizliği) — **bekliyor**.
- Otomasyonun beyaz listesi doğru kapsamda mı, ilk gerçek koşudan sonra
  `git log -1 --name-only` ile **ölçülmeli** (bu tur çalışmadı; sonraki tetik 00:01).
- `data/` altına sır düşerse otomasyon yine alır. Beyaz liste kod sızmasını kesti,
  **veri sızmasını kesmedi**. Gerekirse `data/` için ayrı bir desen mandalı.

---

## Devir — D-287 turu (tarihî kayıt)

Bu bölüm devir notunun kaynağıdır (D-219 mantığı). Ajan hafıza dosyasına yazılmadı: ölçüldü,
dört `*_project_context.md` dosyasında bu hattın hiçbir izi yok — hat panoya bağlı değil,
doğrudan ürün sahibiyle yürüyor.

### Bu turda bitenler (D-287)

| İş | Sonuç | Kanıt |
|---|---|---|
| Karar A — `ac` yanlış kapı uyarısı | `chat.acik_sahipler()` + `cmd_ac` stderr uyarısı, **engelleme yok** | `tests/test_ajan_chat.py` 21 geçti (15→21) |
| Karar B — karar numarası kancaya | `test_karar_numara_tekligi.py` pre-commit'e eklendi; `karar_no.py` **değişmedi** (mandal zaten vardı) | Sahte D-286 başlığı → commit **durdu** (`2 <= 1` düştü), geri alındı → yeşil. Kanca yeni maliyet **19,4 sn** |
| Karar C — yazma kapısı ölçümü | motor çağıran **163**, gerçekten YAZAN **70**, doğrudan `create_engine` **25**, motorsuz yazan **0**; dağılım `src/` 22, `scripts/` 47, **`web_dashboard/` 0** | mimari **değiştirilmedi** (ürün sahibi kararı) |
| NACE doğrulama | doğrulama **reddedildi**, ağırlık **çekilmedi**, iki mandal kondu | `tests/test_panel_durustluk.py` 19 geçti (17→19), kırarak doğrulandı |

**Karar C okuması (ürün sahibine):** yazma kapısı **tek değil** — 25 dosya `create_engine`'i
doğrudan çağırıyor, 24'ü `connection.py`'yi atlıyor. Ama panel **hiç yazmıyor** (0), yani
canlı-DB ayrımının dayandığı risk panelde yok. Motorsuz gizli yazma yolu da yok (0).

**NACE okuması:** `verified` sıfır değil, değer kümesinde **yok** (`medium` 5732 / `unknown`
2942 / `fallback` 738). Kod doluluğu 8289/9412 = **%88,07**, kanıt kaynaklı NACE **0/9412 = %0**.
Sözlüğü puana bağlamak 8289 **tahmin** koda 1.0 dağıtırdı — puan uydurmanın ta kendisi.
Tavan kilidi (7,5/10) **dürüst**, bu yüzden ağırlık gerçeğe çekilmedi; kilit kaldıracak olan
şey kanıt kaynağıdır (`BORC-VKN-01` / MERSİS), bu tur açılmadı.

### Tam takım (D-287 kapanışı)

Sabit sıra `2 failed, 4562 passed, 12 skipped — 190,29 sn`; rastgele sıra `2 failed, 4562 passed,
12 skipped — 176,88 sn`. **Sıra bağımlılığı yok.** Taban 4555 geçti → +7: Karar A 6 mandal +
NACE 2 mandal − aşağıdaki yeni kırmızı 1.

| Kırmızı | Sahip | Sebep | Karar |
|---|---|---|---|
| `test_dokuman_politikasi.py::test_d219_ajan_context_dosyalari` | yasu | `yasu_project_context.md` 213 > 200 satır | **Kesilmedi** (D-226), bilinen kırmızı |
| `test_kok_izin_listesi.py::test_zaman_damgali_yedek_git_te_izlenmiyor` | Yasin (otomasyon) | `_ARSIV_tek_kullanimlik/_pytest_rerun.txt` git'e **izlendi** → `1 <= 0` düştü | **Kesilmedi** — benim dosyam değil, ürün sahibi kararı bekliyor (`git rm --cached`) |

### ⚠ Yeni tehlike — otomatik günlük commit tüm ağacı süpürüyor

`dfc5f0a Yasin — Otomatik gunluk commit (29.09.2026 12:01)`: **352 dosya, 41619 ekleme**.
Bu commit tur ortasında çalıştı ve **uçuştaki dosyalarımı** (`src/company_master/chat.py`,
`scripts/ajan_chat.py`, `tests/test_ajan_chat.py`, `tests/test_panel_durustluk.py`,
`scripts/hooks/pre-commit`, hatta D-241 gereği sonradan sildiğim `scripts/_nace_olcum.py`)
tarihe soktu. Yedek dosyasını izleyen de aynı commit.

**Sonuç:** "tek tek sahnele, `git add -A` yasak" kuralı üç ajan için geçerli ama otomasyon bu
kuralın dışında ve kuralı **fiilen geçersiz kılıyor**. HEAD artık `38ad9f7` değil `dfc5f0a`.
Karar ürün sahibinin: otomasyon ya durdurulmalı ya da `git add -A` yerine beyaz liste ile
çalışmalı. Ölçüldü, kesilmedi, bekliyor.

### ÜRÜN SAHİBİNE SORU — `BORC-SCRIPTS-01` (cevapsız silme YOK)

`ask_followup_question` aracı üç denemede de düştü; soru kanala sorulamadı, buraya yazıldı.
**Ölçüm bitti, kesme kararı sizde.** Ölçülen tablo:

| Yer | Ne | Sayı | Durum |
|---|---|---|---|
| `scripts/_*` | girdi | 41 | 29 `.py` **hepsi derlenir**, **0 çürük**, 1 dizin (`_arsiv`), 11 veri |
| `scripts/_*` | üretim çağıranı | **0** | tüm isabetler belge/rapor (D-270 uygulandı) |
| Kök | index hayaleti tek kullanımlık betik | **76** | diskte YOK, git index'inde VAR (check 42, run 16, debug 8, verify 6, clean 2, add 1, count 1) |
| Kök | bozuk-kabuk çöpü | 2 | `0)`, `{t.get('assignee')` — 0 bayt, D-221 ihlali |
| Ağaç | başka ajanların commit edilmemiş silmesi | 94 | utku/ihsan/yasu aktif — **dokunulmadı** |

Devir notunun dayandığı **"borcumuz kalsın" kararı kaynaksızdır**: bu defterde,
`AGENTS.md`'de ve `git log --all -i --grep="borcumuz"` içinde **yok**.

Üç seçenek:
1. **Borç kalsın** — ölçüm tablosu yeterli teslimdir, tavan (76/2) artmayı engeller.
2. **Yalnız çöpü kes** — 2 bozuk-kabuk dosyası silinir (D-221), gerisi durur.
3. **Hepsini kes** — 76 index hayaleti commit'lenir, `scripts/_*` tasfiye edilir.
   Dikkat: bu, başka ajanların açık işiyle aynı ağaçta olur.

Seçim yapılmadan **hiçbir silme yapılmadı**.

- **Kaldığım yer:** D-286 yazıldı. **Hash yazılmıyor:** bu satıra hash yazan commit hash'i
  değiştirir (sonsuz gerileme). Konum dalın tepesidir: alt depo `chore/monorepo-merge`,
  üst depo `master`; `git log --oneline -3` ile okunur.
- **TEŞHİS DÜZELTİLDİ (D-286):** D-281'in "D-273…D-280 D-227+D-272 ihlalidir" iddiası
  **yanlıştı**. Ürün sahibi bildirdi: o kayıtlar **emirle** yazıldı, ihlal değil, ajan
  suçlu değil. Ölçülen gerçek sapma: numara **iki ayrı dosyadan** tahsis ediliyordu ve
  D-227 mandalı çatışmayı **göremiyordu** (yalnız `AGENTS.md`'yi, yalnız `(D-NNN — KAH`
  biçimini tarıyordu). Çözüm: `python scripts/karar_no.py` — **tek havuz**.
  D-227'ye ürün sahibi istisnası eklendi: kayıt başka dosyada durabilir, **numaranın
  kaynağı** tektir.
- **Eşzamanlı ajan yarışı CANLI ve İKİ KEZ yaşandı:** kaydı önce `D-283` yazdım, yazarken
  başka ajan aynı numarayı deftere verdi → `D-284`'e taşıdım; tam takım koşusunda
  **ikinci kırmızı** geldi (`CATISMA: ['D-281','D-284']`), çünkü yasu deftere `## D-284`
  **ve** `## D-285` yazmıştı. **Ölçüm anlıktır, tahsis değildir.**
- **TAHSİS ARTIK ATOMİK (D-286):** `python scripts/karar_no.py --al` numarayı
  `data/karar_tahsis/D-NNN.txt` dosyasını `O_EXCL` ile açarak **kapatır**; dosya varsa bir
  sonrakine geçer. Kırılarak doğrulandı: ardışık iki tahsis `D-286` ve `D-287` verdi.
  Kayıt tahsisli **D-286**'ya taşındı (yasu'nun D-284/D-285'ine dokunulmadı), deney artığı
  `D-287.txt` düşürüldü. Düz `karar_no.py` yalnız **ölçer**, tahsis etmez.
- **Test tabanı yeni: 4555 passed, 12 skipped, 1 FAILED.** Sabit sıra (`-p no:randomly`)
  ve rastgele (`--randomly-seed=286`, 269.26s) **aynı** sonucu verdi → sıra bağımlılığı yok.
  4527 → 4555: +1 benim tahsis mandalım, +27 başka ajanların yeni testleri
  (yasu'nun `test_ostim_birlestirme_kalite.py` 18 test dahil).
- **AÇIK KIRMIZI — benim işim değil, düzeltilmedi:**
  `tests/test_dokuman_politikasi.py::test_d219_ajan_context_dosyalari` —
  `yasu_project_context.md` **213 satır**, D-219 tavanı **200**. Dosya yasu'nun açık işi
  (oturum sırasında düzenleniyordu); başka ajanın hafıza dosyasını kesmem D-219'un sahipliğini
  bozar. Çözüm sahibinde: eski oturum bloklarını `archive/yasu_context_<YYYYMM>.md`'ye taşı.
  Mandal doğru çalıştı — kusuru **ben yazmadım, mandal yakaladı**.
- **Yeni ayrım (D-281, ezberlenecek):** diskte yok + index'te yok = **rezervasyon** (meşru);
  diskte yok + index'te **var** = **index hayaleti** (commit edilmemiş silme). Kilit
  dosyasındaki `scripts/ajan_cakisma_kilidi.py` **hayalet değil**, ihsan'ın rezervasyonu.
- **KİLİT ARTIK ZORLANIYOR (D-286):** `scripts/kilit_zorla.py` + `scripts/hooks/pre-commit`.
  Gerçek commit denemesiyle **kırılarak** doğrulandı: kanca ateşledi, `DURDU` bastı,
  `git log` `6c52bdd`'de kaldı — commit olmadı. **Ölçülen tavan:** rezervasyon
  (ne diskte ne index'te) **stage edilemez**, bu yüzden commit anındaki zorlayıcı
  rezervasyonu asla yakalayamaz. Yalnız var olan dosyayı korur.
- **Kimlik:** `AJAN` env yok, `huginn.ajan` git config yok; tek kaynak `git config user.name`.
  Her ajan `git config huginn.ajan <ad>` kurarsa zorlayıcı kimliksiz halde de durur.
- **Ürün sahibi kararı bekliyor (taşıma YAPILMADI):** eşzamanlı ajan izolasyonu, D-272/7'deki
  üç seçenek. Önerim 1+2 (sıra düzeni + var olan kilidi zorlamak); ayrı worktree canlı
  veritabanını ayırmadığı için tek başına yetmez. **Canlı DB ölçümü:** üç ajan da aynı
  Supabase Postgres'e yazıyor (~80 betik + ~20 modül `get_engine` çağırıyor), göç kapısı tek.
- **Açık 4 borç, öncelik ürün sahibinde:** `BORC-VKN-01` (kaynak yok, MERSIS A/B kararına
  bağlı), `BORC-NACE-DOGRULAMA-01`, `BORC-SICIL-DAIRE-01` (§5 saklı karar),
  `BORC-SCRIPTS-01` (76 hayalet **donduruldu**, ürün sahibi kararı). `BORC-KARAR-NUMARA-01`
  **kapandı**.
- **Araç tuzağı:** çok satırlı `python -c` cmd.exe'de **sessizce hiçbir şey yapmaz** —
  çıktı yok, çıkış kodu 0. Tek satır `-c` veya gerçek dosya kullan; "komut geçti" ekranı
  kanıt değil (D-260). `ask_followup_question` bu turda **üç kez** kusurla düştü.
- **Bir sonraki turda ilk iş:** bu defteri oku, `AGENTS.md`'yi baştan tarama. Borcun son sözü
  **en yüksek D numarasında**dır, dosyadaki son satırda değil. Ve devir notunun her fiilini
  ölç: **beş turdur devir notunun adlandırdığı borç yanlış çıkıyor** (D-267/1 deseni).

## Ilgili Nodlar

- [[AGENTS]]
- [[docs/HEDEF_VERI_KAPSAMI]]

---

## D-273 — TOBB üyelik erişimi: düz HTTP kanıt almaz (2026-09-29)

**Gözlem (ölçüldü):** `httpx.get(".../goster.php?Guid=...")` → **HTTP 200** ama
**gövde boş**. Sebep: içerik JavaScript ile yükleniyor + oturum şart.

**Karar:** Düz HTTP ile tarama **YAPILMAZ**. Kanıt katmanı oturum üzerinden
alınır. Kanıt dosyası kendi verisiyle birlikte saklanır (D-216 uyum).

## D-274 — MERSİS: 17 hane mi 16 hane mi?

**Gözlem (ölçüldü):** Ekranda 17 haneli `0012032074100024`; ilk 10 hane
`0120320741` geçerli VKN. Kanonik biçim **16 hane** (`0120320741000024`);
baştaki sıfır bozukluk/alan hizası artığıdır.

**Karar:** Kaynak **kanonikleştirme** tabakasından geçer: 17 hane + başta `0`
ise ilk hane düşürülür. VKN doğrulaması **yalnız** `kimlik_no.py`
üzerinden yapılır (K-1: tek kapı). Alan boşsa `None` yazılır, tahmin edilmez.

## D-275 — VKN doğrulaması ikinci algoritma yazılmaz

`ticaret_sicili_kanit.py` ilk halinde **kendi VKN algoritmasını** yazıyor ve
gerçek VKN'leri reddediyordu (ikiz mantık riski). Bağlayıcı tek kapı:
`src/company_master/etl/kimlik_no.py::vkn_gecerli`.

**Karar:** İkinci uygulama yasak. Bkz. K-1.

## D-276 — TOBB girişi: `multipart/form-data` kök nedeni (2026-09-29)

**Gözlem (ölçüldü):** Doğru e-posta/şifre ile giriş yine başarısız, sunucu
tam olarak `0` dönüyor. Sayfa kaynağında form `enctype="multipart/form-data"`
ve JS `new FormData(this)` ile POST ediyor.

**Karar:** `httpx` `data=` yerine **`files=`** kullanılır
(`{"Alan": (None, deger)}`). Başarıda sunucu **tam olarak `"1"`** döner.
Doğrudan TOBB hesabı kullanılır — **e-Devlet sorgu geçmişi oluşmaz**.

**Yan ölçüm:** oturum ömrü **~2-3 dakika**; sunucu tek çerez veriyor
(`atrsrv-*`). Çerez diske yazılıp geri yükleniyor (`cookie_kaydet/yukle`).

## D-277 — "Tüm Ankara tek seferde" önerisi: ÖLÇÜLDÜ, MÜMKÜN DEĞİL

KAHİN'in önerisi canlı denendi:
`POST /view/hizlierisim/ilangoruntuleme_ok.php` + `SicilMudurluguId=18` +
tarih aralığı → sunucu **reddediyor**:
*"Sicil No veya En Az 5 Karakter Ticaret Unvanı Giriniz"*.

**Karar:** İl+tarih tek başına sonuç vermez. Gerçek toplu yol
`TicaretUnvani` (ölçüldü: `AKANA` → **71 ilan tek istekte**, sayfalama yok).
14.000 firma = 14.000 unvan/sicil sorgusu; "fırsat" değil, aynı yük.

## D-278 — OCR GEREKMEZ; TOBB abonelik verisi XML'dir (KAHİN düzeltmesi)

**Tetikleyici:** KAHİN "gövdeler XML/ham metin olarak iletilir, PDF'e gerek
yok" dedi. Benim önceki "PDF scan → OCR şart" kararım **gerekçesizdi**.

**Doğrulama (ölçüldü):** resmî Abonelik sayfasının tablosunda 3. sütun
**"HİZMET SUNUŞ ŞEKLİ"** ve üç seviyenin de hizmeti **"WEB SERVİS"**.

| Düzey | Aranabilirlik | 2026 | Birim |
|---|---|---|---|
| Düzey_1 | **Aranamaz (non-searchable)** PDF | 484.932 TL | 0,521 TL/ilan |
| Düzey_2 | Aranabilir | 951.792 TL | 1,023 TL/ilan |
| **Düzey_3** | **Aranabilir** | **1.427.688 TL** | **1,535 TL/ilan** |

**Kararlar:**
1. **OCR hattı pasife alındı, SİLİNMEDİ.** `OCR_ETKIN=False` +
   `OcrPasifHatasi` kapısı + `--aktif` / `--durum`. Kapalıyken **HTTP atılmaz**
   (`tests/test_gazete_ocr_pasif.py`). Yeniden lazım olabilir.
2. **Ayrım kanıta bağlandı:** *ücretsiz üye PDF'i* gerçekten scan (ölçüldü:
   `font=0`, `Tj=0`, `ToUnicode=0`, 3 görsel XObject, A4@200DPI) → o yol
   OCR'a muhtaç. *Abonelik verisi* ise makine-okunur → OCR gerektirmez.
3. **Düzey_3 alan listesi** projenin tam boşluklarını kapatıyor: NACE ana+alt,
   **Vergi No**, Vergi Dairesi, UAVT Adres Kodu, Ortaklar (sermaye dahil),
   Temsilciler, Amaç Konu, Müfterek Listesi (JSON).
4. **Yasal uyarı (sayfada yazılı):** *"Gazetede yayımlanan ilan metni esas
   kabul edilmeli."* Ham veri **kaynak değil, aday**; `IlanKaniti` kapısından
   geçmeden `company_master`'a girmez.
5. **Satın alma kararı KAHİN'inkidir** (1.427.688 TL). Öneri: önce
   **MERSİS merkezî** sorguyu değerlendir (ücretsiz olabilir).

**Genel ders:** kütüphane "boş döndü" dedi → **scan mı metin katmanı mı
ayırt edilmeden karar verilmez**; `scripts/pdf_kanit_analiz.py` ile ölçülür.
Kullanıcının alan bilgisi **reddedilmez, doğrulanır** — burada doğrulanınca
iki günlük OCR işi boşa çıktı.

## D-279 — Abonelik 1 aylık DEĞİLDİR, ama KAPSAM TESPİTİ DOĞRU (KAHİN itirazı)

**KAHİN'in itirazı:** *"1 aylık ücret ödemekle firma bilgilerini tam toplanmaz;
ücret sadece o ayın şirket bilgilerini gösterir, açılış kapanış vs; aradığımız
veri orada değil."*

İki ayrı iddia var; ikisi de ölçüldü.

### 1. "1 aylık" → **YANLIŞ** (sayfada yazılı)

| Kanıt | Alıntı |
|---|---|
| Süre | **"(Yıllık)"** — üç seviyenin de satırında |
| Hesap | *"2026 yılında **251 iş günü** vardır. (251 x 1.932) = 484.932 TL"* |
| Günlük ayrı ürün | *"2026 yılı bir günlük gazete ücreti **2.730 ₺**"* |

→ Abonelik **yıllık**, 251 iş gününün tamamı. Aylık değil.

### 2. "Sadece o dönemin verisi / aradığımız veri orada değil" → **DOĞRU**

Empirik ölçüm — `448217` (AKANA) üzerinde **4 ilan** bulundu:

| Yayın yılı | İlan türü |
|---|---|
| 2026 | ŞUBE (ADRES DEĞİŞİKLİĞİ) |
| 2026 | ŞUBE (YÖNETİM - TEMSİL) |
| **2025** | ŞUBE (YÖNETİM - TEMSİL) |
| **2020** | ŞUBE AÇILIŞ |

> **2026 aboneliği bu 4 ilanın yalnızca 2'sini kapsar → %50.**
> Geçmiş yıllar ayrı alınır; "fihrist" ilan türlerini içerir, **firma
> sicil kaydının tamamını değil**.

Kanıt: `scripts/abonelik_kapsam_olcer.py` → `data/kesif_abonelik_kapsam.json`

### Karar

1. **TOBB aboneliği 14.000 firmanın TAM sicil verisini vermez.** Kullanıcının
   çekincesi ölçümle doğrulandı. 1.427.688 TL **bu iş için harcanmaz.**
2. **Düzey_3'ün gerçek değeri:** *zaman-serisi*. Tek bir firmanın yıllar boyu
   tüm ilan hareketi (kuruluş, adres, temsilci, sermaye) → **büyüme/çöküş
   sinyali**. 14.000 firma × 1 anlık görüntü değil, **birden çok yılın
   farkı**. Sektör analizi ve OSINT zenginliği için değerlidir — ama
   "firma master verisi" işini **çözmez.**
3. **Firma master verisi (adres, ortak, temsilci, VKN, NACE) MERSİS veya
   Ticaret Sicili Müdürlüklerinden gelir.** TOBB = türetilmiş/ikincil kaynak.
4. **D-278'in satın alma önerisi GERİ ÇEKİLDİ.** Düzey_3 alınmayacak.

> **Net sonuç:** TOBB kanıt katmanı **tekil doğrulama + değişim tespiti** için
> kalır (ücretsiz, kanıtlı). 14.000'lik ana veri → **MERSİS merkezî**.

## D-280 — OCR "daha ucuz" DEĞİLDİR; erişim ve doğruluk darboğaz (KAHİN)

**KAHİN'in yönlendirmesi:** *"Düzey_3 (1.427.688 TL) OCR ile taramak daha ucuz...
abonelik sonraki süreçte yapılabilir."* → Doğru yön, **gerekçesi ölçüldü ve
kısmen çürütüldü.** Tahmin yapılmadı: `scripts/ocr_maliyet_olcer.py` çalıştırıldı
(7 model denendi, 1 sayfa canlı).

### 1. Erişim: 7 modelden **1'i** çalışıyor

| Model | Sonuç |
|---|---|
| `openai/gpt-4o-mini` | ✅ **TAMAM** |
| `gc/gemini-2.5-flash-lite` | ❌ 403 (yetki yok) |
| `bzl/gemini-3.1-pro-preview` | ❌ 402 (kredi yok) |
| `cl/openai/gpt-4o` | ❌ 402 (kredi yok) |
| `ag/gemini-3.5-flash-low` | ❌ boş cevap |
| `ag/gemini-3.6-flash-low` | ❌ boş cevap |
| `gemini/gemini-3.5-flash-lite` | ❌ boş cevap |

→ **Erişim tek darboğaz.** Yedek model havuzu yok; 1 sağlayıcı çökerse hatt durur.

### 2. D-280 KÖK NEDEN (yeni bulgu): cevap ayrıştırma hatası

`openai/gpt-4o-mini` **HTTP 200** döndü ama `r.json()` patladı:
`JSONDecodeError: Extra data: line 37`. Gövdenin sonu: `data: [DONE]`
— **SSE kalıntısı JSON'a eklenmiş**. Model cevabı **geçerliydi**, ayrıştırma
başarısızdı.

**Çözüm:** `_cevap_ayikla()` — önce `r.json()`, hata olursa `data:` kalıntısı
kesilip elle ayrıştırılır.

> Ders: "OCR çalışmıyor" sandım; aslında **istemci hatalıydı**.

### 3. Ölçülen maliyet ve süre (tek sayfa, gerçek)

| Ölçüm | Değer |
|---|---|
| Model | `openai/gpt-4o-mini` |
| Süre | **5,89 sn** |
| Token | **49.146** |
| Çıkarılan alan | 9 |

**Projeksiyon (ölçümden türetildi, varsayım yok):**

| Kapsam | Token | Süre |
|---|---|---|
| 14.000 firma | 688 milyon | **~23 saat** |
| 930.000 ilan (tam yıl) | 45,7 milyar | **~63 gün** |

> **D-280 KARARI:** "OCR daha ucuz" **DOĞRULANMADI.** Düzey_3 (yıllık
> 1.427.688 TL) karşısında OCR'ın avantajı **belirsiz**: 14.000 ölçekte
> makul, 930.000'lik tam yıllık kapsamda **63 gün** sürer.

### 4. Doğruluk: OCR **MERSİS'te hata yaptı** (kritik)

| | Değer | Hane |
|---|---|---|
| Ekrandaki gerçek | `0012032074100024` | 17 |
| OCR çıktısı | `001203074100024` | **15** |

`2074` → `0741`: **kayıp hane.** Yani OCR **sessizce bozuk** veri üretti.

**D-274 kanonik kapısı bunu YAKALADI:** 15 hane → `mersis_kanonik_16 = None`
(reddedildi), 17 hane → kanonikleştirildi. *Kanonik kapı olmasaydı bu bozuk
değer `company_master`'a girerdi.*

### 5. Karar

1. **OCR tek başına 14.000 ölçekte denenebilir** (~23 saat, erişim çalışırken)
   — ama **çıktı zorunlu olarak kanonik kapıdan geçmeli** (D-274).
2. **930.000'lik tam yıl kapsamı OCR ile pratik DEĞİLDİR** (63 gün + tek
   sağlayıcı riski) → ileride abonelik buysa **Düzey_3 makul**.
3. **Abonelik kararı KAHİN'inkidir; bu ölçüm kararın girdisidir.** Şimdilik
   alınmaz — kabul edildi.
4. **OCR hattı PASIF kalır** (D-278). Maliyet ölçümü `--aktif` ile yapıldı.

> **Genel ders:** "X daha ucuz" iddiası, **ölçülmeden kabul edilmez.**
> Buradaki gerçek darboğaz fiyat değil, **erişim ve doğruluk** oldu.

## D-281 — e-Devletsiz kaynak araştırması: OSTİM = 8.473 firma, ücretsiz, yasal

**Soru:** e-Devlet kullanmadan 14.000 firmanın verisi toplanabilir mi?
**Yöntem:** Tahmin değil, ölçüm. `scripts/osb_kaynak_olcer.py`,
`osb_veri_yapisi_olcer.py`, `osb_api_avla.py`, `ostim_detay_olcer.py` (canlı).

### 1. MERSİS ve Bakanlık hizmetleri → **e-Devlet zorunlu** (ölçüldü)

| Kaynak | Bulgu |
|---|---|
| `mersis.gtb.gov.tr` / `mersis.ticaret.gov.tr` | *"E-Devlet Yönetimi ile Giriş entegrasyon aşamasındadır"* |
| `turkiye.gov.tr/gtb-ticari-isletme-ve-sirket-sorgulama` | Giriş: e-Devlet şifresi / e-İmza / TCKK / İnternet bankacılığı |
| `ticaret.gov.tr/…/e-devlet-hizmetlerimiz` | "Ticari İşletme ve Şirket Sorgulama" **e-Devlet** altında |

> **Sonuç:** e-Devletsiz **resmî merkezî** yol **yoktur**. D-279'daki
> "MERSİS merkezî" önerisi bu nedenle **e-Devlet'e bağımlı** çıktı.

### 2. Alternatif kaynaklar → **8/8 erişilebilir** (ölçüldü)

`ostim.org.tr` (200) · `atonet.org.tr` (200) · `atb.org.tr` (200) ·
`aso.org.tr` (200) · `gib.gov.tr` (200) · `ticaret.gov.tr` (200)

**Yasal kapı açık** (`robots.txt` ölçüldü):
- `ostim.org.tr` → yalnız `/admin/`, `/portal/`, `/auth/` yasak
- `atb.org.tr` → `Allow:` (tümü serbest) · `aso.org.tr`, `atonet.org.tr` → engel yok

→ `/firmalar` taraması **robots.txt'e aykırı DEĞİLDİR.**

### 3. ⭐ OSTİM: 8.473 firma, sayfalama ile TAM toplanabilir

Sayfa metninde **ölçüldü**: `Toplam 8473 sonuç bulundu`

| Ölçüm | Değer |
|---|---|
| Toplam firma | **8.473** (sayfada yazılı) |
| Sayfa başına | 300 |
| Sayfa sayısı | **29** |
| Doğrulama | sayfa 1+2+29 → 300+300+**73** = 673 ✓ (son sayfa 73) |
| Sayfa 30 | 0 sonuç → sınır doğru |

> **8.473 = 14.000 hedefinin %61'i, ücretsiz, yasal, kalıcı adresli.**

### 4. Alan eksikliği — OSTİM tek başına YETMEZ (ölçüldü)

Detay sayfası alan taraması (**11 alan denendi, 6 bulundu**):

| Alan | Durum |
|---|---|
| unvan · adres · telefon · e-posta · web · faaliyet · sektör | ✅ |
| **NACE** · **VKN** · **ticaret sicil no** · yetkili/ortak | ❌ **YOK** |

> **Karar:** OSTİM = **kimlik + iletişim** kaynağı (VKN olmadan join
> kurulamaz). Eksik alanlar **GIB VKN** ve **Ticaret Sicili** ile
> tamamlanmalı. OSTİM tek başına master veri **DEĞİLDİR** (D-216).

### 5. Karar

1. **MERSİS önerisi D-281 ile düzeltildi:** e-Devlet zorunlu → kullanıcının
   istemediği yol. **Ana kaynak olarak düşüldü.**
2. **OSTİM 8.473 firma** → ücretsiz temel küme olarak alınabilir
   (izinli, kalıcı adresli, sayfalama ölçülmüş).
3. **Entegrasyon zorunlu:** OSTİM (unvan/adres) → **GIB VKN** →
   **Ticaret Sicili/MERSİS**. Her biri kendi kapısından geçer.
4. **Bu bir araştırma turudur; toplu indirme BAŞLATILMADI.** Ölçek işi için
   ayrı görev + KAHİN onayı gerekir (bir önceki borçta açık kalan madde).
5. **VATAN/Hukuk onayı:** ticari amaçlı toplu derleme için kaynak kurumların
   kullanım şartları ayrıca doğrulanmalıdır. `robots.txt` izni hukuki
   izin **değildir.**

> **Genel ders:** "e-Devlet gerekir" önyargısı ölçümle çürütüldü; resmî
> merkezî yol kapandı ama **8.473 firma ücretsiz ve yasal** bulundu.

## D-282 — Hukuk + VKN araştırması: iki ÖNEMLİ bulgu (KAHİN)

KAHİN iki konuyu birden istedi: (1) hukuki uygunluk, (2) GİB VKN yolu.
İkisi de **ölçüldü**. Birincisi **kritik engel**, ikincisi **zaten yapılmış iş**.

### 1. ⛔ OSTİM Kullanım Koşulu — ticari kullanımı açıkça yasaklıyor

**Alıntı** (`ostim.org.tr/kurumsal/gizlilik-politikasi` → "Kullanım Koşulları"):
> *"Bu web sitesi sadece **bilgi amaçlı ve ticari olmayan** kullanım için
> hazırlanmıştır."*

Aynı politikanın diğer hükümleri:

| Hüküm | Alıntı |
|---|---|
| Üçüncü tarafa aktarım | *"elde edilen veriler belirlenen amaçlar ve kapsam dışında **üçüncü kişilere açıklanmayacaktır**"* |
| Ziyaretçi verisi | *"ziyaretçilerin kişisel verilerini **toplamaz** ve herhangi bir üçüncü tarafa **vermez**"* |
| Gerekçe | *"gizli bilginin tamamının veya herhangi bir kısmının **kamu alanına girmesini**… engellemek için tüm tedbirleri alma"* |

> **D-282 KARARI:** OSTİM 8.473 firma listesi **ticari amaçlı ürün verisi
> olarak kullanılamaz.** D-281'deki "8.473 ücretsiz ve yasal" ifadesi
> **DÜZELTİLDİ**: teknik olarak erişilebilir, ama **ticari kullanım
> koşulu bunu yasaklıyor.**
>
> Bu, 14.000'lık hedef için ciddi darboğazdır. Karar **KAHİN'in.**

### 2. ✅ GİB VKN yolu: e-Devlet zorunlu

| Kaynak | Bulgu |
|---|---|
| `turkiye.gov.tr/gib-intvrg-vergi-kimlik-numarasi-sorgulama` | e-Devlet şifresi / e-İmza / TCKK / bankacılık |
| `gib.gov.tr/…/vergi-kimlik-numarasi-sorgulama` | HTTP 200 ama **içerik boş** (JS-rendered) |
| `gib.gov.tr/e-hizmetler`, `/acik-veri` | **404** — yayımlanmıyor |
| `gib.gov.tr/…/VERI_PAYLASIMI.pdf` | **404** |

> Projenin kendi notu (`vkn_bulma_stratejisi.md` §7) bunu zaten yazmıştı:
> *"GİB VKN Doğrulama (vkn.gov.tr) — sorgu servisi **captcha/bot korumalı**;
> tekil doğrulama için uygun, **toplu kazımaya uygun değil**."*
> Ölçüm bunu **doğruladı**. GİB'de e-Devletsiz toplu yol **yok**.

### 3. ⭐ En önemli bulgu: VKN işi **zaten denenmiş ve başarısız olmuş**

Projede mevcut çıktı ölçüldü — `data/ostim/firmalar_vkn_ekli.jsonl`:

| Ölçüm | Değer |
|---|---|
| Toplam kayıt | **5.040** |
| unvan · adres · sektor · slug | **%100** |
| telefon | %92 · e-posta %48 · web %100 |
| **`vergi_no`** | **%0 — 5.040/5.040 boş** |

**Neden başarısız olduğu loglarda yazılı** (`logs/vkn_extractor_v2.log`):
> `İşlenen: 5485/5485, **VKN bulundu: 3**, Atlanan placeholder: **2.646**,
> Çekim hatası: 774`

> Yani 5.485 denemenin **5.482'si (%99,9) sonuç vermedi.**
> Web kazıması da (`vkn_web_run2.log`): *"Taranan site: 30, **VKN bulunan: 0**"*.

**Kök neden (yeni):** OSTİM detay sayfası **VKN'yi hiç yayımlamıyor**
(ölçüldü: 11 alan denendi, `vergi_no` **yok** — D-281). Yani web kazıması
hedefi **kaynağın vermediği** bir alandaydı.

### 4. Bağımlılık tuzağı (D-282 kuralı)

`data/ostim/firmalar_vkn_ekli.jsonl` 5.040 satır, `web_sitesi` %100 dolu —
ancak bunlar **OSTİM'ın kendi listelediği** alanlar. Proje kaydı bunları
"kaynak" sanıyor. Oysa:
- OSTİM → unvan/adres/telefon/e-posta (VKN **yok**)
- Web → site var ama içinde VKN çıkmadı (%0)
- GİB → e-Devlet

> **Sonuç: VKN eksikliği OSTİM kaynaklı DEĞİLDİR; proje içi bir
> varsayımdan kaynaklanmıştır.** Yeniden denemek aynı sonucu verir.

### 5. Karar tablosu

| Alan | Durum |
|---|---|
| OSTİM 8.473 (ticari) | ⛔ **Koşulla yasak** (D-282 §1) |
| GİB VKN e-Devletsiz | ❌ **Yok** (ölçüldü) |
| Web kazıması VKN | ❌ **Zaten denendi: %0** |
| MERSİS | ❌ e-Devlet |
| TOBB Düzey_3 | ❌ Kapsam yetersiz (D-279) |

> **Açık kalan tek yasal yol: e-Devlet (KAHİN'in önceki tercihi) veya
> OSTİM'den resmî yazılı izin.** Her ikisi de KAHİN'in kararıdır.

> **Genel ders:** "VKN web'den bulunur" varsayımı **3 kez ölçüldü** ve
> 3'ünde de başarısız çıktı. Var olmayan alanı kazımak boşa çalışmaktır;
> **önce kaynağın alanı var mı diye bak.**

## D-283 — Veri çekme politikası + KIYASLAMA cevabı (KAHİN onayı)

> KAHİN: *"veriyi ticari kullanılacak şekilde çek, kolon kolon, tane tane,
> doluluk oranları ile referansla, kolonları karıştırma. Politikamız var,
> listeyi yap. Sonra ihsan'a gönder."*

### 1. Kaynak adresleri (ölçülmüş)

| # | Adres | Doğrulama |
|---|---|---|
| 1 | `https://ostim.org.tr/firmalar` | `Toplam 8473 sonuç` |
| 2 | `https://ostim.org.tr/firmalar?page=N` | 300+300+73 ✓, sayfa 30 boş |
| 3 | `https://ostim.org.tr/firmalar/<slug>` | HTTP 200, 78.554 bayt |
| 4 | `https://ostim.org.tr/sitemap.xml` | 10 URL — **firmaları içermez** |
| 5 | `https://ostim.org.tr/robots.txt` | `/admin/`, `/portal/`, `/auth/` yasak |

### 2. Çekme politikası P-1..P-10 (KAHİN onayladı: 2026-09-29)

| # | Kural | Uygulama | Dayanak |
|---|---|---|---|
| P-1 | Sahte UA yok | Sabit gerçek UA | politika |
| P-2 | Sayfa başına 1 istek | 1 liste + 1 detay | ölçüm |
| P-3 | Nazik gecikme | **2 sn** | nazik kazıma |
| P-4 | Gece vardiyası yok | 3.297 firma ≈ **1,8 saat** | hesap |
| P-5 | 403/401 = **açık hata** | boş liste sayılmaz | **K-5** |
| P-6 | `tekil/toplam < %95` → **başarısız** | tur reddi | **K-4** |
| P-7 | Ham dosya `"w"` | kopyalamaz | **K-3** |
| P-8 | Sayfa imzası tekrarında dur | 3 koruma | **K-1** |
| P-9 | Yeniden çalıştırılabilir | durum dosyası | **K-1** |
| P-10 | Maskeli alan kopyalanmaz | KVKK | — |

### 3. Filtreleme — kolonlar KARIŞTIRILMAZ (K-2)

| Kolon | Kural |
|---|---|
| `unvan` | Asla normalize/kısaltma edilmez (D-11) |
| `adres`·`telefon`·`emailler` | **Yalnız OSTİM detay sayfasından** |
| `nace_code` | `nace_source` ile birlikte; tahmin ≠ resmi |
| `nace_confidence` | high=resmi · medium=türetilmiş · none=yok |
| `vergi_no` | Yalnız doğrulanmış; tahmin yasak (D-274) |
| `kaynak_adi` / `kaynak_turu` | `ostim` / `osb` (K-2 zorunlu kolon) |

> **Ölçülen K-2 riski:** `firmalar_full.jsonl` NACE'leri **4 haneli ve
> `sektor_reverse`** (türetilmiş tahmin) — 7.047 kayıt. ASO'nun resmi 6
> haneli NACE'i ile **aynı güvenle karıştırılmamalı.**

### 4. ⭐ KIYASLAMA CEVABI (KAHİN'in asıl sorusu)

`scripts/veri_karsilastir.py` → `data/karsilastirma_raporu.json`

| Set | Kayıt | adres | web | sosyal | sektor | NACE |
|---|---|---|---|---|---|---|
| `firmalar_full` | 8.313 | ⛔ %0 | ⛔ %0 | ⛔ %0 | %69,4 | %84,8 (4 hane, türetilmiş) |
| `firmalar_vkn_ekli` | 5.040 | ✅ %100 | ✅ %100 | ✅ %100 | ✅ %100 | — |

| Ölçüm | Değer |
|---|---|
| Ortak unvan | 4.954 (%60,0) |
| **`b` ile yeni unvan** | **0** |
| `a` ile kalan (detaysız) | **3.297** |

**Zenginleştirme katkısı** (eşleşen 4.954): `adres` +4.952 · `web_sitesi`
+4.952 · `sosyal_medya` +4.952 · `sektor` +1.398 · `vergi_no` **0**

> **CEVAP: EVET zenginleştirir** — ama **3 kolonda**, ve yeni firma
> getirmez. Asıl kazanç: **3.297 firmanın adres/web/sosyal medya alanı.**
> `vergi_no` sorunu çözülmez (D-282: hiçbir kaynakta yok).

**KAHİN ONAYI (2026-09-29):** Politika P-1..P-10 uygulanacak; 3.297 eksik
detay taranacak; ardından ihsan'a teslim.

## D-284 — Organize hareket + izin dilekcesi + birlestirme (D-283 devam)

KAHİN: *"ihsan ajanı ile organize hareket edin… problem varsa ihsan
ajanına chat'ten yaz, bekliyorum."*

### 1. İhsan'a yazıldı (ajan chat D-210 — zorunlu kanal)

`data/orchestrator/ajan-chat.jsonl` → **3 kayıt** bu görevde:

| Önem | Konu |
|---|---|
| kritik | OSTIM detay sayfası **K-2 ihlali** (kolon karışması) + düzeltme |
| yuksek | **Kıyaslama sonucu** (zenginleşme ölçümü) |
| yuksek | **Görüşme talebi** (2 karar: izin adımı + birlestirme sahipliği) |

Ayrıca `chat_gonder.py` ile **2 mesaj** (`data/orchestrator/chat/messages.jsonl`).

### 2. ⛔ K-2 İHLALİ — tarama sırasında yakalandı ve düzeltildi

KAHİN'in uyarısı üzerine kolonlar tek tek denetlendi. İlk pilot çıktısı
**kullanılamazdı**:

| Kolon | Çıkan (YANLIŞ) | Neden |
|---|---|---|
| `web_sitesi` | `htk.org.tr` | fuar sitesi, firma değil |
| `sosyal_medya` | `ostim-osb` | **sitenin kendi** sosyal hesabı |
| `adres` | boş | etiket `<strong>` ile geliyordu |

**Kök neden:** Sayfada iki ayrı blok var — (1) firma bilgi kutuları,
(2) site menüleri/footer. İlk sürüm bunları **ayırmıyordu**.

**Düzeltme:** `_bilgi_kutulari()` yalnız
`<p bg-secondary fw-bold>Başlık</p><div bg-light>…</div>` kutularını okur;
anahtar `bölüm:etiket` olur (`Merkez:Telefon`).

**Doğrulama (gerçek çıktı):**
```
Merkez:Telefon → +90 552 005 29 35
Merkez:Adres   → AHIT EVRAN CAD. 63
Merkez:E-Posta → mehmetcantugay1@gmail.com
```
Pilot: **5/5 başarılı**, P-6 tekil oranı **%100**, 0 hata.

### 3. İzin dilekçesi taslağı hazırlandı

`scripts/ostim_izin_dilekcesi.py` → `plans/OSTIM-izin-dilekcesi-taslagi.md`
(2.606 karakter). Kapsam dışı bırakılanlar **yazılı**: VKN, ortak, temsilci
kimlik bilgisi, mali tablo. Teknik taahhütler: robots.txt, 2 sn bekleme,
sahte UA yok, günlük limit.

> **Gönderimi KAHİN yapar** (resmî yanıt kurumun adına yazılmalı).

### 4. Birlestirme hazır (kuru çalışma ölçüldü)

`scripts/ostim_set_birlestir.py --kuru`:

| Ölçüm | Değer |
|---|---|
| liste | 8.313 |
| detay | 5.045 |
| **çıkış** | **8.313** (artış yok — doğru) |
| unvan eşleşmesi | 5.002 |

**Doldurulan alanlar:** `web_sitesi` +5.000 · `sosyal_medya` +5.000 ·
`adres` +4.997 · `sektor` +1.410 · `emailler` +9 · `telefonler` +2

**Doluluk değişimi:**

| Kolon | Önce | Sonra |
|---|---|---|
| **adres** | %0,0 | ✅ **%60,1** |
| **web_sitesi** | %0,0 | ✅ **%60,1** |
| **sosyal_medya** | %0,0 | ✅ **%60,1** |
| sektor | %69,4 | ✅ %86,4 |
| `vergi_no` | %0,0 | %0,0 (değişmedi — kaynak yok) |

**K-2 uyum ölçüldü:** `kaynak_adi` + `kaynak_turu` her kayıtta ✓ ·
`vergi_no` yalnız doğrulanmış ✓ · NACE tahmini `nace_source` ile işaretli ✓

### 5. Karar

1. **Birlestirme kodu hazır ve kuru çalışmada doğrulandı** — dosyaya
   yazılmadı (`--kuru`), çünkü ihsan'ın yönlendirmesi bekleniyor.
2. **Detay taraması** (3.297) izin sonrası başlayacak.
3. **ihsan'dan beklenen:** (a) izin adımının sahibi, (b) birlestirme
   sorumluluğu.
## D-285 — OSTİM birleştirmesi kalite denetimi: kirp ölçüldü, 10.002 → 0

**Tarih:** 2026-09-29 · **Ajan:** yasu · **Görev:** ALTYAPI-TICARET-KANIT-01

### 1. Bağlam

D-283'te parser düzeltmesi sonrası "site/footer verileri firma kolonlarına
karışmış" uyarısı vardı ama **ölçülmemişti**. D-285 bu iddiayı ölçer ve
kanıtlanan kısımları düzeltir.

### 2. Karar

1. **Birleştirme çıktısı kalite denetiminden geçmeden teslim edilemez.**
   Araç: `scripts/birlestirme_kalite_kontrol.py` · Rapor:
   `data/birlestirme_kalite_raporu.json`.
2. **"Aynı değer binlerce firmada" ölçümü zorunlu kuraldır.** Tekil oranı
   %50'nin altına düşen kolon kirp sayılır ve teslim edilmez.
3. **Filtre listeleri tahminle değil ÖLÇÜMLE yazılır.** Ölçüm bir
   domain'de/numarada tekrar göstermiyorsa liste **boş bırakılır** —
   doğru veriyi silmemek, kirli veriyi tutmaktan önce gelir.
4. **Dolgu metni alan bazlı uygulanır.** `-` ve `n/a` yalnız serbest metin
   alanlarında geçersizdir; URL ve telefon alanlarında aranmaz.
5. **Birlestirme temizdir** (K-2 kaçış = 0). Detay taraması yazılı izin
   olmadan başlatılmaz (D-281 borcu).

### 3. Ölçülen bulgular

| # | Kolon | Kirp | Adet |
|---|-------|------|------|
| 1 | `sosyal_medya` | OSTİM'in kendi hesapları (`OstimOSB`, `ostim-osb`, `x.com/ostimosb`) | **5.000** |
| 2 | `web_sitesi` | `isim.org.tr` (OSB altyapısı) | **2.155** |
| 3 | `web_sitesi` | `ostimistihdam.com` (iş başvuru portalı) | **475** |
| 4 | `web_sitesi` | `htk.org.tr` (fuar/organizasyon domain'i) | 2 |
| 5 | `adres` | `"Adres bilgisi girilmemistir"` dolgu metni | 87 |

**Toplam K-2 kaçışı: 10.002 → 0.**
Web tekillleşme oranı: **%46,7 → %97,7.**

### 4. Telefon taraması — boş sonuç dürüstçe kaydedildi

Varsayım: "OSTİM merkez telefonu her firmada tekrar ediyor" → sabit numara
listesi yazıldı. **Ölçüm bunu çürüttü:** en çok tekrar eden numara 5 kez
(`903124397800`). Yani merkez numara veriye *bulaşmamış*. Liste
`frozenset()` olarak **boş bırakıldı**; tahminle iyi telefon numaraları
silinmedi. Regresyon testi buna karşı koruma içerir.

### 5. Regresyon testi iki gerçek hatayı yakaladı

## D-289 — İzin taslağı hazır; kazıyıcı politikaya uyduruldu

**Tarih:** 2026-09-29 · **Ajan:** yasu · **Görev:** ALTYAPI-TICARET-KANIT-01
**KAHİN kararı:** izin başvurusunun sahibi **KAHİN**; yasu izinli olarak
devam edecek.

### 1. Dilekçe — iki hata düzeltildi

`plans/OSTIM-izin-dilekcesi-taslagi.md` yeniden üretildi
(`scripts/ostim_izin_dilekcesi.py`).

1. **Yanlış kanıt dosyası atfı.** Eski taslak
   `data/ostim_kaynak_olcumu.json` dosyasına atıf yapıyordu; **dosya
   yoktu**. Yerine gerçekten var olan kanıtlar yazıldı.
2. **8.473 iddiası ölçümle çelişiyordu.** Site "Toplam 8473 sonuç"
   diyor, elimizdeki liste 8.313 (8.313 benzersiz slug, tekrar yok).
   Fark **ölçüldü**: liste 28-29. sayfalarında 13 yeni firma var —
   liste tarama sırasında güncellenmiş. Dilekçe artık iki sayıyı da
   ayrı ayrı veriyor ve farkın kaynağını belirtiyor.
   Kanıt: `data/ostim/kapsam_dogrulama.json`.

Ayrıca politika metni **canlı olarak yeniden okundu**; dosyadaki kopya
bozuktu (HTML entity kaçışları çözülmemiş: `G├╝ZL├╝L├╝K`). Birebir
alıntı: *"Bu web sitesi sadece bilgi amaçlı olarak ticari olmayan kullanım
için hazırlanmıştır"*. `robots.txt` birebir doğrulandı (`/firmalar/`
**serbest**).

### 2. Kazıyıcı — 4 politika maddesi kodda DEĞİLDİ

D-283'te yazılan politika P-1..P-10'un dördü hiç uygulanmamıştı:

| Politika | Durum | Düzeltme |
|---|---|---|
| P-3 2 sn gecikme | `time.sleep` **hiç çağrılmamıştı** (beyaz satır) | `if i > 1: time.sleep(GECIKME)` |
| P-8 sayfa imzası | fonksiyon yoktu | `imza()` + tekrarında kayıt **atlanır** |
| P-1/P-2 robots.txt | `robots_kontrol` parametresi **hiç tanımlı değildi** | `robots_uyumlu_mu()`, varsayılan **açık** |
| P-9 güvenli resume | dosya `"w"` ile **yeniden yazılıyordu** | mevcut kayıtlar okunur, slug ile birleştirilir |

P-9 bulgusu en ciddisiydi: 3.297 kayıt `--limit 500` ile 7 parçaya
bölünseydi, **her parçada önceki 6 parçanın verisi silinirdi**.

### 3. Pilot — "5/5" yetmezdi, satır denetimi gerekti

İlk pilot K-2 açısından temizdi (0/5 kirp) ama sosyal medyada
`{"instagram": "accounts"}` vardı. Bu bir hesap değil, sayfadaki geçici
login linkinin (`/accounts/login/?next=`) son parçasıydı.

**Ders: regex doğru olsa bile sahte hesap üretebilir.** `_gercek_hesap_mi()`
eklendi; düzeltilmiş parser ile pilot tekrar koşuldu:

- 5/5 başarılı, 0 hata, P-3 uygulandı (11,1 sn = 2 sn × 5)
- `accounts` sahtesi **gitti**, gerçek `333Reklam` hesapları **korundu**
- K-2 kaçış **0/5**

### 4. Doğrulama

```bash
python -m pytest tests/test_ostim_detay_parser.py -q        # 17/17
python -m pytest tests/test_ostim_birlestirme_kalite.py -q  # 18/18
python -m pytest tests/test_ostim_detay_parser.py \
  tests/test_ostim_birlestirme_kalite.py -q                # 35/35
```

### 5. Karar

1. **Detay taraması izin gelene kadar başlatılmaz.** (D-281 borcu)
   > **KAHİN kararı (2026-09-29): "izin olayı EN SON PLAN."**
   > Yazılı izin süreci **ertelendi** — en son iş kalemi. Tarama zaten
   > tamamlandı; bu madde artık **verinin kullanımı** içindir:
   > `OSTIM_TEMIZ.jsonl` üründe **yayımlanmayacak** ve üçüncü taraflara
   > dağıtılmayacak, izin gelene kadar.
2. İzin geldiğinde hattın tümü hazırdır: P-1..P-10 uygulanmış, 35 test
   yeşil, kalite denetimi mevcut.
3. Eksik detay sayısı 3.297 değil **3.339** — liste güncellendiği için
   arttı (D-286 ölçümü).

### 6. Güvenlik borcu — KAPATILDI (KAHİN, 2026-09-29)

- ~~TOBB parolası değiştirilmeli~~ → **KAHİN kararıyla kapatıldı**
- `data/tobb_cookie.json` canlı oturum çerezidir; paylaşılmaz


1. `_DOLGU_METIN` içindeki `-` **her alanda** aranıyordu. `sosyal_medya`
   bir dict olduğu için `str(dict)` üzerinde arama yapılıyor ve URL'li
   **her** hesap reddediliyordu — düzeltme, kirp veriyi temizlerken iyi
   veriyi de siliyordu. Alan bazlı düzeltme yapıldı (`_METIN_ALAN`).
2. `tests/test_ostim_detay_parser.py` fixture'ı gerçek sayfa yapısını
   yansıtmıyordu; parser'ın doğru olduğu ortaya çıktı.

### 6. Teslim edilen çıktı

- 8.313 kayıt, 8.275 tekil unvan, 19 kolon
- `kaynak_adi` / `kaynak_turu` %100 dolu
- NACE güven: `medium` 7.047 / `none` 1.266 — OSTİM resmî NACE
  yayımlamaz, sektörden türetilir (K-2)
- `vergi_no` 0 dolu — OSTİM'de VKN yoktur; bu kaynakla zenginleştirilemez

### 7. Ölçüm aracı

```bash
python scripts/birlestirme_kalite_kontrol.py   # statik denetim
python -m pytest tests/test_ostim_birlestirme_kalite.py -q   # 18/18
```



## D-290 — Tarama koruma duvarı: izole çıktı + kaynak kilidi

**KAHİN talebi (2026-09-29):** "eski database tekrar kirli ve hatalı
olmasını istemiyorum, her türlü önlemi al." Görev:
`VERI-OSTIM-TAM-TARAMA-01` (P1, yasu).

### 1. Karar

1. **Çıktı izole klasöredir.** `data/ostim/tamamlama_2026-09-29/`.
   Mevcut hiçbir dosyaya dokunulmaz — yeni kayıt eski verinin
   **üzerine yazılmaz**.
2. **Kaynak dosyalar SHA-256 kilitlidir.** Değişmişse tur **durdurulur**
   (`koruma_kontrolu()`). Bozma testi yapıldı: dosya bozulunca
   `"KAYNAK DOSYALAR DEĞİŞMİŞ"` çıktı, geri alınınca serbest bıraktı.
3. **Tarama SQLite'a dokunmaz** (ölçüldü: 0 `sqlite`/`INSERT` referansı).
   `companies` tablosu 8.313 → **8.313** değişmedi.
4. **Onay olmadan `companies`'a hiçbir şey yazılmaz.**

### 2. Ölçülen sonuç (ilk 1.000 kayıt)

- 1.000 işlendi · **0 hata** · 0 P-8 imza tekrarı · 0 K-2 kaçışı
- Tempo **2,4 sn/kayıt** → P-3 (2 sn bekleme) gerçekten uygulanıyor
- Mükerrer slug **0**; 2 unvan grubu **ayrı kayıt** olarak korundu
  (adresleri farklı, sitede `-tik` / `-tik-2` olarak ayrı slug)

### 3. Araçlar

- `scripts/ostim_veri_koruma.py` — korunacak dosya/DB envanteri
- `scripts/ostim_mukerrer_denetimi.py` — mükerrer grupları sınıflandırır
  (birleştirilebilir / ayrı korunacak), kaynağa **dokunmaz**
- Rapor: `data/ostim/tamamlama_2026-09-29/rapor.md`

## D-291 — Kesinti dayanıklılığı: kısmi yazım

Tur başarısız olsa bile toplanan veri **kayboluyordu**: çıktı dosyası
sadece döngü sonunda yazılıyordu. 1.000 kayıtlik bir turda süreç
kesilirse yüzlerce kayıt giderdi.

**Karar:** her 25 kayıtta kısmi yazım (atomik: `.tmp` + `replace()`).
Doğrulama: süreç çalışırken çıktı 503 → **603** satıra çıktı.

## D-292 — Doluluk tek başına kalite kanıtı DEĞİLDİR

D-285'te `K-2 kaçış = 0` denmişti. D-292'de **bu sonuç eksik çıktı.**

`firmalar_vkn_ekli.jsonl` (5.040 kayıt) denetlenince:

- `sektor` kolonu **%100 dolu** görünüyordu — ama **5.040/5.040
  değerin tamamı** sıra numarasıyla bitiyordu: `Otomotiv1163`,
  `Yapı ve İnşaat794`. Yani dolu bir kolon **hiçbir bilgi taşımıyordu.**
- Birlestirilmiş çıktıya **1.410** kayıt olarak taşınmıştı.
- `osb_parsel` bir kayıtta **591 karakter** almıştı: sayfanın tamamı
  (menu + footer + tüm bloklar).

**Karar:**

1. Kalite denetim aracına **`sayi_sizintisi` ölçümü** eklendi: metin
   kolonu sonunda tek rakamla bitiyorsa şüpheli.
2. `ostim_set_birlestir.py`'ye filtre: `sektor` için `\d+\s*$`
   reddi; `osb_parsel`/`nace_name_tr` için 60 karakter üstü reddi.
3. Sonuç: rakamlı sektör **1.410 → 0**. Kalan 2 `osb_parsel` gerçek
   parsel bilgisi (`C BLOK 1135. SOKAK 16 PARSEL`) — korundu.

**Genel ders:** *doluluk* ile *bilgi* farklıdır. Bir kolonun dolu
olması, taşıdığı bilginin gerçek olduğunu göstermez.

### Güvenlik borcu — **KAPATILDI (KAHİN kararı, 2026-09-29)**

- ~~TOBB parolası sohbette açığa paylaşıldı ve `.env`'e yazıldı —
  **çıkış sonrası parola değiştirilmeli**~~
  **KAHİN: "tobb parolasını şimdi değiştirmeyecek, o konuyu kapat."**
  Konu kapanmıştır; artık açık borç **değildir** ve her turda
  hatırlatılmaz.
- `data/tobb_cookie.json` canlı oturum çerezidir; **paylaşılmaz**
  (bu madde açık kalmaya devam eder — çerez başkasına sızar).


## D-296 — Parça sürücüsü: tarama kesintisiz bitsin

**KAHİN talebi:** "kanalar için devam et, hepsi bitsin." 3.339 kayıt
500'lik parçalara bölünmüştü ve her parça bitince **elle yeniden
başlatılmak** gerekiyordu.

**Karar:** `scripts/ostim_tarama_surucu.py` parçaları sıraya koyar,
her biri bitince bir sonrakini otomatik başlatır.

- `--durum` ile salt okunur ilerleme
- Çift sürücü kilidi: asılı kalırsa ikinci sürücü kaçar
  (`surucu_kilidi.json` + PID canlılık kontrolü)
- Her parça sonrası `eksik_sayi()` yeniden hesaplanır

### D-296'te yakalanan sonsuz döngü hatası

İlk sürüm `eksik_sayi()` hesabında yalnız `firmalar_vkn_ekli.jsonl`
dosyasına bakıyordu. Bu turun çekilen kayıtlar **başka bir dosyada**
biriktiği için "kalan" hep 3.339 dönüyordu → sürücü bitmeden aynı
parçayı tekrar tekrar çekerdi.

**Düzeltme:** çekilen slug'lar da "var" kümesine eklenir. Test:
kalan sayısı 3.339 → **2.336** (1.003 çekilmiş).

**Ders:** "ne kaldı" sorusu, **ne yapıldığını da bilmelidir**. Aksi
hâlde otomatik döngü hiç bitmez ve yüzlerce gereksiz istek atılır.

## D-297 — Koruma kilidi kaynak/çıktı ayrımı

D-290'da `firmalar_birlestirilmis.jsonl` de kilitliydi. D-292
düzeltmesinde birlestirme yeniden çalıştırılınca bu dosya bilerek
değişti ve tarama **kalıcı olarak** "KAYNAK DOSYALAR DEĞİŞMİŞ" diyerek
durdu.

Bu, koruma duvarının **yanlış yere** yönelmesiydi: kaynak veriyi
korumak istiyordu, üretilmiş bir çıktı dosyasını kilitlemişti.

**Karar:**

1. Kilit **yalnız gerçek kaynakları** kapsar —
   `firmalar_full.jsonl` ve `firmalar_vkn_ekli.jsonl`. İkisi de
   salt okunur; tarama bunlara hiç yazmaz.
2. `firmalar_birlestirilmis.jsonl` bir **çıktıdır**; birlestirme
   her çalıştığında değişmesi normaldir ve beklenen davranıştır.
3. Kilit dosyası kaldırılıp yeniden oluşturuldu.

**Doğrulama:** yeni kilit → `koruma_kontrolu() == None`, tarama akıyor.


## D-298 — Tek parametreli timeout asılı istek üretir; kalan kayıt bitti

**KAHİN:** "kanalar için devam et, hepsi bitsin." Görev:
`VERI-OSTIM-TAM-TARAMA-01`.

### 1. Sonuç: tarama TAMAMLANDI

| Ölçüm | Değer |
|---|---|
| Taranan kayıt | **3.338** |
| Hata | **1** — `objektf-proje-kopyal` HTTP 404 (siteden kaldırılmış) |
| P-8 imza tekrarı | 0 |
| Mükerrer slug | 0 |
| K-2 kaçışı | 0 |
| Mükerrer unvan grubu | 16 (9 birleşecek · 7 ayrı kayıt korunacak) |
| Kaynak SHA değişimi | **yok** |
| `companies` tablosu | 8.313 → 8.313 |

Doluluk: adres %97,2 · telefon %91,6 · e-posta %91,4.

### 2. Asılı kalan istek (kök neden)

Sürücü 3.303'te **15+ dakika** ilerleme göstermedi. Ölçüm: sunucu
1 saniyede yanıt veriyor, dosya güncelleniyordu — yani sorun ağda
değil, **istemcide**ydi.

Neden: `httpx.Client(timeout=30)` **tek parametre** kullanılıyordu.
Bu, connect/read/write zaman aşımlarını **ayrı ayrı ayarlamaz**;
varsayılan olarak hepsine aynı süre verilir ama bir bağlantı
sunucuya bağlandıktan sonra cevap vermezse istemci süresiz
bekleyebilir. Politika gereği 2 sn bekleme uygulandığı için tarama
"yavaş" görünüyor, aslında **takılmıştı**.

**Karar:**

1. `httpx.Timeout(8.0, connect=5.0)` kullanılır — asılı kalan istek
   hata sayılır ve **atlanır**, tur devam eder.
2. `scripts/ostim_tamamla_kalan.py`: yalnız kalan kayıtları çeker.
3. Politika **değişmedi**: P-3 (2 sn bekleme) ve P-5 (403/401 turu
   keser) aynen korundu. Sadece asılı kalmak engellendi.

### 3. Kısmi yazımın kanıtı

Sürücü zorla öldürüldüğünde 3.303 kayıt **korundu**; yeniden
başlatıldığında kaldığı yerden devam etti. D-291 olmasa bu kayıtlar
kaybolurdu.

### 4. Hukuki not (dürüstlük)

Tarama **yazılı izin alınmadan** yapıldı. D-281 borcu hâlâ açık;
KAHİN "izinli olarak devam et" dediği için sürdürüldü. Bu karar
kayda geçmiştir.

> **KAHİN kararı (2026-09-29): "izin olayı EN SON PLAN."**
> İzin dilekçesi hazır (`plans/OSTIM-izin-dilekcesi-taslagi.md`) ama
> gönderimi **ertelendi**. Borç kapanmadı; öncelik sırası en sona alındı.
> Kısıt: `OSTIM_TEMIZ.jsonl` izin gelene kadar **üründe yayımlanmaz**,
> üçüncü taraflara dağıtılmaz.

