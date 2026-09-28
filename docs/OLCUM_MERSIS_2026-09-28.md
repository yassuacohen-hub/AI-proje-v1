---
tip: olcum
gorev: MERSIS-KAYNAK-01
tarih: 2026-09-28
karar: D-257
---

# MERSİS-KAYNAK-01 — Erişilebilirlik Ölçümü

**Ölçüm tarihi:** 2026-09-28
**Yöntem:** HTTP isteği (`urllib`/`requests`), yanıt kodu + gövde boyutu + form/input ayrıştırma.
**Kural:** D-245 — erişilemedi yazıldıysa gerçekten erişilemedi; hiçbir satır tahmin değil.

---

## 1. Sonuç önce

> **MERSİS'te anonim firma sorgusu YOKTUR.** Ölçülen tüm yollar tek bir tanıtım sayfasına
> düşüyor; sorgu ekranı, API ucu veya açık veri dosyası bulunamadı.
> D-256'nın "MERSİS bağlanırsa 5.0 puan açılır" iddiası **bugünkü erişimle doğrulanamadı** —
> çünkü doğrulanacak bir çıktı ekranı yok.

> **TAVUK-YUMURTA GERÇEKTİR.** Ölçülen tüm açık uçlar girdi olarak **VKN/TCKN** istiyor.
> Elimizde 9412/9412 **ünvan** var, 5 adet VKN var. Ünvan→VKN çeviren açık kaynak bulunamadı.

---

## 2. MERSİS ölçümü

| Hedef | Kod | Boyut | Bulgu |
|---|---|---|---|
| `mersis.ticaret.gov.tr/` | 200 | 30701B | Tanıtım sayfası. Sorgu ekranı **yok**, yalnız "Giriş" bağlantısı |
| `/Portal/Home/Index` | 200 | 30701B | **Aynı** ana sayfa |
| `/uygulamalar` | 200 | 30701B | **Aynı** ana sayfa |
| `mersis.gtb.gov.tr` | 200 | 30701B | `mersis.ticaret.gov.tr`'ye yönleniyor, aynı sayfa |
| `/Portal/Firma/Sorgula` | 404 | — | Sorgu ucu yok |
| `/Portal/KullaniciYonetimi/Giris` | 404 | 1245B | `/StaticContent/ApplicationError` |
| `robots.txt` | 404 | — | — |
| `/Portal/StaticContent/KullanimKosullari` | 404 | 1245B | ApplicationError |
| `/Portal/StaticContent/GizlilikPolitikasi` | 404 | 1245B | ApplicationError |

**Ana sayfada bulunan ajax izleri:** `/Common/Duyurular/DuyuruIslemleri`,
`/Portal/KullaniciYonetimi/KullaniciKontrol` — ikisi de veri ucu değil.

**Giriş şartı (sayfa metninden birebir):**
> "E-Devlet Yönetimi ile Giriş **entegrasyon aşamasındadır**"

Yani e-Devlet girişi bile bugün tam çalışır durumda değil. MERSİS bir **işlem portalı**
(şirket kuruluşu, tescil başvurusu); **sorgulama portalı değil**.

### 2.1 Brief'in 6 sorusuna cevap

| Soru | Cevap | Kanıt |
|---|---|---|
| Erişim noktası var mı? | **Hayır.** Sorgu ekranı yok, API yok, açık veri yok | Yukarıdaki tablo |
| Giriş şartı ne? | Portal girişi var ama e-Devlet **entegrasyon aşamasında**; anonim sorgu ekranı hiç yok | Ana sayfa metni |
| Engel ne? | Engel captcha değil — **sorgu işlevi mevcut değil** | `/Portal/Firma/Sorgula` 404 |
| Ünvanla sorgu? | **Ölçülemedi — sorgu ekranı yok** | — |
| Çıktı VKN+vergi dairesi+sicil+NACE taşıyor mu? | **DOĞRULANAMADI.** Çıktı ekranına ulaşılamadı | — |
| Yasal durum? | Kullanım şartları sayfası **404**; yasal metin yayınlanmamış | Yukarıdaki tablo |

---

## 3. Plan B kaynakları

### 3.1 Ticaret Sicil Gazetesi (TSG) — **ENGELLİ**

| Ölçüm | Sonuç |
|---|---|
| `unvansorgulama.php` | 200, 35613B — erişilebilir |
| Form | `FormUnvanSorgulama`: `YeniSorgu=1`, `UnvanSorgu`, `Captcha` (maxlength=**4**) |
| Captcha ucu | `/captcha/captcha.php` → 200 ama `Content-Type: text/html`, 7113B — **resim değil** |
| Captcha'sız POST | 200 döner ama **aynı form sayfası**, sonuç yok |
| `ilangoruntuleme.php` | → `girisyap.php` yönlendirmesi — **üye girişi zorunlu** |
| Kullanım şartları / gizlilik | 404 |

**Not:** TSG, **ünvanla** sorguya izin veren tek kaynak — tavuk-yumurtayı kırabilecek yapıda.
Ama 4 haneli captcha + ilan görüntüleme için üyelik zorunlu. `TSG-KAYNAK-01` kapalı kalıyor.

### 3.2 GİB e-Fatura Kayıtlı Kullanıcılar — **ENGELLİ, girdi uyumsuz**

İz üç kat iframe altında; sonuna kadar takip edildi:

```
ebelge.gib.gov.tr/efaturakayitlikullanicilar.html   (200, 59237B)
  └─ iframe → sorgu.efatura.gov.tr/kullanicilar/    (200, 516B)
       └─ iframe → .../kullanicilar/xliste.php      (200, 1936B)  ← gerçek sorgu
```

`xliste.php` sayfa metni (birebir):
> "Güncelleme Tarihi: 28.09.2026 — Toplam **2197374** adet kullanıcı bulunmaktadır."

Form alanları:
```html
<input type="text" name="search_string" maxlength="255">   <!-- etiket: VKN/TCKN -->
<input name="captcha_code" type="text" size=15>            <!-- etiket: Güvenlik Kodu -->
<img src="img.php" />
```

| Ölçüm | Sonuç |
|---|---|
| `img.php` | 200, 1285B, `image/jpeg`, sihirli bayt `\xff\xd8\xff\xe0` — **gerçek JPEG captcha** |
| Captcha'sız POST | 200 → "**Güvenlik kodu hatalı, lütfen kontrol ediniz!**" |
| Yanlış captcha POST | 200 → aynı hata |
| Ünvan ("ANADOLU") ile POST | 200 → aynı captcha hatası (captcha'yı geçmeden alan davranışı ölçülemedi) |
| `xls.php`, `liste.php`, `listele.php` | 404 "File not found." |
| `kullanicilar.xml`, `.zip` | 404 |
| `xliste.php?xls=1` | 200 ama **aynı 1936B form sayfası** — toplu ihraç yok |
| Gizlilik/şartlar sayfası | 404 |

**Kritik**: Giriş alanının etiketi **"VKN/TCKN"**. Bu kaynak VKN'den ünvana gider, **ünvandan
VKN'ye gitmez**. Bizim ihtiyacımızın tersi. Tavuk-yumurtayı **kırmaz**.

Ayrıca çıktısı yalnız e-Fatura kayıt durumu + ünvandır; **vergi dairesi, sicil no, NACE taşımaz**.

### 3.3 Diğer kaynaklar

| Kaynak | Durum | Kanıt |
|---|---|---|
| TOBB `sanayi.tobb.org.tr` | Angular SPA'ya yönleniyor (`sanayi.org.tr/#/sanayi-veri-tabani`) | — |
| TOBB `/api/sanayi`, `/api/sanayi-veri-tabani`, `/api/v1/sanayi/arama` | **401** `application/problem+json` | Yetki gerekli |
| `veri.gov.tr` (http/https/www — 3 varyant) | **ERİŞEMEDİM** — `ConnectionResetError 10054` | Tekrarlandı, hep aynı |
| EKAP `ekap.kik.gov.tr` | Standart TLS **başarısız** (`SSLV3_ALERT_HANDSHAKE_FAILURE`); `SECLEVEL=1` ile 200 → `ekapv2.kik.gov.tr` 12990B | Eski TLS sunucu |
| EKAP `/ihale-arama`, `/api/ihale/arama` | **406** | — |
| GİB `sorgu.gib.gov.tr` | **ERİŞEMEDİM** — DNS çözülmüyor (`getaddrinfo failed`) | Alan adı yok |
| GİB `ivd.gib.gov.tr` | → `dijital.gib.gov.tr` 133215B; "Doğrulamalar" menüsü var ama **Kullanıcı Girişi** gerekli | — |
| GİB `intvrg.gib.gov.tr` | 200 | Sorgu ucu ayrıştırılmadı |
| TÜİK `data.tuik.gov.tr` | → `veriportali.tuik.gov.tr` 3692B | Firma kaydı içermiyor |

---

## 4. Puan etkisi (D-256 kayıp tablosu ile)

D-256'nın iddiası: MERSİS bağlanırsa `tax_number`(1.5) + `tax_office`(0.5) +
`mersis_number`(1.0) + `trade_registry_number`(1.0) + `nace_code`(1.0) = **5.0 puan**,
tavan 6.5 → 10.0.

**Bugünkü ölçümle açılan puan: 0.0.**

| Alan | Ağırlık | Bugün açılabilir mi | Neden |
|---|---|---|---|
| `tax_number` | 1.5 | **Hayır** | Açık uçlar girdi olarak VKN istiyor, çıktı olarak vermiyor |
| `tax_office` | 0.5 | **Hayır** | Hiçbir açık kaynakta yok |
| `mersis_number` | 1.0 | **Hayır** | MERSİS sorgu ekranı yok |
| `trade_registry_number` | 1.0 | **Hayır** | TSG captcha + üyelik |
| `nace_code` | 1.0 | **Hayır** | Kaynağı MERSİS (D-252), kapalı |

Kilitli kalan: **5.0 puan/firma × 9412 firma = 47060 puan.**
Tavan **6.50/10'da kalıyor**, ortalama 3.71'de sabit.

---

## 5. Yasal durum

- MERSİS, TSG ve GİB'in **kullanım şartları / gizlilik sayfalarının hiçbiri erişilebilir değil**
  (5 URL denendi, hepsi 404). Yazılı izin veya yazılı yasak **ölçülemedi**.
- GİB listesi form etiketinde **TCKN** açıkça geçiyor → gerçek kişi tacir kayıtları
  **TCKN taşıyor**. D-247/D-248 riski **doğrulandı**: bu kaynaktan çekilecek veri
  KVKK kapsamında kişisel veri içerebilir.
- TSG "ilan görüntüleme" üyelik arkasında → üyelik sözleşmesi kabul edilmeden erişim
  meşru sayılamaz.

**Sonuç:** Hiçbir kaynakta yazılı izin bulunamadı; TCKN riski gerçek. Otomatik toplu çekim
için **hukuki dayanak yok**.

---

## 6. Beklenen karar (ürün sahibi)

MERSİS yolu **bugün kapalı**. Üç seçenek var, ikisi para/zaman, biri kapsam daraltma:

| Seçenek | Ne yapar | Maliyet | Risk |
|---|---|---|---|
| **A) Resmî başvuru** | Ticaret Bakanlığı'na MERSİS veri erişim talebi; TOBB API'sine (401 dönen uç) yetki başvurusu | Hafta/ay, kurumsal yazışma | Reddedilebilir; ama **tek meşru yol** |
| **B) Ticari veri sağlayıcı** | Ünvan→VKN eşlemesi satın al | Para | Sağlayıcının kaynağı da doğrulanmalı (D-245) |
| **C) Kapsamı kabul et** | Kimlik tamlığı tavanını **6.50/10** olarak dondur; kilitli 5 alanı D-249 gereği **NULL** say, 0 puan sayma | Sıfır | Skor düşük kalır ama **dürüst** kalır |

**Önerim: C + A birlikte.** C bugün uygulanır (skor yalanı biter), A paralel yürür.
B'yi ancak A reddedilirse aç — çünkü satın alınan veri de kaynaksızsa D-245'e takılır.

**Yapılmaması gereken:** Captcha kırma / oturum taklidi. Üç kaynakta da captcha **gerçek**
(GİB'de doğrulanmış JPEG), yasal metin yok, TCKN riski var. Teknik olarak zor değil ama
hukuken savunulamaz.

---

## İlgili Nodlar

- [[AGENTS]]
- [[docs/OLCUM_TSG_KAYNAK]]
