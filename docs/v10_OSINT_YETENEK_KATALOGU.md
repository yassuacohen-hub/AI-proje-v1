# V10 — OSINT & 9Router Yetenek Kataloğu (Canlı Doküman)

> **Sürüm:** 1.0.2 | **Son güncelleme:** 2026-09-12
> **Durum:** Canlı — iş ilerledikçe, yeni yetenekler doğrulandıkça ve kararlar alındıkça **güncellenir**.
> **Sahip:** Ürün Sahibi + Koordinatör Ajan (birlikte yönetilir)
> **İlişkili:** [`docs/9ROUTER_SEMANTIK_KATMAN_MIMARISI.md`](9ROUTER_SEMANTIK_KATMAN_MIMARISI.md), `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md` (V9)

---

## 1. Amaç ve Kapsam

Bu doküman, sistemin **9Router AI Gateway + OSINT kazıma motoru** üzerinden sunabileceği tüm yetenekleri tek çatı altında toplar:

- **Neyi zaten yapabiliyoruz?** (çalışan ve canlı doğrulanmış yetenekler)
- **Neyi yapacağız?** (önerilen/planlanan yetenekler, öncelik ve gerekçe)
- **Nasıl eşleşiyor?** (yetenekların birbirini nasıl beslediği: örneğin embed + matcher → dublikasyon)
- **OSINT pipeline'ında hangi aşamada devreye girecek?** (veri akışı)

Motivasyon: V10 yönetim yapısında yetenekler çeşitli raporlara (görev panosu, mimari rapor, ajan tanımları) dağılmış durumda. Bu katalog, **tek başvuru kaynağı (SSOT)** olarak yetenek bütününü görünür kılar ve sunucuya taşınma (VPS/tünel) yol haritasını besler.

**Kapsam dışı:** Ticari/satış görünümleri, Streamlit arayüz detayları (MVP kuralı: önce veri, sonra arayüz).

---

## 2. Mevcut Yetenekler (Doğrulanmış )

> Doğrulanmış = kod + birim test + (uygunsa) canlı çağrı ile kanıtlanmış.
> Canlı doğrulamalar: 2026-09-11 (9R-03) ve 2026-09-12 (9R-04: web_fetch/web_search), hem lokal (`http://localhost:20128`) hem tünel (`https://r3qmzpf.abc-tunnel.us`) uçlarıyla yapıldı.

### 2.1 9Router Gateway İstemcisi — [`gateway/ninerouter_client.py`](../src/company_master/gateway/ninerouter_client.py)

| Yetenek | Açıklama | Girdi | Çıktı | Örnek Kullanım |
|---|---|---|---|---|
| **health** | Gateway ayakta mı + API anahtarı geçerli mi | — | `bool` | Tünel/lokal kontrol: `NineRouter().health()` → `True` |
| **list_models** | Modelleri listele (kind filtreli: `embedding`/`chat`/`web`) | `kind: str` | `list[dict]` | 15 embedding modeli görüntülendi |
| **embed** | Metni vektöre çevirir | `input: str/list[str]`, `model` | `list[list[float]]` (1536 boyut) | `nr.embed(["firma metni"])` → 1536-d |
| **chat** | Doğal dil üretim/çıkarım | `messages/body`, `model` | `str` | `nr.chat("Tek kelime: tamam mı?")` → `"Tamam."` |
| **web_fetch** | URL→markdown/html çekme (OSINT, kariyer sayfaları) | `url`, `provider` | `str` (markdown) | **✅ Canlı doğrulandı (9R-04): firecrawl + tavily** |
| **web_search** | Web araması (OSINT / şirket keşfi) | `query`, `provider` | `dict` | **✅ Canlı doğrulandı (9R-04): tavily** |

**Canlı doğrulanmış görünüm:**
- `base_url` normalizasyonu (sonda `/v1` ve trailing slash temizlenir) → tünel `https://r3qmzpf.abc-tunnel.us` + lokal `http://localhost:20128` her ikisi çalışır.
- İstemci çift import deseni (`src.company_master` önce, bare `company_master` yedek) — embedder'da "kurulu degil" hatasını kökten çözdü.

### 2.2 Vektör Katmanı — [`vector/`](../src/company_master/vector/)

| Yetenek | Dosya | Açıklama | Doğrulama |
|---|---|---|---|
| **Embedder** (batch+retry) | [`embedder.py`](../src/company_master/vector/embedder.py) | Metin listesini chunk'layıp 9Router'a gönderir; retry + hata raporu | Birim test (mock) ✅ |
| **Vektör Depo** | [`store.py`](../src/company_master/vector/store.py) | ChromaDB (yoksa in-memory fallback); upsert/query/cosine/metadata filtre | Birim test ✅ |
| **VectorService** | [`service.py`](../src/company_master/vector/service.py) | `index_firmalar`, `find_similar`, `deduplicate_by_vkn` üst seviye API | Birim test ✅ |

### 2.3 Eşleştirme (Matcher) — [`entity_resolution/matcher.py`](../src/company_master/entity_resolution/matcher.py)

| Yetenek | Açıklama | Doğrulama |
|---|---|---|
| **VKN exact eşleşme** | Aynı VKN'li kayıtları eşleştir | ✅ |
| **Unvan fuzzy** | rapidfuzz tabanlı unvan benzerliği skoru | ✅ (test) |
| **Semantik eşleşme** | `match_semantic` — vektör benzerliği ile | ✅ (test, mock) |
| **Üçlü skor** | VKN + unvan + vektör birleşik eşleşme kararı | ✅ |

### 2.4 Arama — [`search/engine.py`](../src/company_master/search/engine.py)

| Yetenek | Durum |
|---|---|
| PostgreSQL FTS (trigram) + JSONL fallback | ✅ Çalışıyor (semantik değil) |

### 2.5 İlan Zenginleştirme Altyapısı — [`job_intelligence/`](../src/company_master/intelligence/job_intelligence/)

| Yetenek | Durum |
|---|---|
| Apify client + kaynaklar (`base`, `apify_client`, `company_career`, `iskur`, `kariyer_net`) | ✅ Hazır |
| Pipeline (`normalizer`, `analyzer`) | ✅ Regex tabanlı analizör çalışıyor; **9R-03 chat zenginleştirme eklendi** |

### 2.8 Chat Tabanlı İlan Zenginleştirme — [`chat_enricher.py`](../src/company_master/intelligence/job_intelligence/pipeline/chat_enricher.py)

| Yetenek | Açıklama | Doğrulama |
|---|---|---|
| **chat() zenginleştirme** | İlan metni → sektör/pozisyon/skill (9Router `chat()` üzerinden) | ✅ Birim test + canlı demo (`apify_run-*.jsonl`, 3/3 kayıt chat) |
| **Regex fallback** | 9Router yoksa/hata ise mevcut skorlayıcı devreye girer (graceful degradation) | ✅ Birim test |
| **Karakter temizliği** | LLM C1 kontrol karakterleri strip + UTF-8 mojibake önlemi (`resp.content` decode) | ✅ Birim test (TestUtf8Decode) |
| **`enrich_with_chat`** | `SignalAnalyzer` üzerinden toplu zenginleştirme + istatistik sonucu | ✅ Birim test |

### 2.6 OSINT Kazıma Motoru — [`engine/osint_engine.py`](../src/company_master/engine/osint_engine.py)

| Yetenek | Açıklama |
|---|---|
| `status` / `check` / `run` / `pipeline` / `quality` | Kaynak durumu, robots/KVKK izni, çalıştırma, tam pipeline, kalite gate |
| `source_registry` | Kaynak şemaları (OSTIM, ASO, İvedik, kariyer siteleri) |
| `scraping_permission_router` | interval + KVKK-safe politikaları |
| `quality_gate` | Kalite puanı + eşik kontrolü |
| `post_scrape_workflow` | Kazıma sonrası iş akışı |

### 2.7 Çevresel / Operasyonel

| Yetenek | Durum |
|---|---|
| NINEROUTER_URL lokal + tünel desteği | ✅ `.env` → tünel; `.env.example`'da lokal notu |
| `.env` güvenliği (anahtar asla loglanmaz) | ✅ Doğrulama scriptleri maskeli/`bool` çıktı |
| 92 test yeşil (vector + orchestrator) | ✅ 2026-09-11 |
| 9R-03 regresyon: chat_enricher + analyzer + ninerouter = 57 test yeşil | ✅ 2026-09-11 |
| 9R-04: ninerouter_client web_fetch/web_search sözleşme testleri = 14 test yeşil (9 eski + 5 yeni) | ✅ 2026-09-12 |
| Tam süit (bilinen 3 apify/webhook hatası hariç): 388 passed, 1 skipped | ✅ 2026-09-11 |

---

## 3. OSINT Kazıma Motoru ile Entegrasyon Noktaları

> Mimaride: kaynak (Apify) → kalite (quality_gate) → zenginleştirme (9Router) → eşleştirme (matcher) → indeks (ChromaDB) → sinyal/arama.

```
                    ┌────────────────────────────────────────────────────┐
                    │              OSINT PIPELINE (özellik akışı)        │
                    └────────────────────────────────────────────────────┘
 KAYNAK KEŞFİ       A1. web_search (potansiyel firma/ilan keşfi)   [9R-04+]
                    A2. Apify Actor + sources (anti-bot kazıma)
                        ├── kariyer.net / iskur / company_career / OSB siteleri
                        └── scraping_permission_router (robots+KVKK izni)
                          │
 KAZIMA             B1. osint_engine run/pipeline
                      ├── ham JSONL çıktı (firmalar_*.jsonl, apify_run-*.jsonl)
                      └── scrape state takibi
                          │
 KALİTE             C1. quality_gate (min-score, saha doğrulama)
 C.2 kalite puanı eksikse → yeniden kazıma/anomali işaretle
                      │
 ZENGİNLEŞTİRME     D1. **[✓ 9R-03]** chat() → ilan metninden sektör/pozisyon/skill
                    D2. **[ÖN-1]** embed() → semantik NACE/sınıflandırma
                    D3. **[9R-04]** web_fetch() → kariyer sayfası markdown → chat() özet
                    D4. **[ÖN-6]** chat() → firma özeti (opportunity card metni)
                      │
 EŞLEŞTİRME         E1. matcher.match() → VKN exact + unvan fuzzy + vektör
                    E2. deduplicate_by_vkn → aynı VKN grubu (pilot: 0 ortak)
                    E3. **[ÖN-2]** global dedup → isim varyantı grupları
                      │
 İNDEKS/ARAMA       F1. vector/store → ChromaDB koleksiyonları
                    F2. search/engine → FTS (trigram) hızlı filter
                    F3. **[ÖN-3]** semantik arama → doğal dil sorgu
                      │
 SİNYAL/ÜRETİM       G1. ilan çokluğu → büyüme sinyali (opportunity gate)
                    G2. **[ÖN-4]** kariyer/ilan verisi → sinyal skorlama beslemesi
                    G3. **[ÖN-7]** karar verici çıkarımı (web_fetch+chat)
```

### Aşama → Yetenek Eşleme Tablosu

| Pipeline Aşaması | Hangi Yetenek | Aşama Şartı |
|---|---|---|
| Kaynak keşfi | web_search | 9R-04 sonrası |
| Kazıma | Apify + registry + permission_router | Hazır ✅ |
| Kalite | quality_gate, chat anomali tespiti (öneri) | Gate hazır; chat önerisi |
| Zenginleştirme | chat() ilan, embed() NACE, web_fetch() kariyer | ✓ 9R-03 (chat), ÖN-1, 9R-04 |
| Eşleştirme/dedup | matcher, deduplicate_by_vkn | Hazır ✅ (+ ÖN-2) |
| İndeks/arama | store, engine, semantik arama | Hazır ✅ (+ ÖN-3) |
| Sinyal/üretim | chat özet, büyüme sinyali, karar verici | Aşamalı (ÖN-4/5/7) |

---

## 4. Önerilen / Planlanan Yetenekler

> Öncelik sınıflandırması: **P-MVP** (sunucuya taşınmadan ürünü anlamlı kılar) / **P-GROWTH** (ölçekleyen) / **P-LATER** (altyapı veya pazar olgunlaşınca).
> Her madde: öncelik, gerekçe, etki, hangi mevcut parçayı beslediği.

| # | Yetenek | Öncelik | Özet | Gerekçe | Etki |
|---|---|---|---|---|---|
| ÖN-1 | **Semantik NACE/sınıf atama** | P-MVP | Firma unvan+faaliyet metni → embed → NACE/OSTİM sektör etiketine en yakın eş | FTS/keyword NACE isabetsiz; veri kalitesi skoru düşük | Kalite puanı + segmentasyon doğruluğu |
| ÖN-2 | **Global dedup (isim varyantı)** | P-MVP | "X Makina San." vs "X MAKİNA Tic." → cosine + matcher grup | V8 Bulgu #4; birden çok kaynak birleşince ikiz kayıtlar artacak | Temiz veri, doğru skorlama |
| ÖN-3 | **Doğal dil semantik arama** | P-MVP | Dashboard: "robotik kaynak yapan sac metal" → top-10 firma | FTS'nin ötesinde demo/satış etkisi | Kullanıcı deneyimi + satış |
| ÖN-4 | **Büyüme sinyali** | P-MVP | Aynı firma çok/yeni ilan → "büyüyor" sinyali | 9R-03 verisinin ikinci kullanımı, ek maliyet ≈ 0 | Opportunity gate beslenir |
| ÖN-5 | **Firma özeti (opportunity card)** | P-GROWTH | chat → 1 paragraf "kim, ne üretir, neden şimdi" | Satış temsilcisi ön araştırmasını azaltır | Satış verimliliği |
| ÖN-6 | **Skor gerekçesi üretimi** | P-GROWTH | Tri-score sonucunu doğal dile çevir ("neden 78/100") | V6 şeffaflık + satış itiraz hazırlığı | Güven/şeffaflık |
| ÖN-7 | **Karar verici çıkarımı** | P-GROWTH | web_fetch kariyer sayfası → isim/pozisyon → chat çıkarım | Contact limits kuralıyla birleşince satış döngüsü kısalır | Doğrudan satış |
| ÖN-8 | **Gateway sağlık izleme + alarm** | P-GROWTH | cron → health() + kesinti alarmı | VPN kaynaklı hataları erken yakalar | Operasyonel kararlılık |
| ÖN-9 | **Model yönlendirme (maliyet kontrolü)** | P-GROWTH | embed→ucuz/model, chat→akıllı model; list_models ile seçim | API maliyeti; sunucuya taşınınca daha kritik | Maliyet kontrolü |
| ÖN-10 | **RAG asistanı** | P-LATER | Şirket DB + kariyer sayfaları üzerinde soru-cevap | Self-serve müşteri etkileşimi | Farklılaşma |
| ÖN-11 | **Adversarial test üretimi** | P-LATER | chat ile matcher/skorlayıcıyı zorlayan sentetik firma | V9 100×100×100 simülasyon kuralları | Kalite güvencesi |
| ÖN-12 | **Kalite gate otomatik gözden geçirme** | P-LATER | chat ile scrape anomali/eksik tespiti | Kalite ajan iş yükü azalır | Ölçeklenebilirlik |
| ÖN-13 | **Yetkilendirme/allowlist** | P-LATER | Tünel IP allowlist + TLS (sunucu taşınması) | KVKK/çevresel güvenlik | Güvenlik |

### Yetenek Kombinasyonları (ne neyle eşleşirse ne çıkar)

| Bileşim | Ortaya Çıkan Yetenek | Sonuç Örneği |
|---|---|---|
| embed + store | Semantik arama | Doğal dil sorgu → top-10 firma |
| embed + matcher | Global dedup / entity resolution | İsim varyantı ikiz kayıt grupları |
| embed + NACE etiketleri | Otomatik sınıflandırma | Faaliyet metni → NACE kodu atanır |
| chat + analyzer | İlan zenginleştirme (✓ 9R-03) | İlan metni → sektör/pozisyon/skill |
| chat + skor | Skor gerekçesi | 78/100 → "neden" paragrafı |
| web_fetch + chat | Kariyer sayfası özeti / karar verici | Markdown → firma/insan bilgisi |
| web_search + web_fetch | OSINT keşif akışı | Sinyal arama → sayfa inceleme |
| health + cron | Sağlık izleme | Gateway ayakta mı + alarm |
| list_models + embed/chat | Model yönlendirme | Maliyet/kalite dengesi |

### Yol Haritası (Gerçekçi Aşama Önerisi)

| Aşama | Ne Zaman | Öne Çıkanlar | Koşul |
|---|---|---|---|
| **Aşama 1** | Şimdi | ✓ 9R-03 ilan zenginleştirme; kalan: 9R-04 web fetch/search | Pano görevi 9R-04 |
| **Aşama 2** | 9R-04 sonrası | ÖN-1 semantik NACE, ÖN-2 global dedup | Vektör katmanı olgunlaştı |
| **Aşama 3** | Sunucuya taşınma öncesi | ÖN-3 semantik arama, ÖN-8 sağlık izleme, ÖN-13 güvenlik | Sunucu/sanal makine |
| **Aşama 4** | Ürün olgunlaşınca | ÖN-5/6/7 satış üretimi, ÖN-10 RAG, ÖN-11 test üretimi | Pazar sinyali |

---

## 5. Mimari Bağımlılıklar

| Katman | Bileşen | Bağımlı Olduğu | Not |
|---|---|---|---|
| Gateway | 9Router [ninerouter_client.py](../src/company_master/gateway/ninerouter_client.py) | `NINEROUTER_URL/KEY/MODEL`, requests | Tünel/lokal her ikisi destekli |
| Vektör | ChromaDB (`vector/store.py`) | `chromadb` pakedi | Lazy import; yoksa in-memory fallback |
| Vektör | Embedder | Gateway embed + model sabit `text-embedding-3-small` (1536-d) | Boyut tutarlılığı kritik |
| Eşleştirme | matcher | rapidfuzz + (isteğe bağlı) vektör | Vektör yoksa VKN+fuzzy çalışır |
| Veri | firmalar_*.jsonl, apify_run-*.jsonl | — | Kaynak veri katmanı |
| Arama | PostgreSQL FTS + JSONL | `search/engine.py` | Semantik katman ayrı |
| İlan | job_intelligence pipeline | Apify + chat (✓ 9R-03) | Regex fallback korunur |
| OSINT | osint_engine + registry + quality_gate + permission_router | — | Kazıma orkestrasyonu |
| Yönetim | V10 (görev panosu, ajan, AGENT_SYNC) | task_board + file_locks | Çakışma koruması |
| Çevre | `.env` / `.env.example` | NINEROUTER_* | Anahtarlar asla log değil |

**Kritik kurallar (V9/MVP):**
- Veri + temizleme + iş akışı kanıtlanmadan web arayüzüne geçilmez; arayüz ihtiyacı Streamlit ile sınırlı.
- KVKK/PII ham veri tünel üzerinden çıkarılmaz; yalnız türetilmiş alanlar gönderilir.
- 9Router yoksa sistemde **regex/fallback modu** çalışmaya devam eder (graceful degradation).

---

## 6. Karar Günlüğü / Tartışma Notları

> Bu bölüm, yeteneklerin birlikte değerlendirildiği canlı not defteridir. Yeni bilgi geldikçe madde eklenir/güncellenir.

| Tarih | Karar/Not | Açıklama |
|---|---|---|
| 2026-09-12 | **9R-04 web_fetch/web_search kapandı** | `web_fetch(provider='firecrawl'/'tavily')` + `web_search(provider='tavily')` canlı doğrulandı — lokal **ve** tünelde 4 web model göründü (`ollama/fetch`, `tavily/search`, `tavily/fetch`, `firecrawl/fetch`). Firecrawl + Tavily anahtarları 9Router Dashboard → Providers üzerinden bağlandı (SQLite `providerConnections`). Mimari not: 9Router'un Dashboard'unda `firecrawl` doğrudan seçenek olarak yoktu; firecrawl kaydı `https://api.firecrawl.dev/v1/scrape` endpoint'iyle elle bağlandı. Tavily hem search hem fetch destekli. |
| 2026-09-11 | **9R-03 chat zenginleştirme kapandı** | `chat_enricher.py` + `analyzer.enrich_with_chat` entegrasyonu. Canlı demo 3/3 chat (Developer→BİLİŞİM, Engineer→GENEL, Stajyer→GENEL). UTF-8 mojibake + C1 kontrol karakter düzeltmeleri eklendi. 9Router yoksa regex fallback korunur. |
| 2026-09-11 | **9R-02e çevresel düzeltme kapandı** | İki kök neden: import path uyuşmazlığı + çift `/v1`. Çözüm: dual import + URL normalizasyonu. |
| 2026-09-11 | **`.env` tünel adresine geçti** | Neden: sunucuya taşıma hedefi; lokal fallback korunuyor. `.env.example`'a lokal notu eklendi. |
| 2026-09-11 | **Dedup pilot sonucu: 0 ortak VKN** | 5040 OSTIM satırı zaten benzersiz VKN'li. Sonuç: dedup asıl değeri **birden çok kaynak birleşince** ortaya çıkacak (ÖN-2). |
| 2026-09-11 | **Maliyet kontrolü zorunlu** | Tünel = canlı API tüketimi. Embed'de önbellek + batch; chat'te regex fallback önceliği kabul. |
| AÇIK | **Tünel adresi ne kadar kalıcı?** | `*.abc-tunnel.us` geçici olabilir; sunucu taşınırken NINEROUTER_URL'in kalıcı DNS ile yenilenmesi planlanmalı. |
| KAPALI ✅ | **Web fetch/search provider'ları (9R-04)** | Firecrawl (fetch) + Tavily (search+fetch) 9Router Dashboard → Providers üzerinden eklendi; lokal + tünel canlı doğrulandı (2026-09-12). |
| AÇIK | **Embed modeli sabitleme** | `text-embedding-3-small` (1536-d) sabit tutulacak; boyut değişirse ChromaDB koleksiyonları bozulur. |
| AÇIK | **Semantik NACE sınıflandırma verisi** | `data/nace_rev2_tr.json` + `nace_to_ostim_sektor.json` zaten var; etiket vektörleri önbelleklenecek. |
| AÇIK | **KVKK/veri çıkış politikası** | chat/web_fetch isteklerinde hangi alanların gönderilebileceği netleştirilecek. |

---

## 7. Sürüm Geçmişi ve Güncelleme Takvimi

| Sürüm | Tarih | Değişiklik | Yazar |
|---|---|---|---|
| 1.0.0 | 2026-09-11 | İlk sürüm — kataloğun SSOT kapsamı; mevcut yetenekler (doğrulanmış), OSINT entegrasyon aşamaları, öneri listesi (ÖN-1..13), karar günlüğü | Koordinatör Ajan + Ürün Sahibi |
| 1.0.1 | 2026-09-11 | 9R-03 kapandı — chat_enricher (sektör/pozisyon/skill + regex fallback + UTF-8/kontrol karakter önlemi), analyzer entegrasyonu, canlı demo, regresyon | Koordinatör Ajan + Ürün Sahibi |
| 1.0.2 | 2026-09-12 | 9R-04 kapandı — web_fetch (firecrawl + tavily) ve web_search (tavily) canlı doğrulandı (lokal + tünel); unit test + sözleşme testleri; provider bağlama akışı (9Router SQLite) dokümante edildi | Koordinatör Ajan + Ürün Sahibi |

**Güncelleme takvimi (önerilen):**
- **Her görev kapanışında** (9R-03/04 ve öneri gerçeklemelerinde): bölüm 2 → "Doğrulandı" taşı, bölüm 4 → ilerleme notu, bölüm 6 → karar ekle.
- **Haftalık gözden geçirme:** ürün önceliklerine göre ÖN-1..13 sıralamasını yeniden değerlendir.
- **Sürüm kuralı:** yapısal kapsam değişikliği → minor/major; madde ekleme/düzeltme → `x.y.z` patch. Tarih her güncellemede yenilenir.

---

### Tartışmaya Açık Maddeler (özet — ayrıca takip)

1. **Tünel adresi kalıcılığı** — sunucuya taşınırken DNS/URL stratejisi.
2. **Provider seçimi (9R-04)** — ✅ ÇÖZÜLDÜ: Firecrawl (fetch) + Tavily (search+fetch) ikisi de bağlandı; firecrawl sunucuya taşınırken self-host adayı, tavily PRATİKTE default.
3. **Abonelik/güvenlik çıkışı** — KVKK-uyumlu alan beyaz listesi (hangi alanlar chat/web_fetch'e gidebilir).
4. **Öncelik onayı** — ÖN-1 (semantik NACE) mi ÖN-4 (büyüme sinyali) mi önce? İkisi de aynı veriyle beslenebilir.
5. **Dedup stratejisi** — global dedup hangi kaynak birleşimiyle başlatılmalı (OSTIM + ASO + İvedik)?
6. **Güncelleme takvimi sorumlusu** — kataloğun bakımı haftalık kimde olacak (koordinatör ajan önerisi: koordinatör + Ürün Sahibi onayı).

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]]
