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
| **Orkestrator (Engine)** | `src/company_master/engine/osint_engine.py` | CLI: `status` / `check` / `run` / `pipeline` / `quality` |
| **Quality Gate** | `src/company_master/engine/quality_gate.py` | Veri kalitesi konturu, DQT kurallari + DB skor filtreleme |
| **CLI Koprusu** | `scripts/osint_engine.py` | PYTHONPATH otomatik ayarli giris noktasi |
| **Post-Scrape Workflow** | `scripts/post_scrape_workflow.py` | Quality Gate -> ingest -> footer VKN -> kalite -> KPI (subprocess zinciri) |
| **Scrape Watcher** | `scripts/scrape_watcher.py` | Scrape bitisini dosya-stabilitesi ile tespit eder, workflow'u tetikler (detached) |

## Kalite Kontrol (Quality Gate)

OSINT Scraper Motoru, gelen veri yapisini otomatik olarak kalite sinirlarindan gecirir. Bu, sisteme girilen veri yapisinin kalitesini olcup filtreleyen en onemli moduldur.

### Calisma Prensibi
```
Scraper Ciktisi (JSONL)
        |
        v
 Quality Gate
    - DB Seviye Skor (VKN, Adres, Tel, Email, Web, NACE, Parsel, Unvan)  -> 0-100
    - Data Quality Toolkit Kurallari (NotNull, Regex, Custom)
    - Birlesik Skor: %70 DB + %30 DQT Pass Rate
        |
        v
 Filtreleme (min_score eksi)
    - Geçenler -> temiz.jsonl (+ quality metadati)
    - Reddedilenler -> rapor
```

### Kullanim

```bash
# Terminal CI icin
python -m company_master.engine.quality_gate data/ostim/firmalar_detayli.jsonl data/ostim/firmalar_temiz.jsonl --min-score 30

# OSINT Engine icine dahil olarak
python -m company_master.engine.osint_engine quality ostim-detail --min-score 30

# DQT olmadan calistir
python -m company_master.engine.quality_gate input.jsonl output.jsonl --no-dqt --min-score 50
```

### Birlesik Skor Formulu

| Boyut | Puan | Kaynak |
|-------|------|--------|
| VKN (vergi no) | 15 | quality_recalc.py |
| Adres | 15 | quality_recalc.py |
| Telefon | 15 | quality_recalc.py |
| E-posta | 15 | quality_recalc.py |
| Web sitesi | 10 | quality_recalc.py |
| NACE kodu | 15 | quality_recalc.py |
| OSB parsel | 10 | quality_recalc.py |
| Ticaret unvani | 5 | quality_recalc.py |
| **Toplam DB** | **100** | |
| DQT Pass Rate | 0-100 | Data Quality Toolkit |
| **Birlesik Skor** | **%70 DB + %30 DQT** | quality_gate.py |

### Diger Komutlar

```bash
# Durum + router politikalari
python scripts/osint_engine.py status

# Izin kontrolu (robots.txt + KVKK)
python scripts/osint_engine.py check ostim-detail

# Kaynak calistir (scrape bitince pipeline otomatik)
python scripts/osint_engine.py run aso

# Sadece pipeline (scrape'siz ingest->VKN->recalc->KPI)
python scripts/osint_engine.py pipeline ostim-detail

# Quality Gate kontrolu
python scripts/osint_engine.py quality ostim-detail --min-score 30

## Wiki Automation

Wiki otomasyon scriptleri `wiki_automation/` klasöründe:

```bash
# Tek tek calistirma
python wiki_automation/wiki_ingest.py       # Yeni/duzenlenmis sayfalari tespit
python wiki_automation/wiki_sync_agents.py  # task_board agent dosyalarini senkronize et
python wiki_automation/wiki_lint.py         # Saglik kontrolu
python wiki_automation/wiki_index.py        # index.json güncelle

# Otomatik duzeltme (eksik frontmatter, broken link placeholder)
python wiki_automation/wiki_lint.py --fix

# CI modu (hata varsa exit code 1)
python wiki_automation/wiki_lint.py --ci

# Orkestrator (hepsini sirali calistir)
python wiki_automation/run_all.py --fix --commit
```

### wiki_lint.py Kontrolleri
- **Orphans**: task_board.json'da olmayan wiki dosyalari
- **Broken Links**: [[task-id]] / [[agent-id]] gecersiz linkler
- **Contradiction Density**: Son 24 saatte contradictions sayisi
- **Stale Content**: 7 gun üzeri guncellenmeyen aktif gorevler
- **Frontmatter**: Gerekli alanlar (task_id, sahip, durum, updated_at)

```