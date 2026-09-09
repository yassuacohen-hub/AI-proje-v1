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

## Kural 3: Tabela İsmi (trade_name) = Marka/İlgi Alanı

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

## Kural 4: Görsel Sunum Kuralı

Dataframe ve tablolarda Markdown yıldızı (**) KULLANILMAZ; temiz metin olarak gösterilir. "Tabela İsmi" ayrı bir sütun olarak sağlanır.

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
