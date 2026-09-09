-- 0012_users_and_catalog.sql — Y19/Y22 takibi: Monetizasyon MVP (V7 Hybrid Credit)
-- Kredi modeli: V7/V8 dokümanı — Contact/Match credits (usage-metered)
-- Kurumsal e-posta kaydı + manuel onay kuyruğu + tier bazlı kredi + API key (enterprise)

CREATE TABLE IF NOT EXISTS users (
  user_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email             VARCHAR(255) UNIQUE NOT NULL,
  email_domain      VARCHAR(100),
  company_name      VARCHAR(255) NOT NULL,
  linked_company_id UUID,                     -- 14k kayitla eslesti ise
  nace_code         VARCHAR(10),
  products_desc     TEXT,                     -- ne uretiyor/satiyor (serbest metin)
  target_nace       TEXT,                     -- kime satmak istiyor (virgullu ana gruplar: '28,25,45')
  goal              VARCHAR(20) DEFAULT 'tumu', -- musteri|tedarikci|ortagi|tumu
  contact_name      VARCHAR(255),
  website           VARCHAR(255),
  kvkk_consent      BOOLEAN DEFAULT FALSE,
  role              VARCHAR(10) DEFAULT 'user',  -- user|admin
  status            VARCHAR(20) DEFAULT 'onay_bekliyor', -- onay_bekliyor|onayli|reddedildi
  tier              VARCHAR(20) DEFAULT 'terminal',      -- terminal|strategic|enterprise
  credit_balance    INT DEFAULT 0,           -- V7 Hybrid Credit
  api_key           VARCHAR(64),             -- sadece enterprise tier
  rejection_note    TEXT,
  created_at        TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_status ON users (status);

-- Kredi hareketleri (denetlenebilir - admin/otomasyon tum yukleme ve dusmeleri kaydeder)
CREATE TABLE IF NOT EXISTS credit_ledger (
  ledger_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  delta      INT NOT NULL,                   -- +yukleme / -tuetim
  reason     VARCHAR(60) NOT NULL,           -- approve|credit_pack|match|contact_reveal|adjust
  balance_after INT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ledger_user ON credit_ledger (user_id, created_at DESC);

-- Urun katalogu (V9 SSOT; firma-yetenek eslestirmesi icin temel)
CREATE TABLE IF NOT EXISTS product_categories (
  category_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code         VARCHAR(20) UNIQUE NOT NULL,
  label_tr     VARCHAR(120) NOT NULL,
  nace_group   VARCHAR(2),                -- bagli NACE ana grubu ('29' vb.)
  description  TEXT,
  active       BOOLEAN DEFAULT TRUE,
  created_at   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_pcat_nace ON product_categories (nace_group);
