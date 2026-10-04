-- 0037 geri alma.
-- KVKK gorusu (KVKK-TCKN-02) aksi yonde gelirse event_person/person_role
-- bu dosya ile dusurulur; veri kalmaz.

BEGIN;

DROP INDEX IF EXISTS uq_company_events_source_guid;

ALTER TABLE company_events
    DROP COLUMN IF EXISTS person_role,
    DROP COLUMN IF EXISTS event_person,
    DROP COLUMN IF EXISTS source_guid;

ALTER TABLE companies
    DROP COLUMN IF EXISTS son_teyit_tarihi;

COMMIT;
