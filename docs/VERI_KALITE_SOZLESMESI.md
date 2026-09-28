# Veri Kalite Sözleşmesi

> **Amaç:** Her alanın ne olduğu, neyin kabul edilmediği ve geçersiz değerin ne
> olacağı burada **yazılıdır**. Kazıyıcı bu belgeye uyar; belge kazıyıcıya uymaz.
>
> **Kurucu ilke (D-245):** Doluluk ≠ geçerlilik. Bir kolonun dolu olması, içindeki
> değerin o kolonun adına uygun olduğunu kanıtlamaz.
>
> **Tarih:** 2026-09-27 · **Karar:** ÜRÜN SAHİBİ (Yol 1) · **Durum:** Vergi alanı
> bağlayıcı, diğer alanlar taslak (ölçüm bekliyor).

---

## 0. Neden bu belge var

Ankara OSB firma veritabanında 9412 firma ölçüldü. `vergi_no` kolonunun gerçek içeriği:

| İçerik | Adet | Ne olduğu |
|---|---:|---|
| Boş | 8651 | veri yok |
| 6 haneli | 526 | ASO **ticaret sicil no** — yanlış kolona yazılmış |
| 11 haneli, sağlama BOZUK | 122 | TCKN değil, kazıyıcı çöpü |
| 5 haneli | 78 | çöp |
| Rakam dışı (`1725-KAZAN`) | 23 | adres/parsel kırıntısı |
| 4 haneli | 5 | çöp |
| **10 haneli geçerli VKN** | **5** | gerçek veri |
| **11 haneli geçerli TCKN** | **2** | gerçek veri |

**Sonuç: 9412 firmada toplam 7 geçerli vergi numarası var** — 761 dolu satırın %99,1'i
vergi numarası değil. Kolon dolu görünüyordu; içeriği vergi numarası değildi.
Bu belge o hatanın tekrarını engellemek için var.

İkiz kolon `tax_number` ayrıca 40 satırda dolu (4 geçerli VKN, 21 sicil no, 14 bozuk
11 hane, 1 çöp) — `vergi_no` ile birleşik toplam 770 dolu, 7 geçerli.

> **Ölçüm mandalı:** `python scripts/_olcum_k6.py` — bu tablodaki her sayı o betiğin
> çıktısıdır. Tablo değişecekse önce betik koşulur (D-246 madde 1).

**Kök neden:** Her kazıyıcı kendi regex'i ile karar veriyordu. 526 ASO satırı, tek bir
kazıyıcının sicil numarasını vergi numarası sanmasıyla oluştu. Merkezî doğrulayıcı yoktu.

---

## 1. Sözleşme kalıbı — her alan 6 maddeyle tanımlanır

Yeni alan eklenirken bu altı satır doldurulmadan kod yazılmaz:

| # | Madde | Ne cevaplar |
|---|---|---|
| 1 | **Anlam** | Alan tam olarak neyi tutar? Tek anlam, tek cümle. |
| 2 | **Biçim** | Regex / uzunluk / karakter kümesi. |
| 3 | **Sağlama** | Biçimden öteye geçen doğrulama (checksum, sözlük, DNS…). Yoksa "yok" yazılır. |
| 4 | **Kabul edilmez** | Bu alana sızması muhtemel *benzer* veriler açıkça sayılır. |
| 5 | **Geçmezse** | Reddedilen değer ne olur? (yazılmaz / ayrı kolona / karantinaya) |
| 6 | **Kim doldurur** | Tek kapı adı. Kazıyıcı asla doğrudan yazmaz. |

**Madde 4 en kritik maddedir.** 526 satırlık hata, "kabul edilmez" listesi yazılmadığı
için oluştu. Benzer veri her zaman aynı kolona sızmaya çalışır.

---

## 2. Bağlayıcı kurallar

### K-1 — Doğrulama tek kapıdan geçer

Kazıyıcı, ETL veya betik; bir alana değer yazmadan önce o alanın doğrulayıcısını çağırır.
Kazıyıcı içinde alan biçimi kararı verilmez.

> Gerekçe: 526 ASO satırı, kazıyıcının kendi kararını vermesiyle oluştu.

### K-2 — Geçersiz değer kolona yazılmaz

Doğrulama geçmeyen değer `NULL` bırakılır. "Bir şey olsun" diye yazılmaz.
Ham değer `source_records.raw_payload` içinde zaten durur; kaybolmaz.

> Gerekçe: Yarı geçerli değer, boş değerden tehlikelidir — raporda geçerli sayılır.

### K-3 — Bir kolon bir anlam taşır

`vergi_no` hem VKN hem sicil no hem üye no tutamaz. Yeni anlam = yeni kolon.

### K-4 — Türetilmiş alan elle yazılmaz

`tuzel_tip` gibi başka kolonlardan hesaplanan alanlar kazıyıcı tarafından doldurulmaz;
kaynak kolonlardan türetilir. İki kaynak çelişirse türetme başarısız olur, tahmin edilmez.

### K-5 — Kimlik Dosyası Tamlığı yalnızca sözleşmeli alandan beslenir

Puanlayıcıya sinyal eklenirken o alanın bu belgede tanımlı olduğu ve doğrulamadan
geçtiği gösterilir. Tanımsız alan puan üretmez.

> Gerekçe: `website_domain` dolu olduğu için ~2660 firmaya haksız puan verilmiş.

### K-6 — Ağırlık seti tek yerde, sürüm numarasıyla tutulur (D-250)

Ölçülen şeyin adı **Kimlik Dosyası Tamlığı** (0–10). "Kalite puanı" demek yasak:
eksiklik firmanın değil, bizim toplama başarımızındır.

**Ağırlık seti v1 — toplam 10.0:**

| Grup | Alan | Ağırlık |
|---|---|---|
| Kimlik omurgası (6.0) | ticaret unvanı | 1.0 |
| | `vkn` | 1.5 ⚠️ geçici |
| | `vergi_dairesi` | 0.5 |
| | `mersis_no` | 1.0 |
| | `ticaret_sicil_no` + `sicil_dairesi` | 1.0 |
| | `nace_code` | 1.0 |
| Erişim (4.0) | adres | 1.5 |
| | `telefon` | 1.5 |
| | `eposta` | 0.7 |
| | `website_domain` | 0.3 |

Bağlayıcı kurallar:

1. **Ağırlıklar tek sözlükte durur**, `puan_surumu` ile birlikte yazılır. SQL'e,
   panele veya rapora kopyalanmaz (K-4 türevi).
2. **Yalnızca doğrulamadan geçen alan puan kazandırır.** Dolu ama geçersiz değer
   0 puandır (K-1, K-2 devamı).
3. **Zenginlik verisi (çalışan sayısı, iş ilanı, sosyal medya) puana girmez.**
   Ayrı "zenginlik rozeti" olarak gösterilir. Gerekçe: ~%100 boş olduğu için
   puana katılırsa tüm firmalar aynı oranda düşer, puan ayırt etme gücünü kaybeder.
4. **`vkn` ağırlığı 1.5'tir, hedefi 3.0.** GİB kaynağı bağlanana kadar düşük
   tutulur; yükseltme sürüm v2 gerektirir (`GIB-MUKELLEF-01`).
5. **Ulaşılabilir tavan gösterilir.** Kaynağı olmayan alanların ağırlığı toplamdan
   düşülerek "bugün en fazla kaç alınabilir" hesaplanır. 2026-09-28 itibarıyla
   tavan **6.0/10** (vergi dairesi + MERSİS + sicil + VKN kaynağı yok).
6. **Ağırlık seti değişirse eski satırlar "yeniden hesap bekliyor" işaretlenir.**
   Sürüm eşleşmeyen puan panelde gösterilmez.

> Gerekçe: Ağırlık seti değiştiğinde eski puanlar sessizce yanlış olur —
> KALITE-PUAN-01'de 583 bayat skorun kökü budur.

---

## 3. Alan sözleşmeleri

### 3.1 `vkn` — Tüzel kişi vergi kimlik numarası · **BAĞLAYICI**

| # | |
|---|---|
| **Anlam** | Tüzel kişinin (LTD, A.Ş., kooperatif) GİB vergi kimlik numarası. |
| **Biçim** | `^[0-9]{10}$` — tam 10 hane, yalnızca rakam. |
| **Sağlama** | GİB VKN mod-10 algoritması. [`vkn_gecerli()`](../src/company_master/etl/kimlik_no.py:24) |
| **Kabul edilmez** | TCKN (11 hane), ticaret sicil no, oda üye no, MERSİS no, parsel no, telefon. |
| **Geçmezse** | Yazılmaz (`NULL`). Ham değer `raw_payload`'da kalır. |
| **Kim doldurur** | [`kimlik_dogrula()`](../src/company_master/etl/kimlik_no.py:50) — tek kapı. |

### 3.2 `tckn` — Gerçek kişi / şahıs işletmesi · **BAĞLAYICI**

| # | |
|---|---|
| **Anlam** | Şahıs işletmesinin sahibinin TC kimlik numarası. Mevzuatta gerçek kişi ayrı vergi numarası almaz; TCKN vergi numarası yerine geçer. |
| **Biçim** | `^[1-9][0-9]{10}$` — tam 11 hane, sıfırla başlamaz. |
| **Sağlama** | NVİ TCKN çift-basamak algoritması. [`tckn_gecerli()`](../src/company_master/etl/kimlik_no.py:38) |
| **Kabul edilmez** | VKN (10 hane), 11 haneye "yuvarlanmış" VKN, telefon numarası, sicil no. |
| **Geçmezse** | Yazılmaz (`NULL`). |
| **Kim doldurur** | [`kimlik_dogrula()`](../src/company_master/etl/kimlik_no.py:50) |
| **⚠️ KVKK — saklama** | **KARAR VERİLDİ (D-248):** TCKN saklanır. Diğer firma alanlarıyla aynı akıştan toplanır. Saklama süresi: **firma kaydı aktif olduğu sürece** (ürün sahibi "süresiz" dedi; hukuken savunulabilir ifade budur — bkz. D-248/2). |
| **⚠️ KVKK — gösterim** | Admin panelinde açık. Kullanıcı panelinde `tckn_kullaniciya_gorunur` ayarıyla aç/kapa; varsayılan **KAPALI**. Tek kapı: [`tckn_sun()`](../src/company_master/settings/user_settings.py:377). → D-247 |
| **⚠️ KVKK — 3. kişiye aktarım** | **BLOKE.** TCKN'yi ücretli pakete koymak ayrı hukuki temel gerektirir; meşru menfaat burada yetmez. Hukuki görüş alınmadan kod yazılmaz. → `KVKK-TCKN-02` |

### 3.3 `tuzel_tip` — Şahıs mı, şirket mi · **TÜRETİLMİŞ**

| # | |
|---|---|
| **Anlam** | Firmanın hukukî kişilik tipi. |
| **Biçim** | `tuzel` \| `sahis` \| `bilinmiyor` |
| **Sağlama** | `vkn` dolu → `tuzel`. `tckn` dolu → `sahis`. İkisi de boş → `bilinmiyor`. İkisi de dolu → **çelişki**, `bilinmiyor` + uyarı. |
| **Kabul edilmez** | Elle atama; ünvandan tahmin (LTD geçiyor diye `tuzel` denmez). |
| **Geçmezse** | `bilinmiyor`. |
| **Kim doldurur** | Türetme katmanı (K-4). Kazıyıcı asla. |

> **Ölçüm notu:** 11 haneli 124 satırın 101'i ünvanında LTD/A.Ş. taşıyor. Yani ünvandan
> tahmin bu veride yanlış sonuç verir — çünkü sayıların kendisi zaten geçerli TCKN değil.
> Kural doğru, veri kirli. Bu yüzden `tuzel_tip` yalnızca **sağlamadan geçmiş** kolondan türetilir.

### 3.4 `ticaret_sicil_no` + `sicil_dairesi` — Ticaret sicil kaydı · **BAĞLAYICI**

| # | |
|---|---|
| **Anlam** | Ticaret odası sicil numarası. Vergi numarasının yedeği **değil**, bağımsız bir kimliktir; `vkn` ile birlikte de dolu olabilir. |
| **Biçim** | `ticaret_sicil_no`: 3–6 haneli rakam dizisi (metin, baştaki sıfır korunur). `sicil_dairesi`: ilçe adı veya `NULL`. |
| **Sağlama** | Resmî sağlama algoritması yok — yalnızca biçim. Tireli değerde no + daire ayrıştırılır (`623-KAZAN` → `623`, `KAZAN`). |
| **Kabul edilmez** | 10 hane (VKN) ve 11 hane (TCKN) — sicil kolonuna yazılmaz. 2 haneden kısa, 7 haneden uzun. |
| **Geçmezse** | İki alan da `NULL`. |
| **Kim doldurur** | [`sicil_dogrula()`](../src/company_master/etl/kimlik_no.py:68) tek kapısı (K-1). |

> **Ölçüm (ham veri kanıtı):** `source_records.raw_payload` içinde ham alan adı
> **`ticaretSicilNo`** — tahmin değil, kaynak etiketi. 620 dolu kayıt:
> aso.org.tr 592, ostim.org.tr 28. Yani *"6 hane = ASO"* varsayımı **yanlıştı**;
> OSTİM kayıtlarında da sicil no var.
>
> | Biçim | Adet | No uzunluğu |
> |---|---:|---|
> | Tiresiz | 595 | 6 hane 519, 5 hane 68, 4 hane 8 |
> | Tireli (`623-KAZAN`) | 25 | 3 hane 14, 4 hane 11 |
>
> Tireli 25 kayıt **çöp değil**: ilçe sicil dairesi taşıyor (KAZAN 11, ELMADAĞ 6,
> AKYURT 3, BEYPAZARI 3, NALLIHAN 1, ÇUBUK 1). Bu yüzden ayrı `sicil_dairesi`
> alanı açıldı — tek kolona sıkıştırmak K-3 ihlali olurdu.
>
> Kabul aralığı 3–6 hane bu ölçümden geldi; ilk yazdığım 4–6 aralığını
> mandal reddetti (`623` üç hane). Sayı ölçümden, ölçüm ham veriden.

### 3.4b `mersis_no` — MERSİS numarası · **BAĞLAYICI** (kaynak ÖLÇÜLMEDİ)

| # | |
|---|---|
| **Anlam** | Merkezi Sicil Kayıt Sistemi numarası. Tescilli tüzel kişilerin benzersiz kimliği. |
| **Biçim** | Tam 16 haneli rakam dizisi (metin). |
| **Sağlama** | **İlk 10 hane = `vkn`.** Bu 10 hane VKN mod-11 sağlamasından geçmelidir; geçmezse MERSİS numarası yanlıştır. |
| **Kabul edilmez** | 16 haneden farklı uzunluk. Rakam dışı karakter. İlk 10 hanesi geçersiz VKN olan değer. |
| **Geçmezse** | `NULL`. VKN türetilmez. |
| **Kim doldurur** | `mersis_dogrula()` tek kapısı (K-1). Yazılacak — `MERSIS-KAYNAK-01`. |

> **Türetme kuralı (ürün sahibi, 2026-09-28):** tüzel kişilerde
> `vkn = mersis_no[:10]`. Bu, VKN'yi ikinci bir kaynak sorgusu olmadan kazandırır
> ve iki alanı karşılıklı denetler: VKN sağlaması MERSİS'in de sağlamasıdır.
>
> ⚠️ **Yalnızca tüzel kişi.** Şahıs firmalarında kimlik TCKN'dir (11 hane) ve
> MERSİS'in ilk 10 hanesinden türetilemez. Türetim `tuzel_tip = 'tuzel'` koşuluna
> bağlıdır; aksi hâlde D-245 ihlali (dolu ama geçersiz) yeni kılıkta tekrarlanır.
>
> **Kaynak durumu:** numaranın toplanabilirliği **ÖLÇÜLMEDİ**. Bilinen şey
> türetme kuralı, bilinmeyen şey erişim. `MERSIS-KAYNAK-01` açık.

### 3.5 `telefon` — **TASLAK, ÖLÇÜLMEDİ**

| # | |
|---|---|
| **Anlam** | Firmaya ait erişilebilir telefon numarası. |
| **Biçim** | Öneri: E.164 normalize (`+90XXXXXXXXXX`). |
| **Sağlama** | TR alan kodu sözlüğü + uzunluk. |
| **Kabul edilmez** | Faks, VKN/TCKN, posta kodu, tarih. |
| **Geçmezse** | Yazılmaz. |
| **Kim doldurur** | ÖLÇÜLMEDİ. |

### 3.6 `eposta` — **TASLAK, ÖLÇÜLMEDİ**

| # | |
|---|---|
| **Anlam** | Firmaya ait iletişim e-posta adresi. |
| **Biçim** | RFC'ye yakın regex + tek `@`. |
| **Sağlama** | Alan adı MX kaydı (isteğe bağlı). |
| **Kabul edilmez** | Portal yöneticisinin adresi, `info@osb...` gibi **kaynak sitesine** ait adres (→ bkz. 3.7 kaynak sızıntısı). |
| **Geçmezse** | Yazılmaz. |
| **Kim doldurur** | ÖLÇÜLMEDİ. |

### 3.7 `website_domain` — **TASLAK, KUSUR BİLİNİYOR**

| # | |
|---|---|
| **Anlam** | Firmanın **kendi** web sitesi alan adı. |
| **Biçim** | Geçerli alan adı; şema/yol taşımaz. |
| **Sağlama** | Bilinen kusur: alan dolu olduğu için ~2660 firmaya haksız kalite puanı verilmiş. |
| **Kabul edilmez** | **Kaynak sitesinin kendi alan adı** (`ostim.org.tr`, `aso.org.tr`) — bu kaynak sızıntısıdır, firmanın sitesi değildir. |
| **Geçmezse** | Yazılmaz + puan üretmez (K-5). |
| **Kim doldurur** | ÖLÇÜLMEDİ. |

### 3.8 `nace_code` — **TASLAK, KUSUR BİLİNİYOR**

| # | |
|---|---|
| **Anlam** | Firmanın birincil NACE Rev.2 faaliyet kodu. |
| **Biçim** | Resmî NACE biçimi. |
| **Sağlama** | Resmî NACE sözlüğünde bulunmalı — uydurulamaz. |
| **Kabul edilmez** | "30. MESLEK GRUBU" gibi oda meslek grubu metni; `nace_validity` kolonuna karışmış değerler. |
| **Geçmezse** | Yazılmaz; sektör sayacına girmez. |
| **Kim doldurur** | ÖLÇÜLMEDİ. |

---

## 4. Açık kararlar

| Kimlik | Konu | Sahip |
|---|---|---|
| ~~`KVKK-TCKN-01`~~ | ~~TCKN saklanacak mı? Erişim kısıtı ve saklama süresi.~~ **KAPANDI** → D-247 (gösterim), D-248 (saklama). | — |
| `KVKK-TCKN-02` | TCKN ücretli pakete konulabilir mi? Üçüncü kişiye aktarımın hukuki temeli + erişim kaydı. **Hukuki görüş gerekli.** | ÜRÜN SAHİBİ |
| `SEMA-VKN-01` | `vergi_no`/`tax_number` ikizliğinin `vkn`/`tckn`/`ticaret_sicil_no`/`tuzel_tip` ile değişimi. K-6 gereği `vergi_dairesi` + `mersis_no` de eklenir. | KAHİN → ÜRÜN SAHİBİ |
| `OLCUM-ALAN-01` | 3.5–3.8 alanlarının gerçek anatomisinin ölçülmesi (3.4 ölçüldü). | UTKU |
| `GIB-MUKELLEF-01` | VKN/TCKN'nin *gerçekten kayıtlı olduğunu* doğrulama. Aşağıdaki nota bakılmadan başlanmaz. | ÜRÜN SAHİBİ → KAHİN |
| `MERSIS-KAYNAK-01` | MERSİS no toplanabilir mi? **GİB'den önce denenir** (D-250/9): ücretsiz + VKN'yi de getirir. Erişim ÖLÇÜLMEDİ. | KAHİN |
| ~~`KALITE-PUAN-01`~~ | ~~Hangi ağırlık seti? Alt skorlar puana girsin mi?~~ **KAPANDI** → D-250, K-6. | — |

> **GIB-MUKELLEF-01 notu — tek tek sorgu YERİNE toplu liste.**
>
> Ürün sahibi `ebelge.gib.gov.tr/earsivkayitlikullanicilar.html` adresini gösterdi ve
> "sürekli sorgu yasak, azar azar VPN ile" dedi. Bu yöntemi **önermiyorum**, iki nedenle:
>
> 1. **Gereksiz.** O sayfa tek tek sorgu için değil; GİB **kayıtlı kullanıcı listesini
>    dosya olarak** yayınlar. 9412 firma için 9412 istek yerine **1 indirme** yeter.
>    Sonra eşleştirme yerel veritabanında yapılır — ağ trafiği yok, hız sınırı yok.
> 2. **Riskli.** VPN ile hız sınırını aşmak, erişim koşullarını bilerek dolanmak olur.
>    IP bloğu en hafif sonucu; asıl maliyet ticari bir veri ürününün kaynak meşruiyetini
>    kaybetmesi. Bir müşteri "bu veriyi nasıl doğruladınız?" diye sorduğunda
>    "VPN ile sorgu yaptık" cevabı verilemez.
>
> **Önerilen yol:** listeyi dosya olarak indir → yerel tabloya yaz → `vkn` ile eşle →
> `vkn_kayitli` (bool) + `vkn_kaynak_tarihi` alanlarını doldur. Liste periyodik güncellenir.
>
> **Kapsam uyarısı:** e-arşiv kayıtlı kullanıcı listesi *e-belge kullanan* mükellefleri
> kapsar, tüm mükellefleri değil. Yani listede **olmamak** "mükellef değil" demez.
> Bu yüzden sonuç alanı `vkn_gecerli` değil `vkn_earsiv_kayitli` olarak adlandırılmalı —
> aksi hâlde eksik kapsam "geçersiz" sanılır (D-245: doluluk ≠ geçerlilik).
>
> **Karar bekleyen:** liste dosyası indirilebiliyor mu (erişim denenmedi, ÖLÇÜLMEDİ);
> güncelleme sıklığı; listede olmayan firmalar için ne yapılacağı.

---

## 5. Bu belgeyi değiştirme

1. Sözleşme değişikliği **ölçümle** gelir, tahminle değil.
2. Yeni alan → 6 maddesi doldurulur, sonra kod yazılır.
3. Ölçülmemiş alan `ÖLÇÜLMEDİ` işaretlenir. Sayı uydurulmaz.
4. Sözleşmeyi gevşetme kararı ÜRÜN SAHİBİNE aittir ve AGENTS.md'ye D-NN olarak düşer.

---

## İlgili Nodlar

- [[../AGENTS]]
- [[../plans/brief_utku_VERI-KOLON-IKIZ-01]]
