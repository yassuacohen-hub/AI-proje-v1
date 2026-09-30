# VERI-LONCA-FIRMA-01 — Rapor (yasu)

**Görev:** VERI-LONCA-FIRMA-01 · **Sahip:** yasu · **Tarih:** 2026-09-30
**Brif:** `plans/brief_yasu_VERI-LONCA-FIRMA-01.md`
**Ham veri:** `data/pilots/VERI-LONCA-FIRMA-01/firma_ornek_alanlar.json`
**Supabase yazma:** YOK (salt okunur ölçüm)

---

## 1. Görevin çıkış noktası: bir hatam

KAHİN ekran görüntüsü gönderdi ve önceki tespitimi düzeltti. Haklıydı:

> *"ayrı görev aç ve son kontrolü ve kararı ihsan review yaparken versin tekrar
> emin ol ve iyice bak görmediğin şeyler varmı bakmadığın durumlar oluşmuşmu
> örnek şirket taramamda mail ve telefon buldum"*

**HATAM:** `/FirmaBilgisi?Id=` ucunu **hiç denemedim**. Önceki turlarda
*"GET ile arama sonucu gelmiyor, tarama yapılamaz"* deyip görevi kapattım.
Oysa o sayfa GET ile açılıyor ve **e-posta, telefon, faks, web, adres,
unvan** veriyor.

Neden kaçırdım: ana sayfadaki linkleri taradım ve yeterli saydım.
Oysa detay sayfaları **arama sonucundan** geliyor, ana sayfada görünmüyor.

---

## 2. KAHİN'in verdiği TAM Id ile ölçüm

`Id` parametresi ekran görüntüsünde **kırpılmıştı**. KAHİN tam değerini
verdi → ölçüm yapıldı.

### 2.1 Yedi alan — **6/7 doldu**

| Alan | Değer | Durum |
|---|---|---|
| `unvan` (#firmaAdi) | AKANA MÜHENDİSLİK VE TİCARET | ✅ |
| `il` (#ilAdi) | SİNCAN / ANKARA | ✅ |
| `adres` (#firmaAdresi) | malıköy BAŞKENT OSB MAHALLESİ 5. CADDE NO :6 SİNCAN / ANKARA | ✅ |
| `telefon` (#firmaTel) | 0 (312) 640-1595 | ✅ |
| `faks` (#firmaFaks) | 0 (312) 645-1593 | ✅ |
| `eposta` (#firmaEposta) | info@akana.com.tr | ✅ |
| `web` | www.w3.org | ⚠️ **yanlış** — aşağıda |

**Ölçüm:** HTTP 200, 94.090 bayt, 0,38 sn, 1 tablo.

### 2.2 Teknik düzeltme: alanlar `id` etiketiyle çekiliyor

İlk regex denemelerim yanlış alan üretti (`telefon` → *"0 (312) 640-1595 Faks 0"*).
Ham HTML incelendi ve **sayfanın kendi `id` etiketleri** bulundu:
`#firmaAdi`, `#ilAdi`, `#firmaAdresi`, `#firmaTel`, `#firmaFaks`.

Regex tahmini yerine bu etiketler kullanıldı — **6/6 alan temiz** geldi.

### 2.3 `web` alanı yanlış dönüyor

`www.w3.org` çıktı — bu **W3C** (web standartları), firmanın sitesi değil.
Sayfada `<meta name="description">` içinde geçiyor ve ilk eşleşmeye yakalanıyor.
**Düzeltilmedi** — çözüm `og:url` veya `<a href>` içinden almak, ayrı ölçüm ister.

### 2.4 Ürün kataloğu — 9 satır, **NACE değil**

| Ürün |
|---|
| UÇUŞ KONTROL SİSTEMİ |
| 3 BOYUTLU ARAMA RADARI SÜRÜCÜ KOMPLESİ |
| SAVUNMA SANAYİNE YÖNELİK ÖZEL MAKİNE İMALATI |
| BALİSTİK KOVAN KLONLAMA SİSTEMİ |
| SUDA YÜZER HÜCUM KÜPRÜSÜ KARADA SERİ SÜRÜŞ DİŞLİ KUTUSU SİSTEMİ |
| MAKİNA İMALAT SANAYİİ… |
| ELEKTROMEKANİK DÜZLEME SİSTEMİ |
| MÜHENDİSLİK VE İTHALAT (TTK - M.371 - F.7) |

> **Kritik ayrım:** Bunlar **üretim ürünleri**, NACE kodu değil.
> Firma detay sayfasında **NACE kodu hiç yok**.

---

## 3. NACE sorusu — KAHİN'in sorduğu asıl konu

> *"nace kod eşleşme yapabilir miyiz bir kaynak olarak kullanır mı bizdeki
> nace kod sayısı çok az ve geliştirmek gerek"*

### 3.1 **Eski kayıt bayat — NACE artık %88,1 dolu**

Canlı ölçüm (Supabase, 9.412 firma):

| Ölçüm | Değer | Eski kayıt |
|---|---|---|
| `nace_code` dolu | **8.289 / 9.412 = %88,1** | ~~%0,1~~ |
| Farklı NACE kodu | **261** | — |
| `nace_source` dolu | 9.412 / 9.412 | — |

**NACE geliştirmeye gerek yok.** Kayıt bayatlamış.

### 3.2 **Ama asıl sorun kalite** — doluluk yanıltıcı

| `nace_source` | Adet | Pay | Anlamı |
|---|---|---|---|
| `sector_default` | **5.679** | %60,3 | sektör varsayılanı, **kanıt değil** |
| `unknown` | **2.504** | %26,6 | **hiç kaynak yok** |
| `fallback` | 654 | %6,9 | geri düşüş |
| `invalid_cleared` | 554 | %5,9 | geçersiz temizlenmiş |

**3.158 firma (%33,5)** ya varsayılan ya hiç bilinmiyor.
Gerçekten *ölçülmüş* NACE ≈ **%66**.

> Teknik olarak dolu görünüyor ama 5.679 kayıt kanıt değil. Bu, NACE
> geliştirme işinden daha önemli.

### 3.3 Lonca bu işe yarar mı? **Kısmen — doğrudan hayır**

| Yol | Durum |
|---|---|
| Firma detayından NACE atama | ❌ Sayfada NACE kodu **yok** |
| Ürün kataloğu → NACE | ⚠️ Dolaylı; ürün adı → sektör metin eşleştirme |
| **254 NACE kodu / 30 bölüm, GET ile açık** | ✅ **En somut katkı** |
| Bizim 261 koddan lonca kapsamında olan | **171** |

**Loncanın gerçek değeri firma verisi değil, NACE sözlüğüdür.**
254 kodun CIF/CPA adları, bizim `sector_default` 5.679 kaydın
**çapraz doğrulaması** için kullanılabilir.

### 3.4 Ölçülemeyen: firma bazlı kesişim

lonca'da unvan araması **POST `/Ara`** ile yapılıyor ve WAF **3/3 reddediyor**.
`Id` üretim yolu ölçülemedi → firma bazlı kesişim **"bilinmiyor"** (D-217).

---

## 4. Ölçüm tablosu

| Ölçüm | Sonuç |
|---|---|
| `/FirmaBilgisi` HTTP | 200, 94.090 bayt, **0,38 sn** |
| 7 alan | **6/7** dolu (`web` yanlış) |
| Ürün kataloğu | **9 satır** |
| POST `/Ara` WAF | **3/3 red** (`temel`, `fetch-meta`, `navigate`) |
| GET deneme | 7/7 açık |
| `/Sektor` sayfasında `FirmaBilgisi` Id | **0** |
| NACE doluluğu (bizim) | **%88,1** (8.289) |
| NACE gerçek (ölçülmüş) | **~%66** |
| Lonca NACE kodu | **254 kod / 30 bölüm** |

---

## 5. Karar gerekiyor (ihsan)

1. **8.289 dolu NACE güvenilir mi?** `sector_default` 5.679 kayıt
   kanıt olmadığı halde NACE gibi duruyor. Temizlenmeli mi?
2. **Lonca 254 kodu doğrulama sözlüğü** olarak kullanılsın mı?
3. **3.158 kaynaksız firma** önce mi ele alınsın?
4. **`web` alanı** — `www.w3.org` gibi yanlış eşleşme düzeltilsin mi?

---

## 6. Ölçülmeyenler

- Firma bazlı kesişim (POST WAF kapalı)
- `web` alanı doğru çıkarımı (çözülmedi)
- `/Sektor` sayfasındaki tablonun içeriği (0 satır geldi)
- Çoklu Id ölçümü — tek Id ile sınırlı kaldım
