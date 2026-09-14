---
name: osint-web-scraping-toolkit
description: >-
  OSINT istihbari ve web kazıma motoru için modüler kılavuz.
  Apify webhook alicılarını (events.jsonl, dlq.jsonl), HTTP istemci,
  rate-limit politikaları, anti-bot bypass ve Obsidian entegrasyonunu
  içerir.
author:
  - Cline
  - Kilo Code
version: 1.0.0
license: Apache-2.0
tags:
  - osint
  - scraping
  - apify
  - webhook
  - istihbarat
---

# OSINT Web Kazıma ve İstihbarat Toolkit

Bu beceri, **"Huginn Data Insights – Osint Engine"** modülüyle
bütüncül çalışır. Ajanlar aynı havuzdaki skill’i okur; doğrusal artık
tekrarlı kod üretmez.

## İlgili Modüller / Dosyalar

- `src/company_master/engine/osint_engine.py` — kazıma + istihbarat fonksiyonları
- `scripts/apify_webhook_receiver.py` — webhook event’leri jsonl olarak yazar
- `data/orchestrator/apify_webhook_events.jsonl` — canlı olay akışı
- `data/orchestrator/apify_webhook_dlq.jsonl` — hatalı olay kuyruğu (DLQ)

## Quickscrape — Tek Satır Kazıma

```python
from company_master.engine.osint_engine import quick_scrape

result = quick_scrape(
    url="https://example.com",
    selectors={"title": "h1", "price": ".price"},
    timeout=10,                 # saniye
    retries=3,                  # exponential backoff
    respect_robots=True,       # robots.txt kontrol
    proxy_pool=None            # None → varsayılan rotasyon
)
# result = {"title": "...", "price": "..."}
```

## Rate-Limit & Anti-Bot Politikası

1. **Robots kontrol edilir** (`robotparser`).
2. **Domain bazlı paketleme**: maks 1 istek / 2 sn.
3. **User-Agent rotasyonu**: `osint_engine.USER_AGENTS` listesinden rastgele.
4. **Başarısız 3 kez** → kuyruk (`dlq`)’a at, manuel retry için.

## Apify Webhook Entegrasyonu (Obsidian Notu)

> Bu bölüm `AGENTS.md` → “Harici Ajan Protokolü” bölümünden
> otomatik aktarılır. Obsidian `V10/08-Ajanlar` dizininde eşleşir.

Webhook receiver, her yeni event’i `apify_webhook_events.jsonl`’e
ekler. DLQ (`apify_webhook_dlq.jsonl`) içinde hatalı event’ler,
`retry_dlq_events.py` ile yeniden işlenebilir.

### Event Örneği

```json
{"event_type":"run.finished","apify_run_id":"abc123","status":"SUCCEEDED","dataFile":".json","created_at":"2026-09-12T17:00:00Z"}
```

### DLQ Retry (manuel)

```bash
python scripts/retry_dlq_events.py --max 10
```

## Örnek İstihbarat Akışı

```
quick_scrape  →  parse_html  →  filter_rules  →  Obsidian kaydı
   ↓              ↓              ↓                ↑
 webhook      quality_score    relevance        └─ metadata.md
```

## Hata Yönetimi ve Günlük

- `osint_engine.py` içinde `except`’ler **asla sessiz kalmaz**.
- Hata her zaman loglanır + DLQ’ya eklenir.
- Retry politikası 3 kez, exponential backoff (1s → 2s → 4s).

## Obsidian Entegrasyonu

- **Kaynak dosya:** `src/company_master/engine/osint_engine.py`
- **Not defteri:** `AI proje v1/V10/06-Kurulum/02_osint_notes.md`
- **Karar defteri:** `data/orchestrator/decision_log.jsonl` → her kazıma oturumunda
  `log_decision("kazima_baslat", "osint", "URL: <url>, selectors: <n>")`

## Edge Cases

- URL geçersiz → `ValueError("Geçersiz URL")` fırlat.
- Selector eksik → `None` döner (varsayılan değeri yok).
- Proxy çalışmazsa → otomatik fallback default pool’a geçer (loglanır).

---

## Ticari İstihbarat (Commercial Intelligence)

Bu beceri, şirket araştırma ve ticari istihbarat görevleri için de kullanılır.

### Şirket Araştırması

- Şirket web siteleri, kariyer sayfaları, hakkımızda sayfaları incelenir.
- Organizasyon yapıları analiz edilir.
- İş modelleri belirlenir.
- Şirket ilişkileri çıkarılır.
- İştirak ve holding yapıları eşleştirilir.
- Büyüme sinyalleri tespit edilir.
- Operasyonel değişimler analiz edilir.
- Yönetim değişiklikleri izlenir.

---

## Açık Kaynak İstihbaratı (OSINT)

Aşağıdaki kaynaklardan veri toplayabilir, ilişkilendirebilir ve analiz edebilir:

### Kurumsal Kaynaklar

- Şirket Web Siteleri
- Kariyer Sayfaları
- Hakkımızda Sayfaları
- Basın Bültenleri
- Faaliyet Raporları
- Sürdürülebilirlik Raporları
- Kurumsal Bloglar

### Resmi Kaynaklar

- Ticaret Sicil Kayıtları
- Ticaret Sicil Gazetesi
- MERSİS
- KAP
- Kamu İhale Verileri
- Resmi Gazete
- Patent ve Marka Verileri

### Haber Kaynakları

- Ekonomi Haberleri
- Finans Haberleri
- Sektörel Yayınlar
- Basın Duyuruları
- Yatırım Haberleri

### Sosyal Medya Kaynakları

- LinkedIn
- X
- Facebook
- Instagram
- Youtube
- Medium

### Teknoloji Kaynakları

- GitHub
- GitLab
- Docker
---
*Skill bu havuzda her ajan tarafından paylaşılır. Orijinal marketplace
referansı: `.agents/marketplace/skills/web-design-guidelines/` (UI) ve
`content-research-writer/` (iş modeli adaptasyonu).*
