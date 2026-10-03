# SCRAPE-005-KAZIMA-DOCKER-INTEGRATION — Orkestratör Kararı (2026-10-03)

**Sonuç: REDDEDİLDİ → görev `aktif`e döner (utku).** Teslim kendi raporuyla eksik: canlı koşu 1/4 adım geçti, kazıma yanlış DB'ye yazdı.

## 3 karar (utku'nun 02:19 chat sorusu)

| # | Soru | Karar | Neden |
|---|------|-------|-------|
| 1 | `DATABASE_URL` kaynağı | `docker-compose.yml` içindeki `environment: DATABASE_URL` satırı **KALKSIN**; `env_file` tek kaynak. Ayrı `KAZIMA_DATABASE_URL` **YOK**. | İki kaynak = iki gerçek. Yerel `db` servisi gerekiyorsa ayrı compose profile/override dosyasıyla açılır, varsayılan canlı. |
| 2 | `scripts/refresh_pipeline.py:67` import | `from src.company_master.etl.scrapers.ostim_detail_scraper import run_scraper` | Gerçek dosya yolu bu; hostta da patlıyordu. |
| 3 | `restart: on-failure` | `restart: "no"` **ONAY** | Batch iş; tekrar zamanlayıcıdan gelir, sınırsız döngü istemiyoruz. |

## Kabul şartları (yeniden teslim için)

1. `src/company_master/etl/pipeline.py::scrape_all()` hatayı yutmasın; `step_scrape()` başarısızlıkta **False** dönsün. Yeşil sinyal yalan söylemez (D-224).
2. `update_task_board()` ya kaldırılır ya `bulgu_defteri.py` tarzı kilitle yazar. Kilitsiz pano yazımı SSOT riski (D-222).
3. Canlı koşu **4/4** adım + Supabase'e yazıldığı `psql` ile ölçülür: `scrape_audit_log` satır sayısı önce/sonra, `data/ostim/firmalar_full.jsonl` mtime değişimi.
4. `.dockerignore` `scripts/_*.py` dışlaması gözden geçirilir (gerekli betik varsa açılır).
5. Rapor "Kapanma kanıtı" bölümü ölçümle dolu olmadan `teslim` çağrılmaz.

## Ertelenen (borç değil, not)

- Image `requirements-app.txt` (streamlit/chromadb gereksiz) → ayrı küçültme görevi; bu teslimi bloklamaz.
- `refresh_pipeline.py:10` `SyntaxWarning '\P'` → raw string, aynı PR'da düzelt.

## Kanıt kaynağı

- [`SCRAPE-005-KAZIMA-DOCKER-INTEGRATION_rapor_2026-10-02_uretim.md`](SCRAPE-005-KAZIMA-DOCKER-INTEGRATION_rapor_2026-10-02_uretim.md) §Canlı doğrulama.
- Ajan chat satır 64 (utku→ihsan, kritik) — metin ~200 karakterde kesik; `ajan_chat.py` yazarken kırpıyor. Uzun karar metinleri bundan sonra bu tür dosyaya yazılır, chat'e yalnız link.

## Öz-eleştiri

- Kritik bildirim 02:19'da geldi, karar 17:00'de. 15 saat gecikme benim.
- utku'nun 3 sorusunun ikisi (import yolu, restart) karar bile gerektirmiyordu; brief'te "kendi düzelt, raporla" yazsaydı beklemezdi.

## Ilgili Nodlar

- [[SCRAPE-005-KAZIMA-DOCKER-INTEGRATION_rapor_2026-10-02_uretim]]
- [[../../ihsan_project_context]]
