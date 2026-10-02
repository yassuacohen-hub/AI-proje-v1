# Faz 6 — Küresel İstihbarat Ağı Kapsam Araştırması

**Görev:** `DOC-GLOBAL-INTEL-ARASTIRMA-01` · **Rol:** utku (üretim) · **Tarih:** 2026-10-02
**Hub:** `hubs/PLAN_STRATEGY_HUB.md` · **Kit:** ADMIN-KİT (D-196)

> **Bu bir KOD görevi değildir.** Şema, göç, tablo ve Python kapsam dışıdır.
> Çıktı tek markdown belgesidir. Kod gereken her madde "ayrı görev gerekir" diye
> işaretlenmiştir.

---

## D-66 Doğrulama Kaydı — varsayımların beşi de açılıp görüldü

Brif "verdiğim satırlara güvenme, teyit et (D-245)" diyordu. Beş varsayım da
kendi ölçümüyle doğrulandı:

| Varsayım | Sonuç | Kanıt |
|---|---|---|
| SSOT var, ~1687 satır | **1687 — birebir tuttu** | `yedekler/Huginn Data Insights (HUGIns).txt` |
| `871-873` = Faz 6 başlığı | Tuttu | `Faz 6` / `Global Corporate Intelligence Network` |
| `875-885` = Nihai Misyon | Tuttu | *"İnternet üzerindeki her şirket için… Kimdir? Güvenilir midir? Risk taşır mı?"* |
| `11-17` = 7 soru | Tuttu (tam 7 satır) | gerçek şirket mi / yasal yükümlülük / dolandırıcılık / sürdürülebilirlik / sahiplik / dijital güvenlik / itibar |
| `25-32` = 8 kitle | Tuttu (tam 8 satır) | satın alma ekipleri → tedarik zinciri yöneticileri |
| FAZ6 belgesi diskte yok | **Doğru, yoktu** | brif yazılmadan önce teyit edildi |
| FAZ5 envanter belgesi var | **Var** (20.786 B) | `docs/FAZ5_VENDOR_DUE_DILIGENCE_KAPSAM.md` |

> **SSOT yolu briften farklı çıktı.** Brif `yedekler/…` yolunu vault içinde
> aradığı için ilk denemede "yok" göründü; dosya **depo kökünde** bulundu.
> D-245'in istediği oldu: numaraya değil dosyaya bakıldı, sonuç değişmedi.

---

## Faz A — Uçurum ölçüldü: bugün kaç ülke, kaç firma?

### Ölçüm tablosu

| Ölçüm | Değer | Nasıl ölçüldü |
|---|---|---|
| Veri setindeki toplam kayıt | **8987** | `python scripts/osb_veri_denetim.py` → `TOPLAM kayit : 8987` |
| Tekil firma (`company_slug`) | **8296** | aynı çıktı → `TEKIL company_slug: 8296` |
| Kapsanan ülke sayısı | **ölçülemedi: `companies` tablosunda ülke kolonu yok, sayılacak alan yok** | findstr `country`/`ulke`/`nation` → 50 migration'da 3 eşleşme, `companies`'ta **0** |
| Şemada ülke kolonu (`companies`) | **YOK** | `0001_core.sql:34-62` — 26 kolonun tamamı açılıp görüldü, ülke/ulke/nation **yok** |

Ek ölçümler (aynı çıktıdan): mükerrer **44**, kimliksiz satır **647**, mojibake adı **0**.

Kapı doğrulaması: `osb_veri_denetim.py --self` → `self-check OK`
(muhasebe: 8296 + 44 + 647 = 8987 ✓) ve `--kontrol 8987` → **çıkış kodu 0, uyuşmazlık yok**.

### 🔴 Kritik ayrım — 8987 `companies` tablosu DEĞİLDİR

Bu, D-260'ın tam olarak tarif ettiği tuzak: **"ölçtüğümüz veri seti, ürünün
veri seti değil."** Betik `data/osb/*/firmalar.jsonl` dosyalarını okuyor
(`osb_veri_denetim.py:21,31`) — ham kazıma çıktısını. `companies` tablosu
ayrı bir sayı:

| Kümе | Kayıt | Bu belgede ölçüldü mü |
|---|---|---|
| `data/osb/` ham kazıma | 8987 | ✅ bu tur |
| `companies` tablosu | **9412** | ❌ D-263/D-267 ölçümü (2026-09-28); bu turda **yeniden ölçülmedi** |

İkisi farklı işler: kazıyıcı kaç satır üretti (8987), normalize/dedup sonrası
kaç firma kaldı (9412). Aynı belgede ikisini tek "firma sayısı" diye yazmak
D-260 ihlali olurdu.

### "Yalnız Türkiye" varsayımı — teyit edildi, ama dolaylı kanıtla

Doğrudan bir ülke kolonu olmadığı için bu, sorguyla değil **üç bağımsız
yapısal kanıtla** doğrulanıyor:

1. **Kaynak envanteri (ölçüldü):** 12 kaynağın **12'si de** Türk OSB'si —
   `anadolu`, `aso`, `aso2`, `baskent`, `cubuk`, `dokumcu`, `elmadag`,
   `kazan_hab`, `ostim`, `polatli`, `polatli_ticaret`, `sereflikochisar`.
   Tek bir yabancı kaynak yok.
2. **Şemada sabit kodlanmış coğrafya:** `0001_core.sql:49` →
   `is_ankara BOOLEAN DEFAULT FALSE`. Coğrafi kapsam bir kolona gömülmüş.
3. **Kurumsal kavram:** `0001_core.sql:50-51` → `is_osb_member` +
   `osb_id UUID REFERENCES osbs(osb_id)`. "OSB" (Organize Sanayi Bölgesi)
   Türkiye'ye özgü bir kurumsal yapıdır; `osbs` tablosunun tamamı Türk OSB'leri.

> **Yanlış negatif tuzağı (D-266):** İlk `findstr` turu **boş döndü** ve
> "ülke kolonu yok" denilebilirdi. Boş sonuç, bozuk komut da olabilir —
> bu yüzden **pozitif kontrol** çalıştırıldı: aynı biçimde `vkn` arandı ve
> **12 satır** döndü. Tırnaklama hatası PowerShell'de `\"` kaçışı olmadığı
> içindi; düzeltilince `country` araması **gerçekten 3 eşleşme** verdi.
> Komut çalışmadan sonuç yazılsaydı, belge bir sonraki turda çürürdü.

### Ülke kolonu "yok" ama projede ülke geleneği zaten **iki tane** — ve tutmuyor

Bu, brifin beklemediği bir bulgu. `companies`'ta ülke kolonu yok; ama **aynı şemada**
iki ayrı ülke temsili şimdiden kullanılıyor:

| Yer | Tanım | Biçim | Kanıt |
|---|---|---|---|
| `job_postings` | `location_country TEXT DEFAULT 'Türkiye'` | serbest metin, **sabit varsayılan** | `0013_job_intelligence.sql:20` |
| `user_activity_log` | `ulke_kodu CHAR(2) NULL` — yorumda `ISO 3166-1 alpha-2` | **doğru biçim** | `0017_user_activity_log.sql:20` |

Yani doğru biçim projede zaten var, yanlış biçim de var, ikisi de
`companies`'a **taşınmamış**. "Ülke kolonu ekle" demek "üçüncü gelenek ekle"
olmaktı — D-211'in ikiz yasağının canlı örneği.

---

## Faz B — "Küresel" ne demek: üç ölçek

SSOT'taki Nihai Misyon üç soru soruyor (`875-885`): *"Kimdir? Güvenilir
midir? Risk taşır mı?"* Bu üç soruyu cevaplamanın üç farklı yolu var ve
maliyetleri birbirinden çok uzak.

### Ölçek 1 — Türkiye derinleşmesi ("küresel değil ama sağlam")

- **Ne demek:** Ülke eklemiyoruz. Elimizdeki ~9 bin kaydı, SSOT'un 7 sorusunun
  olabildiğince çoğunu cevaplayacak şekilde zenginleştiriyoruz. "Küresel"
  iddiasını hiç kurmuyoruz; hedef **Türkiye'de sağlam**.
- **Gereken yeni veri kaynağı:** **kaynak adı araştırılmadı.** Gerekçe ölçümdür,
  göz ardı etme değil: D-257 üç yolu da tek tek ölçtü ve kapattı —
  MERSİS'te anonim sorgu ekranı **yok** (4 uç aynı 30701B tanıtım sayfası,
  `/Portal/Firma/Sorgula` = 404), TOBB API üç uçta **401**, TSG **captcha**'lı,
  GİB e-Fatura yönü **ters** (VKN → unvan gider, unvan → VKN gitmez) ve
  form etiketi **TCKN** içeriyor (D-247 riski doğrulandı).
- **Gereken şema değişikliği:** **yok.** `identity_completeness` ve
  `score_version` kolonları mevcut, tek kapı `etl/quality_recalc.py`'de.
- **Engel:** Kimlik omurgası kaynakları kapalı olduğu için tavan
  **7.50/10**'da kilitli (`tax_office` 0.5 + `mersis_number` 1.0 +
  `nace_code` 1.0). D-250/3 gereği `tax_number` ağırlığı 1.5'te kalıyor;
  VKN kaynağı gelirse sürüm v2 olmalı, o an tüm 9412 puan bayatlanır.
- **7 sorudan kaçını cevaplar: 1/7** — yalnız *"Gerçek bir şirket olup
  olmadığı"* (OSB üye listesi = o OSB'de kayıtlı gerçek tüzel kişi).
  Kalan 6 sorunun verisi hiçbir kaynakta yok. *(Bu sayı ölçüm değil,
  aşağıdaki alan envanterinden yürütülmüş yargıdır — bkz. Öz-eleştiri.)*

### Ölçek 2 — Komşu ülkeler (AB + bölge)

- **Ne demek:** AB'de ortaklaşa kullanılan kurumsal sicil üzerinden o ülkedeki
  firmaları **mevcut kimlik defteri modelimize** oturtmak. NACE zaten Avrupa
  standardı olduğu için sektör eşlemesi ek maliyet getirmiyor.
- **Gereken yeni veri kaynağı:** AB İşletme Sicili / **BRIS** (Business
  Registers Interconnection System) — adı biliniyor, **ölçülmedi, pilot
  gerekir**. BRIS çapraz sınır kayıtları için çalışır; şirketin finansal
  verisini vermez, yani 7 sorunun 6'sını cevaplamaz.
- **Gereken şema değişikliği:** `companies`'a ülke kolonu +
  `company_identifiers`'a ülke kapsamlı `identifier_type`. **Ayrı görev gerekir.**
- **Engel:** Her ülkenin sicil yapısı farklı ve BRIS tek noktada toplanmıyor.
  Ortak olan tek şey NACE — o da şemada **zaten Avrupa'ya özgü** (bkz. E3).
- **7 sorudan kaçını cevaplar: 2/7** — "gerçek şirket mi" + "yasal varlık
  sicil kaydı". Kalan 5 soru Ölçek 1 ile aynı eksiklerde kalır.

### Ölçek 3 — Gerçek küresel (SSOT'un yazdığı hedef)

- **Ne demek:** *"İnternet üzerindeki her şirket için"* — Kimdir / Güvenilir
  midir / Risk taşır mı, saniyeler içinde. Bu bir veritabanı işi değil;
  7 sorunun **6'sı** kamuya açık resmi kaynaklarda **yok** (sahiplik
  şeffaflığı, kurumsal itibar, ölçülebilir dijital güvenlik seviyesi
  ancak ticari sağlayıcılarda var).
- **Gereken yeni veri kaynağı:** **kaynak adı araştırılmadı.** Sağlayıcı
  seçimi ayrı görev + hukuk değerlendirmesi gerektirir. Sağlayıcının verisi
  de D-245'e tabidir: satın alınan veri de aynı biçim doğrulamasından geçmeli.
- **Gereken şema değişikliği:** ülke kapsamı + kimlik türü kapsamı +
  kanıt/iddia ayrımı. D-310'un 5 katmanı zaten **süreç** tanımı, şema değil.
- **Engel:** Sınır ötesi veri aktarımı (KVKK → GDPR) ve her ülkenin kamuya
  açık firma verisinin ticari yeniden kullanım hakkı. **Ölçülmedi** —
  teknik okuma bunu ölçemez (bkz. Öz-eleştiri 1).
- **7 sorudan kaçını cevaplar: 7/7 yalnız maliyetli sağlayıcıyla**; açık
  kaynakla 1/7'nin üstüne çıkmaz.

---

## Faz C — Beş teknik engel, her biri ölçümle

### E1 — `companies` tablosunda ülke kolonu yok; projede zaten iki tutarsız ülke geleneği var

- **Nerede görünür:**
  `src/company_master/schema/migrations/0001_core.sql:34-62` (`companies`, 26 kolon — ülke yok)
  · `0013_job_intelligence.sql:20` (`location_country TEXT DEFAULT 'Türkiye'`)
  · `0017_user_activity_log.sql:20` (`ulke_kodu CHAR(2) NULL`, yorum: ISO 3166-1 alpha-2)
- **Neden engel:** "Hangi ülkeyi kapsıyoruz?" sorusu bir sorguyla değil
  **tahminle** cevaplanıyor — ve iki farklı gelenek birbiriyle uyuşmuyor.
  Doğru biçim (`CHAR(2)`, ISO 3166-1 alpha-2) projede zaten var, yanlış biçim
  de var; ikisi de `companies`'a taşınmamış. Yeni bir ülke kolonu eklemek
  **üçüncü** geleneği doğurur (D-211).
- **Aşmanın yolu:** `companies`'a tek ülke kolonu (ISO 3166-1 alpha-2 `CHAR(2)`,
  0017'deki geleneği **aynen** taşı), `job_postings.location_country`'ı ona
  bağla ve serbest metni düşür. **Ayrı görev gerekir.**

### E2 — Kimlik tekilleştirme Türkçe vergi numarasına bağlı; ama genellenebilir defter zaten var

- **Nerede görünür:**
  `0001_core.sql:39` (`tax_number TEXT UNIQUE` — VKN)
  · `0002_relations.sql:22-30` (`company_identifiers`, `UNIQUE(identifier_type, identifier_value)`)
  · `0027_ikiz_kolonlari_birlestir.sql:67` (`ci.identifier_type IN ('vkn','tckn')`)
- **Neden engel:** `tax_number` bir **UNIQUE** kolon ve VKN'i varsayıyor;
  başka ülkede karşılığı yok. D-257 ölçümü: 9412 firmada **5** geçerli VKN.
  Yani sorun yalnız "veri az" değil — **şema önceliğinin** Türkiye'de olması;
  `tax_number` adı dünya çapında yanlış okunur. İyi haber: `company_identifiers`
  çok biçimli bir kimlik defteri ve `identifier_type` ile **zaten** çalışıyor.
  Genişlemenin gerçek yeri `tax_number` değil, burası.
- **Aşmanın yolu:** Genişleme `company_identifiers` üzerine kurulur (ülke
  kapsamlı `identifier_type`); `tax_number` Türkiye'ye özgü kalır ve öyle
  belgelenir. **Ayrı görev gerekir.**

### E3 — Sektör standardı NACE'a bağlı; NAICS karşılığı şemada hiç yok

- **Nerede görünür:**
  `0002_relations.sql:59-67` (`nace_codes`, `nace_version` alanıyla)
  · `0006_nace_details.sql:5` (`companies.nace_code`)
  · `findstr /C:"naics" src\company_master\schema\migrations\*.sql` → **0 satır** (50 dosya tarandı)
- **Neden engel:** NACE Avrupa standardı; ABD'de NAICS kullanılır ve şemada
  **hiç yok** (0 eşleşme). `company_industries.nace_code` FK'si NACE'e bağlı
  olduğundan ABD firmaları bu modelde sektör-siz kalır — "her şirket" hedefi
  için doğrudan kapsam kaybı.
- **Aşmanın yolu:** `nace_codes`'ı ülke/küme bağımsız bir sınıflandırma
  çatısına ayırmak (NACE + NAICS yan yana, ülke kapsamlı). **Ayrı görev gerekir.**
  *Uyarı:* D-252 ölçümü — NACE kodlarımızın **%100'ü tahmin**, gerçek kod **0**.
  Yapı doğru olsa da veri doğrulanmamış; **önce** D-257'deki kaynak borcu
  çözülmeli, sonra yapı genişletilmeli.

### E4 — Coğrafi kapsam şemada kolon olarak sabit kodlanmış

- **Nerede görünür:**
  `0001_core.sql:49` (`is_ankara BOOLEAN DEFAULT FALSE`)
  · `:50` (`is_osb_member`)
  · `:51` (`osb_id UUID REFERENCES osbs(osb_id)`)
- **Neden engel:** "Ankara'da mı?" sorusu **bir kolona gömülmüş** ("Ankara'da
  mı" sorusunu yanıtlayan genel bir konum sorgusu yok). Genişleme bu kolonu
  yanlış yerde bırakır ya da ikinci bir `is_xxx` ailesi doğurur (D-211).
  `is_osb_member`/`osb_id` de Türkiye'ye özgü: OSB (Organize Sanayi Bölgesi)
  Türkiye kurumsal yapısına özgüdür ve ölçülen 12 kaynağın 12'si de Türk OSB'si.
- **Aşmanın yolu:** `is_ankara` yerine genel konum sorgusu — `company_locations`
  zaten var (`0002_relations.sql:36-53`: `city`, `district`, `latitude`,
  `longitude`, `geocode_confidence`). **Ayrı görev gerekir.** D-258'in
  dersi: kolon adı/adresi değişince **27 indeks + 14 panel + sema beyanı**
  birlikte taranır — "yarım göç" bu dosyada yedi ayrı yerden çıkmıştı.

### E5 — Dil varsayımı Türkçe karakterlere kurulu

- **Nerede görünür:**
  `src/company_master/api/core/normalize.py:602-604` (`_TRADE_FOLD_MAP`, `str.maketrans`, 8 Türkçe harf)
  · `normalize.py:681` (`_TR_LOWER_MAP`)
  · `src/company_master/etl/kaynak_bagla.py:22` (`TR_MAP`)
- **Neden engel:** Almanca `ß`, İspanyolca `ñ`/`ç`, Fransızca `é`/`è`/`à`,
  Lehçe-Cek `ł`/`ś`/`ż`/`č`/`ř`/`ů`/`ď`/`ť`/`ň` bu haritada **hiç yok**.
  Tabela ismi çıkarma (`_TRADE_NAME_STOP_WORDS`) Türkçe kurum ekleri
  varsayıyor. Ayrıca **brifin işaret ettiği dizin yanlıştı** (aşağıya bak).
- **Aşmanın yolu:** Katlama haritası dil parametresi almalı; durum tablosu
  (Apple CLDR) tek kaynak olmalı. **Ayrı görev gerekir.**

> **Brif sapması — ölçülen, tahmin edilen değil.** Brif E3 için
> `src\company_master\entity_resolution\*.py` içinde `maketrans`/`encoding`
> aranmasını söylüyordu. **Çalıştırıldı: 0 eşleşme.** Doğru yer arandı ve
> bulundu: normalleştirme `entity_resolution`'da değil, **`api/core/normalize.py`**
> ve `etl/kaynak_bagla.py`'de. Brif'in dizini yanlıştı. Bu turda E5'i "yok"
> diye yazsaydım, tam olarak D-266'nın hatası olurdu: **mandalın kapsamı,
> koruduğu şeyin yüzeyini kapsamalıdır.**

---

## Faz D — Karar önerisi: üç yol

| Yol | Ne yapar | Artısı | Eksisi | Ne zaman başlanmalı |
|---|---|---|---|---|
| **A** | Faz 6'yı **ertele**; Faz 1-4 bitene kadar dokunma | Odak dağılmaz. 7 sorudan 1'ini cevaplamak bile bugün tavanı 7.50'ye taşımak. | Hedef kağıtta kalır. | — |
| **B** | Yalnız **şemayı hazırla** (ülke kolonu + kimlik türü kapsamı), veri sonra | Ucuz. Geri dönülmez karar vermez, mevcut model bozulmaz. | Boş kolon = **ölçülmüş** D-249 riski (0024 göçünde 8140 sahte 0). | Faz 1-4 kapanınca **ve** veri kaynağı bulunduktan sonra |
| **C** | Tam genişleme: harici küresel veri sağlayıcı | SSOT hedefine ulaşır. | Maliyet + sınır ötesi veri hukuku. Sağlayıcının verisi de D-245'e tabi. | KAHİN sağlayıcı **ve** bütçe kararı verirse |

### ← ÖNERİM: **A — ertele**

**Gerekçe:** E1-E5'in beşi de *veri* eksikliği değil **öncelik** eksikliği
sorunudur; ve ölçülen tablo elimizdekinin tamamının tek bir ülkenin tek bir
bölgesinden geldiğini gösteriyor (12/12 kaynak Türk OSB'si, `is_ankara`
kolonu, OSB kavramı). B yolunun bedeli zaten yaşandı: D-249'un ölçülmüş
vakasında 0024 göçü 8140 sahte 0'ı buldu — o kolonlar veri geldiğinde doğru
çalıştı. Aynı hata ülke kolonunda tekrarlanırsa **boş kolon**, veri yokken
"0 firma" gibi okunur ve karar D-260 gereği reddedilir. C yolu ise 7 sorunun
6'sı için yalnız ticari sağlayıcıya bağımlı; sağlayıcı adı araştırılmadı ve
hukuki dayanak ölçülmedi.

**Ertelemenin maliyeti sıfır değil, ama ölçülebilir:** Bu turda harcanan iş
kod değil **bilgidir**; E1-E5 yazılı olduğu için B veya C kararı verildiğinde
bu belge güncellenerek doğrudan yol haritasına dönüşür.

---

## Faz E — Öz-eleştiri

1. **Hukuki engelleri ölçmedim — bu belgenin en zayıf yeri.** Sınır ötesi veri
   aktarımı (KVKK → GDPR), her ülkenin kamuya açık firma verisinin ticari
   yeniden kullanım hakkı, TCKN'nin ülke dışına çıkması (D-247/D-248 riski
   D-257'de zaten doğrulandı). Bunlar teknik okumayla ölçülemez. Ölçek 2 ve
   Ölçek 3'ün "eksisi" sütunu bu yüzden **tahmin**, ölçüm değil.
2. **"7 sorudan kaçını cevaplar" sayıları ölçüm değil, yargıdır.** 1/7, 2/7,
   7/7 sayılarını ölçülmüş alan envanterinden mantık yürüterek çıkardım;
   soru bazında tek tek doğrulamadım. D-260 gereği bu sayılar kanıttan ağırdır
   ve Ürün Sahibi birinin sayısını değiştirerek karar verebilir.
3. **Boş `findstr` sonucuna neredeyse güveniyordum.** İlk tur boş döndü;
   "ülke kolonu yok" yazmak bir sonraki dize hazırdı. Pozitif kontrol
   (`vkn` → 12 satır) tırnaklama hatasını ortaya çıkardı. D-266'nın kuralı
   burada da geçerli: **bir bekçinin sessizce hiçbir şey bulmaması, bir
   şey bulduğu kadar güvenilirdir.**
4. **Maliyet tahmin etmedim.** Faz D tablosunun "Ne zaman başlanmalı" sütunu
   bir zaman ister; A yolu dışındaki ikisine yalnız **koşul** yazabildim
   (bütçe/sağlayıcı kararı). Sahte bir maliyet rakamı yazmak D-260 olurdu.

---

## Bulgu (kapsam dışı — pano/rapor düzeltmesi ister)

- 🔴 **Ülke kolonu "yok" ama projede iki tutarsız ülke geleneği zaten var.**
  `job_postings.location_country` (serbest metin, sabit `'Türkiye'`) ile
  `user_activity_log.ulke_kodu` (ISO 3166-1 alpha-2 `CHAR(2)`) aynı şemada
  birbiriyle uyuşmuyor. Doğru biçim `companies`'a taşınmamış. **Ayrı görev
  gerekir**; bu belgede kod yazılmadı.
- 🟡 **NACE Avrupa'ya özgü; NAICS şemada yok** (50 migration tarandı, 0
  eşleşme). "Her şirket" hedefi ABD kapsamında bugün sektör-siz kalır.
  Yapı genişletmesi **veri doğrulamasından önce** yapılırsa (D-252: NACE'in
  %100'ü tahmin, gerçek kod 0) boş kolon riski doğar.
- 🟡 **`is_ankara` kolonu bir soruyu cevaplıyor.** Genel bir konum sorgusu
  varken (`company_locations`) coğrafi kapsam tek bir bayrağa gömülmüş.
  D-258'de aynı tür değişiklik 7 ayrı yerde yarım göç bırakmıştı.
- 🔵 **BRIS adı biliniyor ama ölçülmedi.** Ölçek 2'nin tek somut kaynak
  adayı; pilot olmadan maliyet çıkarılamaz.

---

## Bu belgeden çıkan ayrı görevler (hiçbiri bu belgede yapılmadı)

| # | Gereken iş | Neden ayrı |
|---|---|---|
| 1 | `companies`'a ISO 3166-1 alpha-2 ülke kolonu ekle; `job_postings.location_country`'ı ona bağla | Göç + 27 indeks taraması gerekir (D-258). Bu bir belge yazı işi değil |
| 2 | `company_identifiers.identifier_type`'a ülke kapsamı ekle; `tax_number`'ı "Türkiye'ye özgü" diye belgele | Semantik değişiklik; mevcut UNIQUE kısıtı etkilenir (D-251/2 ikiz yasağı) |
| 3 | Sınıflandırma çatısını NACE + NAICS'e genişlet | Şema göçü **ve** D-252'de açık olan NACE doğrulama borcu (gerçek kod 0) |
| 4 | `is_ankara`'yı genel konum sorgusuna taşı | Aynı dosyada sema beyanı + panel + indeks var; yarım göç riski |
| 5 | Dil katlama haritasını CLDR tabanlı, dil parametreli yap | `normalize.py` + `kaynak_bagla.py` — her iki yazıcı aynı turda düzeltilmeli (D-267/6) |
| 6 | BRIS pilotu (ölçek 2'nin tek somut kaynak adayı) | Kaynak erişimi ölçülmeden plan yazılamaz (D-310 Katman 1) |

> Bu tablo **görev açma listesidir, açılmış görev değildir** (D-77: pano
> bakımı orkestratörün). Sıralama ölçülen engel ağırlığına göredir.

---

## Ölçüm kaynakları (hepsi çalıştırıldı)

| Komut | Sonuç |
|---|---|
| `python scripts/osb_veri_denetim.py` | 8987 kayıt · 8296 tekil · 44 mükerrer · 647 kimliksiz · 0 mojibake |
| `python scripts/osb_veri_denetim.py --self` | `self-check OK` (8296+44+647 = 8987 ✓) |
| `python scripts/osb_veri_denetim.py --kontrol 8987` | çıkış kodu 0 — beyan ölçümle uyuştu |
| `findstr /S /I /N /C:"country" /C:"ulke" /C:"nation" src\company_master\schema\migrations\*.sql` | 3 eşleşme: `0013:20`, `0013:45`, `0017:5`, `0017:20` — `companies`'ta **0** |
| `findstr /S /I /N /C:"vkn" …` (**pozitif kontrol**) | 12 eşleşme → komut sağlam |
| `findstr /S /I /N /C:"nace" …` | `nace_codes` (0002:59-67), `companies.nace_code` (0006:5), `nace_version` (0002:74) |
| `findstr /S /I /N /C:"naics" …` | **0 satır** (50 migration) |
| `findstr /S /I /N /C:"maketrans" /C:"encoding" src\company_master\entity_resolution\*.py` | **0 eşleşme** → brifin dizini yanlış, gerçek yer `api/core/normalize.py` |
| `findstr /S /I /N /C:"maketrans" src\company_master\api\*.py src\company_master\etl\*.py` | `api/core/normalize.py:602,681` · `etl/kaynak_bagla.py:22` |
| `0001_core.sql:34-62` (26 kolon, tamamı açıldı) | ülke kolonu yok; `is_ankara:49`, `is_osb_member:50`, `osb_id:51` |
| `0001_core.sql:72-83` (`sources` tablosu) | ülke kolonu yok; `source_type` 8 değerli CHECK |

---

## İlgili Nodlar

- [[Huginn Data Insights/AGENTS]] — D-238 (ölçüm canlı DB'de) · D-260 (beyan kanıt değildir) · D-266 (mandalın kör noktası) · D-267/6 (yazıcıyı da düzelt)
- [[hubs/PLAN_STRATEGY_HUB]] — B-14 kapanış kaydı
- [[docs/FAZ5_VENDOR_DUE_DILIGENCE_KAPSAM]] — bağımlılık: elimizde ne var
- [[plans/brief_utku_DOC-GLOBAL-INTEL-ARASTIRMA-01]] — görev brifi
- [[D-257]] — MERSİS kapıldı, kimlik kaynakları kapalı (E2'nin veri tarafı)
- [[D-252]] — NACE üç katman, kodların %100'ü tahmin (E3'ün veri tarafı)
- [[D-249]] — "veri yok" ≠ "0 puan" (Yol B'nin ölçülmüş riski)
- [[D-310]] — Agentik kazıma mimarisi, beş katman (yeni ülke kaynakları için)
- [[scripts/osb_veri_denetim]] — kalıcı ölçüm kapısı
- [[src/company_master/schema/migrations/0001_core]] — `companies` / `osbs` / `sources` tanımı
- [[src/company_master/schema/migrations/0002_relations]] — `company_identifiers` · `nace_codes` · `company_locations`
- [[src/company_master/api/core/normalize]] — Türkçe katlama haritası (E5)