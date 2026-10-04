-- 0050: Web Kazıma Denetim Tabloları (scrape_audit_log, scrape_pages, scrape_errors)
--
-- Karar: D-310 (Beş Katmanlı Kontrol), D-261 (content_hash idempotent dedup),
--        D-323 (0046 numarası risk_skorlari.sql tarafından alınmıştı; göç 0050'ye taşındı)
-- SSOT: plans/2026-10-01_docker_taşıma_kazıma_entegrasyon_değerlendirmesi.md:106-243
--
-- NEDEN YENİ GÖÇ: Kazıma işlerinin merkezi kaydı yok; dedup DB-level UNIQUE kısıtla
-- sağlanır; Apify/Scrapling/9Router/requests+BeautifulSoup sonuçlarını tek yerde tutar.
--
-- Tarih: 2026-10-02 (orijinal taslak: 2026-10-01, numara çakışması nedeniyle 0046→0050)

BEGIN;

-- Tablo 1: scrape_audit_log
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'scrape_audit_log') THEN
    CREATE TABLE scrape_audit_log (
      audit_id BIGSERIAL PRIMARY KEY,
      timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
      source_name VARCHAR(100) NOT NULL,
      source_url TEXT NOT NULL,
      task_id VARCHAR(50),
      action VARCHAR(50) NOT NULL,
      status VARCHAR(20) NOT NULL,
      bytes_fetched BIGINT,
      duration_ms FLOAT,
      error_msg TEXT,
      llm_used BOOLEAN DEFAULT FALSE,
      llm_model VARCHAR(100),
      cost_usd NUMERIC(12, 6) DEFAULT 0.00 CHECK (cost_usd = 0),
      created_at TIMESTAMPTZ DEFAULT now(),
      updated_at TIMESTAMPTZ DEFAULT now()
    );
    COMMENT ON TABLE scrape_audit_log IS 'Kazıma işlerinin merkezi denetim günlüğü (D-310)';
    COMMENT ON COLUMN scrape_audit_log.cost_usd IS 'Varsayılan 0; ücretli fallback kullanıldıysa manuel güncelleme (D-309)';
    COMMENT ON COLUMN scrape_audit_log.llm_model IS 'Kullanılan model: qwen-7b-chat / deepseek-chat / jina-reader';
    CREATE INDEX idx_scrape_audit_timestamp ON scrape_audit_log(timestamp DESC);
    CREATE INDEX idx_scrape_audit_source ON scrape_audit_log(source_name);
    CREATE INDEX idx_scrape_audit_status ON scrape_audit_log(status);
  END IF;
END $$;

-- Tablo 2: scrape_pages
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'scrape_pages') THEN
    CREATE TABLE scrape_pages (
      page_id BIGSERIAL PRIMARY KEY,
      source_url TEXT NOT NULL,
      url_hash VARCHAR(64) NOT NULL,
      content_hash VARCHAR(64) NOT NULL,
      raw_content TEXT NOT NULL,
      raw_content_length BIGINT,
      extracted_json JSONB,
      extracted_fields JSONB DEFAULT '{}',
      llm_used BOOLEAN DEFAULT FALSE,
      llm_model VARCHAR(100),
      cost_usd NUMERIC(12, 6) DEFAULT 0.00 CHECK (cost_usd = 0),
      parsing_duration_ms FLOAT,
      fetch_timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
      created_at TIMESTAMPTZ DEFAULT now(),
      UNIQUE(source_url, content_hash)
    );
    COMMENT ON TABLE scrape_pages IS 'Web kazıma ham içeriği (dedup; idempotent re-run aman)';
    COMMENT ON COLUMN scrape_pages.url_hash IS 'SHA256(normalize(source_url)); B0 → Canonical URL match';
    COMMENT ON COLUMN scrape_pages.content_hash IS 'SHA256(raw_content); zaman damgası değil, yalnız içerik';
    COMMENT ON COLUMN scrape_pages.extracted_json IS 'Full kazıma çıktısı (HTML nodes vs); debug';
    COMMENT ON COLUMN scrape_pages.extracted_fields IS '{company_name: "...", phone: [...], ...}';
    CREATE INDEX idx_scrape_pages_url_hash ON scrape_pages(url_hash);
    CREATE INDEX idx_scrape_pages_content_hash ON scrape_pages(content_hash);
    CREATE INDEX idx_scrape_pages_fetch_timestamp ON scrape_pages(fetch_timestamp DESC);
    CREATE INDEX idx_scrape_pages_created_at ON scrape_pages(created_at DESC);
  END IF;
END $$;

-- Tablo 3: scrape_errors
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'scrape_errors') THEN
    CREATE TABLE scrape_errors (
      error_id BIGSERIAL PRIMARY KEY,
      audit_id BIGINT REFERENCES scrape_audit_log(audit_id) ON DELETE CASCADE,
      page_id BIGINT REFERENCES scrape_pages(page_id) ON DELETE SET NULL,
      error_code VARCHAR(50),
      error_message TEXT,
      retry_count INT DEFAULT 0,
      next_retry_at TIMESTAMPTZ,
      fallback_tried BOOLEAN DEFAULT FALSE,
      created_at TIMESTAMPTZ DEFAULT now()
    );
    COMMENT ON TABLE scrape_errors IS 'Rollback ve diagnostik için hata kaydı';
    CREATE INDEX idx_scrape_errors_audit_id ON scrape_errors(audit_id);
    CREATE INDEX idx_scrape_errors_next_retry ON scrape_errors(next_retry_at) WHERE next_retry_at IS NOT NULL;
  END IF;
END $$;

COMMIT;

-- Göç DDL izi taşır (3 CREATE TABLE + 10 CREATE INDEX) — `veri-gocu:` beyanı
-- YAZILMAZ: o beyan yalnız semada izi olmayan saf veri göçleri içindir (D-267/7).
-- Buraya yazılırsa tablo yanlışlıkla düşürülürse defter "VERI" deyip susar,
-- yani yarınki gerçek alarm bugün yanlış alarmla maskelenir (D-267/7).
--
-- `dusen-iz` beyanı da YOK: bu göç `audit_log`/`pages`/`errors` tablolarına
-- dokunmadı. Düşürdüğü izi beyan etmek, hiç dokunmadığı izi "düşürdü" diye
-- işaretlemektir (D-253/2).
