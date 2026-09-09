# AGENT_SYNC — Otomatik Olusturuldu (task_board'dan)

> Son guncelleme: 2026-09-09T12:26:10
> Kaynak: data/orchestrator/task_board.json

## ⚡ SISTEM V2 — TUM AJANLARA (2026-09-09, ONEM: YUKSEK)

**Artik calisma ortami degisti — yeni gorevlerde buna uyma kurali:**

1. **API Docker konteynerinde** (restart: unless-stopped, port 8000, health=200). Yeni kod yazarken:
   - Bagimliliklari `requirements-app.txt`'e ekle (Dockerfile image'i oradan kurar)
   - Non-root kurali: konteynerde `appuser` calisir, dosya yazma icin `logs/`, `data/` yazilabilir olmali
2. **Yerel PostgreSQL 16 devrede** (`localhost:5433`, db `huginn`, sifre `huginn_local_dev`, profil `localdb`):
   - 14.000 firma + 8.905 entity_resolution + 14.000 source_records yuklu
   - **Sorgular ~30x hizli** (11 ms vs Supabase 300-900 ms) → testleri ve agir isleri yerelde kos
   - Baglanti: `DATABASE_URL=postgresql+psycopg://huginn:huginn_local_dev@localhost:5433/huginn`
   - `restore_db.py` artik JSONB uyumlu (SQLite backup -> PostgreSQL restore calisir)
3. **Git/GitHub:** private repo `yassuacohen-hub/AI-proje-v1` — otomatik gunluk push (04:00, `scripts/git_auto_push.bat`). Commit disiplini: `git_auto_push.bat` elle de calistirilabilir. `.env`, `backups/`, `*.db` gitignore'da — gizli veri koyma.
4. **Otomasyon zinciri:** 03:00 DB backup → 04:00 git push → 08:00 change notify (Telegram).
5. **KVKK maskeleme aktif:** `web_app.py → apply_kvkk_mask` (`?mask=1` veya `DASH_MASK_PII=1`). Musteri ucu ciktilarinda e-posta/telefon maskeleme varsayilani unutma.

**Yeni arastirma gorevleri acildi:** Y15 (yerel DB trigram index), Y16 (sektor zekasi/MVP market brain), Y17 (yeni veri kaynaklari: TOBB/ihale/KOSGEB), Y18 (abonelik tier tasarimi), Y19 (V9 smart matching MVP). Detaylar panoda (id: Y15-Y19).


## Aktif Isler

| Gorev | Baslik | Sahip | Oncelik | Durum |
|-------|--------|-------|---------|-------|
| P3-2 | VKN web kazima genisle (sadece footer de | web_kazima | plan | blocked |
| P4-3 | OSTIM detay sayfasindan vergi_no kazima  | web_kazima | P1 | blocked |
| Y10 | MERSIS VKN zenginlestirme pipeline'i | gelistirici | P1 | blocked |
| Y11 | GIB VKN dogrulama entegrasyonu | arastirmaci | P1 | plan |
| DENET-1 | Git deposu baslatma (git init + ilk comm | devops | P1 | blocked |
| P6-1 | İş ilanları ve çalışan sayısı veri topla | web_kazima | P1 | cancelled |

## Tamamlananlar (Son 10)

| Gorev | Baslik | Sahip | Bitis |
|-------|--------|-------|-------|
| P5-3 | Veri güncelliği metriği | backend | 2026-09-09 |
| P5-4 | Telefon format validasyonu | gelistirici | 2026-09-09 |
| P5-5 | Kaynak çeşitliliği metriği | kalite | 2026-09-09 |
| DENET-2 | Karakter kodlama (mojibake) düzeltmesi | koordinator | 2026-09-09 |
| DENET-3 | AGENTS.md tekrar eden blok temizliği + g | koordinator | 2026-09-09 |
| DENET-4 | Kok dizin gecici/deneme dosyalarinin tem | devops | 2026-09-09 |
| DENET-5 | Yazim hatali 'Huginin Data Insights' kla | koordinator | 2026-09-09 |
| DENET-6 | project_state.md kopyalarinin (iso/utf8) | mimar | 2026-09-09 |
| DENET-7 | company_master.db / test.db amacinin dok | backend | 2026-09-09 |
| P6-2 | E-posta DNS MX doğrulama implementasyonu | backend | 2026-09-09 |

## Son Handoff'lar

- **P1-1**: Ivedik scraper implementasyonu tamam (kod hazir)
- **P1-2**: Başkent scraper implementasyonu tamam (kod hazir)
- **P4-5**: Duplicate temizligi tamam; veri tekillestirildi, a
- **P4-1**: Kalite skoru 27.5 -> ~64 tamamlandi
- **P4-4**: Dashboard performans izleme ve slow query optimiza

- **Y17**: Yeni veri kaynaklari arastirmasi tamamlandi (TOBB, il ozu, KOSGEB, ihale, EKAP). Sonuc: data/orchestrator/y17_result.json

## 2026-09-09 � P7 Job Intelligence Mod�l� Planlamas�

### Altyap� Haz�r
- Migration 0007: 5 tablo + 2 view + trigger
- Source Registry: company-career-pages, iskur, kariyer-net
- Permission Router: �SKUR (kvkk_safe), Kariyer.net (kvkk_safe=False)
- Post-Scrape Pipeline: +3 ad�m (ingest, analyze, score)

### Task Da��l�m� (P7-1..P7-11)
| Task | Sahip | �ncelik | Durum |
|------|-------|---------|-------|
| P7-1: Migration | gelistirici | P0 | plan |
| P7-2: Mod�l yap�s� | mimar | P0 | plan |
| P7-3: Company Matcher | gelistirici | P0 | plan |
| P7-4: Career Pages Scraper | web_kazima | P0 | plan |
| P7-5: �SKUR Scraper | web_kazima | P1 | plan |
| P7-6: Kariyer.net Scraper | web_kazima | P2 | blocked |
| P7-7: Ingest Script | gelistirici | P0 | plan |
| P7-8: Signals Analyzer | arastirmaci | P0 | plan |
| P7-9: Intelligence Scorer | arastirmaci | P0 | plan |
| P7-10: Scores Recalc | gelistirici | P0 | plan |
| P7-11: Workflow Entegrasyonu | gelistirici | P0 | done |

### MVP S�ras� (�lk 2 Hafta)
1. Migration + Company Matcher + Career Pages Scraper + �SKUR Scraper + Ingest
2. Analyzer + Scorer + Recalc Script + Pipeline entegrasyonu

### �lgili Ajanlar Bilgisi
- **Mimar (P7-2):** Mod�l yap�s�n� `src/company_master/intelligence/job_intelligence/` alt�na kur
- **Geli�tirici (P7-1,3,7,10):** Migration, Matcher, Ingest, Recalc scriptleri
- **Web Kaz�ma (P7-4,5,6):** Career Pages, �SKUR, Kariyer.net scraper�lar�
- **Ara�t�rmac� (P7-8,9):** Sinyal analizi ve skorlama motoru
