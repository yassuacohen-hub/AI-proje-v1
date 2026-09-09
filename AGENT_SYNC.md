# AGENT_SYNC â€” Otomatik Olusturuldu (task_board'dan)

> Son guncelleme: 2026-09-09T12:26:10
> Kaynak: data/orchestrator/task_board.json

## Aktif Isler

| Gorev | Baslik | Sahip | Oncelik | Durum |
|-------|--------|-------|---------|-------|
| P3-2 | VKN web kazima genisle (sadece footer de | web_kazima | plan | blocked |
| P4-3 | OSTIM detay sayfasindan vergi_no kazima  | web_kazima | P1 | blocked |
| Y10 | MERSIS VKN zenginlestirme pipeline'i | gelistirici | P1 | blocked |
| Y11 | GIB VKN dogrulama entegrasyonu | arastirmaci | P1 | plan |
| DENET-1 | Git deposu baslatma (git init + ilk comm | devops | P1 | blocked |
| P6-1 | Ä°ÅŸ ilanlarÄ± ve Ã§alÄ±ÅŸan sayÄ±sÄ± veri topla | web_kazima | P1 | cancelled |

## Tamamlananlar (Son 10)

| Gorev | Baslik | Sahip | Bitis |
|-------|--------|-------|-------|
| P5-3 | Veri gÃ¼ncelliÄŸi metriÄŸi | backend | 2026-09-09 |
| P5-4 | Telefon format validasyonu | gelistirici | 2026-09-09 |
| P5-5 | Kaynak Ã§eÅŸitliliÄŸi metriÄŸi | kalite | 2026-09-09 |
| DENET-2 | Karakter kodlama (mojibake) dÃ¼zeltmesi | koordinator | 2026-09-09 |
| DENET-3 | AGENTS.md tekrar eden blok temizliÄŸi + g | koordinator | 2026-09-09 |
| DENET-4 | Kok dizin gecici/deneme dosyalarinin tem | devops | 2026-09-09 |
| DENET-5 | Yazim hatali 'Huginin Data Insights' kla | koordinator | 2026-09-09 |
| DENET-6 | project_state.md kopyalarinin (iso/utf8) | mimar | 2026-09-09 |
| DENET-7 | company_master.db / test.db amacinin dok | backend | 2026-09-09 |
| P6-2 | E-posta DNS MX doÄŸrulama implementasyonu | backend | 2026-09-09 |

## Son Handoff'lar

- **P1-1**: Ivedik scraper implementasyonu tamam (kod hazir)
- **P1-2**: BaÅŸkent scraper implementasyonu tamam (kod hazir)
- **P4-5**: Duplicate temizligi tamam; veri tekillestirildi, a
- **P4-1**: Kalite skoru 27.5 -> ~64 tamamlandi
- **P4-4**: Dashboard performans izleme ve slow query optimiza

## 2026-09-09 — P7 Job Intelligence Modülü Planlamasý

### Altyapý Hazýr
- Migration 0007: 5 tablo + 2 view + trigger
- Source Registry: company-career-pages, iskur, kariyer-net
- Permission Router: ÝSKUR (kvkk_safe), Kariyer.net (kvkk_safe=False)
- Post-Scrape Pipeline: +3 adým (ingest, analyze, score)

### Task Daðýlýmý (P7-1..P7-11)
| Task | Sahip | Öncelik | Durum |
|------|-------|---------|-------|
| P7-1: Migration | gelistirici | P0 | plan |
| P7-2: Modül yapýsý | mimar | P0 | plan |
| P7-3: Company Matcher | gelistirici | P0 | plan |
| P7-4: Career Pages Scraper | web_kazima | P0 | plan |
| P7-5: ÝSKUR Scraper | web_kazima | P1 | plan |
| P7-6: Kariyer.net Scraper | web_kazima | P2 | blocked |
| P7-7: Ingest Script | gelistirici | P0 | plan |
| P7-8: Signals Analyzer | arastirmaci | P0 | plan |
| P7-9: Intelligence Scorer | arastirmaci | P0 | plan |
| P7-10: Scores Recalc | gelistirici | P0 | plan |
| P7-11: Workflow Entegrasyonu | gelistirici | P0 | done |

### MVP Sýrasý (Ýlk 2 Hafta)
1. Migration + Company Matcher + Career Pages Scraper + ÝSKUR Scraper + Ingest
2. Analyzer + Scorer + Recalc Script + Pipeline entegrasyonu

### Ýlgili Ajanlar Bilgisi
- **Mimar (P7-2):** Modül yapýsýný `src/company_master/intelligence/job_intelligence/` altýna kur
- **Geliþtirici (P7-1,3,7,10):** Migration, Matcher, Ingest, Recalc scriptleri
- **Web Kazýma (P7-4,5,6):** Career Pages, ÝSKUR, Kariyer.net scraper’larý
- **Araþtýrmacý (P7-8,9):** Sinyal analizi ve skorlama motoru
