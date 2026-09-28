-- Migration 0017: user_activity_log (VERI-ADMIN-AKTIVITE-LOG-13)
-- SSOT §8.4 EK BULGU-8 + §10 sira 3: giris/arama/AI kullanim logu DB'de hic yoktu.
-- K1 Churn 3-sinyal, K9 Arama Boslugu, G4 gercek DAU bu tabloya bagli.
-- KVKK: SSOT §11 KK-10 (1B) — ip_adresi 30 gun ham, sonra /24 maskeleme (AYRI gorev).
--       ulke_kodu suresiz. KK-11 (2A): son kullanici olaylari burada, admin eylemleri admin_audit'te.
-- Yalnizca sema acar; veri yazmaz (yazma isi API-ADMIN-AKTIVITE-YAZ-14).
-- Geri alma: down/0017_user_activity_log.sql
--
-- D-254 / 0027: ip_adresi -> ip_address oldu (D-251/1; audit_logs.ip_address emsali).
-- Tablonun diger izleri gecerli, dosya bazli isaret kullanilmiyor.
-- dusen-iz: user_activity_log.ip_adresi
CREATE TABLE IF NOT EXISTS user_activity_log (
  id          BIGSERIAL PRIMARY KEY,
  user_id     UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  olay_tipi   VARCHAR(20) NOT NULL CHECK (olay_tipi IN ('giris', 'arama', 'ai_kullanim')),
  olay_zamani TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  detay       JSONB NULL,                -- arama terimi, sonuc adedi vb.
  basarili    BOOLEAN NOT NULL DEFAULT TRUE,
  ip_adresi   INET NULL,                 -- ham IP; 30 gun sonra /24 maskelenir (yerinde UPDATE)
  ulke_kodu   CHAR(2) NULL               -- ISO 3166-1 alpha-2
);
CREATE INDEX IF NOT EXISTS idx_activity_user_zaman ON user_activity_log (user_id, olay_zamani DESC);
CREATE INDEX IF NOT EXISTS idx_activity_tip_zaman ON user_activity_log (olay_tipi, olay_zamani DESC);
