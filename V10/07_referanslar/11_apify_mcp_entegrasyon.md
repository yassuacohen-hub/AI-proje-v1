# Apify + MCP Entegrasyonu — APIFY-01 / APIFY-03 / MCP-01 / MCP-02

> - **Tarih:** 2026-09-11
> - **Klas:** Entegrasyon referansı
> - **Bağlantılar:** [[10_apify_entegrasyon_arastirmasi_20260910]] · [[01_versiyon_9_baglam_dokumani]]
> - **İlgili görevler:** APIFY-01, APIFY-02, APIFY-03, MCP-01, MCP-02

---

## 1. Durum Özet

| Görev | Sahip | Durum | Açıklama |
|-------|-------|-------|----------|
| APIFY-01 | kilo | **done** | Apify entegrasyonu araştırması (GO kararı) |
| APIFY-02 | web_kazima | done | Apify REST adaptörü + polling pilot (`apify_client.py`, `apify_job_source.py`) |
| APIFY-03 | kilo | **done** | Webhook alıcısı + kalıcı olay işleme |
| MCP-01 | kilo | **done** | Kontrollü Apify MCP erişimi (Policy Engine + Adapter) |
| MCP-02 | kilo | **done** | Huginn MCP sunucusu + ters connector |

---

## 2. APIFY-01: Entegrasyon Araştırması

**Sonuç: GO** — Apify, OSINT_Scraper_Motoru için en iyi entegrasyon adayıdır.

- Apify REST API: `https://docs.apify.com/api/v2`
- Token: `APIFY_TOKEN` env değişkeni (asla kodda hardcoded yok)
- Maliyet: Free $5/ay → Scale $199/ay; 1 CU = 1GB RAM × 1 saat
- **Strateji:** Yerel scraper'lar + gerektiğinde Apify → ortak doğrulama + karantina → PostgreSQL → sinyal motoru
- Anti-bot: Apify Built-in proxy + headless Chromium (kariyer.net, LinkedIn için)
- KVKK: Apify cloud'da veri işlenir; KVKK_SAFE_DOMAINS ile uyumlu yönetilebilir
- **Hukuki:** Apify sözleşme/DPA sayfaları doğrulanamadı — üretim öncesi hukuki inceleme gerekir

Kaynak: `data/orchestrator/apify_research_result.json`, `AI proje v1/V10/07_referanslar/10_apify_entegrasyon_arastirmasi_20260910.md`

---

## 3. APIFY-02: REST Adaptörü (tamamlandı — web_kazima)

- `src/company_master/intelligence/job_intelligence/sources/apify_client.py` — ApifyClient (REST API, polling, dataset pagination)
- `src/company_master/intelligence/job_intelligence/sources/apify_job_source.py` — ApifyJobSource (BaseJobSource uyumlu)
- `tests/test_apify_client.py` — 12 test (2 pre-existing mock hatası var, ilgili değil)
- SourceSpec registry'de `apify` source_id olarak kayıtlı (henüz enabled=false, token gerekir)

---

## 4. APIFY-03: Webhook + Kalıcı Olay İşleme (yeni — kilo)

### Mimari

```text
Apify POST /api/webhooks/apify
       │
       ├─ 1. Secret token doğrula (?secret= veya Authorization: Bearer)
       ├─ 2. (Opsiyonel) HMAC-SHA256 imza doğrulama
       ├─ 3. actorRunId idempotency kontrolü (in-memory + JSONL)
       ├─ 4. 200 OK dön (hızlıca)
       └─ 5. Event routing (asenkron):
            SUCCEEDED    → dataset çek → ingest_job_postings.py subprocess
            FAILED/ABORTED/TIMED_OUT → ErrorLedger + Telegram alert
```

### Dosyalar

| Dosya | Rol |
|-------|-----|
| `scripts/apify_webhook_receiver.py` | ApifyWebhookReceiver sınıfı, WebhookEvent, CLI |
| `scripts/manage_apify_webhooks.py` | Webhook kaydet/listele/sil/test CLI |
| `web_app.py` | `POST /api/webhooks/apify` endpoint |
| `tests/test_apify_webhook_receiver.py` | 22 test (mock'lu) |

### Güvenlik

- **Secret token:** `APFY_WEBHOOK_SECRET` env değişkeni
- **HMAC:** `sha256={hexdigest}` header (`X-Apify-Signature`); Apify docs'te tutarlı HMAC garanti edilmediği için secret + API yeniden doğrulama ana mekanizmadır
- **IP whitelist:** Apify webhook IP'leri firewall'da whitelist edilmeli (uygulama kodda kontrol edilmez)
- **HTTPS:** deployment katmanı zorunlu kılar
- **Idempotency:** `actorRunId` anahtarı; JSONL (`data/orchestrator/apify_webhook_events.jsonl`) ile process restart sonrası da korunur

### Event flow

```python
# web_app.py endpoint (asenkron değil — hızlıca 200 OK döner)
@app.post("/api/webhooks/apify")
def apify_webhook(request, secret, authorization, x_apify_signature):
    result = receiver.process_webhook(payload, secret, x_apify_signature)
    if result["status"] != "ok":
        raise HTTPException(401)
    return result
```

---

## 5. MCP-01: Kontrollü Apify MCP Erişimi (yeni — kilo)

Policy Engine ile Apify MCP tool'larına erişim kontrolü.

### Dosyalar

| Dosya | Rol |
|-------|-----|
| `src/company_master/mcp/policy_engine.py` | PolicyEngine, PolicyDecision, SpendEntry |
| `src/company_master/mcp/apify_adapter.py` | ApifyAdapter (MCP tool wrapper) |
| `tests/test_mcp.py` | Policy Engine + Adapter testleri (33 test) |

### Permission Model

- **allowed_tools:** explicit whitelist (`apify_run_actor:kariyer_net`, `apify_run_actor:company_career`, `apify_get_dataset`, `apify_list_actors`)
- **Wildcard engeli:** `apify_run_actor:*` asla onaylanmaz
- **Spend approval:** günlük limit $5, aylık limit $150 (Apify credit); `data/orchestrator/mcp_spend_log.jsonl`
- **Data limits:** max 10.000 dataset rows, max 50.000 token çıktı
- **NACE scope:** opsiyonel; boşsa tüm kodlar onaylanır

### Tools

| Tool | Argümanlar | Açıklama |
|------|-----------|----------|
| `apify_run_actor` | `actor_id`, `run_input`, `max_items`, `max_charge_usd` | Whitelist'teki actor'ı çalıştır |
| `apify_get_dataset` | `dataset_id`, `max_items`, `clean` | Dataset'i oku (policy kontrolü) |
| `apify_list_actors` | — | İzinli actor'ları + limitleri listeler |

---

## 6. MCP-02: Huginn MCP Sunucusu (yeni — kilo)

Huginn'in dahili verilerini MCP tool'ları olarak sunar.

### Dosyalar

| Dosya | Rol |
|-------|-----|
| `src/company_master/mcp/huginn_server.py` | HuginnMCPServer, HuginnToolResult |

### Tools

| Tool | Argümanlar | Açıklama |
|------|-----------|----------|
| `get_source_policy` | `source_id` | SourceSpec + izin kararı |
| `get_collection_run_status` | `run_id` | task_board.json'dan durum |
| `submit_evidence_batch` | `evidence`, `source_id` | JSONL'ye kanıt gönder, run_id üret |
| `report_collection_failure` | `source_id`, `error`, `run_id` | ErrorLedger + log |

### Güvenlik

- `submit_evidence_batch`: `evidence` sadece metadata (title/url/company); PII veya secret içermemeli
- `report_collection_failure`: ErrorLedgerEntry ile kaydedilir
- Policy Engine ile entegre: tüm tool çağrıları yetki kontrolünden geçer

---

## 7. Entegrasyon ve Akış

```text
Harici ajan (MCP) ──┐
                    ├──────→ PolicyEngine.check()
Huginn MCP Server ──┤
                    ├───→ ApifyAdapter.apify_run_actor()
                    │        └──→ ApifyClient (REST API)
                    │               └──→ ingest_job_postings.py (subprocess)
                    │                       └──→ SignalAnalyzer (P7-8)
                    │                       └──→ IntelligenceScorer (P7-9/P7-10)
                    └───→ HuginnMCPServer.submit_evidence_batch()
                         └──→ data/job_intelligence/mcp_evidence_*.jsonl

Apify webhook (alternatif akış) ──→ /api/webhooks/apify
                                    └──→ ApifyWebhookReceiver
                                         └──→ ingest_job_postings.py (subprocess)
```

---

## 8. Kullanım

### Webhook kurulumu (Apify UI)

1. `python scripts/manage_apify_webhooks.py --register --actor-id ziyrak/kariyer-scraper --url https://your-domain.com/api/webhooks/apify`
2. Çıktıdaki `APFY_WEBHOOK_SECRET=...` değerini `.env`'ye kaydedin
3. Webhook URL: `https://your-domain.com/api/webhooks/apify?secret=<APFY_WEBHOOK_SECRET>`

### MCP server başlatma

```bash
# MCP paketi kuruluysa:
pip install mcp
python -c "
from company_master.mcp.huginn_server import HuginnMCPServer
from company_master.mcp.apify_adapter import ApifyAdapter
from company_master.mcp.policy_engine import PolicyEngine

policies = PolicyEngine()
adapter = ApifyAdapter(policies=policies)
server = HuginnMCPServer(policies=policies)

# Tool listesi
print(server.list_tools() + adapter.list_tools())

# Tool çağrısı
result = server.call_tool('get_source_policy', {'source_id': 'apify'})
print(result)
"
```

---

## 9. Maliyet ve Limitler

| Bileşen | Limit | Varsayılan |
|---------|-------|-----------|
| Günlük Apify harcama | `daily_spend_limit` | $5.00 |
| Aylık Apify harcama | `monthly_spend_limit` | $150.00 |
| Max dataset rows | `max_dataset_rows` | 10.000 |
| Max output tokens | `max_output_tokens` | 50.000 |
| Webhook event log | — | `data/orchestrator/apify_webhook_events.jsonl` |
| MCP spend log | — | `data/orchestrator/mcp_spend_log.jsonl` |

---

## 10. Açık Sorunlar

1. Apify sözleşme/DPA belgeleri (404) — hukuki inceleme gerekir, üretim öncesi kapatılamaz
2. Apify webhook HMAC'i docs'te tutarlı doğrulanamadı — secret token + API yeniden doğrulama kullanılıyor
3. `test_apify_client.py` 2 pre-existing test hatası (mock setup eksikliği) — APIFY-02'nin, ilgili değil
4. MCP paketi kurulu değil; adapter ve server framework-agnostic çalışıyor, MCP runtime opsiyonel

---

## Ilgili Nodlar

- [[Huginn Data Insights/AI proje v1/V10/07_referanslar/01_veri_kaynagi_envanteri]]


- [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]]
