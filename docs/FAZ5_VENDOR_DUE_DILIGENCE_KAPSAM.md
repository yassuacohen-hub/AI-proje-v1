# Faz 5 — Vendor Due Diligence (Tedarikçi Ön Denetimi) Kapsam Araştırması

> **Bu bir KOD görevi DEĞİLDİR.** Göç dosyası, tablo, Python modülü, test — hiçbiri
> bu belgede üretilmiştir. Tek çıktı bu dökümandır.
> Kod gerektiği düşünülen yerler "**ayrı görev gerekir**" diye işaretlenmiştir.

**Görev:** `DOC-VENDOR-DD-ARASTIRMA-01` · **Ajan:** yasu · **Oncelik:** P3
**SSOT:** `yedekler/Huginn Data Insights (HUGIns).txt` (kök dizinde)
**SSOT satır sayısı (ölçüldü):** 1687 — brifin varsayımı doğru.

> **Kanıt kuralı (D-260):** Bu belgedeki her tablo/kolon adı
> `src/company_master/schema/migrations/*.sql` içinde **grep ile aranarak** doğrulanmıştır.
> Doğrulanamayan hiçbir ad yazılmamıştır; olmayan veri **"veri yok"** diye yazılmıştır
> (D-249: "veri yok" ile "0" aynı şey değildir).

---

## 0. Neden bu görev bir kod görevi değil

SSOT'ta Faz 5'in tüm içeriği **3 satır**dır. Ölçüldü:

| Kanıt | `dosya:satır` | Ne yazıyor |
|---|---|---|
| Faz 5'in tüm içeriği | `(HUGIns).txt:867-869` | `Faz 5` + `Vendor Due Diligence Platformu` — başka hiçbir şey |
| Karşılaştırma: Faz 2 | `(HUGIns).txt:791-822` | 8 skorun adı, her biri 0-100 ile tarif edilmiş |
| Karşılaştırma: Faz 3 | `(HUGIns).txt:756-774` | 10 düğüm türü sayılmış |

Faz 2 ve Faz 3 için tablo adı, kolon adı ve akış SSOT'ta **vardır**; kod brifi
yazılabilmiştir (`VERI-RISK-MOTORU-01`, `VERI-ENTITY-GRAPH-01`). Faz 5 için hiçbiri yoktur.
Kod brifi yazmak tamamını uydurmak olurdu — bu D-260 ihlalidir.

**Bu yüzden görev: eksik tanımı SSOT'un VAR OLAN parçalarından türetmek.**

### Dayanaklar

1. **Müşterinin 7 sorusu** — `(HUGIns).txt:11-17` (verbatim aşağıda)
2. **8 müşteri kitlesi** — `(HUGIns).txt:25-32`; Faz 5 bunlardan **"Satın alma ekipleri"** (`:25`)
   ve **"Tedarik zinciri yöneticileri"** (`:32`) kitlesinin işidir
3. **Nihai Misyon** — `(HUGIns).txt:875-885`
4. **Faz 2'nin 8 skoru** — `(HUGIns).txt:791-822`

---

## 1. Elimizde ne var — 7 sorunun karşılığı

| # | Müşterinin sorusu (verbatim, SSOT satırı) | Bugün cevaplayabiliyor muyuz? | Hangi veriyle | Eksik olan |
|---|---|---|---|---|
| 1 | "Gerçek bir şirket olup olmadığı" (`:11`) | **kısmen** | `companies.legal_name`, `companies.tax_number` (0001_core.sql:37,39) | MERSİS teyidi yok — D-257 uyarınca **kapalı**; `companies.mersis_number` kolonu var (0001_core.sql:40) ama **doldurulmuyor** |
| 2 | "Yasal yükümlülüklerini yerine getirip getirmediği" (`:12`) | **hayır** | — | **Vergi borcu / SGK borcu / beyan durumu hiçbir tabloda yok.** `certifications` tablosu var (0002_relations.sql) ama içeriği `cert_type` alanı ile **genel**, vergi/sgk ayrımı yok |
| 3 | "Dolandırıcılık riski taşıyıp taşımadığı" (`:13`) | **hayır** | — | `company_risk_scores.fraud_risk_score` kolonu **0047'de değil, 0046'da** tanımlı (`0046_risk_skorlari.sql:32`) — **tablo dosyada var, hesaplama çalışmıyor** (Faz 2 görevi hesaplamayı kapsam dışı bıraktı, D-238) |
| 4 | "Finansal ve operasyonel açıdan sürdürülebilir olup olmadığı" (`:14`) | **hayır** | — | **Finansal veri hiç yok.** `annual_turnover` **şemada yok** (yalnız `0018_visibility_layer.sql:18`'de bir yorum satırında geçiyor, kolon değil). `companies.employee_count` var (0001_core.sql:44) ama `0024_kalite_skor_olu_sinyal.sql:22` "0 dolu kayıt → hepsi NULL" diyor |
| 5 | "Sahiplik yapısının şeffaflığı" (`:15`) | **hayır** | — | Ortaklık/ortak bilgisi **veri olarak yok**. `key_personnel` tablosu var ama **yönetici** içindir, ortak içindir (`0002_relations.sql`); ortaklık zinciri için ayrı tablo yok. Faz 3 `shared_partner` kenar türü şemada **tanımlı ama boş** (`0047_entity_graph.sql`) |
| 6 | "Dijital güvenlik seviyesi" (`:16`) | **kısmen** | `company_tech_profile.technologies`, `.tech_categories` (0002_relations.sql) | Bu **teknoloji envanteridir**, güvenlik değerlendirmesi değildir. `cyber_security_score` yalnız 0046'da kolon olarak var, hesaplanmıyor |
| 7 | "Kurumsal itibarının durumu" (`:17`) | **hayır** | — | `company_risk_scores.reputation_score` kolonu var (0046) ama hesaplanmıyor. İtibar için **kaynak veri tanımı yok** |

### Tablonun boşluğu — ölçülen özet

**7 sorunun 4'üne cevap veremiyoruz, 2'sine kısmen, 1'ine evet.**
Cevap veremediğimiz 4 sorunun **hiçbirinde** eksik olan şey bir "ekran" değil,
**kaynakta veri bulunmaması**. Bu ayrım önemlidir: ekran yapmak eksik veriyi
oluşturmaz (D-260).

### Mevcut tabloların envanteri (ölçüldü)

`src/company_master/schema/migrations/*.sql` içinde **54 tablo** `CREATE TABLE` ile tanımlı.
Denetleme için ilgili olanlar:

| Tablo | Ne tutar | Kanıt |
|---|---|---|
| `companies` | ana firma kaydı, `legal_name`, `tax_number`, `status`, `osb_id` | 0001_core.sql:34 |
| `company_identifiers` | vkn / mersis / ticaret_sicil türü kimlikler | 0002_relations.sql:25 |
| `company_locations` | adres kayıtları | 0002_relations.sql |
| `company_contacts` | telefon / e-posta / web | 0002_relations.sql |
| `key_personnel` | yönetici (ad, pozisyon, `is_public`) | 0002_relations.sql |
| `company_industries` | NACE kodu + `is_primary` | 0002_relations.sql:70 |
| `certifications` | sertifika (`cert_type`, `expiry_date`, `is_valid`) | 0002_relations.sql |
| `evidence` | kanıt kaydı (`source_reliability`, `independence_score`) | 0003_intelligence.sql |
| `company_state` | `financial_pressure_state`, `growth_state` vb. | 0003_intelligence.sql:81 |
| `company_intelligence_scores` | büyüme/genişleme/teknoloji skorları | 0003_intelligence.sql |
| `commercial_signals` | sinyal (`strength`, `recency`, `independence`) | 0003_intelligence.sql |
| `company_risk_scores` | **8 güven skoru** (0046) | 0046_risk_skorlari.sql:26 |
| `company_edges` | firma ilişki ağı (0047, Faz 3) | 0047_entity_graph.sql |
| `quarantine_firms` | karantina havuzu | 0002_relations.sql |
| `ihale_ilanlari` | kamu ihaleleri | 0042_tender_kolonlari_ingilizce.sql |


---

## 2. Tedarikçi Denetim Soruları

SSOT'un 7 sorusu, **satın almacı gözüyle** (kitle `(HUGIns).txt:25` ve `:32`) denetim
sorusuna çevrildi. Her soru üç parça taşır. Kolon adları **grep ile doğrulandı**.

> **D-245 notu:** Brifin örneğinde `companies.vkn` yazıyordu. Diskte böyle bir kolon
> **yoktur**. VKN'nin kanonik kolonu **`companies.tax_number`**'dır
> (`0001_core.sql:39`, yorumu: `-- VKN (boş olabilir)`). Aşağıda doğru ad kullanıldı.

### S1 — Bu tedarikçi gerçekten var mı, kayıtlı mı?
- **Neden önemli:** Olmayan firmaya avans ödemesi en sık görülen tedarik zinciri zararıdır.
- **Hangi veriyle cevaplanır:** `companies.legal_name` (var — `0001_core.sql:37`),
  `companies.tax_number` (var — `0001_core.sql:39`, UNIQUE), `companies.status`
  (var — `0001_core.sql:42`; active/inactive/unknown). MERSİS teyidi: **veri yok**
  (D-257 uyarınca kapalı; `companies.mersis_number` kolonu var — `0001_core.sql:40`
  — ancak doldurulmuyor).
- **SSOT dayanağı:** `(HUGIns).txt:11`

### S2 — Vergi ve SGK borcu var mı, yasal yükümlülüğünü yerine getiriyor mu?
- **Neden önemli:** Vergi borcu olan tedarikçiye ödeme yapmak alıcı tarafında
  sorumluluk doğurur; çoğu KBY'de **peşin ödeme yasağı** vardır.
- **Hangi veriyle cevaplanır:** **veri yok.** Şemada vergi borcu, SGK borcu, beyan
  durumu ya da vergi teyidi tutan **hiçbir tablo/kolon yok**. `certifications`
  tablosu var (`0002_relations.sql`) ama `cert_type` serbest metindir; "veri borcu
  yok" tipi kayıt için standart yoktur. `source_records.raw_tax_number`
  (`0001_core.sql:95`) yalnız kimlik numarasıdır, borç bilgisi değildir.
- **SSOT dayanağı:** `(HUGIns).txt:12`

### S3 — Bu firma konklanmış ya da dolandırıcılık sicilinde var mı?
- **Neden önemli:** Sahte tedarikçi en pahalı hatadır; teslim sonrası tespit edilir
  ve para geri dönmez.
- **Hangi veriyle cevaplanır:** **veri yok.** `company_risk_scores.fraud_risk_score`
  kolonu **şemada tanımlı** (`0046_risk_skorlari.sql:32`) ama **hesaplama çalışmıyor**
  — 0046 görevi yalnız tablo açtı, hesabı kapsam dışı bıraktı (D-238). Kolon bu
  yüzden **NULL**'dur. NULL ≠ 0 (D-249): "temiz" değil, **"ölçülmedi"**.
- **SSOT dayanağı:** `(HUGIns).txt:13`

### S4 — Finansal olarak ayakta mı, sürdürülebilir bir tedarikçi mi?
- **Neden önemli:** Zayıf mali yapılı bir tedarikçi sözleşmeyi ortada bırakır ve
  üretim hattını durdurur.
- **Hangi veriyle cevaplanır:** **veri yok.** `annual_turnover` **şemada kolon
  değildir** — yalnız `0018_visibility_layer.sql:18`'de bir alan grubu yorumunda
  geçer. `companies.employee_count` var (`0001_core.sql:44`) ancak
  `0024_kalite_skor_olu_sinyal.sql:22` açıkça "employee_count: 0 dolu kayıt → hepsi
  NULL" der. `company_state.financial_pressure_state` **TEXT kolonu** olarak var
  (`0003_intelligence.sql:81`) ama **doluluğu ölçülmedi**; NULL ise "ölçülmedi"dir.
  Bilanço/beyanname veri kaynağı **hiç bağlı değil**.
- **SSOT dayanağı:** `(HUGIns).txt:14`

### S5 — Kim borçlu? Ortaklık zinciri kimde, şeffaf mı?
- **Neden önemli:** Sahiplik gizliliği peşin ödeme riskini ve dolandırıcılık
  ihtimalini artırır; grup şirketlerinden biri iflâs ettiyse tüm grup riske girer.
- **Hangi veriyle cevaplanır:** `key_personnel.full_name` + `.position`
  (`0002_relations.sql` — **yönetici** içindir). **Ortak bilgisi: veri yok** —
  ortaklık/ortak tablosu şemada bulunmuyor. Faz 3'ün `shared_partner` kenar türü
  (`0047_entity_graph.sql` kanonik listesi) bu boşluğu kapatmak için **tanımlı ama
  boş bırakıldı** (D-249) — kaynak veri yok.
- **SSOT dayanağı:** `(HUGIns).txt:15`

### S6 — Dijital altyapısı tedarik zincirine uygun mu?
- **Neden önemli:** Tedarikçinin ERP/OTM bağlantısı yoksa sevkiyat ve stok takibi
  elle yapılır; gecikme ve fire riski doğar.
- **Hangi veriyle cevaplanır:** `company_tech_profile.technologies` (JSONB),
  `.tech_categories` (JSONB), `.modernization_signals` (JSONB),
  `.tech_stack_maturity` (NUMERIC) — `0002_relations.sql`. **Dijital GÜVENLİK
  değerlendirmesi için veri yok:** `company_risk_scores.cyber_security_score`
  kolonu var (`0046_risk_skorlari.sql:29`) ama hesaplanmıyor (aynı boşluk).
  KVKK sızıntısı geçmişi için kaynak bağlantısı yok.
- **SSOT dayanağı:** `(HUGIns).txt:16`

### S7 — Sektöründeki itibarı ve geçmiş performansı nasıl?
- **Neden önemli:** Sektörde uzun süredir çalışan, ihalelerde ve referansta görünen
  firma yeni tedarikçiye göre daha öngörülebilirdir.
- **Hangi veriyle cevaplanır:** `ihale_ilanlari` (kamu ihaleleri — 0042),
  `ihale_katilimcilar` (katılımcı firmalar), `company_events` (TSG olayları — 0037),
  `evidence.source_reliability` + `.independence_score` (`0003_intelligence.sql`).
  **Doğrudan itibar skoru: veri yok** — `company_risk_scores.reputation_score`
  kolonu var (`0046_risk_skorlari.sql:27`) ama hesaplanmıyor.
- **SSOT dayanağı:** `(HUGIns).txt:17`

### S8 — Bu firma hangi OSB'de, aynı anda kaç OSB üyesi var?
- **Neden önemli:** Çok OSB üyeliği ölçek göstergesidir; tek OSB'de sıkışmış küçük
  bir firma büyük siparişi karşılayamayabilir.
- **Hangi veriyle cevaplanır:** `companies.osb_id` (FK — `0001_core.sql:51`),
  `osbs.name` (master — `0001_core.sql:19`), Faz 3'ün `company_edges` `same_osb`
  kenarı (`0047_entity_graph.sql`). Bu **tek sorudur ki Faz 3 tamamlandığı için
  cevaplanabilir durumdadır** — üretici
  `src/company_master/graph/kenarlar.py:osb_komsulari()` hazırdır

---

## 3. Eksik Veri Kaynakları

Emir #39 ("eksik yerlerin kaydını tutalım") karşılığı. **Engel kolonu boş bırakılmamıştır** —
"bilmiyorum" geçerli bir cevaptır ve yazılmıştır.

| Eksik | Kimin işi | Nasıl elde edilir | Engel | Tahmini değer |
|---|---|---|---|---|
| Vergi borcu / beyan durumu | **bilmiyorum** — GİB ile lisans koşulu gerekir | GİB e-BEYANNAME / borç sorgusu; OAI entegrasyonu araştırılacak | **Lisans + mahremiyet**: üçüncü taraf veri satımı hukuki dayanak gerektirir (D-257 benzeri). Ücretli veya kurum içi erişim | Çok yüksek — sözleşmen en sık iptal nedeni |
| SGK borcu durumu | **bilmiyorum** | SGK (e-Devlet / 4A) sorgusu; API erişimi araştırılacak | e-Devlet oturum açma + kişiye özel veri; hukuki dayanak yok | Yüksek — peşin ödeme yasağına bağlı |
| Ticaret sicili teyidi (MERSİS) | İhsan (hukuki karar) | MERSİS sorgusu | **KAPALI** — D-257 uyarınca izin süreci sahibi İhsan, ajan göndermez | Yüksek — "gerçek şirket mi" sorusunun tek otoriter cevabı |
| Konkolo / iflas sicili | **bilmiyorum** | Resmî Gazete konkloro ilanları; ticaret sicil gazetesi arşivi | Serbest erişim yok; arşiv toplama gerekir | Yüksek — dolandırıcılık riskinin en ucuz göstergesi |
| Ortaklık / ortak bilgisi | **bilmiyorum** — SSOT'ta karşılığı yok | MERSİS ortaklık beyanı (kapalı) veya ortaklık değişikliği ilanları | MERSİS kapalı; alternatif kaynak araştırılacak | Yüksek — S5'in tamamı bu veriye bağlı |
| Finansal tablolar (ciro, bilanço) | **bilmiyorum** | Halka açık şirketler için KAP/BDDK; özel şirketler için **kaynak yok** | Özel şirket finansal verisi **ticari sır**; kamuya açık değil | Çok yüksek — S4'ün tamamı |
| Siber güvenlik değerlendirmesi | **bilmiyorum** | Dış rating (SecurityScorecard vb. — ücretli), CERT kayıtları, KVKK ihlal bildirimleri | Ücretli lisans + **ölçülmemiş**: hangi sağlayıcının hukuki olarak kullanımı uygun, bilinmiyor | Orta — S6'nın yarısı |
| Sigorta / kredi geçmişi | **bilmiyorum** | Kredi kayıt büroları (KKB) — kişiye özel, sözleşmeli | KVKK + lisans; bireysel onay gerekir | Düşük — erişimi zor, değeri sınırlı |

**Sayı:** 8 eksik kaynak. **6'sının kimin işi olduğu bilinmiyor** — bu, Faz 5'in
gerçek engelidir: ekran değil, **veri erişimi**.

---

## 4. Yol Önerileri

> **Süre kolonu TAHMİNDİR.** Tahmin olduğu açıkça yazıldı; ölçüm değildir (D-260).
> Tek kişilik ekip ve mevcut kod tabanı varsayımıyla 1 hafta = 5 iş günü alınmıştır.

| Yol | Ne yapar | Artısı | Eksisi | Süre (tahmin) |
|---|---|---|---|---|
| **A** | Yalnız mevcut 8 skoru tek "tedarikçi karnesi" ekranında toplar | En hızlı; yeni veri gerektirmez; Faz 2'nin çıktısını tek yerde gösterir | Yeni bilgi üretmez; 8 skor hesaplanmadığı için ekran **boş** gelir (D-249) | 3 gün (tahmin) |
| **B** | 8 soruyu ayrı ayrı cevaplayan modül; cevaplanamayanları **"ölçülmedi"** olarak yazar | Dürüst; Faz 5'i gerçekten kurar; eksik veri listesini ürünün içine gömer | Faz 2 bitmeden anlamlı sonuç vermez; "ölçülmedi" etiketi satışta zor görünür | 8 gün (tahmin) |
| **C** | Harici veri satın alır (ticaret sicil sağlayıcı) | Boşluğu gerçekten kapatır | Maliyet + sözleşme + hukuki değerlendirme (D-257); en yavaş | 4-8 hafta (tahmin) |

### ← ÖNERİM: **Yol B**

**Gerekçe:** Yol A en hızlı ama **ekranı boş bir ürün** üretir — 8 skor kolonu şemada
var, hesabı yok; 8 sütunlu boş tablo "0 puan" gibi okunur ve bu tam olarak D-249'un
yasakladığı sessiz yalan olur. Yol C boşluğu kapatır ama hukuki karar gerektirir
(D-257) ve ajan karar veremez. Yol B ise **ölçülebilen doğru yanıtı** üretir: 8
sorumuzun 4'üne "ölçülmedi" der, 1'ine (OSB) gerçekten cevap verir, kalan boşluğu
ürün içinde görünür kılar — bu da emir #39'un ("eksik yerlerin kaydını tutalım")
karşılığıdır.

**Bağımlılık uyarısı:** Yol B, Faz 2'nin **hesaplama** tarafının bitmesine bağlıdır.
0046 tabloyu açtı, hesabı yazmadı (D-238). Bu, **ayrı bir görev gerekir**.

---

## 5. Öz-eleştiri

- **Bu araştırmanın en zayıf yeri:** Faz 5'i **satın alma gözüyle** türettim
  (`(HUGIns).txt:25`). Tedarik zinciri yöneticisi kitlesi (`:32`) farklı sorular
  sorar — onun için asıl soru "firmayı denetlemek" değil, "birden fazla tedarikçiyi
  aynı anda izlemek ve aralarındaki bağı görmek" olur. Bu da doğrudan Faz 3'ün
  `company_edges` kenarına işaret eder; benim çerçevem o boyutu **atlamış olabilir**.
  İki kitlenin ihtiyacını karşılaştırmadım.
- **İkinci zayıflık:** Kolon adlarını **şemada varlık** olarak doğruladım, **doluluk** olarak
  doğrulamadım. `company_state.financial_pressure_state` ve `companies.employee_count`
  şemada var; kaç satırda dolu olduğunu ölçmedim. "Var" ile "dolu" farklı şeydir
  ve bu belgede ikisini birbirine karıştırmış olabilirim.
- **Üçüncü zayıflık:** Süre tahminleri **ölçüm değil, sezgi**. Benzer bir modülün
  gerçek süresini referans almadan yazdım.

---

## 6. Önerilen sonraki adımlar (her biri ayrı görev gerekir)

1. **Faz 2 hesaplama görevi** — 8 skoru dolduran motor (`company_master/risk/`).
   Yol B'nin ön koşulu. *Kanıt:* [[Huginn Data Insights/plans/brief_utku_VERI-RISK-MOTORU-01]]
   — tablo açıldı (`0046_risk_skorlari.sql`), **hesap yazılmadı** (D-238).
2. **Faz 5 modülü** — 8 soruyu ayrı ayrı cevaplayan, "ölçülmedi" ayrımını koruyan modül.
3. **Eksik veri kaynakları araştırması** — vergi/SGK/konkolo için erişim ve hukuki
   dayanak araştırması (D-257 usulü: karar sahibi İhsan).
4. **MERSİS izin süreci** — İhsan'ın sahipliğinde, ajan göndermez.

---

## 7. Kanıt dosyaları (D-218/D-184)

Bu belgedeki her tablo/kolon adı **grep ile doğrulandı**. Doğrulayan dosyalar:

| Kanıt | Yer | Ne doğruladı |
|---|---|---|
| Ana şirket şeması | `src/company_master/schema/migrations/0001_core.sql` | `companies` PK'si `company_id` (`:35`), `tax_number` (`:39`), `mersis_number` (`:40`), `employee_count` (`:44`), `osb_id` (`:51`), `osbs` (`:19`) |
| İlişki şeması | `src/company_master/schema/migrations/0002_relations.sql` | `company_industries` (`:70`), `key_personnel`, `company_tech_profile`, `certifications`, `company_contacts` |
| Zekâ şeması | `src/company_master/schema/migrations/0003_intelligence.sql` | `evidence.source_reliability`, `company_state.financial_pressure_state` (`:81`) |
| **Faz 2 skor tablosu** | `src/company_master/schema/migrations/0046_risk_skorlari.sql` | 8 skor kolonu (`:27-32`) — **hesap yok** |
| **Faz 3 ilişki ağı** | `src/company_master/schema/migrations/0047_entity_graph.sql` | `same_osb` kenarı, `shared_partner` boş (D-249) |
| Görünürlük katmanı | `src/company_master/schema/migrations/0018_visibility_layer.sql` | `annual_turnover`'ın **yalnız yorum** olduğu (`:18`) — kolon değil |
| Kalite skoru | `src/company_master/schema/migrations/0024_kalite_skor_olu_sinyal.sql` | "employee_count: 0 dolu kayıt → hepsi NULL" (`:22`) |
| Risk motoru kodu | `src/company_master/risk/skorlar.py` | Faz 2 motoru — bu belgede **boş** olduğu yazıyor |
| Doğrulama testi | `tests/test_dokuman_politikasi.py` | D-218 kapısı (≥2 wikilink) |

### Ölçüm zinciri

```
SSOT (HUGIns).txt:11-17, :25-32, :867-869, :875-885
  └─> bu belge (7 soru → 8 denetim sorusu → 8 eksik kaynak)
        └─> yol seçimi (Yol B önerildi)
              └─> ön koşul: Faz 2 hesaplama (0046 var, hesap yok)
                    └─> Faz 5 modülü (yok — ayrı görev)
```

---

## İlgili Nodlar

- [[Huginn Data Insights/hubs/PLAN_STRATEGY_HUB]] — görev kapanış kaydı (B-14)
- [[Huginn Data Insights/AGENTS]] — D-218 (graf) · D-219 (ajan hafızası) · D-245 (kolon adı ölçümü) · D-249 (veri yok ≠ 0) · D-260 (kanıtsız iddia yasak) · D-257 (hukuki karar sahibi) · D-238 (ölçüm kapsamı) · D-184 (köprü)
- [[Huginn Data Insights/plans/brief_yasu_DOC-VENDOR-DD-ARASTIRMA-01]] — bu görevin brifi
- [[Huginn Data Insights/plans/brief_utku_VERI-RISK-MOTORU-01]] — Faz 2, 8 skor (tablo açık, hesap yok)
- [[Huginn Data Insights/plans/brief_yasu_VERI-ENTITY-GRAPH-01]] — Faz 3, ilişki ağı (S8'i besler)
- [[Huginn Data Insights/plans/brief_yasu_VERI-OSB-TEMIZLIK-01]] — benzer "ölçülmemiş veri" kararı, paralel borç
- [[Huginn Data Insights/data/orchestrator/osb_temizlik_raporu_2026-10-01]] — aynı "beyan ≠ veri" dersi, OSB tarafı
- [[Huginn Data Insights/docs/BORC_DEFTERI]] — 6 eksik kaynağın bilinmeyen kısmı borç olarak yazılabilir
- `data/orchestrator/task_board.json` — `DOC-VENDOR-DD-ARASTIRMA-01` pano kaydı

  (canlı yazım D-238 kapsamı dışında).
- **SSOT dayanağı:** `(HUGIns).txt:14` + `:32`
