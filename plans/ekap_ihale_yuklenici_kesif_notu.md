# EKAP / İhale–Yüklenici Eşleştirme — Keşif Notu

> **Durum:** keşif tamamlandı, uygulama bekliyor
> **Tarih:** 2026-09-27
> **Kapsam:** OSB duyuru toplama + kamu ihalesi yüklenici tespiti + firma veritabanı eşleştirme
> **Kural:** Bu notun her satırı **canlı istekle ölçüldü**. Tahmin/varsayım ayrı başlıkta işaretlidir.

---

## 1. Ölçülen Gerçekler (kanıtlı)

### 1.1 EKAP v2'ye taşınmış — en önemli bulgu

Eski `.aspx` adresleri artık yaşamıyor. Yönlendirme zinciri **okundu**:

```
GET /EKAP/Yasaklilik/YasakliSorguVatandas.aspx
  302 -> /EKAP/Yasaklilik/YasakliSorgu.aspx
  302 -> /EKAP/Default.aspx
  302 -> https://ekapv2.kik.gov.tr/
  son gövde: 12990B, VIEWSTATE YOK, <title>EKAP</title>, <base href="/">
```

`12990B + VIEWSTATE yok` = **Angular SPA kabuğu**. Yani "sayfa yok" değil, "sayfa yeniden yazılmış".

Menüden **okunan** (uydurulmayan) gerçek adresler:

| İşlev | Adres | Ölçülen durum |
|---|---|---|
| Sonuç İlanı Arama | `ekap.kik.gov.tr/EKAP/Ortak/KSP/KSPSonucIlaniArama.aspx` | ✅ **53334B — ÇALIŞIYOR, veri çekildi** |
| İhale Arama | `ekapv2.kik.gov.tr/ekap/search` | SPA (12990B) |
| Doğrudan Temin Arama | `ekapv2.kik.gov.tr/ekap-dt/search` | SPA |
| Yasaklı Sorgulama | `ekap.kik.gov.tr/EKAP/Yasaklilik/YasakliSorguVatandas.aspx` | SPA'ya 302 |
| Sözleşme Devri | `ekapv2.kik.gov.tr/sorgulamalar` | SPA |
| Kurul Kararları | `ekapv2.kik.gov.tr/sorgulamalar/kurul-kararlari` | SPA |
| İtirazen Şikayet | `ekap.kik.gov.tr/EKAP/Vatandas/SikayetSorgu.aspx` | SPA'ya 302 |

**Sonuç:** Eski nesil tek ayakta kalan kapı `KSPSonucIlaniArama.aspx`. Diğer her şey SPA → `requests + bs4` ile alınamaz.

### 1.2 Çalışan kapı nasıl kırıldı (sabitlenecek erişim reçetesi)

Üç engel, üç çözüm — hepsi ölçümle doğrulandı:

1. **SSL el sıkışma reddi.** KİK eski cipher kullanıyor; modern OpenSSL reddediyor.
   Çözüm: `create_urllib3_context(ciphers="DEFAULT@SECLEVEL=1")` taşıyan özel `HTTPAdapter`.
2. **Arama tetiklenmiyor.** Buton normal `<input type=submit>` değil, ASP.NET `LinkButton`.
   Çözüm: `__EVENTTARGET = "ctl00$ContentPlaceHolder1$lnkbtnIlanAra"`.
3. **`__VIEWSTATE` BOŞ — bu sayfa onu kullanmıyor.** ⚠️ *Önceki turda "VIEWSTATE var" yazmıştım, **yanlıştı**; ölçümle düzelttim.*
   Ölçülen gizli alanlar: `__PIT` **744kr**, `__PITC` **208kr**, `__EVENTVALIDATION` **456kr**, `__VIEWSTATE` **0kr**.
   Sadece VIEWSTATE gönderince sunucu **500** döndü (5325B *"Sayfada hata oluştu"*).
   Çözüm: **sayfadaki tüm `input[type=hidden]` alanlarını olduğu gibi geri gönder** — alan adı ezberleme.
4. **"Kayıt bulunamadı".** Tarih alanları **dolu** verilince boş sonuç dönüyor. Çözüm: boş bırak.
5. **IKN hücresinde boşluk var:** `"2003      /78132"`. Regex `^\d{4}\s*/\s*\d+` olmalı; `^\d{4}/\d+` **0 satır** ayıklar.

Alınan gerçek veri (girişsiz, e-imzasız, captcha'sız — **10 başlık**, `post=74585B`):
```
2003/78132 | temizlik ve ilaçlama işi                        | ADANA NUMUNE HASTANESİ | 08.01.2004
2003/88713 | ZONGULDAK KDZ.EREĞLİ DEVLET HASTANESİ EK BİNA…  | ZONGULDAK BAYINDIRLIK  | 12.01.2004
```

Sayfadaki alan kimlikleri (okundu): `txtBoxIKNYil`, `txtBoxIKNSira`, `txtIsinAdi`, `txtIdareAdi`, `hdnAktIKN`, `__PIT`, `__PITC`.

### 1.3 Çalışan kapının sınırları (küçümsenmemeli)

| Sınır | Ölçüm |
|---|---|
| **Yüklenici kolonu YOK** | Liste 4 kolon: IKN, İşin Adı, İdare, Yayım Tarihi |
| **Detay açılmıyor** | IKN hücresine postback attım → aynı liste döndü (74581B ≈ 74597B) |
| **250 kayıt tavanı** | "Toplam Kayıt Sayısı: 250" (25 sayfa × 10) |
| **Veri güncel değil** | Dönen kayıtlar 2003–2004 tarihli |
| **Tarih filtresi kırık** | Dolu tarih = boş sonuç → dilimleme yapılamıyor |

**Dürüst yorum:** Bu kapı ihale *başlıklarını* verir, **yükleniciyi vermez**. Asıl hedef için yeterli değil.

### 1.4 Veritabanı tarafı — eşleştirmenin anahtarı YOK

Gerçek veri `backups/company_master_pre_dedup_20260908_090326.db` (2.6MB).
⚠️ `company_master.db` ve `data/app.db` **0 byte / 0 tablo** — canlı veritabanı boş, veri yedekte.

Tablolar: `companies`, `osbs`, `quarantine_firms`. **8313 firma.**

| Alan | Doluluk |
|---|---|
| `legal_name` | 8313 / 8313 → **%100** |
| `is_osb_member`, `osb_id`, `nace_validity` | %100 |
| `primary_email` | 3668 → %44 |
| **`vergi_no`** | **%0** |
| **`tax_number`** | **%0** |
| **`mersis_number`** | **%0** |
| `trade_name`, `osb_parsel` | %0 |

[`entity_resolution.py`](../src/company_master/etl/entity_resolution.py:2) zaten var ve mantığı doğru: *"vergi_no birincil, unvan fuzzy yedek"*.
**Ama birincil anahtar tamamen boş** → eşleştirme %100 ünvana mahkûm.

Ünvan gürültüsü ölçüldü: `TİC` 4406, `SAN` 3621, `ŞTİ` 3353, `LTD` 3249, `A.Ş.` 1511+663, `LİMİTED` 896 kez.
Ortalama uzunluk 41 karakter, 8271/8313 tekil. Türkçe karakter + karışık büyük/küçük harf:
`2H Yazılım Bilişim İnşaat Makina İhr. İth. San. Ve Tic. Ltd. Şti`

### 1.5 OSB tarafı (önceki ölçüm)

4/4 OSB sitesi erişilebilir, **hiçbirinde ayrı ihale sayfası yok** — ihaleler `/duyurular` akışına gömülü.
→ "İhale izleyici" değil, **"duyuru toplayıcı + ihale filtresi"** doğru tasarım.

### 1.6 NACE / sektör eşleşmesi — ürün sahibinin sorusu, ölçüldü

> *"NACE kodu ile de eşleşemez mi, sektör açıklamaları bazlı? Daha güçlü sinyal olmaz mı?"*

**Fikir teorik olarak doğru:** NACE resmî sınıflandırma, ünvan ise pazarlama metni. Ölçüm:

**a) Firma tarafında NACE kodu YOK.** 7 veritabanı dosyası tarandı:

| Alan | Ölçüm |
|---|---|
| `nace_code` kolonu | **hiçbir tabloda yok** |
| `nace_validity` | 8313/8313 dolu ama **tamamı `'unknown'`** → anlamlı değer **0** |
| `description` | 0/8313 → **%0** |

10 adet `nace_*.py` doldurma script'i ve `logs/nace_doldur.log` var — **çalışma yapılmış ama sonuç hiçbir veritabanına yazılmamış.**

**b) Referans sözlükleri VAR ve kaliteli:**

| Dosya | İçerik |
|---|---|
| `data/nace/turkiye_nace.json` | 2142 NACE kaydı (`code_6digit`, `code`, `name_tr`) |
| `data/nace_to_ostim_sektor.json` | **17 sektör → 123 NACE kodu** eşlemesi |
| `data/nace_hedefleri.json` | NACE grubu → hedef firma sayısı |

**c) Sözlükle eşleşme denendi — ünvan kesişimiyle yan yana ölçüldü:**

Sözlükten sektör→kelime kümesi çıkarıldı, hem firma ünvanı hem ihale başlığı aynı sektöre haritalandı.

| Ölçüt | Sonuç |
|---|---|
| Sektöre atanabilen firma | **4113 / 8313 (%49)** |
| Sektör atanabilen ihale | **3 / 7** |
| Sektör isabetliyse aday havuzu | 180–615 firma — **sıralama yok** |

Yan yana karşılaştırma:

| İhale | A) ünvan kesişimi | B) sektör sözlüğü |
|---|---|---|
| temizlik ve ilaçlama işi | **Destek Grup İlaçlama** ✅ | Kimyasallar-Temizlik → 180 firma, ilki *OSGB Danışmanlık* ❌ |
| AKARYAKIT (Motorin, Benzin) | **ADK Akaryakıt** ✅ | sektör atanamadı ❌ |
| YEMEK PİŞİRME VE DAĞITIM | Dağıtım firmaları (zayıf) | *Elektrik-Elektronik* → **yanlış sektör** ❌ |
| Devlet hastanesi ek bina inşaatı | Ereğli Metal İnşaat ✅ | Yapı-İnşaat → 615 firma, alfabetik ilk ❌ |

**Dürüst sonuç:** Sözlük eşleşmesi bugünkü veriyle **ünvan kesişiminden zayıf**. İki nedenle:
1. **Sıralama üretmiyor** — 615 firmalık havuz "aday listesi" değil.
2. **Sektör kelimeleri genel** (`ELEKTRIK`, `TICARETI`) → yanlış sektöre çekiyor; "yemek dağıtımı → Elektrik" bunun kanıtı.

**d) KARAR (ürün sahibi, 2026-09-27): ikisi birlikte kullanılacak.**

Ölçüm ikisinin **farklı işlerde** iyi olduğunu gösteriyor — bu yüzden rakip değil, tamamlayıcı:

| | ünvan kesişimi (idf) | sektör sözlüğü |
|---|---|---|
| Güçlü yanı | **sıralama üretir** (8.33 / 15.06 skor) | **anlam bilir** (ilaçlama ⊂ temizlik) |
| Zayıf yanı | anlamı bilmez → *Devlet Tiyatroları* TRT ihalesine aday | sıralama üretmez → 615 firmalık havuz |

Birleşik kurgu — sözlük **kapı**, kesişim **sıra**:
```
1. ünvan_kesişimi(idf)  -> sıralı aday listesi
2. sektör uyuşmazlığı   -> ELE   (ihale sektörü ≠ firma sektörü ise düşür)
3. sektör uyuşması      -> YÜKSELT (aynı sektörse skoru artır)
4. sektör atanamadıysa  -> DOKUNMA (7 ihalenin 4'ü böyle; ceza verilmez)
```
4. madde kritik: sözlük kapsamı %49 olduğu için "bilmiyorum"u "hayır" saymak veri kaybettirir.
Bu kurgu "Devlet Tiyatroları Genel Müdürlüğü → TRT personel taşıma" saçmalığını keser,
"ADK Akaryakıt → motorin alımı" doğrusunu korur.

⚠️ Birleşik kurgunun **sayısal** kazancı henüz ölçülmedi; uygulama görevinin ilk adımı bu ölçüm olacak.

**Asıl kazanç NACE kolonunu doldurmakta.** `nace_code` dolu olsaydı ihale başlığı → NACE → firma zinciri ünvandan kesinlikle güçlü olurdu. Bu ayrı bir iş kalemi: **`VERI-NACE-01` — 8313 firmaya NACE ataması** (sözlük + script'ler zaten var, eksik olan yazma adımı).

---

## 2. Yeni Öneri — SPA'yı zorlamak yerine ölçmek

`requests` ile SPA'ya saldırmak boşa emek: gövde 12990B kabuk, veri XHR ile geliyor.
İki yol var:

**A) API ucunu ölç (tercih edilen).** SPA'nın kendi çağırdığı JSON uçları var. Bunlar **tarayıcı ağ trafiğinden okunur** — tahmin edilmez. Depoda [`agent-browser`](../../.agents/skills/agent-browser/SKILL.md) becerisi mevcut; tam bu iş için. Ölçüm çıktısı: gerçek endpoint + istek gövdesi + yanıt şeması. Bulunursa JSON API `requests` ile kalıcı ve hızlı çalışır — HTML kazımaktan **kat kat sağlam**.

**B) Headless tarayıcı ile kaz.** API bulunamazsa. Yavaş, kırılgan, bakım maliyeti yüksek. Yedek plan.

**C) Kamu İhale Bülteni.** Sonuç ilanları günlük yayımlanır ve *yüklenici adı + sözleşme bedeli* metinde açıkça yazar. Erişim biçimi **henüz ölçülmedi** — varsayım olarak işaretliyorum.

> ⚠️ **Varsayım uyarısı:** C maddesi ve "yasaklılarda vergi no bulunur" beklentisi **ölçülmemiştir**. Plan bunlara yatırım yapmadan önce ölçüm şart.

---

## 3. Bu yapı hangi sorulara cevap verir

**Satış / fırsat**
1. Hangi müşterimiz son 6 ayda kamu ihalesi kazandı? *(satış tetikleyicisi)*
2. Hangi firma ilk kez kamu işi aldı? *(büyüme sinyali)*
3. Hangi idareler bizim sektöre iş veriyor? *(hedef kurum listesi)*
4. Aynı işi tekrar tekrar alan firma var mı? *(yerleşik tedarikçi tespiti)*

**Firma istihbaratı**
5. Bu firma kamudan toplam ne kadar iş aldı? *(bilanço olmadan ciro sinyali)*
6. Firmanın kamu işi eğilimi artıyor mu azalıyor mu? *(zaman serisi)*
7. Firma hangi iş kollarında ihale alıyor? *(NACE doğrulaması — beyan değil kanıt)*
8. Kamu işi alan firmanın çalışan sayısı tutarlı mı? *(veri kalitesi çapraz kontrolü)*

**Risk**
9. Bu firma yasaklı mı? *(en değerli çıktı — sözleşme öncesi kırmızı bayrak)*
10. Firma hakkında itirazen şikâyet var mı?
11. Sözleşme devretmiş mi? *(taşeronlaşma sinyali)*

**OSB / bölge**
12. Hangi OSB'den kaç firma kamu işi alıyor? *(OSB kıyaslaması)*
13. OSB firmalarının kamu ihalesi payı nedir?
14. Ankara firmaları hangi illerin idarelerinden iş alıyor? *(coğrafi yayılım)*

**Veri kalitesi**
15. Kaç firma ihale kaydıyla eşleşti, kaçı eşleşmedi? *(kapsama oranı)*
16. Eşleşmelerin kaçı kesin, kaçı olasılıksal? *(güven dağılımı)*

---

## 4. Uygulama Planı — 5 aşama, sıralı

### Aşama 0 — EKAP erişimini SABİTLE (önce bu)
Çalışan reçete (§1.2) şu an geçici ölçüm dosyasında; kaybolursa her şey baştan.
→ Kalıcı modüle taşı + sözleşme testi ekle (canlı ağ **olmadan** çalışan, kaydedilmiş yanıtla).
**Çıktı:** yeniden kullanılabilir oturum kurucu + kanıt testi.

### Aşama 1 — Yüklenici kaynağını ÖL (kod yazmadan)
`agent-browser` ile SPA'nın gerçek JSON uçlarını oku: yasaklı sorgulama, ihale arama.
**Kabul ölçütü:** yanıtta yüklenici adı var mı? vergi no var mı? tarih filtresi çalışıyor mu? kayıt tavanı ne?
→ Sonuç olumsuzsa **buradan dön**, boşa kod yazma.

### Aşama 2 — Ünvan normalizasyon çekirdeği
Eşleştirmeden **önce** şart. Türkçe karakter sadeleştirme + hukuki ek sökme + noktalama temizliği.
`2N Cam Teknolojileri ve Yapı Sistemleri Sanayi Ltd. Şti.` → `2n cam teknolojileri ve yapi sistemleri`
Mevcut [`normalize.py`](../src/company_master/etl/normalize.py) ne kadarını yapıyor → **ölçülecek**.
**Kabul ölçütü:** 8313 ünvanda çalıştır; çekirdek çakışması (farklı firma, aynı çekirdek) sayısı raporlanacak.

### Aşama 3 — İki tablo, skorlu eşleşme
- `ihaleler`: IKN, iş adı, idare, tarih, yüklenici_ham_ad, bedel, kaynak
- `ihale_firma_eslesme`: ihale_id, company_id, **skor**, **yöntem**, **durum**

`skor`/`yöntem`/`durum` **pazarlık konusu değil**. Düşük skor = "onay bekliyor", insan onaylar.
Kesin olmayan eşleşmeyi kesinmiş göstermek en tehlikeli senaryo: müşteriye yanlış "bu firma bu ihaleyi aldı" dersek güven gider.

### Aşama 4 — OSB duyuru toplayıcı + ihale filtresi
`/duyurular` akışını topla, ihale anahtar sözcükleriyle filtrele. SSL/buton sorunu burada yok.
Aşama 0–3'ten **bağımsız**, paralel yürüyebilir.

### Aşama 5 — Vergi no boşluğunu kapat (%0 → ?)
Uzun vadeli. Yasaklı listesi vergi no veriyorsa oradan; vermezse MERSİS/GİB ayrı keşif.
**Bu kapanmadıkça eşleştirme olasılıksal kalır.**

---

## 5. Dürüst Değerlendirme

- ✅ İhale **başlıkları** girişsiz alınabiliyor — kanıtlı.
- ❌ **Yüklenici adı henüz hiçbir kaynaktan ölçülmüş değil.** Vizyonun kalbi bu ve elimizde yok.
- ❌ `vergi_no` %0 → eşleştirme olasılıksal. Pazarlamada "tahmini eşleşme" denebilir; **faturalamada kullanılamaz**.
- ⚠️ Canlı veritabanı boş (0 byte), gerçek veri yedekte. Ayrı sorun, ayrı görev.
- ⚠️ EKAP v2 geçişi sürüyor; bugün çalışan `.aspx` yarın kapanabilir. Sözleşme testi bu yüzden şart.

**En kısa yol:** Aşama 0 (erişimi sabitle) → Aşama 1 (yükleniciyi ölç). Aşama 1 olumsuzsa 2–3'e yatırım yapmak israf olur.
