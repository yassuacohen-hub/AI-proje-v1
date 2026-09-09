> **Wiki bilgisi:** Obsidian wiki sayfasi: AI proje v1/V10/11_osint_motoru/OSINT_Scraper_Motoru.md — kod tarafindan erisim icin bu dosya korunur.

# OSINT Scraper Motoru (v1)

> **Durum:** Aktif (v1) · **Tarih:** 2026-09-03 · **Sahip:** Gelistirici Ajan + Harici Ajan (Inkling)

## Nedir?

Ankara B2B Company Master projesinin tum veri toplama akisinin tek catisi:
izin yonetimi (robots.txt + KVKK + rate limit), kaynak kayit defteri,
scraper orkestrasyonu ve post-scrape pipeline (ingest -> VKN -> kalite -> KPI).

## Bilesenler

| Bilesen | Konum | Gorev |
|---------|-------|-------|
| **Permission Router** | `src/company_master/utils/scraping_permission_router.py` | robots.txt (TTL'li cache), KVKK guvenli domain listesi, domain bazli rate limit |
| **Source Registry** | `src/company_master/engine/source_registry.py` | Tum kaynaklarin tanimi (scraper, cikti dosyasi, pipeline baglantisi) |
| **Orkestrator (Engine)** | `src/company_master/engine/osint_engine.py` | CLI: `status` / `check` / `run` / `pipeline` |
| **CLI Koprusu** | `scripts/osint_engine.py` | PYTHONPATH otomatik ayarli giris noktasi |
| **Post-Scrape Workflow** | `scripts/post_scrape_workflow.py` | ingest -> footer VKN -> kalite recalc -> KPI (subprocess zinciri) |
| **Scrape Watcher** | `scripts/scrape_watcher.py` | Scrape bitisini dosya-stabilitesi ile tespit eder, workflow'u tetikler (detached) |

## Kaynaklar (Registry)

| ID | Kaynak | Durum | Cikti |
|----|--------|-------|-------|
| `ostim-detail` | OSTIM Detay Uye Scrape | **CALISIYOR** | `data/ostim/firmalar_detayli.jsonl` |
| `ostim-list` | OSTIM Liste | TAMAM (NACE %84.8) | `data/ostim/firmalar_full.jsonl` |
| `aso` | ASO Firma Rehberi (API) | Veri mevcut (488KB) | `data/aso/aso_full.jsonl` |
| `ivedik` | Ivedik OSB | PLANLI — scraper yok | `data/ivedik/ivedik_full.jsonl` |
| `baskent` | Baskent OSB | PLANLI — scraper yok | `data/baskent/baskent_full.jsonl` |

## Kullanim

```bash
# Durum + router politikalari
python scripts/osint_engine.py status

# Izin kontrolu (robots.txt + KVKK)
python scripts/osint_engine.py check ostim-detail

# Kaynak calistir (scrape bitince pipeline otomatik)
python scripts/osint_engine.py run aso

# Sadece pipeline (scrape'siz ingest->VKN->recalc->KPI)
python scripts/osint_engine.py pipeline ostim-detail
```

## Rate Limit / KVKK Politikasi

- Her domain icin `min_interval` (OSTIM 2.5s, ASO 2.0s, GIB 1.0s)
- `KVKK_SAFE_DOMAINS`: sadece isletme verisi sunan resmi dizinler (OSTIM, ASO, GIB)
- Listede olmayan domainlerde scraper kisisel veri toplanmamali (router uyarir)
- Yeni kaynak eklerken: `DEFAULT_POLICIES`'e politika + `default_sources()`'a SourceSpec

## Yol Haritasi (v2)

1. **Ivedik + Baskent scraper'lari** — Web Kazima Uzmani masa basi analizi sonrasi
2. **Engine state dashboard** — `osint_engine_state.json` uzerinden Streamlit paneli
3. **Zamanlanmis calistirma** — watcher'a cron/schedule destegi (gunluk refresh)
4. **ASO pipeline** — mevcut 488KB ASO verisinin ingest'i (multi-OSB merger ilk adimi)
5. **Multi-OSB merger entegrasyonu** — `scripts/multi_osb_merger_plan.md` uygulanir

## Iliskili Dokumanlar

- `scripts/multi_osb_merger_plan.md` — birlestirme plani
- `scripts/mersis_api_research.md` — MERSIS/Ticaret Sicili API
- `V10/07_referanslar/08_gib_vergino_sorgu_stratejisi.md` — VKN sorgu stratejisi