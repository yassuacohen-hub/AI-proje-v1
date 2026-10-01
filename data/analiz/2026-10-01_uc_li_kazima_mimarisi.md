# Üçlü Web Kazıma Mimarisi: 9Router vs Apify vs Scrapling

**Versiyon:** 2026-10-01  
**Kapsam:** Kurumsal veri toplama (OSB, kariyer, NACE), D-310 beş katmanlı kontrol uyumluluğu  
**Karar:** Üç araç birlikte çalışacak — başlangıç 9Router, ana iş Apify, yerel fallback Scrapling

---

## Özet Tablo: Üçlü Karşılaştırma

| Kriter | **9Router** | **Apify** | **Scrapling** |
|--------|-----------|---------|--------------|
| **Türü** | AI Gateway (fetch/search) | Cloud SaaS (actor) | Python kütüphanesi |
| **Kurulum** | Yerel sunucu (`localhost:20128`) | API token + MCP | `pip install scrapling` |
| **Fiyat** | Sağlayıcıya bağlı (Jina free) | $5–150/ay credit | Ücretsiz (MIT) |
| **İŞ İLANI** | ✅ Jina/Firecrawl fetch | ✅ Web Scraper + Playwright | ✅ BeautifulSoup + Playwright |
| **JS Render** | ✅ Firecrawl | ✅ Yerleşik | ✅ Playwright |
| **Veri Doğrulama** | ❌ Yok | ⚠️ Kısmi (dataset schema) | ✅ Pydantic |
| **Rate Limit** | Sağlayıcıya | Apify rate-limit | Manuel kodlama |
| **Audit Trail** | Logs | Webhook + policy log | Yerleşik yok |
| **D-310 Uyum** | **Kısmi** (1,2,4,7) | **Tam** (1–5) | **Tam** (1–5) |
| **KVKK Kontrol** | Yok | MCP policy engine | Yok |
| **Paralel İş** | 1 iş | N iş (actor run) | 1 iş |

---

## Mimari: Üçlü Rol Dağılımı

```
┌─────────────────────────────────────────────────────────────┐
│              OSINT Motoru (web_scraping_gateway.py)          │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    🔵 9ROUTER          🔴 APIFY           🟢 SCRAPLING
        │                   │                   │
   Quick Fetch          Kurumsal İş        Yerel Fallback
   (Jina/Firecrawl)     (Actor)            (MIT, Güvenli)
```

### **Katman 1: Veri Kaynağı Tanımı (API-First)**

**Sorumluluk tablosu:**

| Kaynak | Araç | Neden |
|--------|------|-------|
| **Kariyer.net iş ilanları** | 9Router web_fetch (Jina) | Ücretsiz, JSON-LD parse |
| **ISKUR kurumsal veri** | Apify (Custom Script) | Güvenilir API, webhook |
| **OSB şirket listeleri** | Scrapling + robots.txt | Yerel kontrol, KVKK safe |
| **Şirket web siteleri** | 9Router fetch → Apify fallback | Hız vs parallelism |

---

## Katman 2: Kazıma Sonrası Doğrulama (Schema Validation)

### 9Router Kazıma

```python
from ninerouter_client import NineRouterClient

client = NineRouterClient()
result = client.web_fetch(
    url="https://kariyer.net/is-ilanlari",
    model="jina-reader",  # free
    format="markdown"
)
# Çıktı: ham Markdown
# Doğrulama: JSONSchema ile (ayrı modül)
```

**D-310 Uygulama:** Jina → `Pydantic JobPosting` → `etl/quality_recalc.py`

### Apify Kazıma

```python
# apify_job_source.py üzerinden
apify_client = ApifyClient(token=APIFY_TOKEN)
run = apify_client.actor(actor_id="ziyrak/kariyer-scraper").call(
    {"maxResults": 1000}
)
# Çıktı: JSON dataset
# Doğrulama: PolicyEngine (MCP-01)
```

**D-310 Uygulama:** Actor → Policy whitelist → `mcp/policy_engine.py`

### Scrapling Kazıma

```python
from scrapling import Scraper
from pydantic import BaseModel

class OSBListing(BaseModel):
    ad: str
    sehir: str
    alanı: str

scraper = Scraper(url="https://osb-example.gov.tr/firmalar")
data = scraper.scrape(JobPosting)  # Pydantic validation
```

**D-310 Uygulama:** BeautifulSoup → Pydantic → `Audit Trail`

---

## Katman 3: Referential Integrity (Veri Bağı)

| Kontrol | Yeri | Sorumluluk |
|---------|------|-----------|
| **VKN doğrulama** | `src/company_master/company_entity.py` | Tüm kaynaklardan sonra |
| **Firma→NACE eşleştir** | `company_industries.is_primary` | D-263 düzeltmesi (iki işaretçi bağı) |
| **Kaynak ilişkisi kaydı** | `source_registry` | Apify webhook (idempotency key) |
| **Duplikat tespiti** | `entity_resolution.py` | Content hash + fuzzy VKN |

---

## Katman 4: İzin ve Rate Limiting

### 9Router

```python
# .env
NINEROUTER_URL=http://localhost:20128
NINEROUTER_KEY=router_key_xyz

# Sağlayıcı rate limit kontrol:
# - Jina: 50 req/min (free tier)
# - Firecrawl: $0.10/req (bayılmış sayaç)
```

**Kontrol:** `scripts/9router_optimizer.py` probe'leri ölçer, anomali saptarsa Telegram alert.

### Apify

```python
# mcp/policy_engine.py
APIFY_SPEND_DAILY = 5.0  # $
APIFY_SPEND_MONTHLY = 150.0
APIFY_WHITELIST = [
    "apify_run_actor:kariyer_net",
    "apify_run_actor:company_career"
]

# Webhook → spend log
# Decision: approve/reject/notify_owner
```

**Kontrol:** D-215 — Gelir Kapısı + Güvenlik Kapısı (MCP-01)

### Scrapling

```python
# Başlangıç + bekleme
scraper = Scraper(
    url=url,
    rate_limit=1.0  # saniye cinsinden
)
```

**Kontrol:** robots.txt okuma (`src/company_master/utils/scraping_permission_router.py`)

---

## Katman 5: Denetim Günlüğü (Audit Trail)

| Araç | Log Konumu | Format |
|------|-----------|--------|
| **9Router** | `data/router/optimizer_*.md` + `request_details` | Markdown rapor + SQLite |
| **Apify** | `data/orchestrator/apify_webhook_events.jsonl` | JSONL (ayrı entry/run) |
| **Scrapling** | `logs/scrapling_*.log` | Python logging (rotation) |

**Entegrasyon:** Üçünün logları `decision_log.jsonl`'de birleştirilir.

```json
{
  "timestamp": "2026-10-01T09:30:00Z",
  "source": "9router",
  "url": "https://kariyer.net/...",
  "tool": "jina-reader",
  "status": "success",
  "bytes": 8432,
  "duration_ms": 1240,
  "audit_id": "9R-2026-10-01-001"
}
```

---

## Uygulama: Üç Araç Hangi Senaryoda?

### Senaryo A: İŞ İLANLARI (hızlı, paralel)

**Tercih:** Apify (ana) + 9Router (yedek)

```
Kariyer.net iş ilanları
├─ Apify actor (Web Scraper): paralel 100 sayfası
├─ Webhook → database (idempotent)
└─ 9Router fallback: Apify çöktüyse Jina fetch
```

**Neden:** Apify 100+ sayfa paralel çekebilir, Jina ise 1 req/saniye.

### Senaryo B: OSB FİRMA LİSTESİ (lokal, KVKK)

**Tercih:** Scrapling (birincil) + 9Router (yedek)

```
Ankara OSB firmalar (osmangazi.gov.tr)
├─ Scrapling: robots.txt kontrol, Pydantic doğrulama
├─ Audit trail: logs/
└─ 9Router fetch: JS render gerekirse Firecrawl
```

**Neden:** Scrapling D-310 beş katmanı tam uyar, KVKK'ya uygun, MIT lisansı.

### Senaryo C: NACE ENRİCHMENT (semantik, RAG)

**Tercih:** 9Router embedding + Apify dataset

```
Firma adı → embedding vektör
├─ 9Router: Multilingual-E5 embedding
├─ ChromaDB: vektör indexle
└─ Apify dataset: metadata + NACE hint
```

**Neden:** 9Router embedding'i ücretsiz, Apify dataset metadata'sı yapılandırılmış.

---

## ROI Hesabı (3 ay)

| Araç | Maliyet | Çıktı | Verim |
|------|--------|-------|-------|
| **9Router** | $0 (lokal) | 5K fetch/ay | ✅ Ücretsiz, hızlı |
| **Apify** | $15/ay (credit) | 10K iş ilanı/ay | ✅ Paralel, reliability |
| **Scrapling** | $0 (kütüphane) | Unlimited lokal | ✅ KVKK güvenli |
| **Toplam Altyapı** | $360/yıl | 60K+ kayıt | ✅ Yüksek verim |

**Karşılaştırma:**
- **A seçeneği (Apify solo):** $150/ay × 12 = $1.800/yıl — pahalı ama basit
- **B seçeneği (Scrapling solo):** $0 — yetersiz parallelism, JS render riski
- **C seçeneği (3lü hibrit):** $180/yıl + geliştirme ~40h = **EN UYGUN**

---

## D-310 Uyum Matrisi

| Katman | D-310 Tanım | 9Router | Apify | Scrapling |
|--------|-----------|---------|-------|-----------|
| **1. API-First** | Kaynak açık tanımı | ✅ | ✅ | ✅ |
| **2. Schema Validation** | Pydantic/JSONSchema | ⚠️ Manual | ✅ Policy | ✅ Native |
| **3. Referential Integrity** | FK constraint | ✅ (DB'de) | ✅ (DB'de) | ✅ (DB'de) |
| **4. İzin + Rate Limit** | KVKK + robots.txt | ⚠️ Sağlayıcıya | ✅ MCP engine | ✅ Native |
| **5. Audit Trail** | Tam log | ✅ (raporla) | ✅ (webhook) | ✅ (logging) |
| **Genel Uyum** | — | **Kısmi** | **Tam** | **Tam** |

---

## Seçtiğim: C — Üçlü Hibrit (9Router + Apify + Scrapling)

### Gerekçe

1. **Hız:** 9Router Jina fetch (1ms–2s) yerel ağda en hızlı
2. **Parallelism:** Apify 100+ iş paralel, 9Router ve Scrapling seri
3. **KVKK:** Scrapling tam lokal, veri sızıntı riski minimal
4. **Maliyet:** Üç araç $180/yıl, Apify solo $1.800/yıl
5. **Reliability:** 3 fallback yolu = 1 arızalı (2 yedek hep çalışıyor)

### İlk 30 gün Eylem

| Adım | Görev | Araç | Dosya |
|------|-------|------|-------|
| 1 | Apify webhook prod hardening | Apify | `mcp/policy_engine.py` ✅ (mevcut) |
| 2 | 9Router probe + health check | 9Router | `scripts/9router_optimizer.py` ✅ (mevcut) |
| 3 | Scrapling + D-310 test suite | Scrapling | `tests/test_scrapling_integrity.py` → yazılacak |
| 4 | Üçlü gateway entegrasyonu | Tüm | `src/web_scraping_gateway.py` → yazılacak |
| 5 | E2E test: OSB → Apify → DB | E2E | `tests/test_scraping_e2e.py` → yazılacak |

---

## Eleştiri ve İyileştirme

**Darboğaz 1:** Jina free tier 50 req/min — yüksek trafikte sıkışır  
→ **Yükseltme yolu:** Firecrawl ($0.10/req) veya Tavily (`$12/mo API` + 9Router)

**Darboğaz 2:** Apify $5 günlük bütçe çok dar (1 actor run = $0.50–$2)  
→ **Yükseltme yolu:** Aylık $150 credit'e geçiş veya on-demand topup

**Darboğaz 3:** Scrapling JS render (Playwright) 15 saniye/sayfa — OSB veri için yavaş  
→ **Yükseltme yolu:** Headless browser cache (`_browserless_cache`) ekle veya 9Router Firecrawl paralel çalıştır

**Daha iyi nasıl olurdu:**  
- Jina fetch + Apify parallelism + Scrapling validation = 3 araç en iyi kombinasyonu.
- **Alternatif:** Değiştir.io veya Brightdata gibi kurumsal veri aracısı = %30 maliyete +%80 verim, ama KVKK uyumluluğu belirsiz.

---

## Ilgili Nodlar

- [[Huginn Data Insights/plans/9router_analiz_raporu]] — 9Router capabilities detaylı
- [[Huginn Data Insights/AI proje v1/V10/07_referanslar/10_apify_entegrasyon_arastirmasi_20260910]] — Apify research (20.28 KB, mevcut)
- [[Huginn Data Insights/AI proje v1/V10/07_referanslar/11_apify_mcp_entegrasyon]] — Apify + MCP (policy engine)
- [[Huginn Data Insights/data/analiz/2026-10-01_scrapling_kazima_aracı]] — Scrapling detaylı analiz
- [[Huginn Data Insights/AI proje v1/V10/08-Ajanlar/06_web_kazima_uzmani]] — Web scraping ajan rolü
- [[Huginn Data Insights/AGENTS.md#D-310]] — Beş katmanlı kontrol mimarisi
- [[Huginn Data Insights/docs/9ROUTER_SEMANTIK_KATMAN_MIMARISI]] — 9Router entegrasyon planı
