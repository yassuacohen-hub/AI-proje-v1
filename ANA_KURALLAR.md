# Huginn Ticari İstihbarat Platformu — Ana Kurallar

> **Kaynak:** `Huginn Data Insights/AI proje v1/V10/09_kurallar_ve_promptlar/11_unvan_kisaltma_ve_tabela_kurallari`

## Kural 1: Firma Adları BÜYÜK HARFLE Yazılır

Tüm firma adları (`legal_name`) her zaman BÜYÜK HARFLE gösterilir.

- **Backend**: `web_app.py` → `normalize_company_name()` fonksiyonu
- **Frontend**: `app.js` → `renderTable()` ve `showDetail()` fonksiyonlarında `.toUpperCase()`

**Örnek:**
- DB'de: `"Arıtes Metal Sanayi ve Ticaret Ltd. Şti."`
- Ekranda: `"ARITES METAL SAN. VE TİC. LTD. ŞTİ."`

## Kural 2: Standart Kısaltmalar Uygulanır

Kısaltmalar **Türkçe karakterli**dir (kaynak doküman Bölüm 2'ye birebir uyumlu).

| Kategori | Özel Kombinasyon | Kısaltma |
|----------|-----------------|----------|
| Şirket Türü | ANONİM ŞİRKETİ | A.Ş. |
| Şirket Türü | LİMİTED ŞİRKETİ | LTD. ŞTİ. |
| Şirket Türü | KOLLEKTİF / KOMANDİT | KOL. ŞTİ. / KOM. ŞTİ. |
| Faaliyet | SANAYİ VE TİCARET | SAN. VE TİC. |
| Faaliyet | SAN VE TİC (noktasız varyant) | SAN. TİC. |
| Faaliyet | İTHALAT VE İHRACAT | İTH. İHR. |
| Faaliyet | İNŞAAT SANAYİ VE TİCARET | İNŞ. SAN. TİC. |
| Faaliyet | MÜHENDİSLİK MİMARLIK | MÜH. MİM. |
| Faaliyet | TURİZM VE TİCARET | TUR. TİC. |
| Faaliyet | GIDA SANAYİ VE TİCARET | GIDA SAN. TİC. |
| Faaliyet | TEKSTİL SANAYİ VE TİCARET | TEK. SAN. TİC. |
| Faaliyet | NAKLİYAT VE TİCARET | NAK. TİC. |
| Faaliyet (tekli) | ELEKTRİK / ELEKTRONİK | ELEK. |
| Faaliyet (tekli) | İNŞAAT | İNŞ. |
| Faaliyet (tekli) | TİCARET | TİC. |
| Faaliyet (tekli) | MÜHENDİSLİK | MÜH. |
| Faaliyet (tekli) | MİMARLIK | MİM. |

**Tam liste:** `web_app.py` içinde `_COMPANY_TYPE_ABBR`, `_ACTIVITY_ABBR`, `_COMBO_ABBR` sözlükleri

## Kural 3: Zorunlu İletişim Dili ve Akıl Yürütme — %100 TÜRKÇE (Demir Kural)

- **Kullanıcı ile İletişim:** Tüm ajanlar (Roo, Kilo, Claude, Cline vb.), kullanıcıyla olan sohbetlerinde, açıklamalarında, durum özetlerinde ve soru-cevaplarda **istisnasız %100 Türkçe** konuşacaktır.
- **Akıl Yürütme / Düşünce Süreci (Thinking/Reasoning):** Ajanlar düşünce adımlarını kullanıcının kolayca takip edebilmesi için **kısa maddeler halinde ve Türkçe** yürütecektir. Edebi veya gereksiz uzun cümlelerden kaçınılarak hem şeffaf takip sağlanacak hem token israfı önlenecektir.
- **Teknik/Kodlama Katmanı:** Kodlar, fonksiyon/değişken isimleri, SQL sorguları, testler ve teknik API terimleri İngilizce olabilir.
- **Token Prensibi:** Token tasarrufu dilden değil, **kısa ve öz yanıt vermekten (bağlam yönetiminden)** sağlanır. Uzun metinler yerine, net ve kısa Türkçe raporlar verilecektir.

## Kural 4: Tabela İsmi (trade_name) = Marka/İlgi Alanı

Tabela ismi, kısaltma ve şirket türü kelimeleri çıkarıldıktan sonra kalan ilk 2-3 kelimeden oluşur.

- **Backend**: `web_app.py` → `extract_trade_name()` fonksiyonu
- **Filtrelenen kelimeler**: `_TRADE_NAME_STOP_WORDS` (VE, SAN., TIC., LTD. STI., A.S., vb.)
- **Uygulama**: Hem ingest sırasında hem API çıktısında uygulanır

**Örnekler:**
- `"ARITES METAL SANAYI VE TICARET LTD. STI."` → `"ARITES METAL"`
- `"DÜNDAR ELEKTRİK SANAYI"` → `"DÜNDAR ELEKTRİK"`
- `"ZMT PTO HIDROLIK"` → `"ZMT PTO"`
- `"GIDA SANAYI VE TICARET A.Ş."` → `"GIDA"`
- `"BUYUK AGAC MOB.INS.SAN. VE TIC. LTD.STI."` → `"BUYUK AGAC"`

## Kural 5: Görsel Sunum Kuralı

Dataframe ve tablolarda Markdown yıldızı (**) KULLANILMAZ; temiz metin olarak gösterilir. "Tabela İsmi" ayrı bir sütun olarak sağlanır.

## Marka Adları ve Dil Sözleşmesi (MRK-04)

### Sözlük

| Marka | Emoji | Kapsam | Teknik önek |
|---|---|---|---|
| **Huginn** | 🦅 | Müşteri yüzeyi (8000) — canlı izleme, "Ne oluyor?" | `huginn_` |
| **Muninn** | 🛡️ | İç ekip yüzeyi (8501) — hafıza, denetim, "Ne oldu, neden?" | `muninn_` |
| **Odin** | ⚡ | Çekirdek/altyapı (görünmez) — karar, yetki, köprü | `odin_` |

### Yazım kuralları (ZORUNLU)

- `Huginn`, `Muninn`, `Odin` **çevrilmez, kısaltılmaz, ekle bölünmez**.
- **Yasak yazımlar:** `Muginn`, `Hugin`, `Munin`, `Hugginn`, `Odın`.
- Türkçe ek alırken kesme işareti: `Huginn'in`, `Muninn'e`, `Odin'in`.
- Dil paketi anahtarları `{marka}_{alan}_{durum}` biçiminde, **en az 3 parça**:
  `huginn_akis_bos` ✅ · `huginn_bos` ❌
- Kod içi teknik önek küçük harf: `huginn_`, `muninn_`, `odin_`.

### "Tarihsel Çatı Adı" kuralı

`huginn` adı **veritabanı adı, repo adı, `HuginnMCPServer`,
`admin@huginn.local`** gibi teknik kimliklerde **hiç değişmez**.
Marka ayrımı yalnızca kullanıcıya görünen metin ve yeni kod
adlandırmasında geçerlidir. **Sıfır migration.**

### Güvenlik supabı — mitolojik dil yasağı

Aşağıdaki metinlerde mitolojik dil **kesinlikle kullanılmaz**:

- Hata mesajları ve hata kodları
- Para, fatura, fiyat, kota bilgisi
- Yetki reddi ve güvenlik uyarıları
- Yasal / KVKK / sözleşme metinleri
- Tablo başlıkları, metrik değerleri, menü etiketleri

**Yasaklı sözcükler (`veri` katmanında):**
`Huginn, Muninn, Odin, Bifröst, diyar, kuzgun, taht, mühür, Valhalla, Asgard`

❌ "Bifröst çöktü, kuzgunlar geri dönemiyor."
✅ "Bağlantı kesildi (503). Yeniden deneniyor."

### Paket → kuzgun mantıksal haritası (fiziksel taşıma YOK)

| Kod dizini | Kuzgun | Gerekçe |
|---|---|---|
| `web_dashboard/` (8000 statik) | 🦅 Huginn | Müşteri yüzeyi |
| `web_dashboard/tabs/admin_*` | 🛡️ Muninn | İç ekip ekranları |
| `src/company_master/engine/`, `intelligence/`, `vector/` | ⚡ Odin | Karar çekirdeği |
| `src/company_master/db/`, `schema/`, `etl/` | 🛡️ Muninn | Hafıza/arşiv |
| `src/company_master/api/`, `gateway/`, `queue/` | 🦅 Huginn | Canlı akış |
| `src/company_master/auth/`, `logging/`, `orchestrator/` | ⚡ Odin | Yetki ve yönetim |

⚠️ Bu tablo **mantıksal**dir. Hiçbir dizin yeniden adlandırılmaz veya
taşınmaz; import yolları değişmez.

## Kural 6: Orkestratörün Token Optimizasyonu ve Tasarruf Sorumluluğu

Orkestrasyon rolünü üstlenen ajan veya koordinatör her kim olursa olsun:
1. **Sürekli Öneri & Önlem Zorunluluğu:** Kullanıcının token maliyetlerini minimize etmek için proaktif olarak bağlam sıkıştırma, gereksiz dosya okumayı önleme ve token tasarrufu önerileri sunmak ve gerekli teknik önlemleri almakla **yükümlüdür**.
2. **Gereksiz Okuma Yasağı:** Tek seferde binlerce satırlık ham kaynak okumak yerine parçalı okuma (`start_line`/`end_line`) veya Wiki sentezlerini kullanmalıdır.
3. **Kısa ve Net İş Brifleri:** Ajanlara atanan görevler laf kalabalığından arındırılmış, doğrudan amaca yönelik kısa talimatlarla verilmelidir.
4. **Denetim:** Token harcamasını artıran tekrarlı veya döngüye giren süreçler tespit edildiğinde derhal kullanıcı uyarılmalı ve süreç optimize edilmelidir.


## Uygulama Noktaları

| Bileşen | Fonksiyon | Durum |
|---------|-----------|-------|
| `web_app.py` | `normalize_company_name()` | ✅ |
| `web_app.py` | `extract_trade_name()` | ✅ |
| `web_app.py` | `normalize_company()` | ✅ |
| `/api/companies` | `normalize_company(row)` | ✅ |
| `/api/companies/export` | `normalize_company(dict(r))` | ✅ |
| `/api/company/{id}` | `normalize_company(row)` | ✅ |
| `app.js` | `renderTable()` → `.toUpperCase()` | ✅ |
| `app.js` | `showDetail()` → `.toUpperCase()` | ✅ |
| `normalize.py` (ETL) | `extract_trade_name()` | ✅ (ayrı implementasyon, senkronize) |

## Yeni Veri Kaynağı Eklendiğinde

Yeni bir veri kaynağı (scraper) eklendiğinde, ingest sırasında bu kurallar otomatik uygulanır:
1. `legal_name` → `normalize_company_name()` ile kısaltmalar uygulanır
2. `trade_name` boşsa → `extract_trade_name()` ile tabela ismi üretilir
3. API'den dönen tüm firma verileri `normalize_company()`'den geçer

---

## Kural Doğrulama Testleri

Kural regresyon testleri `scripts/_kural_testleri.py` dosyasındadır (2026-09-08):
- **Kural 1+2:** 7 vaka (A.Ş., LTD. ŞTİ., İNŞ. SAN. TİC., MÜH. MİM., SAN. TİC. combo, İTH. İHR., TUR. TİC.)
- **Kural 3:** 10 vaka (DÜNDAR ELEKTRİK, GIDA, AKSU KROM, 4N BİLİŞİM vb.)
- **API davranışı:** eski/tabela üretimi
- **Sonuç:** 18/18 GEÇTİ ✓ — `python scripts/_kural_testleri.py`

> ⚠️ Kısaltma sözlüklerinde yazım: `INSAAT` (I'lı) anahtar; çıktı `İNŞ.` (Türkçe). `INSANAT` **yazım hatasıdır, kullanmayın.**

---

## Tamamlanan Altyapı Özellikleri (2026-09-08)

### API Güvenlik ve Performans
| Özellik | Açıklama | Durum |
|---------|----------|-------|
| API Key Auth | `X-API-Key` header veya `?api_key=` query param | ✅ |
| Rate Limiting | 120 istek/dakika, sliding window | ✅ |
| Session Tracking | `X-Source` header ile kaynak izleme | ✅ |
| CORS | `Access-Control-Allow-Origin: *` | ✅ |

### Arama ve Filtreleme
| Özellik | Açıklama | Durum |
|---------|----------|-------|
| Türkçe Arama | ı→i, ş→s, ç→c, ğ→g, ö→o, ü→u normalize | ✅ |
| Çoklu Kaynak | `?sources=aso.org.tr,ostim.org.tr` | ✅ |
| Kalite Filtresi | `?min_quality=50` | ✅ |
| Sayfalama | `?limit=50&offset=0` | ✅ |
| Sıralama | `?order_by=quality_score&order_dir=desc` | ✅ |

### Dashboard UX
| Özellik | Açıklama | Durum |
|---------|----------|-------|
| Skeleton Loading | Tablo yüklenirken shimmer efekti | ✅ |
| Zenginleştir Rozetleri | Eksik alanlar için "zenginleştir" badge | ✅ |
| Watchlist | Yıldızlı izleme, localStorage kalıcı | ✅ |
| Kayıtlı Filtreler | Son filtre 12 saat saklanır | ✅ |
| Detay Paneli | Sağ panelde firma detayları | ✅ |
| CSV Export | Filtrelenmiş veriyi dışa aktarma | ✅ |

### Veri Kalitesi
| Özellik | Açıklama | Durum |
|---------|----------|-------|
| Kalite Skoru | 0-100 arası otomatik hesaplama | ✅ |
| Duplicate Detection | Aynı firma tespiti | ✅ |
| Source Record ID | Orijinal kaynaktan izleme | ✅ |
