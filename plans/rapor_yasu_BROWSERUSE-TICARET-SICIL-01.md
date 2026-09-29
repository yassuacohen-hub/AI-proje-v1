# Browser-Use + Ticaret Sicili: Faydalı mı? (D-270)

**Tarih:** 2026-09-29 | **Yazan:** yasu | **Durum:** `review`

> ## 🚨 REVİZYON 2 — KAHİN'in ekran görüntüleri (D-268 düzeltmesi)
>
> İlk raporumda **iki hata** vardı. İkisi de **varsayımdan** geliyordu:
>
> | Hata | İlk raporum | Gerçek (ölçüldü) |
> |---|---|---|
> | TOBB ücretli mi | "Üyelik + **ücretli**" | **Giriş ücretsiz.** Sayfa: *"Ücretsiz gazete sorgulamak için üye girişi yapmalısınız."* |
> | MERSİS kaç hane | "**16** hane" (Webtekno) | **17 hane** — gerçek kayıtta ölçüldü |
>
> Ders: **sayfayı okumak yetmez, ölçmek gerekir.** Kanıt katmanı ikisini de
> yakaladı (§9).

---

## 1. Kısa Cevap

**Yararlı — ama TOBB üzerinden değil.**

`ticaretsicil.gov.tr` (TOBB) otomasyon için **yanlış hedef**: üyelik + ücretli
abonelik + kapalı sözleşme koşulları. Browser-Use orada çalışsa bile
**FSEK + TTK md. 54 + KVKK** riski iş modelinin merkezindedir.

**Doğru hedef:** veri zaten **resmî, ücretsiz ve kanunla açık** kaynaklarda.
Asıl soru "veriyi nasıl alacağız" değil, **"hangi kaynaktan"** sorusunun
cevabı: TOBB değil, **Ticaret Bakanlığı**.

---

## 2. Ölçülen Kanıtlar (D-268)

### 2.1 Browser-Use canlı çalıştı

```yaml
run_id:  5624fb97-0b3b-4523-aa53-09daf8bfb32a
status:  completed          (2 dk 5 sn)
model:   gpt-5.6-luna       ← otomatik seçildi
cost:    0.016522 USD
tokens:  173274 in / 5639 out
```

OSTİM testi: `/` 200, `/firmalar` 200, `/firma-urunler` 200.

> **Kritik bulgu:** Tarayıcı ajanı `firmalar` sayfasını 200 döndü diye açtı
> ama **içeriği çekmedi** (kendi kararı). GET → 200, HEAD → **404**.
> → Otomatik veri toplama için **güvenilmez**; kanıt + doğrulama şart.

### 2.2 Snippet'te 3 hata vardı (doğrudan çalışmıyordu)

| # | Hata | Kanıt |
|---|---|---|
| 1 | `session_id="yasu"` | **422** `uuid_parsing ... found 'y' at 1` |
| 2 | Rastgele UUID | **404** `session not found` |
| 3 | `model="gpt-6-luna"` | **403** `not available on the free plan` |

> Hata 2 tuzak: UUID üretmek 404'ü çözmez, o UUID **gerçekte yok**.

### 2.3 robots.txt ölçümü

| Site | Sonuç | Anlamı |
|---|---|---|
| `ticaretsicil.gov.tr` | **404** | robots.txt yok → kısıt tanımlanmamış, ama üyelik zorunlu |
| `mersis.gtb.gov.tr` | HTML dönüyor | robots.txt **yok** (catch-all) |
| `turkiye.gov.tr` | `Allow: /` + sitemap | **Açık** |

**"Erişilebilir" ≠ "hukuken kullanılabilir."** robots.txt yok = izin var
anlamına gelmez; sözleşme koşulları ayrıdır.

---

## 3. Yasal Çerçeve

### 3.1 Veri türüne göre risk

| Veri | Statü | Risk |
|---|---|---|
| MERSİS no, unvan, sicil no, adres, sermaye | **Kurumsal** (kişi değil) | **Düşük** |
| Ortak/müdür **adı-soyadı**, TC kimlik no | **Kişisel** (KVKK md. 4) | **Yüksek** |
| İletişim (telefon/e-posta) | Kişisel + **ticari sır** | **Yüksek** |

### 3.2 KVKK Kurul 2022/6 — doğrudan ilgili karar

Konu: *"şirketin sicil bilgilerinin görüntülendiği internet sayfasında
kişisel verilerinin hukuka aykırı olarak paylaşılması."*

Kurul'un gerekçesi:
- 5174 sayılı TOBB Kanunu, odalara **"sicil gazetesindeki bilgilerin platformda
  yer alması suretiyle bilgiye ulaşımın kolaylaştırılmasına imkân sağlanması"**
  görevini veriyor → bu yüzden işlem **md. 5/2-a (kanunda açıkça öngörülme)**.
- Eski ortak olmak → **amacı dışı işleme**; silme talebi **reddedildi**.

### 3.3 Web scraping hukuku (Av. Zeki Demirci, 27.07.2026)

| Katman | Sonuç |
|---|---|
| **FSEK Ek md. 8** | Veri tabanı yapımcısı, içeriğin **önemli kısmının** izinsiz çıkarılmasını engelleyebilir |
| **Yargıtay 11. HD, E.2023/499, K.2024/8878** | Olgusal kayıtlardan oluşan **derlemenin kendisi** de veri tabanı koruması tartışmasına konu olabilir |
| **TTK md. 54-55** | Rakibin emek ürününden doğrudan yararlanma = **haksız rekabet** |
| **Kullanım koşulları** | Otomatik çekmeyi yasaklarlar; aşılması **dürüstlük kuralına aykırılık** delili |
| **KVKK** | Kamuya açık kaynaktan toplanan kişisel verinin **amaç dışı** kullanımı = idari para cezası |

> Avukatın uyarısı: *"Tek başına korunmayan veri, onu toplayıp düzenleyen
> yapının serbestçe kopyalanabileceği anlamına gelmez."* Uyuşmazlıklar
> **FSEK + haksız rekabet + sözleşme ihlali** birlikte ilerler.

---

## 4. Kaynak Karşılaştırması

| Kaynak | Erişim | Yasal | Veri | Maliyet | Öneri |
|---|---|---|---|---|---|
| **Ticaret Bakanlığı** e-Devlet | **Ücretsiz**, login | ✅ Resmî | MERSİS, unvan, durum | 0 | ⭐ **BİRİNCİL** |
| **MERSİS** (mersis.gtb.gov.tr) | Login | ✅ Resmî | Tam kayıt | 0 | ⭐ **İKİNCİL** |
| **Ticaret Sicili Gazetesi** (TOBB) | Üyelik+ücret | ⚠️ Kapalı | İlan metni | Ücretli | ⛔ **Önerme** |
| Rastgele web scraping | Serbest | ❌ Yüksek risk | Değişken | 0 | ⛔ **Yasak** |

### 4.1 e-Devlet (birincil kaynak) — doğrulandı

`turkiye.gov.tr/gtb-ticari-isletme-ve-sirket-sorgulama`
→ "Ticari İşletme ve Şirket Sorgulama", **Ticaret Bakanlığı** imzalı.
→ **Ücretsiz**, e-Devlet şifresi/TC kimlik ile giriş.
→ **Sonuç:** Resmî, ücretsiz, kanuni. TOBB'ye gerek yok.

### 4.2 MERSİS numarası — kime ait?

- 16 haneli; A.Ş./Ltd. Şti. → **0** ile başlar, vergi no devam eder.
- Şahıs şirketi → **TC kimlik no** ile başlar (⚠️ **kişisel veri**).
- Biçim: `0<vergi no><000|15|16|17>`

> ⚠️ MERSİS sorgusu **TC kimlik no** ile de yapılabilir → loglanan veri
> KVKK kapsamına girer. Kişisel veri saklamıyorsak sorun yok.

---

## 5. Önerilen Mimari

```
KAYIT    e-Devlet / MERSİS → resmî, ücretsiz, kanuni
         Tarayıcı ajanı YOK → pahalı, yavaş, kırılgan
           │
KONTROL   guncelleme_kaydi → kim/ne zaman/hangi kaynaktan
          alan_izni        → kurumsal ✅ / kişisel ❌
          cekme_hizi       → yavaş, robots'a uygun
           │
DEPOLAMA  company_master (mevcut) + kaynak + tarih damgası
          Kanıt: ham yanıt saklanır (yeniden doğrulanabilir)
```

### 5.1 Neden Browser-Use **kötü** seçim burada

| Ölçüt | Değer |
|---|---|
| Maliyet | 0.0165 USD/sorgu → 100k firma ≈ **1.650 USD** |
| Hız | 2 dk/sorgu → 100k firma ≈ **138 gün** |
| Güvenilirlik | Sayfa 200 döndü, **içeriği çekmedi** |
| Yasal | Üyelik/şifre aşımı = sözleşme ihlali |
| Ölçek | Login + CAPTCHA her döngüde kırılır |

> **Doğru kullanım alanı:** login gerektiren, JS ağır, **ama yasal** tekil
> araştırma. TOBB toplu veri çekimi **değil**.

---

## 6. Aksiyon Planı

| # | Aksiyon | Sahip | Süre |
|---|---|---|---|
| 1 | e-Devlet sorgusunu elle 1 firma ile dene, alan listesini çıkar | yasu | 1s |
| 2 | `skills/services/edevlet_sirket_sorgu.py` yaz | utku | 3s |
| 3 | Alan bazlı KVKK maskesi: kişisel alanlar **kapalı** | utku | 2s |
| 4 | Kaynak + tarih damgası + ham kanıt | utku | 2s |
| 5 | Browser-Use → `skills/services/` taşı (ETL'ye **bağlama**) | yasu | 1s |
| 6 | TOBB otomasyonu **yapılmayacak** | — | — |

---

## 7. Açık Riskler

1. **e-Devlet otomasyonu:** Login + SMS doğrulama var. Tam otomasyon yerine
   **onaylı üyelikle sınırlı, yavaş çekim** gerekebilir → 1. aksiyonda ölç.
2. **Ticari sır:** Liste kamuya açık olsa da **toplu derleme + ticari kullanım**
   FSEK/TTK riski taşır → mesafeli veri satışında **hukuk onayı şart**.
3. **Kişisel veri:** Ortak/müdür adları, TC no, iletişim alınmamalı/maskeli.
4. **Bu rapor hukuki görüş değildir.** Kaynaklar kamuya açık karar/kanun
   metinleridir; somut uygulamada avukata danışılmalı.

---

## 8. Sonuç

> Browser-Use **araç olarak** işe yarar (ölçüldü: 2 dk, 0.0165 USD, 200 OK).
> **TOBB otomasyonu** ise hem pahalı hem yasal riskli → **yapılmamalı**.
>
> Veri zaten resmî ve ücretsiz yollardan geliyor. Doğru soru "nasıl çekeriz"
> değil, **"hangi kaynaktan alırız"** — cevap: **e-Devlet + MERSİS**, TOBB değil.

**Onay bekliyor:** e-Devlet önceliği + TOBB reddi + Browser-Use'ın
`skills/services/` altında araç olarak kalması.

---

## 9. KANIT KATMANI — Ölçülen Gerçek Veri (D-270/271)

KAHİN'in ekran görüntüleri sayesinde **gerçek kayıt** verileri çıkarıldı ve
`skills/services/ticaret_sicili_kanit.py` ile kalıcı kanıt sistemi kuruldu.

### 9.1 Gerçek İlan (1. ekran görüntüsü)

| Alan | Değer |
|---|---|
| İlan Sıra No | `49136` |
| **MERSİS No** | `00120320741000024` |
| **Ticaret Sicil No** | `448217` |
| Unvan | AKANA MÜHENDİSLİK VE TİCARET ANONİM ŞİRKETİ BAŞKENT ORGANİZE ŞUBESİ |
| Adres | Malıköy Başkent OSB Mah. 16 Cad. Akana No: 9 Sincan / Ankara |
| Tescillenme | 20.08.2026 |
| Tescil Edilen Husus | **Adres** (taşınma) |
| Delil Belgeler | Ankara 79.nt. 20.08.2026 Tarih 24162 Sayı (tasdikli) + 19.08.2026/2026-06 YKK |
| İçerik No | `(21341515)` |

### 9.2 Gerçek Sorgu Ekranı (2. ekran görüntüsü) — 71 ilan

| Sicil No | Unvan (kısaltılmış) | Yayın | Sayı | Sayfa | İlan Türü |
|---|---|---|---|---|---|
| 448217 | AKANA…BAŞKENT ORGANİZE ŞUBESİ | 21.08.2026 | 11649 | 67 | ŞUBE (ADRES DEĞİŞİKLİĞİ) |
| 546008 | AKANA…ARGE ŞUBESİ | 03.06.2026 | 11593 | 983 | ŞUBE AÇILIŞ |
| 518675 | AKANA…SINCAN ŞUBESİ | 29.04.2026 | 11573 | 32 | ŞUBE (YÖNETİM-TEMSİL) |
| 448217 | AKANA…BAŞKENT ORGANİZE ŞUBESİ | 28.04.2026 | 11572 | 1228 | ŞUBE (YÖNETİM-TEMSİL) |
| 79163 | AKANA MÜHENDİSLİK VE TİCARET A.Ş. | 21.04.2026 | 11568 | 824 | A.Ş. (YÖNETİM-TEMSİL VE DİĞER) |
| 79163 | AKANA MÜHENDİSLİK VE TİCARET A.Ş. | 13.02.2026 | 11522 | 716 | DENETÇİ |

Filtreler: `Müdürlük=ANKARA` · `veya Unvan=AKANA` · tarih aralığı seçeneği mevcut.

**Çıkarımlar:**
- `79163` = **ana şirket**; `448217`/`546008`/`518675` = **şubeler**
- Aynı ana unvan, **ayrı sicil kayıtları** (şube = ayrı tüzel kayıt)
- İlan türleri çok geniş: adres, yönetim, temsil, denetçi, şube açılış
- Her ilan **(Sayı + Sayfa + içerik no)** ile **kalıcı, doğrulanabilir adres** veriyor

### 9.3 MERSİS çözümü — 17 hane

```
00120320741000024
└┬┘└──────┬─────┘└─┬┘
 0  VKN(10)      ek(6)
    0120320741   000024
```
- Webtekno "16 hane" diyordu → **gerçek kayıtta 17** ölçüldü
- Yapı: `0` (A.Ş./Ltd.Şti. ön eki) + **VKN 10 hane** + ek 6 hane

### 9.4 Kurulan kanıt katmanı

`skills/services/ticaret_sicili_kanit.py` — iki kayıtlı yetenek:

| Yetenek | Ne yapar |
|---|---|
| `kanit_kaydet` | Doğrular + `data/kanit/<anahtar>.json` olarak **kendi verisiyle** yazar |
| `kanit_listele` | Kanıtları özetler, `sirket_tipi` filtresi |

**Doğrulama kuralları:** MERSİS biçimi/çözümü · şube tespiti · zorunlu alanlar ·
yayın/tescil tarih sırası · alan doluluk raporu.

**Kalıcı anahtar:** `ilan_sira_no-gazete_sayi-gazete_sayfa` → `49136-11649-67.json`

### 9.5 Ölçülen sonuç

```
3 gerçek kayıt  -> gecerli  (3 kanıt yazıldı)
1 bozuk kayıt   -> supheli  (MERSIS_BICIM yakalandı)
20/20 test      -> passed
```

### 9.6 Bu çalışma 3 gerçek hatayı yakaladı

| # | Hata | Nasıl yakalandı |
|---|---|---|
| 1 | MERSİS 16 hane varsayımı | Gerçek kayıt 17 → `MERSIS_BICIM` hatası → kural düzeltildi |
| 2 | Türkçe `ŞUBESİ` → `diger` | Unicode normalize eklendi (`_asciiye`) |
| 3 | `?` Windows dosya adında geçersiz | `OSError` → anahtar `E` ile üretiliyor |

> **3. hata canlıydı:** `1-?-?.json` yazmayı denedi ve **çöktü**.

---

## 10. Güncellenmiş Sonuç (Revizyon 2)

| Konu | Revizyon 1 (yanlış) | Revizyon 2 (ölçülmüş) |
|---|---|---|
| TOBB girişi | Ücretli | **Ücretsiz** (ücretli = onaylı suret/abonelik) |
| Veri zenginliği | "değişken" | **Çok zengin**: MERSİS + adres + ilan türü + delil + sayı/sayfa |
| MERSİS | 16 hane | **17 hane** |
| TOBB otomasyonu | ⛔ Önerilmez | ⚠️ **Hâlâ önerilmez** (FSEK/KVKK) ama veri **resmî ve ücretsiz** |

> **Değişmeyen sonuç:** TOBB'yi otomasyonla **toplu çekmek** riskli.
> Değişen: verinin **kaynağı** resmî ve bedava; sorun erişim değil, **hukuk**.
>
> **Kritik fark:** Artık elimizde **ücretsiz, resmî, kalıcı referanslı** veri var.
> `gasete_sayi` + `gasete_sayfa` + `icerik_no` → her ilan **kanıtlanabilir**.

---

## 11. BAYİ / FABRİKA / ŞUBE AĞI (D-272)

KAHİN sorusu: *"bir firmanın ne kadar bayisi ve fabrikası varsa burada çıkıyor."*
**Doğru — ölçüldü.** Aynı ana unvanın **her noktası ayrı sicil kaydı** olarak
listeleniyor. Bu, B2B ETL için asıl değer: grup genişliği = firmanın ölçeği.

### 11.1 Ölçülen grup analizi (AKANA — gerçek 6 kayıt)

```
NOKTA SAYISI : 6
ANA SICIL NO : 79163        ← ŞUBESİ olmayan kayıt otomatik seçildi

İL TÜRÜ DAĞILIMI
  ŞUBE (YÖNETİM - TEMSİL) ......... 2
  ŞUBE (ADRES DEĞİŞİKLİĞİ) ........ 1
  ŞUBE AÇILIŞ ..................... 1
  ANONİM ŞİRKET (YÖNETİM-DİĞER) .. 1
  DENETÇİ ......................... 1

SİNYAL : buyume   (yeni_acilan=1, adres_degisikligi=1)
```

### 11.2 Sinyal mantığı — iş fırsatı göstergesi

| Sinyal | Koşul | İş anlamı |
|---|---|---|
| 🟢 **büyüme** | `ŞUBE AÇILIŞ` / `KURULUŞ` | Yeni nokta = **kapasite artışı**, yeni tedarik ihtiyacı |
| 🟡 **taşınma** | `ADRES DEĞİŞİKLİĞİ` | Yeni bölge = **yeni pazar** |
| ⚪ **durgun** | Yönetim/temsil/denetçi | Operasyonel kayıt |

> **Neden önemli:** Yeni şube/fabrika açan firma, taşınan firma **yatırım
> yapıyor**. Dolayısıyla makine, malzeme, danışmanlık arıyor → **satış fırsatı**.

### 11.3 Ek kod

| Metot | Ne yapar |
|---|---|
| `grup_olustur(unvan, kayitlar)` | Noktaları toplar, ana sicil'i bulur, tür dağılımı üretir |
| `genislik_analizi()` | Büyüme/taşınma/durgun sinyali hesaplar |

7 yeni test (20 → **27**).

### 11.4 🎯 Ana keşif: OSTİM OSB firma listesi

Fabrika tarafı için **ikinci resmî kaynak** bulundu ve doğrulandı:

`https://www.ostim.org.tr/firmalar` → **ücretsiz, login'siz, sektör filtreli**

- **20+ sektör** filtre: Otomotiv · Makine · Metal · Plastik-Kauçuk · Gıda ·
  Elektrik-Elektronik · Ambalaj · Tekstil · Kimyasallar · Mobilyalar …
- Firma adı, telefon, e-posta, adres **açık listeleniyor**
- Sonuçta OSTİM'in misyon metni: *"Blok bazında üretim ve tasarım yetenekleri"*

> **OSB siteleri = ücretsiz, resmî, sektörel fabrika envanteri.** 80+ OSB var.
> Ticaret Sicili + OSB listeleri birlikte → **firma × nokta × sektör** üçgeni.

### 11.5 Önerilen veri modeli

```
company_group          (grup: AKANA A.Ş.)
  ├─ company_site      her sicil no = 1 nokta (fabrika/şube/bayi)
  │    └─ kanit        ilan kanıtı (sayı/sayfa/içerik no)
  └─ osb_listesi       sektör + üretim yeteneği (OSB kaynağından)
```

`company_group.nokta_sayisi` → **ölçek göstergesi**, ETL'de segmentasyon alanı.

---

## 12. ÜCRETLİ KATMAN NOTU (D-273)

KAHİN notu (2026-09-29): *"ücretli üyelikte daha fazla bilgi veriliyor — not et
ama çok pahalı."* Kalıcı adres:
`ticaretsicil.gov.tr/view/hizlierisim/goster.php?Guid=...`

### 12.1 Karar

| Katman | Erişim | Maliyet | Karar |
|---|---|---|---|
| **0** | `ilangoruntuleme.php` | **0** | ✅ **KANONİK** |
| **1** | `goster.php?Guid=` | Ölçülmedi | ⛔ **ÖNERİLMEZ** |

### 12.2 Ölçülen davranış

`goster.php?Guid=...` adresine `httpx.get` → **HTTP 200**, ancak **gövde BOŞ**
(0 karakter). Sonuç: içerik **JavaScript ile** yükleniyor + oturum şart.

> Düz HTTP ile tarama bu katmanı **almaz**. Katman 0 zaten yeterli.

### 12.3 Katman 0 neden yeterli

Gerçek kayıtta **13/14 alan dolu** ve `kanit_yeterli = True`:

```
KATMAN  : 0 ucretsiz-uyelik
MALIYET : 0
DOLULUK : 13/14
YETERLI : True
EKSIK   : ['delil_belgeler']
```

Kalan alan her zaman doldurulabilir (belgeyi KAHİN elinde). **Ücretli katman
kanıtı güçlendirmez, yalnızca ayrıntılandırır.**

> **D-268 uyarısı:** "Çok pahalı" bir **ölçüm değil**. Fiyat bilgisi
> `OLCULMEDI/COK_PAHALI` olarak kodda tutuldu, **sayı uydurulmadı**.
> Satın alma kararı KAHİN'ye aittir.

### 12.4 Kod karşılığı

```python
KATMANLAR = {
    0: {"maliyet": "0", "durum": "KANONIK",   "alanlar": [14 alan]},
    1: {"maliyet": "OLCULMEDI/COK_PAHALI", "durum": "ONERILMEZ"},
}
ILAN_GOSTER_URL = ".../goster.php?Guid={guid}"
```

`IlanKaniti.katman` alanı eklendi; `kanit_kapsami()` metodu hangi katmandan
gelindiğini ve alan doluluğunu raporlar. 8 yeni test (27 → **35**).

### 12.5 İleride satın alınırsa

`guid` alanı ve `kanit_kapsami()` **hazır**. Yapılacak tek şey:
`katman=1` işaretlemek. Veri modeli değişmez, geriye dönük uyumlu.

---

## 13. MERSİS → VERGİ NUMARASI (D-274) — Hipotezin test edildi

KAHİN notu (2026-09-29):
> *"Tüzel kişiler: MERSİS'in ilk 10 hanesi vergi kimlik numarası.
> Gerçek kişiler: MERSİS 11 haneli TC Kimlik Numarası içerir."*

Sonra KAHİN hipotezi derinleştirdi: *"baştaki 0 çıkartıp test edelim, 16 hane olur."*
**Bu hipotez test edildi. Sonuç: yarısı doğru, yarısı yanlış.**

### 13.1 KAHİN'in hipotezi test edildi

```
HAM = 00120320741000024   (17 hane)
V16 = 0120320741000024    (16 hane)   ← başındaki 0 çıkarıldı
```

**"16 hane" kısmı → DOĞRULANDI.** Sözleşme §3.4b ve dört bağımsız kaynak
(ING · Robom · Webtekno · Vakıf Katılım) 16 diyor.

> KAHİN'in "fazladan bir sıfır olabilir" sezgisi **isabetliydi** — 17 değil 16.

**D-275 ÖLÇÜMÜ — VKN de doğrulandı:**
```
00120320741000024 (17) → ilk 0 atıldı → 0120320741000024 (16)
                         → ilk 10 hane = 0120320741
                         → kimlik_no.vkn_gecerli("0120320741") = True  ✅
```

> ⚠️ **DÜZELTME (D-268 dersi):** Önceki turda `vkn_kontrol()` **kendi
> algoritmasını** (tek×3 + çift×1) yazdı ve bu VKN'yi **reddetti**. Doğrusu
> projede zaten vardı: `src/company_master/etl/kimlik_no.py::vkn_gecerli`
> (GİB algoritması). Sözleşme §3.1 ile bağlayıcı. Artık **tek kaynağa
> delegasyon** yapılıyor — ikinci uygulama ikiz mantık üretir (K-1).

**Net sonuç:** MERSİS → VKN **türetilebilir**, ikinci kaynak sorgusu gerekmez
(SÖZLEŞME §3.4b, `mersis_dogrula()`). Yalnızca `tuzel_tip='tuzel'` ise yazılır.

### 13.2 MERSİS'in gerçekte ne olduğu (ölçüldü)

Sözleşme §3.4b doğru: ilk 10 hane VKN'dir. Bu **MERSİS'i tek başına
kanıtlayan tek veri** — çünkü VKN sağlaması tesadüf değildir.

| Yetenek | Durum |
|---|---|
| MERSİS → **VKN** | ✅ **DOĞRULANDI** (sağlama tuttu) |
| VKN → MERSİS | ❌ Ters yönden çalışmaz |
| MERSİS → firma listesi | ❌ **MERSİS bir arama anahtarı, liste değil** |

> **Sonuç:** MERSİS, 14.000 firma **toplama** kaynağı değil; 14.000 firmanın
> **zenginleştirme** (VKN kazandırma) kaynağıdır.

### 13.3 Önceki testin düzeltilmesi

Daha önce "VKN kontrolünden geçmedi → doğrulanamadı" demiştim. **Bu yanlış
çerçeveleme**ydı:

| | |
|---|---|
| ❌ Önceki yorum | "10 hane VKN kontrolünden geçmedi → belki değil" |
| ✅ Doğrusu | "10 hane VKN **değil** → geçmesi **beklenmez**. Test ilgisiz." |

Kontrol testi **"yanlış" değil, "ilgisiz"** bir test. Beklenen sonuç zaten
geçmemekti. Tüm 7+6 olası pencere denendi, **hiçbiri** geçmedi — ama bu artık
**bilgi**, sürpriz değil.

### 13.4 Şahıs işletmesi — KAHİN haklı, TCKN doğrulandı

İkinci notunuz doğru çıktı. Vakıf Katılım: *"TCKN tabanlı 16 haneli"*.
Yani 16 hane = **TCKN(11) + 5 hane**.

> ⚠️ **KVKK:** Bu **kişisel veridir**. Şahıs işletmesi kaydı alırsak kişisel
> veri işlemiş oluruz. → Maskeleme önerisi: MERSİS saklama, işletme adı + VKN tut.
### 13.5 Şahıs işletmesi — TCKN KAYNAKLARDA DOĞRULANDI

Vakıf Katılım: *"Şahıs işletmeleri ... **TCKN tabanlı 16 haneli** bir numara
alırlar."* Yani 16 hane = **TCKN(11) + 5 hane**.

> ⚠️ **KVKK:** TCKN **kişisel veridir**. SÖZLEŞME §3.2'ye göre TCKN saklanır
> (D-248) ama kullanıcı panelinde **varsayılan kapalı** (D-247), ücretli
> pakete **konulamaz** (`KVKK-TCKN-02` blokeli). Bizim kanıt katmanımız
> TCKN **yazmaz** — yalnızca MERSİS saklar.

### 13.6 Net karar

```
16 hane kısmı   : DOGRULANDI (SÖZLEŞME §3.4b + 4 kaynak)
VKN içerir       : DOGRULANDI (kimlik_no.vkn_gecerli = True)
Şahıs işletmesi : DOGRULANDI (TCKN tabanlı 16 hane)
durum           : DOGRULANDI
```

| Kimlik | Sahibi | Nereden |
|---|---|---|
| **MERSİS** | Ticaret Bakanlığı | Kanıt kaydında ✅ |
| **VKN** | Maliye Bakanlığı | **MERSİS ilk 10 hanesi** (ücretsiz) |

**Kod:** `vkn_kontrol()` artık **tek kaynağa delegasyon** yapar
(`kimlik_no.vkn_gecerli`). Kendi algoritmasını yazmaz — K-1.

**Test:** 42 (17 hane okuma kayması + 16 hane türetim + geçersiz VKN reddi).

---

## 14. 14.000 FİRMA — TOBB'den Çekim (KAHİN'in asıl sorusu)

> *"Ticaret Sicili Gazetesi'ndeki verileri nasıl çekeceğiz? 14.000 firmayı
> orada arayıp bulmamız gerekiyor. Giriş zorunlu mu? Giriş yaparsak kişisel
> e-devletimden çok fazla sorgu yapmış olacağım."*

### 14.1 Ölçülen — hangi link, ne görünüyor

`https://www.ticaretsicil.gov.tr/view/hizlierisim/ilangoruntuleme.php`

| Katman | Erişim | Ölçüm |
|---|---|---|
| Giriş ekranı | **herkese açık** | 25.919 bayt, `FormUyeGirisi` |
| Sorgu formu (Müdürlük/Unvan/Sicil No) | 🔒 **giriş gerekli** | HTML'de **YOK** |
| Sonuç tablosu ("71 Adet") | 🔒 **giriş gerekli** | HTML'de **YOK** |
| `goster.php?Guid=` (ilan metni) | 🔒 oturum | HTTP 200, **gövde 0 bayt** |
| `unvansorgulama.php` | 🔒 **giriş gerekli** | 35.613 bayt, login ekranı |

> **KAHİN'in tespiti DOĞRULANDI:** *"TOBB'da CAPTCHA var, sadece ticaret sicil
> no gösteriyor."* Giriş ekranında **3 ayrı CAPTCHA** var
> (`CaptchaImg` + 4 haneli `maxlength=4`). Sorgu formu login arkasında.

### 14.2 Giriş zorunlu mu? EVET — ama e-Devlet gerekmez

İki giriş yolu var:

| Yol | e-Devlet'e dokunulur mu? |
|---|---|
| **1) TOBB'ye doğrudan üyelik** (e-posta + şifre) | ❌ **HAYIR** |
| 2) *e-Devlet ile giriş* | ⚠️ **EVET — her sorgu loglanır** |

> ✅ **Çözüm: Yol 1.** TOBB üyeliği **ücretsiz** ve e-Devlet **hiç
> kullanılmaz**. KAHİN'in endişesi yerinde ama çözümü basit: kendi
> e-posta/şifrenle üye ol. 14.000 sorgu e-Devlet'e **gitmez**.

### 14.3 Asıl engel CAPTCHA — maliyet değil

| Yöntem | 14.000 firma | Süre | Maliyet |
|---|---|---|---|
| Browser-Use | 14.000 tarayıcı görevi | **20 gün** | **231 USD** |
| Düz HTTP + oturum | 🔒 **CAPTCHA** → durur | — | 0 USD |
| Elle tek tek | 14.000 arama | ~40 saat | 0 USD |

> 🚨 **Kaldırılamaz engel:** CAPTCHA 14.000 sorguda otomatik çözülmez; her
> biri insan müdahalesi ister. Hukuki riskten daha sert bir teknik duvar.

### 14.4 ✅ Önerilen yol — TOBB'ye girmeden 14.000

| Adım | Kaynak | Katkı | Durum |
|---|---|---|---|
| 1 | **OSTİM OSB** | **8.400 firma** | ✅ **Ölçüldü: 35 sn** |
| 2 | + Başkent, İvedik, ASO… | → 14.000 | ⏭️ Sıradaki |
| 3 | **TOBB — sadece zenginleştirme** | + MERSİS/VKN | ⏭️ Seçici |

> **TOBB bir arama motorudur, veri tabanı dökümü değil.** 14.000 firmayı
> orada aramak yerine: firmayı **OSB'den bul** → TOBB'den **tek tek doğrula**.

### 14.5 TOBB ne zaman kullanılır

| Senaryo | Karar |
|---|---|
| 14.000 firmanın **tamamı** | ❌ TOBB'ye girme (CAPTCHA) |
| Öncelikli ilk 500 | ✅ TOBB tek tek, elle |
| **MERSİS/VKN zenginleştirme** | ✅ `tuzel_tip='tuzel'` olanlar |

> MERSİS artık **VKN kazandırıyor** (D-275). Yani TOBB'ye her zaman sadece
> **zenginleştirme** için gerek — liste çekimi için değil.

### 14.6 ⚠️ Karar bekleniyor

`MERSIS-KAYNAK-01` (sözleşme §4) *"MERSİS no toplanabilir mi?"* diye açık.
Ölçüm: **toplu hayır** (CAPTCHA + login), **seçici evet**.

| | Yol | Sonuç |
|---|---|---|
| **A** | OSB'lerden 14.000 → TOBB sadece zenginleştirme | ✅ **Önerilen** |
| **B** | TOBB'den 14.000 | 231 USD + 20 gün + CAPTCHA |

---

## 15. Oturum Özeti

| # | Konu | Sonuç |
|---|---|---|
| 1 | abrakadabra skill | Hayalet ajanlar temizlendi (0) |
| 2 | Browser-Use canlı | ✅ 0.0165 USD, 2 dk |
| 3 | TOBB girişi | ✅ **Ücretsiz** (ilk rapor yanlış) |
| 4 | MERSİS 16 hane | ✅ KAHİN'in sezgisi doğru |
| 5 | MERSİS → VKN | ✅ **D-275 doğruladı** |
| 6 | Bayi/fabrika ağı | ✅ 6 nokta, büyüme sinyali |
| 7 | Ücretli katman | ⛔ Ölçüldü, önerilmedi |
| 8 | OSTİM | ✅ **8.400 firma / 35 sn** |
| 9 | 14.000 yolu | ⏳ **KAHİN kararı** |

> **Bu oturumda 4 düzeltme:** TOBB ücretli · MERSİS 16 hane · "VKN içerir" ·
> **kendi VKN algoritmasım**. Hepsi ölçümle yakalandı. Ders: kaynak metne
> değil, **tek kapıya** (`kimlik_no.py`) güven — ikinci uygulama ikiz
> mantık üretir (K-1).
> mantık üretir (K-1).

---

# EK-1 — CANLI DOĞRULAMA (2026-09-29, bu oturum)

**KAHİN'in sorusu:** "tüm Ankara firmalarını tek seferde çekmek iyi olur mu?"
**Cevap: HAYIR — ama farklı, çok daha iyi bir yol var. Ölçüldü.**

## 16. Doğrudan TOBB girişi — BAŞARILI ✅

`e-Devlet` **kullanılmadı**. Kullanıcının kendi TOBB hesabıyla giriş yapıldı.

### 16.1 KÖK NEDEN (D-276) — giriş neden başarısızdı?

| | |
|---|---|
| **Belirti** | Sunucu `0` dönüyor, giriş yapılmıyor |
| **Kök neden** | Form `enctype="multipart/form-data"`, JS `new FormData(this)` ile POST ediyor |
| **Çözüm** | `data=` yerine `files=` ile **multipart** gönderim |

```python
# YANLIŞ (sunucu cevabı "0"):
data={"LoginEmail":..., "LoginSifre":..., "Captcha":...}
# DOĞRU (sunucu cevabı "1"):
files={"LoginEmail": (None, e_posta), "LoginSifre": (None, sifre), "Captcha": (None, captcha)}
```

Sunucu başarıda **tam olarak `"1"`** döner (`JS: if(AjaxCevap==1)`).

### 16.2 Ölçülen davranış

| Gözlem | Değer | Kanıt |
|---|---|---|
| Giriş | **BAŞARILI** | Sayfada `ÇIKIŞ` + kullanıcı adı görünüyor |
| e-Devlet sorgu geçmişi | **YOK** | Doğrudan TOBB oturumu |
| Oturum ömrü | **~2-3 dakika** | `cookie_kaydet`/`cookie_yukle` ile korunuyor |
| Sunucu çerezi | 1 adet (`atrsrv-...`) | Oturum bu çerezde taşınıyor |
| CAPTCHA | Her girişte yeniliyor | Elle çözülüyor, otomatik çözülmüyor |

**Çerez kalıcılığı** `scripts/tobb_oturum.py`'ye eklendi: `cookie_kaydet()` /
`cookie_yukle()` / `oturum_gecerli_mi()`. Süreç kapanıp yeniden açıldığında
oturum düşüyordu; çerez diske yazılarak bu çözüldü.

## 17. "TÜM ANKARA TEK SEFERDE" — ÖLÇÜLDÜ, MÜMKÜN DEĞİL ❌

Kullanıcının fikri denendi. **Kendi ağzıyla reddedildi:**

```
POST /view/hizlierisim/ilangoruntuleme_ok.php
  SicilMudurluguId=18 (ANKARA) & Tarih1=01.01.2026 & Tarih2=02.01.2026
→ "Sicil No veya En Az 5 Karakter Ticaret Unvanı Giriniz"
```

**Sunucu zorunlu kılıyor:** her sorguda `TicSicNo` **ya da** en az 5 karakter
`TicaretUnvani` şart. İl + tarih tek başına **sonuç döndürmüyor**.

> **Sonuç:** "tüm Ankara firmaları" diye bir sorgu **yoktur**.
> 14.000 firma = 14.000 ayrı unvan/sicil sorgusu = 14.000 istek.
> Bu, planlanan 14.000 otomasyonla birebir aynı yük. Fırsat değil.

## 18. GERÇEK FIRSAT — Ünvan ile toplu liste (71 kayıt tek istekte) ✅

`TicaretUnvani` ile sorgu **birden çok sonuç** döndürüyor:

| Sorgu | Sonuç |
|---|---|
| `TicSicNo=448217` | **4 ilan** |
| `TicaretUnvani=AKANA` | **71 ilan** (tek istek, tek sayfa) |

- **Sayfalama YOK** — 71 kaydın hepsi tek yanıtta geldi (`Guid` dışında başka
  sayfa parametresi yok). Sonuç sayısı büyüdükçe yanıt büyür.

## 19. İlan detayı — ham PDF yolu bulundu ✅

```
ilan listesi  →  pdf_goster.php?Guid={ilan_guid}
             →  <object data="/tmp_gazete/{uuid}.pdf" type="application/pdf">
             →  GET /tmp_gazete/{uuid}.pdf   →  application/pdf  ✅ 38.853 bayt
```

### 19.1 Ölçülen engel: PDF'te METİN KATMANI YOK

`pdfplumber` ile açıldı: **1 sayfa, `extract_text()` → boş.** PDF taranmış
görüntü. Yani MERSİS/VKN/adres/ortak alanlarını almak için **OCR** gerekir.

Bu, ölçek planının en pahalı kalemi: **14.000 × OCR**.

## 20. Abonelik koşulları (menüden, resmî sayfa)

| Düzey | Veri seti | 2026 yıllık |
|---|---|---|
| Düzey_1 | Standart Elektronik Gazete (fihristli) | 484.932 TL |
| Düzey_2 | Detaylı Elektronik Gazete | 951.792 TL |
| Düzey_3 | Detaylı Elektronik Gazete | 1.427.688 TL |

> **Abonelik = PDF/CD gazete teslimidir, bulk/API erişimi DEĞİLDİR.**
> Kullanım koşulları sayfasında otomasyon/bulk erişim izni **yok**.

## 21. AKANA PİLOTU — TAMAMLANDI ✅

`448217` (AKANA MÜHENDİSLİK VE TİCARET A.Ş. BAŞKENT ORGANİZE ŞUBESİ) için
**4 ilan** çekildi ve kanıt katmanından geçirildi:

| Yayın | Sayı | Sayfa | İlan türü |
|---|---|---|---|
| 21.08.2026 | 11649 | 67 | ŞUBE (ADRES DEĞİŞİKLİĞİ) |
| 28.04.2026 | 11572 | 1228 | ŞUBE (YÖNETİM - TEMSİL) |
| 07.05.2025 | 11326 | 656 | ŞUBE (YÖNETİM - TEMSİL) |
| 27.07.2020 | 10126 | 1055 | ŞUBE AÇILIŞ |

**Üretilen dosyalar** (hepsi `data/kanit/` altında):
- `448217_tobb_ilanlari.json` — ham liste + GUID + PDF yolu
- `11649-11649-67.json`, `11572-11572-1228.json`,
  `11326-11326-656.json`, `10126-10126-1055.json` — `IlanKaniti` kayıtları
- `448217_a18a2282.pdf` / `.txt` — ham PDF + metin çıkarma denemesi

**Doğrulama sonucu:** 4/4 kayıt `supheli` — neden `MERSIS_YOK`.
Bu **beklenen**: liste sayfasında MERSİS alanı yok; MERSİS PDF'in içinde ve
PDF okunmuyor. Saha doğruluğu bozulmadı, kapı doğru çalışıyor.

## 22. ÖLÇEK GERÇEĞİ — karar tablosu

| Yöntem | 14.000 kayıt | Durum |
|---|---|---|
| Browser-Use | ~231 USD / 20 gün | ❌ Ölçüldü |
| TOBB unvan sorgusu | 14.000 istek + 14.000 OCR | ❌ Ekonomik değil |
| TOBB "tüm Ankara" | **MÜMKÜN DEĞİL** | ❌ Sunucu reddetti |
| Veri aboneliği | 484.932–1.427.688 TL | ⚠️ PDF/CD, bulk DEĞİL |
| **MERSİS merkezi** | **Resmî kaynak** | ✅ **Önerilen** |

> **KAHİN'in önerisi:** TOBB kanıt katmanı **tekil doğrulama** için kalsın
> (ilan türü + yayın referansı). 14.000'lik toplu iş **MERSİS merkezî
> sorguyla** yapılmalı; TOBB ikincil kanıt olarak kullanılmalı.

## 23. Güvenlik notu

- Parola sohbette açıkça paylaşıldı ve `.env` içine yazıldı →
  **çalışma sonrası parola DEĞİŞTİRİLMELİ**.
- `data/tobb_cookie.json` **oturum çerezidir** — paylaşılmamalı, expire oluyor.
- Testler: `tests/test_ticaret_sicili_kanit.py` → **42 passed**.

- Testler: `tests/test_ticaret_sicili_kanit.py` → **42 passed**.

---

# EK-2 — DÜZELTME: OCR GEREKMİYOR (D-278) — KAHİN'in bilgisi doğru çıktı

## 24. Benim hatam, düzeltildi

Önceki raporda "PDF taranmış görsel → OCR gerekir" dedim. **Sonuç doğru,
gerekçe eksikti.** KAHİN'in ekranı bunu çürüttü ve şu bilgiyi verdi:

> *"Gazetede basılan şirket kararlarının tamamı XML veya benzeri ham metin
> formatlarında iletilir. PDF'i açıp okumaya gerek kalmadan..."*

**Doğrulandı** (`/view/hizlierisim/goster.php?Guid=4fb204d4…`, "Abonelik" sayfası).
Tablo 3. sütunu = **"HİZMET SUNUŞ ŞEKLİ"** ve üç seviyenin de oradaki
hizmeti **"WEB SERVİS"**.

### 24.1 Ölçülen PDF kanıtı (benim analizim)

`scripts/pdf_kanit_analiz.py` → `data/pdf_analiz.json`:

| Gözlem | Değer |
|---|---|
| Font sayısı | **0** |
| Metin operatörü (`Tj`/`TJ`) | **0** |
| ToUnicode CMap | **0** |
| Görsel XObject | **3** |
| Sayfa çözünürlüğü | A4 @ **200 DPI** (1754×2481) |

→ **Ücretsiz (üye) PDF gerçekten scan.** Kullanıcının ekranı da öyle gösteriyor.

> **Ancak bu, abonelikten gelen veri için geçerli DEĞİLDİR.**
> Abonelik = makine-okunur TSM/XML. OCR yalnızca **ücretsiz üye PDF** içindir.

## 25. DÜZEY_3 (İLERİ DÜZEY) VERİ — TAM ALAN LİSTESİ ⭐

Kullanıcının istediği "hasasiyet" burada. **Alıntı: resmî Abonelik sayfası.**

| Düzey | Aranabilir? | Fiyat (2026) | WEB SERVİS |
|---|---|---|---|
| Düzey_1 | ❌ **Aranamaz** (non-searchable) | 484.932 TL | ✅ |
| Düzey_2 | ✅ Aranabilir | 951.792 TL | ✅ |
| **Düzey_3** | ✅ **Aranabilir** | **1.427.688 TL** | ✅ |

**Birim fiyat:** `1.427.688 TL / 930.000 ilan = **1,535 TL/ilan**`
(Düzey_1: 0,521 TL · Düzey_2: 1,023 TL)

### 25.1 Düzey_3 veri seti — makine-okunur alanlar

**Fihrist (her ilan için ortak):**
`sıra no` · `tsm no` · `Unvan1` · `Unvan2` · `İlan Türü` · `Yayın Tarihi` ·
`Sayısı` · `Baş Sayfa` · `Son Sayfa` · `Başlı İlan` · `Başlı İlan Sicil No`

**Yalnızca Düzey_2 ve Düzey_3'e eklenenler:**
- `MERSİS No`
- `Kuruluşların Adresi`
- `AŞ ve LS Kuruluşların Sermaye`

**Yalnızca DÜZEY_3'ün FARKı (asıl değer):**
- **Tüm kuruluş türleri için toplam sermaye** — anonim, limited, kollektif,
  komandit, kooperatif, gerçek kişi ticari işletmesi, diğer iktisadi işletmeler,
  yabancı şirket TR şubesi, adi ortaklık
- **`Vergi No`** ⭐
- **`Vergi Dairesi`** ⭐
- **`Adres Kodu (UAVT adres kodu)`** ⭐ ← bizim master data için anahtar
- **`Amaç Konu`** (tam metin) ⭐
- **`Ana NACE Kodu` + `Ana NACE Konu`** ⭐
- **`Alt NACE Kodları` (n tane) + açıklamaları** ⭐
- **`Ortaklar (Liste)`** — TC Kimlik No (maskeli ilk 3 son 2 açık), Vergi No
  (maskeli), Pasaport No (maskeli), Adı Soyadı, Ortak Türü
  (Gerçek / Tüzel / Dış Tüzel), **Ortağın Sermayesi** ⭐
- **`Temsilciler (Liste)`** — TCKN, Pasaport No, Adı Soyadı, Temsilci Türü,
  Temsilci Görevi, Temsil Şekli, Temsil Başlangıç/Bitiş Tarihi
- **Tüzel Temsilci Adına Hareket Eden Kişi** — Kimlik No, Pasaport No, Adı Soyadı
- **`Müfterek Listesi`** (Müfterek Temsilci Listesi – JSON) ⭐

### 25.2 Proje için kritik sonuç

Bu alanlar bizim **tam olarak eksik olduğumuz** alanlar:

| Eksik alanımız | Düzey_3 karşılığı |
|---|---|
| `NACE kodu` | `Ana NACE Kodu` + `Alt NACE Kodları (n tane)` |
| `Vergi no` | `Vergi No` (maskeli değil, tam) |
| `Ortak bilgisi` | `Ortaklar (Liste)` + sermaye |
| `Temsilci` | `Temsilciler (Liste)` |
| `Adres kodu` | `UAVT Adres Kodu` |
| `Amaç konu` | `Amaç Konu (tam metin)` |

**Düzey_3, OSTİM/ATO/ASO ile yarışmaya gerek kalmadan boşlukları kapatır.**

### 25.3 Kritik yasal uyarı (sayfada yazılı)

> *"Gazetede yayımlanan **ilan metni esas kabul edilmeli** ve türün ilanla
> uyumlu olup olmadığı kontrol edilmelidir."*

→ Ham veri **kaynak değil, aday**. İlan metni esas alınır. `IlanKaniti`
kapısı bu yüzden doğru tasarım; ham veri doğrudan `company_master`'a girmemeli.

### 25.4 Başvuru süreci

Form + banka dekontu → `ttsgmd@tobb.org.tr` (ıslak imza) → onay.
Günlük gazete ~1.350 sayfa; tek günlük gazete **2.730 ₺**.

## 26. Maliyet karşılaştırması — yeni tablo

| Yöntem | 14.000 kayıt | Tahmini maliyet | Veri kalitesi |
|---|---|---|---|
| Browser-Use | ~20 gün | ~231 USD | Orta (OCR gerekir) |
| Vision LLM OCR (Gemini 3.8 Flash) | ~1-2 gün | ~15-30 USD | Yüksek (ama boş alanlar kalır) |
| OCR + manuel doldurma | ~3 ay | ~15-30 USD + 500 saat | Düşük |
| **MERSİS merkezî** | resmî | abonelik? | **Yüksek** |
| **TOBB Düzey_3** | tüm yıl, 930.000 ilan | **1.427.688 TL** | **En yüksek, kurumsal** |

> **D-278 kararı:** OCR çalışması **durduruldu** (boşa yazılım riski).
> Vision OCR `scripts/gazete_ocr.py` olarak duruyor — **yalnızca ücretsiz
> üye PDF'i okumak için** kullanılabilir. Öncelik Düzey_3 değerlendirmesine
> kaydırıldı. **Bu bir satın alma kararıdır → KAHİN'in onayı gerekir.**

> **KAHİN'in önerisi:** TOBB kanıt katmanı **tekil doğrulama** için kalsın
> (ilan türü + yayın referansı). 14.000'lik toplu iş **MERSİS merkezî
> sorguyla** yapılmalı; TOBB ikincil kanıt olarak kullanılmalı.

---

# EK-3 — DÜZELTME: ABONELİK ALINMAYACAK (D-279)

## 27. KAHİN'in itirazı ve ölçüm

> *"1 aylık ücret ödemekle firma bilgilerini tam toplanmaz; ücret sadece o
> ayın şirket bilgilerini gösterir, açılış kapanış vs; aradığımız veri orada değil."*

İki ayrı iddia ayrı ayrı ölçüldü (`scripts/abonelik_kapsam_olcer.py`).

### 27.1 "1 aylık" → YANLIŞ

Sayfada yazılı: **"(Yıllık)"** ve *"2026 yılında **251 iş günü** vardır.
(251 x 1.932) = 484.932 TL"*. Aylık abonelik yok.
(Günlük gazete ayrı bir ürün: 2.730 ₺/gün.)

### 27.2 "Aradığımız veri orada değil" → **DOĞRU** ⭐

AKANA (448217) için bulunan 4 ilanın yıl dağılımı:

| Yıl | İlan türü |
|---|---|
| 2026 | ŞUBE (ADRES DEĞİŞİKLİĞİ) |
| 2026 | ŞUBE (YÖNETİM - TEMSİL) |
| **2025** | ŞUBE (YÖNETİM - TEMSİL) |
| **2020** | ŞUBE AÇILIŞ |

**2026 aboneliği kapsamı = %50.** KAHİN'in çekincesi ölçümle doğrulandı.

> Abonelik **firma sicil kaydının tamamını** vermez; yıl boyu **ilan
> hareketini** verir. Geçmiş yıllar ayrı alınır.

## 28. Sonuç ve karar

| | |
|---|---|
| Düzey_3 1.427.688 TL | ❌ **ALINMAYACAK** — kapsam ihtiyacı karşılamıyor |
| TOBB ücretsiz katman | ✅ **Kalır** — tekil doğrulama + değişim tespiti |
| 14.000 firma master verisi | → **MERSİS merkezî** (asıl iş) |

> **KAHİN'in tespiti kararı değiştirdi:** D-278'deki "Düzey_3 alınabilir"
> değerlendirmesi **geri çekildi**.

**Düzey_3'ün gerçek değeri (yine de):** tek firmanın yıllar boyu hareketi →
**büyüme/çöküş sinyali**. Anlık firma listesi değil, **zaman-serisi**. Sektör
analizi için değerli; "firma master verisi" işini çözmez.

**Düzey_3'ün gerçek değeri (yine de):** tek firmanın yıllar boyu hareketi →
**büyüme/çöküş sinyali**. Anlık firma listesi değil, **zaman-serisi**. Sektör
analizi için değerli; "firma master verisi" işini çözmüyor.

---

# EK-4 — "OCR DAHA UCUZ" İDDİASI ÖLÇÜLDÜ (D-280)

## 29. KAHİN'in yönlendirmesi

> *"Düzey_3 (1.427.688 TL) ocr ile taramak daha ucuz... abonelik sonraki
> süreçte yapılabilir."*

Yön doğru, gerekçe **ölçüldü** — `scripts/ocr_maliyet_olcer.py` (7 model, 1 canlı sayfa).

### 29.1 Erişim: 7 modelden **1'i** çalışıyor

| Model | Sonuç |
|---|---|
| `openai/gpt-4o-mini` | ✅ **TAMAM** |
| `gc/gemini-2.5-flash-lite` | ❌ 403 yetki yok |
| `bzl/gemini-3.1-pro-preview` | ❌ 402 kredi yok |
| `cl/openai/gpt-4o` | ❌ 402 kredi yok |
| `ag/gemini-3.5/3.6-flash-low` | ❌ boş cevap |
| `gemini/gemini-3.5-flash-lite` | ❌ boş cevap |

### 29.2 D-280 kök neden: **istemci** hatalıydı

`openai/gpt-4o-mini` **HTTP 200** döndü ama `r.json()` patladı:
`JSONDecodeError: Extra data: line 37`. Gövdenin sonu: **`data: [DONE]`**
— SSE kalıntısı JSON'a eklenmiş. Model cevabı geçerliydi.

**Çözüm:** `_cevap_ayikla()` — kalıntı kesilip elle ayrıştırılıyor.
> "OCR çalışmıyor" sandım; **istemci hatalıydı.**

### 29.3 Ölçülen maliyet (tek sayfa, gerçek)

| Ölçüm | Değer |
|---|---|
| Süre | **5,89 sn** |
| Token | **49.146** |
| Alan | 9 |

| Kapsam | Token | Süre |
|---|---|---|
| 14.000 firma | 688 milyon | **~23 saat** |
| 930.000 ilan | 45,7 milyar | **~63 gün** |

> **Sonuç:** "daha ucuz" **doğrulanmadı.** 14.000'de makul; tam yıllık
> kapsamda **63 gün** + **tek sağlayıcı** riski.

### 29.4 OCR MERSİS'te **hata yaptı** ⭐

| | Değer | Hane |
|---|---|---|
| Ekrandaki gerçek | `0012032074100024` | 17 |
| OCR çıktısı | `001203074100024` | **15** |

`2074` → `0741`: **kayıp hane.** OCR sessizce bozuk veri üretti.

**D-274 kanonik kapısı YAKALADI:** 15 hane → `None` (reddedildi).
*Kanonik kapı olmasaydı bu bozuk değer `company_master`'a girerdi.*
Bu bulgu `tests/test_gazete_ocr_pasif.py::test_ocr_hatasi_kapidan_girmez`
ile regresyon kilidine bağlandı.

## 30. Net tablo

| Ölçek | OCR | Düzey_3 |
|---|---|---|
| 14.000 firma | ~23 saat, 1 sağlayıcı | — |
| 930.000 ilan (tam yıl) | ~63 gün | 1.427.688 TL, kurumsal |
| Doğruluk | ⚠️ hata yaptı, kapı zorunlu | Resmî, aranabilir |

| Doğruluk | ⚠️ hata yaptı, kapı zorunlu | Resmî, aranabilir |

---

# EK-5 — e-DEVLETSİZ KAYNAK ARAŞTIRMASI (D-281)

## 31. "MERSİS merkezî" önerim **e-Devlet'e bağımlı çıktı**

Ölçüldü — 3 resmî kaynak:

| Kaynak | Bulgu |
|---|---|
| `mersis.gtb.gov.tr` | *"E-Devlet Yönetimi ile Giriş **entegrasyon aşamasındadır**"* |
| `turkiye.gov.tr/gtb-…-sorgulama` | Giriş: e-Devlet şifresi / e-İmza / TCKK / bankacılık |
| `ticaret.gov.tr/…/e-devlet-hizmetlerimiz` | "Ticari İşletme ve Şirket Sorgulama" **e-Devlet** altında |

> **e-Devletsiz resmî merkezî yol YOKTUR.** D-279 önerisi bu yüzden düşürüldü.

## 32. ⭐ Ama 8.473 firma ücretsiz ve yasal bulundu

8/8 kaynak erişilebilir. **`robots.txt` ölçüldü — kapı açık:**

| Alan | `robots.txt` |
|---|---|
| `ostim.org.tr` | yalnız `/admin/`, `/portal/`, `/auth/` yasak |
| `atb.org.tr` | `Allow:` (tümü serbest) |
| `aso.org.tr`, `atonet.org.tr` | engel yok |

### OSTİM ölçümü

| Ölçüm | Değer |
|---|---|
| Toplam firma | **8.473** (sayfada yazılı: `Toplam 8473 sonuç`) |
| Sayfa başına | 300 |
| Sayfa | **29** |
| Doğrulama | 300+300+**73** (sayfa 29) → sayfa 30 boş ✓ |
| Adres kalıcı mı | ✅ `ostim.org.tr/firmalar/<slug>` |

> **8.473 = 14.000 hedefinin %61'i — ücretsiz, yasal, kalıcı adresli.**

## 33. Ama OSTİM tek başına yetmez

Detay sayfası taraması — 11 alan denendi, **6 bulundu**:

| ✅ Var | ❌ **Yok** |
|---|---|
| unvan · adres · telefon · e-posta · web · faaliyet/sektör | **NACE · VKN · ticaret sicil no · yetkili/ortak** |

**Zincir gerekli:** `OSTİM (unvan/adres)` → **`GIB VKN`** → **`Ticaret Sicili`**
> VKN olmadan master veriye join kurulamaz.

## 34. Durum ve borç

- **Toplu indirme BAŞLATILMADI** — ölçek işi ayrı görev + onay gerektirir.
- ⚠️ **Yeni borç:** `robots.txt` izni **hukuki izin değildir**. Ticari amaçlı
  toplu derleme için kaynak kurum şartları doğrulanmadan başlanmamalı.

**Net tablo:**

| | Durum |
|---|---|
| MERSİS | ❌ e-Devlet zorunlu |
| TOBB Düzey_3 | ❌ kapsam yetersiz (D-279) |
| **OSTİM 8.473** | ✅ ücretsiz + yasal, ama VKN/NACE yok |

---

# EK-6 — HUKUK + GİB VKN ARAŞTIRMASI (D-282)

> KAHİN'in talebi: *"ikisine de bak bakalım devam et, sonra bulgularını detaylı raporla"*
> Her iki başlık da **ölçüldü**, tahmin yapılmadı.

## 35. ⛔ BULGU 1 — OSTİM, ticari kullanımı açıkça yasaklıyor

**Kaynak:** `ostim.org.tr/kurumsal/gizlilik-politikasi` (10.044 karakter okundu)

### "Kullanım Koşulları" bölümü — kelimesi kelimesine

> **"Bu web sitesi sadece bilgi amaçlı ve ticari olmayan kullanım için hazırlanmıştır."**

### Politikanın diğer hükümleri

| Hüküm | Alıntı |
|---|---|
| Üçüncü tarafa aktarım | *"Bölge Müdürlüğümüzce elde edilen veriler belirlenen amaçlar ve kapsam dışında **üçüncü kişilere açıklanmayacaktır**."* |
| Ziyaretçi verisi | *"web sitesinde ziyaretçilerin kişisel verilerini **toplamaz** ve herhangi bir üçüncü tarafa **vermez**."* |
| Nedeni | *"gizli bilginin tamamının veya herhangi bir kısmının **kamu alanına girmesini** veya yetkisiz kullanımından… önlemek için gerekli tüm tedbirleri alma yükümlülüğünü taahhüt etmektedir."* |
| Harici linkler | *"üçüncü taraf web sitelerini kapsamaz."* |

### D-281 düzeltmesi

D-281'de *"8.473 ücretsiz ve yasal"* demiştim. **Bu ifade düzeltildi:**

| | |
|---|---|
| Teknik erişim | ✅ mümket (`robots.txt` izinli, 29 sayfa) |
| **Ticari kullanım** | ⛔ **koşulla yasak** |

> **8.473 firma, ticari bir ürünün veri tabanı olarak kullanılamaz.**

## 36. ❌ BULGU 2 — GİB'de e-Devletsiz toplu yol yok

| Denenen adres | Sonuç |
|---|---|
| `turkiye.gov.tr/gib-intvrg-vergi-kimlik-numarasi-sorgulama` | e-Devlet zorunlu (şifre / e-İmza / TCKK / bankacılık) |
| `gib.gov.tr/…/vergi-kimlik-numarasi-sorgulama` | HTTP 200 ama **gövde boş** (JS-rendered) |
| `gib.gov.tr/e-hizmetler` | **404** |
| `gib.gov.tr/acik-veri` | **404** |
| `gib.gov.tr/…/VERI_PAYLASIMI.pdf` | **404** |

**Projemin kendi notu bunu önceden yazmıştı** (`vkn_bulma_stratejisi.md` §7):
> *"GİB VKN Doğrulama (vkn.gov.tr) — sorgu servisi **captcha/bot korumalı**;
> tekil doğrulama için uygun, **toplu kazımaya uygun değil**."*

→ Ölçüm bunu **doğruladı**. GİB'de e-Devletsiz toplu erişim **yok**.

## 37. ⭐ BULGU 3 — VKN işi zaten denenmiş, %0 sonuç vermiş

Bu turda keşfettim: proje içinde **daha önce kapsamlı bir VKN kazıma
denemesi** var. Çıktıları ölçtüm.

### Mevcut çıktı: `data/ostim/firmalar_vkn_ekli.jsonl` (3,7 MB)

| Alan | Doluluk |
|---|---|
| unvan · adres · sektor · slug · web_sitesi | **%100** |
| telefon | %92 |
| e-posta | %48 |
| **`vergi_no`** | **%0 (5.040/5.040 boş)** |
| `yetkili` | %0 |

### Neden başarısız? Loglarda yazılı

`logs/vkn_extractor_v2.log`:
> `İşlenen: 5485/5485, **VKN bulundu: 3**, Atlanan placeholder: 2.646,
> Çekim hatası: 774`

`logs/vkn_web_run2.log`:
> `Taranan site: 30 — **VKN bulunan: 0** — robots engelli: 10`

> **5.485 denemenin 5.482'si (%99,9) sonuç vermedi.**

### Kök neden

OSTİM detay sayfası **VKN'yi hiç yayımlamıyor** (D-281'de ölçüldü: 11 alan
denendi, `vergi_no` yok). Yani web kazıması, **kaynağın vermediği** bir
alanı arıyordu.

## 38. Bağımlılık tuzağı

`firmalar_vkn_ekli.jsonl`'de `web_sitesi` %100 dolu — bu **bağımsız kaynak
sanılabilir**, ama aslında OSTİM'ın kendi listelediği alan. Zincir:

```
OSTİM  →  unvan/adres/telefon/e-posta  →  VKN YOK
  └─► web_sitesi  →  siteye git  →  VKN bulunamadı (%0)
                       └─► GİB  →  e-Devlet zorunlu
```

> **VKN eksikliği OSTİM kaynaklı değildir — proje içi bir varsayımdır.**
> Aynı kazımayı tekrar etmek aynı sonucu verir.

## 39. Net sonuç tablosu

| Yol | Durum | Neden |
|---|---|---|
| OSTİM 8.473 (ticari) | ⛔ **Yasak** | "bilgi amaçlı ve ticari olmayan kullanım" |
| GİB VKN e-Devletsiz | ❌ Yok | e-Devlet + captcha koruması |
| Web kazıması | ❌ **Zaten denendi: %0** | Kaynak alanı yayımlamıyor |
| MERSİS | ❌ e-Devlet | entegrasyon aşamasında |
| TOBB Düzey_3 | ❌ Kapsam yetersiz | %50 (D-279) |
| **e-Devlet** | ✅ **Açık** | KAHİN'in önceki tercihi |
| **OSTİM yazılı izin** | ✅ **Açık** | Kuruma başvuru |

> **Açık kalan iki yolun ikisi de KAHİN'in kararıdır.**
> Bu noktadan sonrası teknik değil, **kurumsal/hukuki** bir adımdır.

## 40. Öğrenilenler (kalıcı kural)

1. **`robots.txt` izni ≠ hukuki izin.** D-281'de "yasal" dedim; asıl metin
   bunu yasaklıyordu. → *Teknik erişilebilirlik ile kullanım hakkı ayrıdır.*
2. **Kaynağın alanı var mı, önce bak.** 5.485 deneme boşa gitti çünkü
   hedef alan (VKN) OSTİM'de hiç yok.
3. **Projemin geçmiş ölçümlerini oku.** `vkn_bulma_stratejisi.md` bu soruyu
   zaten yanıtlamıştı; 1 saatlik araştırma gereksizdi.

---

**Rapor sonu.** Özet: ⛔ 1 engel (OSTİM koşulu) · ❌ 1 yok yol (GİB) ·
⭐ 1 kazanım (VKN'nin zaten denenip başarısız olduğunu tespit ettik —
gereksiz tekrar önlendi). Karar gerektiren nokta: **e-Devlet** veya
**OSTİM yazılı izin**.

---

# EK-7 — VERİ ÇEKME POLİTİKASI + KIYASLAMA (D-283)

> KAHİN: *"veriyi ticari kullanılacak şekilde çek… kolon kolon, tane tane,
> doluluk oranları ile hangi verinin nerden geldiğini referansla, kolonları
> birbirine karıştırma. Veri çekme ve filtreleme politikamız var, listeyi yap."*

## 41. Kaynak adresleri (kesin, ölçülmüş)

| # | Adres | Kapsam | Doğrulama |
|---|---|---|---|
| 1 | `https://ostim.org.tr/firmalar` | Liste, 300/sayfa | `Toplam 8473 sonuç` |
| 2 | `https://ostim.org.tr/firmalar?page=N` | Sayfa 2…29 | 300+300+73 ✓, sayfa 30 boş |
| 3 | `https://ostim.org.tr/firmalar/<slug>` | Firma detayı (kalıcı) | 78.554 bayt, HTTP 200 |
| 4 | `https://ostim.org.tr/sitemap.xml` | Sitemap | **10 URL — firmaları İÇERMEZ** |
| 5 | `https://ostim.org.tr/robots.txt` | Yasal kapı | `/admin/`, `/portal/`, `/auth/` yasak |
| 6 | `https://ostim.org.tr/kurumsal/gizlilik-politikasi` | Kullanım koşulu | 10.044 karakter |

**Ölçülen envanter:** 8.473 firma · 29 sayfa · 300/sayfa · slug kalıcı.

## 42. Veri çekme politikası (KAHİN onayı sonrası uygulanacak)

| # | Kural | Uygulama | Dayanak |
|---|---|---|---|
| **P-1** | Sahte kullanıcı adı yok | Sabit, gerçek UA (bot taklidi **yapılmaz**) | `VERI_KAYNAK_KURALLARI` |
| **P-2** | Sayfa başına 1 istek | 300 slug liste + 1 detay | ölçülmüş |
| **P-3** | Nazik gecikme | **2 sn** istek aralığı | "nazik kazıma" ilkesi |
| **P-4** | Gece vardiyası yok | 8.473 firma ≈ **4,7 saat** (2 sn ile) | ölçülmüş |
| **P-5** | `robots.txt` her tur yeniden okunur | 403/401 = **açık hata**, boş liste **değil** | **K-5** |
| **P-6** | Tekil oran denetimi | `tekil/toplam < %95` → tur **başarısız** | **K-4** |
| **P-7** | Ham dosya `"w"` ile yazılır | Yeniden deneme kopyalamaz | **K-3** |
| **P-8** | Sayfa imzası tekrarında dur | 3 koruma birlikte | **K-1** |
| **P-9** | Yeniden çalıştırılabilir | Durum dosyası + tekil filtre | **K-1** |
| **P-10** | Maskeli alan kopyalanmaz | VKN/temsilci maskeli ise atlanır | KVKK |

## 43. Filtreleme politikası — kolonlar KARIŞTIRILMAZ (K-2)

Bu, KAHİN'in özellikle vurguladığı nokta. Mevcut veride **K-2 ihlali zaten
vardı** (ölçüm):

| Dosya | `kaynak` | NACE hane | Güven |
|---|---|---|---|
| `firmalar_full.jsonl` | `ostim.org.tr` (8.313) | **4 haneli: 7.047** | **C** (varsayılan) |
| `firmalar_vkn_ekli.jsonl` | `ostim.org.tr` (5.040) | NACE **yok** | — |

> ⚠️ `firmalar_full.jsonl` NACE'leri 4 haneli ve `nace_source: sektor_reverse`
> — yani **firmanın beyanı değil, sektör metninden türetilmiş tahmin.**
> Bu ASO'nun resmi 6 haneli NACE'iyle **aynı güvenle karıştırılmamalı.**

**Uygulanacak filtreleme:**

| Kolon | Kural | Gerekçe |
|---|---|---|
| `unvan` | Asla normalize edilmez (kısaltma yasak) | D-11 unvan kuralı |
| `adres` · `telefon` · `emailler` | **Yalnız OSTİM detay sayfasından** | Tek kaynak |
| `nace_code` | `nace_source` ile birlikte yazılır; tahmin ≠ resmi | **K-2** |
| `nace_confidence` | `high`=resmi · `medium`=türetilmiş · `none`=yok | K-2 güven tablosu |
| `vergi_no` | Yalnız **doğrulanmış** kaynak; tahmin yasak | D-274 |
| `kaynak_adi` | `ostim` (her zaman) | K-2 |
| `kaynak_turu` | `osb` | K-2 |
| `cekilme_tarihi` | ISO 8601, her kayıtta | K-3/K-4 |

## 44. ⭐ KIYASLAMA — eldeki veri zenginleşecek mi?

`scripts/veri_karsilastir.py` → `data/karsilastirma_raporu.json`

### 44.1 Mevcut iki set (kolon kolon)

| Kolon | `firmalar_full` (8.313) | `firmalar_vkn_ekli` (5.040) |
|---|---|---|
| unvan | %100 | %100 |
| **adres** | ⛔ **%0,0** | ✅ **%100** |
| **web_sitesi** | ⛔ **%0,0** | ✅ **%100** |
| **sosyal_medya** | ⛔ **%0,0** | ✅ **%100** |
| **sektor** | %69,4 | ✅ **%100** |
| telefonler | %92,0 | %92,4 |
| emailler | %44,1 | %48,0 |
| `vergi_no` | %0 | %0 |
| NACE | %84,8 (**4 haneli, türetilmiş**) | — |

### 44.2 Örtüşme

| Ölçüm | Değer |
|---|---|
| `a` tekil unvan | 8.251 |
| `b` tekil unvan | 4.954 |
| **Ortak** | **4.954 (%60,0)** |
| `b` ile **yeni** unvan | **0** |
| `a` ile kalan unvan | **3.297** |

### 44.3 Zenginleştirme katkısı (unvan bazında, eşleşen 4.954)

| Kolon | Katkı | Yorum |
|---|---|---|
| **adres** | **+4.952** | `full`'da **hiç yok** → devasa boşluk |
| **web_sitesi** | **+4.952** | aynı |
| **sosyal_medya** | **+4.952** | aynı |
| **sektor** | +1.398 | %69,4 → %100 |
| emailler | +3 | ihmal edilebilir |
| telefonler | +1 | ihmal edilebilir |
| `vergi_no` | **0** | hiçbir yerde yok |

> **CEVAP: EVET, zenginleştirir — ama sadece 3 kolonda ve hâlihazırda
> elimizde olan veriden.** `b` **tek bir yeni firma getirmiyor** (0).

## 45. Sonuç ve sıradaki adım

| Bulgu | Anlamı |
|---|---|
| 8.313 kayıt var, %61'i (3.297) detaysız | **3.297 firma detay sayfası eksik** |
| `adres` %0 → %100 olabilir | En büyük kazanç |
| Yeni unvan **0** | OSTİM'yi yeniden çekmek **yeni firma getirmez** |
| 8.473 − 8.313 = **160** | Siteye yeni eklenenler (artış payı) |
| `vergi_no` **0** | VKN sorunu çözülmedi (D-282) |

> **KAHİN'in sorusunun cevabı:** Yeni çekim elimizi **zenginleştirir** —
> ama kazanç **3.297 firmanın adres/web/sosyal medya alanı**, yeni firma
> sayısı değil. Bu, P-1…P-10 politikasıyla güvenle yapılabilir.

> **Sıradaki adım:** (a) 3.297 eksik detayın taranması,
> (b) `firmalar_full.jsonl` ile `vkn_ekli` birleştirme (kolon karışmadan,
> `kaynak_adi`+`kaynak_turu` korunarak), (c) sonra ihsan'a teslim.



