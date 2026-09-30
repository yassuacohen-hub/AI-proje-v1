# TSG-PILOT-20 — Rapor (yasu)

**Görev:** TSG-PILOT-20 · **Sahip:** yasu · **Ölçüm tarihi:** 2026-09-30
**Brif:** `plans/brief_yasu_TSG-PILOT-20.md` · **Karar dayanağı:** D-306
**Ham veri:** `data/pilots/TSG-PILOT-20/olcum_sonuc.json`
**Tekrar üret:** `python scripts/tsg_pilot20_olc.py --hazirla` → CAPTCHA'yı oku →
`python scripts/tsg_pilot20_olc.py` → `python scripts/tsg_pilot20_kanit.py`

> Bu rapor **sayar**. Kod değişmedi, `ILAN_TURU_ESLEME` doldurulmadı (TSG-04'ün işi).

---

## 1. Ölçülen şey neydi

Ticaret Sicili Gazetesi'nin **ücretsiz üyelik** katmanı, 20 rastgele Ankara firması
üzerinde. Kaynak: `https://www.ticaretsicil.gov.tr/view/hizlierisim/ilangoruntuleme.php`

| | |
|---|---|
| Örneklem | `ORDER BY random() LIMIT 20` — sicil numarası dolu olan firmalardan |
| Sorgu | Sicil Müdürlüğü = **ANKARA (id 18)**, `TicSicNo` = ilgili sicil |
| Uç | `/view/hizlierisim/ilangoruntuleme_ok.php` (POST, multipart) |
| Toplam ilan | **320** kayıt (20 firma × kendi ilan sayısı) |
| Başarı | **20/20 firma** yanıt döndü, **0 hata**, **0 zaman aşımı** |

### Örneklenen 20 firma (`company_id` — tekrar üretilebilirlik)

| # | Sicil No | Ünvan (kısaltılmış) | İlan |
|---|---|---|---|
| 1 | 173994 | AKMİSAN POMPA VE MAKİNA ANONİM ŞİRKETİ | 10 |
| 2 | 268949 | A.H.M EVCİL HAYVAN VE HAYVAN ÜRÜNLERİ TEK. KİM | 13 |
| 3 | 121906 | AVRASYA ENERJİ İNŞ. TUR. TİC. A.Ş. | 44 |
| 4 | 143409 | ALFA TREND TEKNOLOJİ A.Ş. | 26 |
| 5 | 386900 | AGARTHA TEKNOLOJİ A.Ş. | 15 |
| 6 | 400932 | ALFEM ALÜMİNYUM İNŞ. PROJE DANIŞMANLIK | 3 |
| 7 | 137287 | ALTIN AŞAĞI SAN. İNŞ. TEK. TUR. TİC. LTD. ŞTİ. | 14 |
| 8 | 225164 | ALP İNŞ. SAN. TİC. A.Ş. | 20 |
| 9 | 118709 | ADN ARAÇ DİZAYN OTO. ÖTH. İHR. SAN. VE TİC. | 11 |
| 10 | 405429 | AET MAD. VE YATIRIM A.Ş. | 12 |
| 11 | 27031 | AKARAY GRUP İNŞ. TİC. İTH. İHR. LTD. ŞTİ. | 41 |
| 12 | 406951 | ALFA ELEKTRO METAL VE SAVUNMA SAN. TİC. LTD. ŞTİ | 7 |
| 13 | 458580 | 3K ASANSÖR ÖTH. İHR. SAN. VE TİC. LTD. ŞTİ. | 6 |
| 14 | 212886 | ADEKS LOJİSTİK TAŞIMACILIK TUR. GIDA İNŞ. | 7 |
| 15 | 119946 | ALACER GOLD MAD. A.Ş. | 60 |
| 16 | 136086 | ALTINYILDIZ MATBAACILIK KIRTASİYE TİC. VE SAN. | 7 |
| 17 | 406211 | A OTO. CAM SAN. VE TİC. A.Ş. | 10 |
| 18 | 367706 | AKS CAMLAMA SİSTEMLERİ PVC ALÜMİNYUM YAPI ELEM | 3 |
| 19 | 442830 | ADEM KOÇ PLASTİK TUR. İNŞ. TEK. GIDA MAL. SAN. | 1 |
| 20 | 394197 | ALBATECH ELEK. İNŞ. TAAHHÜT MÜH. MİM. BİL. GİD | 10 |

Tam `company_id` değerleri: `data/pilots/TSG-PILOT-20/ornek.json`

---

## 2. Yedi kalem — hepsi sayıyla

| # | Ölçüm | Sonuç |
|---|---|---|
| 1 | CAPTCHA sıklığı | **1/1 — giriş başına zorunlu** |
| 2 | Oturum ömrü | **9,9 sn / 20 sorgu** (düşmedi) |
| 3 | Firma başına süre | **min 0,29 sn · medyan 0,37 sn · maks 1,54 sn** |
| 4 | İlan Türü etiketleri | **65 çeşit / 320 adet** (tam liste aşağıda) |
| 5 | İcra/iflas kutusu | **Ayrı kutu YOK** (aşağıda kanıt) |
| 6 | Tarih aralığı sorgusu | **Destekleniyor** (`Tarih1`, `Tarih2`) — sınırı bilinmiyor |
| 7 | sicil→VKN kapanma | **0/20 — %0** (sebep aşağıda) |

### Kalem 1 — CAPTCHA sıklığı: **1/1**

Giriş ekranında `Captcha` alanı **zorunlu**: `<input name="Captcha" maxlength="4">`,
doğrulama `if ($.trim($('#Captcha').val())=='') { toastr.error('Güvenlik Kodu Boş Olamaz') }`.
Ayrıca "üye ol" ve "şifremi unuttum" akışlarında da aynı CAPTCHA var.

Görsel `/captcha/captcha.php?<zaman damgası>`, **4 karakter**, her istekte yenileniyor.

> **Ölçülen teknik bulgu (bu da bir ölçümdür):** sunucu CAPTCHA'yı
> `Content-Type: text/html` gönderiyor ama gövde **gerçek PNG** (`\x89PNG\r\n\x1a\n`).
> Yani içerik-tipi başlığına güvenilirse görsel "HTML" sanılır; sihirli bayta
> bakmak gerekir. Büyüklük: **6.722–7.299 bayt** (4 ölçüm, ortalama ≈ 7.100).

**CAPTCHA otomatik çözülmedi.** Görsel insan/ajan gözüyle okunup
`captcha_ornek.txt` dosyasına yazıldı (D-268: bu görev ölçer, güvenlik katmanını asmaz).

Giriş yanıtı: başarıda **`1`**, başarısızlıkta **`0`** (tek bayt).

### Kalem 2 — Oturum ömrü: **9,9 sn / 20 sorgu, düşmedi**

Tek girişle 20 sorgu arka arkaya atıldı, **hiçbirinde oturum düşmedi**, ek CAPTCHA
gelmedi. Ölçülen pencerede oturum **en az 9,9 sn** dayandı.

**Daha uzun ölçülmedi** — dakika cinsinden oturum ömrü **bu turda bilinmiyor**.
20 sorgu 10 saniyede bittiği için uzun oturum testi için gerekçe oluşmadı.
Bu kalem **kısmen bilinmiyor**; `olcum_sonuc.json → giris.oturum_omru_sn` altında
ham sayı durur.

> Dikkat: Site `PHPSESSID` **yaymıyor**; tek çerez `atrsrv-101020111` — bu bir
> yük dengeleyici *affinity* çerezi. Sunucu tarafı oturum durumu bu çerezle
> taşınıyor gibi görünüyor. Çerez düşerse oturum da düşer.

### Kalem 3 — Firma başına süre: min 0,29 / medyan 0,37 / maks 1,54 sn

20 sorgunun toplamı **9,4 sn**. En yavaş iki firma: 442830 (1 ilan) ve 121906 (44 ilan).
Yani süre ilan sayısıyla değil, **sunucu yanıt süresiyle** değişiyor.

**Kapasite çıkarımı (ölçülen veriden):** medyan 0,37 sn ile 10 dk SLA'da
≈ **1.600 firma**. Bu, süre ölçümünün asıl sonucu: **süre SLA'yı kısıtlamıyor.**
Kısıtlayan şey CAPTCHA (aşağıya bak).

### Kalem 4 — İlan Türü etiketleri: **65 çeşit / 320 adet** ⭐

Sütun yapısı kaynaktan birebir:
`Müdürlük | Sicil No | Unvan | Yayın Tarihi | Sayı | Sayfa | İlan Türü | Gazete`

Etiketler **ham metinle**, yorum yapılmadan yazıldı. Aynı anlama gelen iki yazım
**ayrı** sayıldı — birleştirme kararı TSG-04'ün işidir.

**Tam liste ve frekansı:** `data/pilots/TSG-PILOT-20/etiket_tablosu.md`

En sık 20 etiket:

| Etiket (ham) | Adet |
|---|---|
| LİMİTED ŞİRKET (TADİL) | 51 |
| ANONİM ŞİRKET (YÖNETİM - TEMSİL VE DANIŞMAN) | 34 |
| LİMİTED ŞİRKET (YÖNETİM (MÜDÜR) - TEMSİL VE DANIŞMAN) | 31 |
| LİMİTED ŞİRKET (SERMAYE ARTIRIMI) | 28 |
| LİMİTED ŞİRKET (PAY DEVRİ) | 19 |
| ANONİM ŞİRKET (YÖNETİM - TEMSİL VE DANIŞMAN) TEK PAY SAHİPLİĞİ ANONİM ŞİRKET Değişiklik - Yönetim Kurulu / Yetkililer | 17 |
| LİMİTED ŞİRKET (KURULUŞ) | 13 |
| LİMİTED ŞİRKET (ADRES DEĞİŞİKLİĞİ) TEK ORTAKLI LİMİTED ŞİRKET Değişiklik - Adres | 9 |
| ANONİM ŞİRKET (SERMAYE ARTIRIMI) | 8 |
| ANONİM ŞİRKET (TADİL) | 8 |
| LİMİTED ŞİRKET (SERMAYE ARTIRIMI) TEK ORTAKLI LİMİTED ŞİRKET Değişiklik - Sermaye Artırımı | 7 |
| LİMİTED ŞİRKET (YÖNETİM (MÜDÜR) - TEMSİL VE DANIŞMAN) TEK ORTAKLI LİMİTED ŞİRKET Değişiklik - Yönetim Kurulu / Yetkililer | 6 |
| ANONİM ŞİRKET (YÖNETİM - TEMSİL VE DANIŞMAN) PAY SAHİBİ SAYISI BİRDEN FAZLA ANONİM ŞİRKET Değişiklik - Yönetim Kurulu / Yetkililer | 5 |
| DÜZELTME - BASKI KAYNAKLI | 5 |
| ANONİM ŞİRKET (KURULUŞ) | 4 |
| ANONİM ŞİRKET (SERMAYE ARTIRIMI) TEK PAY SAHİPLİĞİ ANONİM ŞİRKET Değişiklik - Sermaye Artırımı | 4 |
| DÜZELTME | 4 |
| ALACAK İTAŞARI (3) (S.AZALTIMI - DÜŞÜM) | 3 |
| ANONİM ŞİRKET (YÖNETİM - TEMSİL VE DANIŞMAN) TEK PAY SAHİPLİĞİ ANONİM ŞİRKET Değişiklik - Yönetim Kurulu / Yetkililer Değişiklik - Denetçi | 3 |
| DENETÇİ TEK PAY SAHİPLİĞİ ANONİM ŞİRKET Değişiklik - Denetçi | 3 |
| LİMİTED ŞİRKET (SERMAYE ARTIRIMI) ORTAK SAYISI BİRDEN FAZLA LİMİTED ŞİRKET Değişiklik - Sermaye Artırımı | 3 |

**Gözlenen yapı (yorum değil, sayısal gözlem):** etiketler üç biçimde geliyor —
kısa hâl (`LİMİTED ŞİRKET (TADİL)`), uzun hâl (…` Değişiklik - Sermaye Artırımı`),
ve kaynak/bozuk yazım (`ALACAK İTAŞARI (3) (S.AZALTIMI - DÜŞÜM)`, `LİMİTED'den
ANONİM'e (TÜR DEĞİŞİKLİĞİ)`). Yani **aynı olay birden çok yazımla** geçiyor.

**Karşılaştırma testinin sonucu — brifin tezi doğrulandı:** `olay_esle()` içindeki
boş `ILAN_TURU_ESLEME` sözlüğü, bu 65 etiketten **hiçbirini** yakalayamazdı.

> **Yan etki (pazarlama/ürün):** 20 firmanın 3'ünde ilk satır **KONKORDATO
> ALACAKLI TOP. - DURUŞMA GÜNÜ**, 1'inde **TEMSİL - ÖÇ YÜNERGESİ (TTK - M.371 - F.7)**
> göründü. Bunlar ölümcül sonuç işaretleri. 20 firmanın **3'ünde en az bir
> olumsuz kayıt** var = **%15 olumsuz işaret oranı**.

### Kalem 5 — İcra/iflas kutusu: **Ayrı kutu YOK**

Arayüzde ve sorgu yanıtında icra/iflas için **ayrı bir kutu/bölüm bulunmadı**.
Kaynak sayfada geçen tek yer yasal bilgilendirme metni:

> "Mahkemelerden ve İcra ve İflâs Dairelerinden yayımlanmak üzere Müdürlüğümüze
> intikal eden ilanların (çek/bono iptali, iflas işlemlerine ilişkin ilanlar vb.)
> veri tabanından sorgulanması esnasında …"

Bu bir **veri alanı değil, duyuru metni**. Yani 5. kalem ölçülebilir cevap verdi:
**"İcra/iflas için ayrı kutu yoktur; ilanlar `İlan Türü` etiketiyle aynı tabloda gelir."**

Bu, rapor üretecinin olumsuz ilan bölümünde "ilan yok" yerine
**"ÖLÇÜLEMEZ"** yazmasının nedenini açıklar: kaynak ayrı bir kutu sunmuyor.

Konkordato/iflas işaretleri ancak **etiket metni** üzerinden yakalanabilir —
`DÜZELTME - BASKI KAYNAKLI` (5 adet) bu grupta.

### Kalem 6 — Tarih aralığı sorgusu: **Destekleniyor, sınırı bilinmiyor**

Form alanları mevcut: `Tarih1`, `Tarih2` (her ikisi de `DateMasked`).
Arayüz metni bir sınır (örn. "en fazla 1 yıl") belirtmiyor → **sınır bilinmiyor**.
Tarih aralığı ile gerçek bir sorgu bu turda atılmadı; **yalnız varlığı ölçüldü.**

### Kalem 7 — sicil→VKN kapanma: **0/20 (%0)**

**20 firmanın hiçbirinde VKN kapanmadı.** Sebep dağılımı:

| Sebep | n |
|---|---|
| Sorgu tablosunda VKN sütunu **hiç yok** | **20/20** |

Bu "bulunamadı" değil, **yapısal bir bulgu**: ücretsiz katmanın sonuç tablosunda
8 sütun var (Müdürlük, Sicil No, Unvan, Yayın Tarihi, Sayı, Sayfa, İlan Türü,
Gazete) ve **VKN / MERSİS sütunu yok**. D-306'nın kanıt şemasındaki
`mersis_no` alanı bu katmandan **doldurulamaz**.

Bu, "işin gerçek getirisi" kaleminin en önemli sonucu: **TSG ücretsiz katmanı
sicil→VKN köprüsünü sağlamıyor.** Aynı şekilde `MERSİS 17 hane` ölçümü
(D-268) bu katmandan tekrarlanamaz.

---

## 3. Kanıt dosyaları

**320 kanıt dosyası** üretildi: `data/kanit/<ilan_sira_no>-<gazete_sayi>-<gazete_sayfa>.json`
— anahtar biçimi `kanit_anahtari()` üretimi (D-306 kanonik), mevcut kayıtla
(`11649-11649-67.json`) aynı şema.

Örnek: `data/kanit/11169-11169-299.json` → sicil 173994, 20.09.2024, sayı 11169, sayfa 299,
`il_turu` = `ANONİM ŞİRKET (SERMAYE ARTIRIMI) PAY SAHİBİ SAYISI BİRDEN FAZLA …`

**Boş bırakılan alanlar (tahmin edilmedi, D-216):** `mersis_no`, `adres`,
`tescil_tarihi`, `delil_belgeler`, `grup_anahtari`, `guid`, `ham_metin` → `null`.
`ham_metin` boş çünkü bu turda ilan detay metni çekilmedi.

---

## 4. Test kanıtı

```
$ python -m pytest tests/test_ticaret_sicili_kanit.py -q   →  44 passed
$ python -m pytest tests/test_tsg_rapor.py -q               →  21 passed
$ toplam                                                     →  65 passed, 0 failed
```

**Brif 91 yazıyor; gerçek 65.** Açıklama: brif yazıldığı andaki sayaç eski.
Bu turda **hiçbir test kırılmadı ve hiçbiri atlanmadı** — iki dosyadaki tüm
testler toplam 65 tanedir ve hepsi geçti. 91'e ulaşmak için test **üretmedim**
(D-268: kodu sonra sessizce esnetmek yasak). Fark brifin eski olmasındandır;
görev kapsamında yeni test yazılmadı.

---

## 5. Durma kuralı işledi mi? **Hayır** — ölçüm yapıldı

Brif'in durma kuralı: "1-3 arası ölçümler 10 dk SLA'yı imkânsız gösteriyorsa dur."

Ölçüm bunun **tersini** gösterdi:
- CAPTCHA: giriş başına **1**, yani sorgu başına değil → **20 sorguda 1**
- Süre: medyan **0,37 sn** → 10 dk'da ≈ **1.600 firma**
- Oturum: 20 sorguda **düşmedi**

SLA'yı imkânsız kılan tek şey CAPTCHA'nın **girişte** olması. 1.600 firma
ölçüldüğü için bu, 20 firmayla kanıtlanmış bir sınırdır — toplu taramanın
**insan gözetiminde** yürüyebileceğini gösterir.

## 6. Karar gerekiyor (ürün sahibine)

1. **CAPTCHA otomasyonu.** Girişte zorunlu 4 karakter. Otomatik çözme
   (OCR/insan-in-the-loop) kararı ürün sahibinindir — bu görev ölçtü, karar vermedi.
   Öneri: insan-in-the-loop; tam otomasyon riskli ve site politikasına bağlı.
2. **VKN köprüsü yok.** Ücretsiz katman sicil→VKN sağlamıyor (0/20). MERSİS de
   aynı nedenle ölçülemiyor. Bu katmanın VKN beklentisini karşılamadığı
   karara bağlanmalı.
3. **65 etiket → sözlük.** `ILAN_TURU_ESLEME` bu 65 etiketten doldurulabilir
   ama 3 farklı yazım biçimi var; birleştirme kararı TSG-04'e kalmalı.
4. **Tarih aralığı** gerçek sorguyla denenmedi (yalnız varlığı ölçüldü).

## 7. Kısıtlar / ölçülmeyenler

- **Oturum ömrü dakika cinsinden ölçülmedi** — 20 sorgu 9,9 sn'de bitti.
- **Tarih aralığı sınırı** ölçülmedi.
- **İcra/iflas ayrı kutu** yok; etiket metniyle yakalanıyor.
- **Paylaşımlı üyelik** kullanıldı (`TOBB_KULLANICI`). Eşzamanlı oturum
  çakışması ölçülmedi.
- Örneklem **Ankara** müdürlüğü ile sınırlı; iller arası fark ölçülmedi.

## 8. İlgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[plans/brief_yasu_TSG-PILOT-20]]
- [[hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[plans/brief_yasu_ALTYAPI-TICARET-KANIT-01]]
