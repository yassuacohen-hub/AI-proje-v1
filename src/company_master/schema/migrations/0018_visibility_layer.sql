-- Migration 0018: Katmanlı Görünürlük & Kontör Sistemi (ALTYAPI-VERI-GORUNURLUK-01)
-- D-200 — D-208: 9 karar (kontör modül, admin filter, müşteri mask kapalı, alan grubu, kontör düşüm, admin audit, OSINT filter, veri sınıf, silme yok)
-- KVKK 2-katman: Layer 1 (kod: field sınıfı), Layer 2 (tablo: paket×grup görünürlüğü)
-- Modül kontörü: 5 modül (match/ilan/analiz/teklif/kapasite) × 3 tier × farklı maliyet
-- Admin KVKK modu: strict (mutlak) vs lenient (yönetici riski, audit)
-- Geri alma: down/0018_visibility_layer.sql

-- 1. plan_field_group: Paket × Alan Grubu × Görünürlük
-- 6 grup (kimlik, iletişim, lokasyon, dijital, ticari, sınai) × 3 paket (terminal/strategic/enterprise) = 18 satır
CREATE TABLE IF NOT EXISTS plan_field_group (
  plan_field_group_id SERIAL PRIMARY KEY,
  plan VARCHAR(20) NOT NULL CHECK (plan IN ('terminal', 'strategic', 'enterprise')),
  field_group VARCHAR(40) NOT NULL CHECK (field_group IN (
    'kimlik',      -- legal_name, trade_name, company_registration_number, vb.
    'iletisim',    -- primary_phone, primary_email, website, vb.
    'lokasyon',    -- address, city, province, vb.
    'dijital',     -- website_exists, domain_valid, digital_presence, vb.
    'ticari',      -- annual_turnover, employee_count, vb. (finansal)
    'sinai'        -- manufacturing, industry_code, nace_code, vb.
  )),
  visibility VARCHAR(20) NOT NULL DEFAULT 'acik' CHECK (visibility IN ('acik', 'yarisacik', 'kisitli', 'yasak')),
  visibility_note TEXT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (plan, field_group)
);

-- 2. module_cost: Modül × Tier × Maliyet
-- 5 modül × 3 tier = 15 satır (enterprise=0 serbest)
CREATE TABLE IF NOT EXISTS module_cost (
  module_cost_id SERIAL PRIMARY KEY,
  module_id VARCHAR(30) NOT NULL CHECK (module_id IN ('match', 'ilan', 'analiz', 'teklif', 'kapasite')),
  tier VARCHAR(20) NOT NULL CHECK (tier IN ('terminal', 'strategic', 'enterprise')),
  cost_per_query INT NOT NULL DEFAULT 0 CHECK (cost_per_query >= 0),
  effective_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  effective_to TIMESTAMPTZ NULL,  -- NULL = hala geçerli
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (module_id, tier, effective_from)
);

-- 3. admin_kvkk_mode: Admin Modu Geçişi (strict ↔ lenient) + Audit
-- strict: KVKK sınıfı=yasak → tüm maskeleme, kısıtlı → seçici maskeleme
-- lenient: kısıtlı → açık, yasak → hala maskelenir (risk üstüne alınmış, audit zorunlu)
CREATE TABLE IF NOT EXISTS admin_kvkk_mode (
  admin_kvkk_mode_id SERIAL PRIMARY KEY,
  -- MIGRATE-EXEC-02: `admin_users` tablosu bu semada hic yok; admin kayitlari
  -- `users` tablosunda role='admin' olarak tutuluyor -> UndefinedTable hatasi veriyordu.
  admin_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  mode VARCHAR(10) NOT NULL CHECK (mode IN ('strict', 'lenient')),
  changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  previous_mode VARCHAR(10) NULL,
  reason TEXT NULL,  -- değişim sebebi (audit için)
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_admin_kvkk_admin ON admin_kvkk_mode (admin_id, changed_at DESC);

-- 4. İndeksler (sorgu hızı)
CREATE INDEX IF NOT EXISTS idx_plan_field_group_plan ON plan_field_group (plan);
CREATE INDEX IF NOT EXISTS idx_plan_field_group_group ON plan_field_group (field_group);
CREATE INDEX IF NOT EXISTS idx_module_cost_module ON module_cost (module_id);
CREATE INDEX IF NOT EXISTS idx_module_cost_tier ON module_cost (tier);
CREATE INDEX IF NOT EXISTS idx_module_cost_active ON module_cost (effective_to) WHERE effective_to IS NULL;

-- 5. Başlangıç Verileri

-- 5.1 plan_field_group: 18 satır (6 grup × 3 paket)
-- Kimlik: terminal=açık, strategic=açık, enterprise=açık (hepsi açık)
INSERT INTO plan_field_group (plan, field_group, visibility, visibility_note)
VALUES 
  ('terminal', 'kimlik', 'acik', 'Temel firma kimliği (legal_name, trade_name, registration_number)'),
  ('strategic', 'kimlik', 'acik', 'Temel firma kimliği'),
  ('enterprise', 'kimlik', 'acik', 'Temel firma kimliği'),
  
  -- İletişim: terminal=kısıtlı, strategic=yarı-açık, enterprise=açık
  ('terminal', 'iletisim', 'kisitli', 'Telefon/email maskeli'),
  ('strategic', 'iletisim', 'yarisacik', 'Email domain görünür, telefon kısmi'),
  ('enterprise', 'iletisim', 'acik', 'Tam iletişim'),
  
  -- Lokasyon: terminal=kısıtlı (şehir/ülke), strategic=yarı-açık (adres maskeli), enterprise=açık
  ('terminal', 'lokasyon', 'kisitli', 'Şehir + ülke, tam adres maskeli'),
  ('strategic', 'lokasyon', 'yarisacik', 'İl + İlçe, kapı numarası maskeli'),
  ('enterprise', 'lokasyon', 'acik', 'Tam adres'),
  
  -- Dijital: terminal=kısıtlı, strategic=açık, enterprise=açık
  ('terminal', 'dijital', 'kisitli', 'Website varlığı evet/hayır, domain validation sonucu maskeli'),
  ('strategic', 'dijital', 'acik', 'Website, domain, dijital mevcudiyet'),
  ('enterprise', 'dijital', 'acik', 'Website, domain, dijital mevcudiyet'),
  
  -- Ticari: terminal=yasak, strategic=kısıtlı, enterprise=açık
  ('terminal', 'ticari', 'yasak', 'Ciro/çalışan sayısı görülmez'),
  ('strategic', 'ticari', 'kisitli', 'Ciro range (exact değer maskeli), çalışan range'),
  ('enterprise', 'ticari', 'acik', 'Tam ciro, çalışan sayısı, finansal göstergeler'),
  
  -- Sınai: terminal=kısıtlı, strategic=açık, enterprise=açık
  ('terminal', 'sinai', 'kisitli', 'NACE kodu görünür, detay maskeli'),
  ('strategic', 'sinai', 'acik', 'NACE + sektör tanımı'),
  ('enterprise', 'sinai', 'acik', 'NACE + sektör + endüstri detayları')
ON CONFLICT (plan, field_group) DO NOTHING;

-- 5.2 module_cost: 15 satır (5 modül × 3 tier)
-- Terminal tier
INSERT INTO module_cost (module_id, tier, cost_per_query)
VALUES 
  ('match', 'terminal', 10),
  ('ilan', 'terminal', 0),       -- ilan modülü terminal'de kapalı
  ('analiz', 'terminal', 5),
  ('teklif', 'terminal', 0),     -- teklif modülü terminal'de kapalı
  ('kapasite', 'terminal', 3)
ON CONFLICT (module_id, tier, effective_from) DO NOTHING;

-- Strategic tier
INSERT INTO module_cost (module_id, tier, cost_per_query)
VALUES 
  ('match', 'strategic', 5),
  ('ilan', 'strategic', 3),
  ('analiz', 'strategic', 8),
  ('teklif', 'strategic', 2),
  ('kapasite', 'strategic', 2)
ON CONFLICT (module_id, tier, effective_from) DO NOTHING;

-- Enterprise tier (serbest)
INSERT INTO module_cost (module_id, tier, cost_per_query)
VALUES 
  ('match', 'enterprise', 0),
  ('ilan', 'enterprise', 0),
  ('analiz', 'enterprise', 0),
  ('teklif', 'enterprise', 0),
  ('kapasite', 'enterprise', 0)
ON CONFLICT (module_id, tier, effective_from) DO NOTHING;

-- 6. Kontrol: Tablo veri sayısı doğru mu?
-- SELECT COUNT(*) FROM plan_field_group;  -- 18 beklendi
-- SELECT COUNT(*) FROM module_cost;       -- 15 beklendi
-- SELECT COUNT(*) FROM admin_kvkk_mode;   -- 0 beklendi (veri yok, kontrol tablosu)
