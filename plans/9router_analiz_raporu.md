# 9Router SKILL.md Analiz Raporu

> Tarih: 2026-09-11
> Kaynak: https://github.com/decolua/9router/blob/master/skills/9router/SKILL.md
> İndirilen dosyalar:
> - [`plans/9router_SKILL.md`](plans/9router_SKILL.md) — ana giriş dokümanı
> - [`plans/9router_chat_SKILL.md`](plans/9router_chat_SKILL.md) — chat/kod üretimi
> - [`plans/9router_web_search_SKILL.md`](plans/9router_web_search_SKILL.md) — web + X arama
> - [`plans/9router_web_fetch_SKILL.md`](plans/9router_web_fetch_SKILL.md) — URL → markdown dönüşümü
> - [`plans/9router_embeddings_SKILL.md`](plans/9router_embeddings_SKILL.md) — vektör embedding'ler

## 1. 9Router Nedir?

**9Router, yerel/uzak bir AI ağ geçidi (gateway) sunucusudur.** OpenAI uyumlu REST API'si sayesinde **tek anahtarla birçok AI sağlayıcısına** erişim sağlar:

- **Chat / Kod üretimi** → OpenAI, Anthropic, Gemini, Mistral vb.
- **Görsel üretimi** → image-gen modelleri
- **TTS (metin → ses)** → konuşma sentezi
- **STT (ses → metin)** → konuşma tanıma
- **Embedding'ler** → vektör üretimi (RAG, semantik arama)
- **Web arama** → Tavily, Exa, Brave, Perplexity, Xquik vb. (10+ sağlayıcı)
- **Web fetch (URL → markdown)** → Firecrawl, Jina Reader, Tavily Extract, Exa vb.

### Öne Çıkan Özellikler

| Özellik | Açıklama |
|---------|----------|
| **Tek anahtar, çok sağlayıcı** | `NINEROUTER_KEY` ile tüm sağlayıcılara erişim |
| **Otomatik fallback** | Sağlayıcı çökerse diğeri devreye girer (`combo` modeller) |
| **OpenAI uyumlu** | Mevcut OpenAI SDK'ları değişmeden çalışır |
| **Yerel sunucu** | `localhost:20128` veya VPS/uzak sunucu |
| **Modüler beceriler** | Her yetenek ayrı SKILL.md dosyasında |

## 2. Endpoint Yapısı

```
${NINEROUTER_URL}/v1/models           → chat/LLM modelleri listesi
${NINEROUTER_URL}/v1/models/image     → görsel üretim modelleri
${NINEROUTER_URL}/v1/models/tts       → metin-ses modelleri
${NINEROUTER_URL}/v1/models/embedding → embedding modelleri
${NINEROUTER_URL}/v1/models/web       → web arama + fetch modelleri
${NINEROUTER_URL}/v1/models/stt       → ses-metin modelleri
${NINEROUTER_URL}/v1/models/image-to-text → vision modelleri

${NINEROUTER_URL}/v1/chat/completions → OpenAI formatında chat
${NINEROUTER_URL}/v1/messages         → Anthropic formatında chat
${NINEROUTER_URL}/v1/embeddings       → vektör embedding'ler
${NINEROUTER_URL}/v1/search           → web arama (Tavily/Exa/Brave/Perplexity...)
${NINEROUTER_URL}/v1/web/fetch        → URL → markdown/text/html
```

## 3. Projemize (Huginn Data Insights) Ne İşe Yarar?

### 3.1 Web Veri Toplama Motoru (En Kritik Fayda)

| Capability | Proje Kullanımı | Proje Dosyası |
|------------|------------------|---------------|
| **Web Fetch** | Şirket web sitelerinden firmaların kariyer sayfaları, iletişim bilgileri, hakkımızda sayfalarını markdown olarak çekebiliriz → **Açık veri toplama (OSINT)** | [`run_career_scrape.py`](run_career_scrape.py) ↔ [`src/company_master/intelligence/job_intelligence/`](src/company_master/intelligence/job_intelligence/) |
| **Web Search** | Firma ismi + "firma faaliyet alanı", NACE eşleştirme, sektör haberleri → P7 modülünü güçlendirir | [`analyze_websites.py`](analyze_websites.py) ↔ [`scripts/enrich_alternative_sources.py`](scripts/enrich_alternative_sources.py) |
| **X (Xquik) Arama** | Şirket haberleri, duyurular, iş ilanı paylaşımları → OSINT sinyalleri | [`docs/OSINT_SCRAPER_MOTORU.md`](docs/OSINT_SCRAPER_MOTORU.md) |

**MVP kuralına uygun:** Yasal sınırlar içinde AÇIK kaynaklardan veri toplama — robots.txt, KVKK ve rate-limit kuralları zaten OSINT motorunda var; 9Router fetch bunu güçlendirebilir.

### 3.2 Embedding & Semantik Arama

| Kullanım | Açıklama |
|----------|----------|
| **Semantik firma eşleştirme** | P7-3 Company Matcher'ı vektör tabanlı hale getirerek fuzzy matching'den daha güçlü eşleştirme yapabiliriz |
| **RAG (Veri tabanı sorgulama)** | ChromaDB ile doküman yükleme — [`V9 bağlam dokümanı`](AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md) §3.3 vektör mimarisini destekler |
| **Duplicate tespiti** | Benzer firma kayıtlarını embedding benzerliğiyle bulmak (entity_resolution) |

### 3.3 AI Gateway — Çoklu Model Erişimi

| Kullanım | Açıklama |
|----------|----------|
| **Kod üretimi / inceleme** | Tek komutla farklı LLM'lerden (OpenAI, Anthropic, Gemma, Mistral) kod üretimi ve inceleme |
| **Model karşılaştırma** | Aynı prompt'u birden fazla modele gönderip kalite karşılaştırması → `combo` modellerle otomatik fallback |
| **Harici ajan entegrasyonu** | [`07_harici_ajan_protokolu.md`](AI proje v1/V10/08-Ajanlar/07_harici_ajan_protokolu.md) kapsamında harici ajanlara bu gateway üzerinden AI erişimi sağlanabilir |
| **Streamlit arayüz** | [`app.py`](app.py) içinde LLM destekli veri analizi özellikleri eklenebilir |

## 4. Capability Skill'leri Detayı

### 4.1 Chat / Kod Üretimi (`9router-chat`)

- OpenAI formatı: `POST /v1/chat/completions`
- Anthropic formatı: `POST /v1/messages`
- Streaming desteği: SSE `data:` chunk'ları
- Combo modelleri: `vip`, `mycodex` gibi otomatik fallback sağlayan setler

### 4.2 Web Arama (`9router-web-search`)

- 10+ sağlayıcı: Tavily, Exa, Brave, Serper, SearXNG, Google PSE, Linkup, SearchAPI, You.com, Perplexity, Xquik
- `POST /v1/search` endpoint'i
- X/Twitter arama (Xquik) — operatörlerle (from:, to:, # etiket)
- Ülke/dil/zaman filtresi, domain filter
- Pagination desteği (`next_cursor`)

### 4.3 Web Fetch (`9router-web-fetch`)

- 5+ sağlayıcı: Firecrawl, Jina Reader, Tavily Extract, Exa, Ollama Cloud
- `POST /v1/web/fetch` endpoint'i
- Format: `markdown` (varsayılan) / `text` / `html`
- `max_characters` ile çıktı sınırlama
- JS-render edilen sayfalar için Firecrawl öneriliyor

### 4.4 Embedding (`9router-embeddings`)

- 13+ sağlayıcı: OpenAI, Gemini, Mistral, Voyage, NVIDIA, GitHub, Fireworks, Together, Nebius, Jina-AI
- `POST /v1/embeddings` endpoint'i
- OpenAI uyumlu response formatı
- Batch işleme (array input)
- ChromaDB / pgvector entegrasyonunu destekler

## 5. Kurulum ve Kullanım

### 5.1 Kurulum

```bash
export NINEROUTER_URL="http://localhost:20128"  # veya VPS/tunnel URL
export NINEROUTER_KEY="sk-..."                  # Dashboard → Keys
```

**Doğrulama:**
```bash
curl $NINEROUTER_URL/api/health  → {"ok":true}
```

### 5.2 Projemize Entegrasyon Önerisi

```
python örnek — 9Router üzerinden web fetch
┌─────────────────────────────────────────────┐
│ import requests                             │
│                                             │
│ r = requests.post(                          │
│     f"{NINEROUTER_URL}/v1/web/fetch",       │
│     headers={                              │
│         "Authorization": f"Bearer {KEY}",   │
│         "Content-Type": "application/json"  │
│     },                                      │
│     json={                                  │
│         "model": "jina-reader",             │
│         "url": "https://firma.com/kariyer", │
│         "format": "markdown",               │
│         "max_characters": 5000              │
│     }                                       │
│ )                                           │
│ print(r.json()["content"]["text"])          │
└─────────────────────────────────────────────┘
```

## 6. Dikkat Edilmesi Gerekenler

### 6.1 Güvenlik

| Kural | Açıklama |
|-------|----------|
| **`NINEROUTER_KEY` asla koda yazılmaz** | `AGENTS.md` kuralı — `.env` kullanılır |
| **Harici ajana gönderilmez** | `07_harici_ajan_protokolu.md` kuralı |
| **Yerel sunucu tercih** | VPS yerine localhost varsayılan |

### 6.2 Maliyet

| Sağlayıcı | Maliyet Modeli |
|-----------|---------------|
| Tavily | $0.008/arama (`search_cost_usd`) |
| Xquik | 1 kredi/dönen post (`provider_credits_used`) |
| Jina Reader | Ücretsiz (~1M karakter/ay) |
| Firecrawl | Bearer API key — fiyatlandırma kullanıma göre |

### 6.3 Sınırlamalar

- `dimensions` parametresi yalnızca OpenAI v3 modellerinde çalışır
- Google PSE için `cx` (arama motoru ID) zorunlu
- SearXNG için API anahtarı gerektirmez (self-hosted)
- Her provider'ın rate limit farklıdır
- Web fetch'te `links` yalnızca Ollama Cloud provider'da döner

## 7. Sonuç — Bu MD Bize Ne Kazandırır?

### Mevcut Kod Tablosu (Proje Projeksiyonu)

| Proje İhtiyacı | 9Router Etkisi | Öncelik |
|----------------|---------------|---------|
| **P7-4 Career Pages Scraper** | Firecrawl/Jina ile markdown olarak kariyer sayfası çekme | **Yüksek** |
| **P7-8 Job Signal Analyzer** | X arama ile şirket haberleri sinyalleri | **Yüksek** |
| **P7-3 Company Matcher** | Embedding ile semantik eşleştirme (fuzzy yerine) | **Orta** |
| **Entity Resolution** | Vektör benzerliği ile duplicate tespiti | **Orta** |
| **ChromaDB vektör mimarisi (V9 §3.3)** | Embedding API ile vektör üretimi | **Orta** |
| **RAG + Streamlit arayüz** | LLM destekli doğal dil veri sorgulama | **Düşük** |
| **Harici ajan AI erişimi** | Gateway üzerinden çoklu model desteği | **Düşük** |

### Kritik Sonuç

> **9Router, projemizin web veri toplama motorunu tek bir API üzerinden 10+ sağlayıcıya bağlama olanağı verir.** Mevcut `apify_job_source` ve `iskur/kariyer_net` scraper'larının yanına **Firecrawl (JS render) + Jina Reader (ücretsiz, hızlı) + X arama (OSINT)** kombinasyonu eklenebilir. Ayrıca embedding API ile Company Matcher'ı semantik eşleştirmeye yükseltmek mümkün.

## 8. Önerilen Adımlar

1. **Öncelik:** `NINEROUTER_URL` ve `NINEROUTER_KEY` değerlerinin kurulu olup olmadığını kontrol et (`.env` dosyası)
2. **Pilot test:** `jina-reader` ile bir firmanın kariyer sayfasını markdown olarak çek ve mevcut OSINT motoruyla karşılaştır
3. **Görev oluştur:** `task_board.json`'a `9R-01: 9Router web-fetch entegrasyonu` görevi ekle
4. **Entegrasyon:** [`src/company_master/intelligence/job_intelligence/sources/`](src/company_master/intelligence/job_intelligence/sources/) altına `ninerouter_job_source.py` ekle

---

## Ek: İndirilen Dosyalar

| Dosya | İçerik |
|-------|--------|
| [`plans/9router_SKILL.md`](plans/9router_SKILL.md) | Ana giriş — setup, modeller, hata kodları |
| [`plans/9router_chat_SKILL.md`](plans/9router_chat_SKILL.md) | Chat/kod üretimi + streaming |
| [`plans/9router_web_search_SKILL.md`](plans/9router_web_search_SKILL.md) | 10+ sağlayıcı web arama + X arama |
| [`plans/9router_web_fetch_SKILL.md`](plans/9router_web_fetch_SKILL.md) | URL → markdown/text/html fetch |
| [`plans/9router_embeddings_SKILL.md`](plans/9router_embeddings_SKILL.md) | 13+ sağlayıcı embedding API |