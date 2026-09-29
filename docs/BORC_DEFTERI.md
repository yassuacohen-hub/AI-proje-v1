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
| `BORC-NACE-DOGRULAMA-01` | `nace_validity` alanı kaynaksız | ACIK | D-258 | — |
| `BORC-PANO-BORC-00` | borç listesinin kanonik kaydı yok | KAPANDI | D-271 | D-272 |
| `BORC-SCRIPTS-01` | `scripts/` altında 41 `_*` girdi (29 `.py` hepsi derlenir, **0 çürük**, üretim çağıranı **0**); kökte ayrıca **76 index hayaleti** tek kullanımlık betik. D-281'de ölçüldü ve **tavanlandı** (76/2), kesme ürün sahibinde | ACIK | D-255 | — |
| `BORC-KARAR-NUMARA-01` | bu defterde 8 karar kaydı var (D-273…D-280); D-227 (numara yalnız `AGENTS.md`) + D-272 (defter durum tutar) ihlali | ACIK | D-281 | — |
| `BORC-SICIL-DAIRE-01` | 619 firmada sicil no var, sicil dairesi yok | ACIK | D-260 | — |
| `BORC-VKN-01` | VKN kanalı ölü, kaynak bulunamadı | ACIK | D-253 | — |
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

## Devir — sonraki oturum (D-281 sonrası)

Bu bölüm devir notunun kaynağıdır (D-219 mantığı). Ajan hafıza dosyasına yazılmadı: ölçüldü,
dört `*_project_context.md` dosyasında bu hattın hiçbir izi yok — hat panoya bağlı değil,
doğrudan ürün sahibiyle yürüyor.

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

- **Kaldığım yer:** D-281 yazıldı. **Hash yazılmıyor:** bu satıra hash yazan commit hash'i
  değiştirir (sonsuz gerileme). Konum dalın tepesidir: alt depo `chore/monorepo-merge`,
  üst depo `master`; `git log --oneline -3` ile okunur.
- **Karar numarası çatışması (yeni borç `BORC-KARAR-NUMARA-01`):** başka ajan bu deftere
  **D-273…D-280** arası 8 karar kaydı yazdı. `AGENTS.md` en yüksek D = 272'de kaldı.
  D-227 (numara yalnız `AGENTS.md`'den) ve D-272 (defter **durum**, AGENTS.md **gerekçe**)
  birlikte ihlal. Bu turun kaydı çakışmasın diye **D-273 → D-281**'e kaydırıldı.
  Taşıma **YAPILMADI** — başka ajanın işi sessizce taşınmaz, karar ürün sahibinde.
- **Test tabanı yeni: 4527 passed, 12 skipped, 1 FAILED.** Sabit sıra (`-p no:randomly`,
  215.80s) ve rastgele (`--randomly-seed=281`, 175.54s) **aynı** sonucu verdi → sıra
  bağımlılığı yok. 4511 → 4527: +2 benim D-281 mandalım, +14 başka ajanların yeni testleri.
- **AÇIK KIRMIZI — benim işim değil, düzeltilmedi:**
  `tests/test_dokuman_politikasi.py::test_d219_ajan_context_dosyalari` —
  `yasu_project_context.md` **213 satır**, D-219 tavanı **200**. Dosya yasu'nun açık işi
  (oturum sırasında düzenleniyordu); başka ajanın hafıza dosyasını kesmem D-219'un sahipliğini
  bozar. Çözüm sahibinde: eski oturum bloklarını `archive/yasu_context_<YYYYMM>.md`'ye taşı.
  Mandal doğru çalıştı — kusuru **ben yazmadım, mandal yakaladı**.
- **Yeni ayrım (D-281, ezberlenecek):** diskte yok + index'te yok = **rezervasyon** (meşru);
  diskte yok + index'te **var** = **index hayaleti** (commit edilmemiş silme). Kilit
  dosyasındaki `scripts/ajan_cakisma_kilidi.py` **hayalet değil**, ihsan'ın rezervasyonu.
- **Ürün sahibi kararı bekliyor (taşıma YAPILMADI):** eşzamanlı ajan izolasyonu, D-272/7'deki
  üç seçenek. Önerim 1+2 (sıra düzeni + var olan kilidi zorlamak); ayrı worktree canlı
  veritabanını ayırmadığı için tek başına yetmez.
- **Açık 5 borç, öncelik ürün sahibinde:** `BORC-VKN-01` (kaynak yok, MERSIS A/B kararına
  bağlı), `BORC-NACE-DOGRULAMA-01`, `BORC-SICIL-DAIRE-01` (§5 saklı karar),
  `BORC-SCRIPTS-01` (yukarıdaki soru), `BORC-KARAR-NUMARA-01`.
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

## Güvenlik borcu (açık)

- TOBB parolası sohbette açıkça paylaşıldı ve `.env`'e yazıldı →
  **çalışma sonrası parola değiştirilmeli**.
- `data/tobb_cookie.json` canlı oturum çerezidir; paylaşılmamalı, expire olur.
- **D-281 yeni borç:** 8.473 firma için ticari amaçlı toplu derlemenin
  hukuki uygunluğu doğrulanmadan **toplu indirme başlatılamaz**
  (`robots.txt` izni hukuki izin **değildir**).





- TOBB parolası sohbette açıkça paylaşıldı ve `.env`'e yazıldı →
  **çalışma sonrası parola değiştirilmeli**.
- `data/tobb_cookie.json` canlı oturum çerezidir; paylaşılmamalı, expire olur.



