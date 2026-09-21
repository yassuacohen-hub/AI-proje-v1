# AUDIT-ENC-02 — Repo Geneli Kodlama Denetimi + kodlama_denetim.py Kapsam Kontrolü

- **Denetleyen:** cline (tarih: 2026-09-15)
- **Kapsam:** BOM / UTF-16 / NUL / 0-bayt / py_compile + EOL (CRLF) durumu; kodlama_denetim.py kapsam yeterliliği
- **Karar önerisi:** kapsam içi **temiz**; CRLF ihlal olarak eklenmemeli; tek seferlik `git add --renormalize .` önerilir

## 1. Kapsam içi (src, tests, web_dashboard, scripts) — TEMİZ

| Kontrol | Sonuç |
|---|---|
| `python scripts/kodlama_denetim.py` | **EXIT 0** — ihlal 0 (utf8_bom: 0, utf16: 0, nul: 0, bos: 0, compile: 0) |
| `data/kodlama_allowlist.json` | bom: 0, compile: 0 — ratchet tam sıkılıkta (muafiyet kalmadı) |

## 2. Kapsam dışı tam-repo taraması (`--tam-repo`, EXIT 1 — beklendik)

| İhlal | Adet | Nerede |
|---|---|---|
| utf8_bom | 71 | `AI proje v1/` ağacı (V10 dokümanları, cop_kutusu arşivi), `docs/`, `logs/`, kök kalıntılar (`web_app.py`, `locustfile.py`, `system_prompt.md`, `write_destek.py`, `run_career_scrape.py`, `wiki_automation/`, `tests/company_master/` eski kopyaları) |
| compile | 5 | 4 × `AI proje v1/` ağacı (`_tmp_aso_bulk.py`, `_tmp_gen_p41.py`, `ingest_job_postings.py`, `company_career.py`) + 1 × `AI proje v1/scripts/check_email_dist.py` (kökteki düzeltilmiş sürümün eski kopyası) |
| utf16 | 1 | `AI proje v1/src/company_master/schema/migrations/0006_normalize_compat.py` (KR-1'de kökte temizlenen 0006'nın arşiv kopyası) |
| nul | 2 | `AI proje v1/V10/CHANGELOG.md` + aynı 0006 arşiv kopyası |
| bos (0-bayt) | 6 | `AI proje v1/Kimlik Doğrulama Sistemi.md`, `Kullanıcı Yönetimi.md`, `Mimari Kararlar.md` + kök düzey kopyaları |

**Değerlendirme:** Tüm ihlaller kullanıcı belgeleri, arşiv/backup ağacı (`AI proje v1/`, `backups/.kilo`) ve eski çalışma-kopyası kalıntılarında; **üretim kodu kapsamında 0 ihlal**. Ratchet (allowlist boş) korunuyor; bu dosyalar için aksiyon önerilmez (kapsam dışı bilinçli tercih).

## 3. EOL (CRLF) analizi — talimattaki ek denetim

- `git config core.autocrlf` = **true**; `.gitattributes` içinde `text eol=lf` tanımlı.
- Working copy: kapsam içi 565 .py dosyasının **379'u CRLF** (%67); tüm repo 2888 dosyada 2602 CRLF (%90).
- **Depo içi (index) EOL:** **861 dosya i/lf**, **35 dosya i/crlf**, 22 i/none (ikili).
- **Sonuç:** Working-copy CRLF'leri git'e girişte LF'e normalize ediliyor (`i/lf w/crlf` çiftleri bunun kanıtı) — **CRLF'in kodlama_denetim.py'ye ihlal olarak eklenmemesi doğru karardır**; eklenmesi 379 dosyalık yanlış pozitif üretirdi.
- **Tek gerçek bulgu:** depoya CRLF olarak girmiş **35 dosya** (`i/crlf`) — liste: `data/nace/*.json`, `src/data_quality_toolkit/**` (çoğunluk), `src/company_master/{__init__,db/__init__,etl/__init__,search/fulltext,seed/seed_ankara_osb,intelligence/market_brain,etl/scrapers/ostim_scraper_full}.py`, `tests/{test_platform,company_master/test_migrate,data_quality_toolkit/*}.py`, `scripts/{kalite_analizi,test_ostim_scrape}.py`, `run_tests.py`, `.instructions.md`, 2 README.
  - **Öneri (düşük öncelik):** tek seferlik `git add --renormalize .` ile bunlar da `i/lf`'e çekilir; işlevsel etkisi yok, platformlar-arası diff temizliği sağlar. Ayrı hijyen commit'i (roo kararı).

## 4. kodlama_denetim.py kapsam kontrolü

- Mevcut kapsam (`src`, `tests`, `web_dashboard`, `scripts`) + atlanan ağır dizinler (`data`, `.kilo`, `backups`, `AI proje v1`, `workspace`) **doğru ve yeterli**: üretim kodunun tamamı kapalı, kullanıcı belgeleri/arşivler bilinçli dışarıda, `--tam-repo` ile de görünür kalıyor.
- **Öneri 1:** CRLF ihlal olarak eklenmesin (bkz. §3); gerekirse salt-rapor `--crlf-rapor` modu düşünülebilir.
- **Öneri 2:** `git add --renormalize .` (35 i/crlf dosyası için) — yukarıdaki öneri.
- **Öneri 3 (bilgi):** `AI proje v1/` ağacı repo'da kaldıkça `--tam-repo` her zaman EXIT 1 verecek; bu beklenen davranış (kapsam içi CI adımı varsayılan taramayı kullanıyor ve yeşil).

## Metodoloji notu

Ara rapor çıkışında PowerShell `>` yönlendirmesi geçici dosyayı UTF-16 yazdı (KR-4 kök nedeni birebir teyit edildi). Geçici dosya silindi; bu rapor editör aracıyla UTF-8 (BOM'suz) yazıldı ve doğrulandı (BOM: False, NUL: 0).
