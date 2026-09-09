# OSINT Scraper Motoru

> **Durum:** Aktif (v1) · **Tarih:** 2026-09-03 · **Sahip:** Geliştirici Ajan + Harici Ajan (Inkling)

İlgili: [[09_osint_rol_tanimi]] · [[06_web_kazima_uzmani]] · [[10_ankara_osb_sentez]] · [[08_gib_vergino_sorgu_stratejisi]] · [[project_state]]

## Nedir?

Ankara B2B Company Master projesinin tüm veri toplama akışının tek çatısı:
izin yönetimi ([[03_kvkk_ve_veri_politikasi]] + robots.txt + rate limit),
kaynak kayıt defteri, scraper orkestrasyonu ve post-scrape pipeline
(ingest → VKN → kalite → KPI).

## Bileşenler

| Bileşen | Konum | Görev |
|---------|-------|-------|
| **Permission Router** | `src/company_master/utils/scraping_permission_router.py` | robots.txt (TTL'li cache), KVKK güvenli domain listesi, domain bazlı rate limit |
| **Source Registry** | `src/company_master/engine/source_registry.py` | Tüm kaynakların tanımı (scraper, çıktı dosyası, pipeline bağlantısı) |
| **Orkestratör (Engine)** | `src/company_master/engine/osint_engine.py` | CLI: `status` / `check` / `run` / `pipeline` |
| **CLI Köprüsü** | `scripts/osint_engine.py` | PYTHONPATH otomatik ayarlı giriş noktası |
| **Post-Scrape Workflow** | `scripts/post_scrape_workflow.py` | ingest → footer VKN → kalite recalc → KPI (subprocess zinciri) |
| **Scrape Watcher** | `scripts/scrape_watcher.py` | Scrape bitişini dosya-stabilitesi ile tespit eder, workflow'u tetikler (detached) |

## Kaynaklar (Registry)

| ID | Kaynak | Durum | Çıktı |
|----|--------|-------|-------|
| `ostim-detail` | OSTIM Detay Uye Scrape | **ÇALIŞIYOR** | `data/ostim/firmalar_detayli.jsonl` |
| `ostim-list` | OSTIM Liste | TAMAM (NACE %84.8) | `data/ostim/firmalar_full.jsonl` |
| `aso` | ASO Firma Rehberi (API) | Veri mevcut (488KB) | `data/aso/aso_full.jsonl` |
## Kullanım

```bash
# Durum + router politikaları
python scripts/osint_engine.py status

# İzin kontrolü (robots.txt + KVKK)
python scripts/osint_engine.py check ostim-detail

# Kaynak çalıştır (scrape bitince pipeline otomatik)
python scripts/osint_engine.py run aso

# Sadece pipeline (scrape'siz ingest→VKN→recalc→KPI)
python scripts/osint_engine.py pipeline ostim-detail
```

## Rate Limit / KVKK Politikası

- Her domain için `min_interval` (OSTIM 2.5s, ASO 2.0s, GİB 1.0s)
- `KVKK_SAFE_DOMAINS`: sadece işletme verisi sunan resmi dizinler (OSTIM, ASO, GİB)
- Listede olmayan domainlerde scraper kişisel veri toplamamalı (router uyarır)
- Kurallar: [[03_kvkk_ve_veri_politikasi]] · [[05_acik_veri_ve_kazina_politikasi]]
- Yeni kaynak eklerken: `DEFAULT_POLICIES`'e politika + `default_sources()`'a SourceSpec

## Rol Bağlantısı

Motor, [[09_osint_rol_tanimi]]'deki OSINT ajan rolünün **araç/takviye katmanıdır**:
ajan'ın manuel kazıma yapması yerine, motor kaynakları kayıtlı politikalar uyarınca
otomatik toplar ve [[06_web_kazima_uzmani]]'nın izin/kaynak kontrolüne uyar.

## Yol Haritası (v2)

1. **İvedik + Başkent scraper'ları** — [[06_web_kazima_uzmani]] masa başı analizi sonrası
2. **Engine state dashboard** — `osint_engine_state.json` üzerinden Streamlit paneli
3. **Zamanlanmış çalıştırma** — watcher'a cron/schedule desteği (günlük refresh)
4. **ASO pipeline** — mevcut 488KB ASO verisinin ingest'i (multi-OSB merger ilk adımı)
5. **Multi-OSB merger entegrasyonu** — [[10_ankara_osb_sentez]] kararları uygulanır

## Wiki Bağlantıları

- [[09_osint_rol_tanimi]] — OSINT rol tanımı (ajan promptu)
- [[06_web_kazima_uzmani]] — kazıma izin/kaynak kontrolü
- [[10_ankara_osb_sentez]] — Karar 9 (NACE) ve OSB kaynak kararları
- [[08_gib_vergino_sorgu_stratejisi]] — VKN sorgu stratejisi
- [[03_kvkk_ve_veri_politikasi]] — KVKK kuralları
- [[05_acik_veri_ve_kazina_politikasi]] — açık veri/kazıma politikası
- [[01_veri_kaynagi_envanteri]] — veri kaynağı envanteri
- [[project_state]] — güncel durum
- [[10_mvp_kapsam]] — MVP kapsamı
- [[CHANGELOG]] — değişiklik kayıtları
| `ivedik` | İvedik OSB | PLANLI — scraper yok | `data/ivedik/ivedik_full.jsonl` |
| `baskent` | Başkent OSB | PLANLI — scraper yok | `data/baskent/baskent_full.jsonl` |