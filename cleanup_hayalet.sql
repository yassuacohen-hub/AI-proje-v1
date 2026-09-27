-- VERI-HAYALET-TEMIZ-01: Tam temizlik (tek transaction)
-- 1. Keeper ID'lerini belirle (her legal_name için en eski company_id)
-- 2. Tüm FK tablolarını batch güncelle
-- 3. Hayalet kayıtları tek seferde sil
-- 4. UNIQUE INDEX oluştur

BEGIN;

-- Geçici tablo: her legal_name için keeper (en eski company_id)
CREATE TEMP TABLE tmp_keeper AS
SELECT legal_name, MIN(company_id::text)::uuid as keeper_id
FROM companies
GROUP BY legal_name
HAVING COUNT(*) > 1;

-- Geçici tablo: silinecek duplikatlar
CREATE TEMP TABLE tmp_dupes AS
SELECT c.company_id, c.legal_name
FROM companies c
JOIN tmp_keeper k ON c.legal_name = k.legal_name
WHERE c.company_id != k.keeper_id;

-- 1. company_industries güncelle
UPDATE company_industries ci
SET company_id = k.keeper_id
FROM tmp_dupes d
JOIN tmp_keeper k ON d.legal_name = k.legal_name
WHERE ci.company_id = d.company_id;

-- 2. source_records güncelle (source_id -> company_id join)
UPDATE source_records sr
SET source_id = k.keeper_id
FROM tmp_dupes d
JOIN tmp_keeper k ON d.legal_name = k.legal_name
WHERE sr.source_id = d.company_id;

-- 3. company_identifiers güncelle
UPDATE company_identifiers ci
SET company_id = k.keeper_id
FROM tmp_dupes d
JOIN tmp_keeper k ON d.legal_name = k.legal_name
WHERE ci.company_id = d.company_id;

-- 4. company_locations güncelle
UPDATE company_locations cl
SET company_id = k.keeper_id
FROM tmp_dupes d
JOIN tmp_keeper k ON d.legal_name = k.legal_name
WHERE cl.company_id = d.company_id;

-- 5. company_contacts güncelle
UPDATE company_contacts cc
SET company_id = k.keeper_id
FROM tmp_dupes d
JOIN tmp_keeper k ON d.legal_name = k.legal_name
WHERE cc.company_id = d.company_id;

-- 6. company_products güncelle
UPDATE company_products cp
SET company_id = k.keeper_id
FROM tmp_dupes d
JOIN tmp_keeper k ON d.legal_name = k.legal_name
WHERE cp.company_id = d.company_id;

-- 7. entity_resolution güncelle
UPDATE entity_resolution er
SET company_id = k.keeper_id
FROM tmp_dupes d
JOIN tmp_keeper k ON d.legal_name = k.legal_name
WHERE er.company_id = d.company_id;

-- 8. job_postings güncelle
UPDATE job_postings jp
SET company_id = k.keeper_id
FROM tmp_dupes d
JOIN tmp_keeper k ON d.legal_name = k.legal_name
WHERE jp.company_id = d.company_id;

-- 9. Hayalet kayıtları sil (tek seferde)
DELETE FROM companies
WHERE company_id IN (SELECT company_id FROM tmp_dupes);

-- 9. UNIQUE INDEX oluştur
CREATE UNIQUE INDEX uq_companies_legal_name ON companies(legal_name);

-- Temizlik
DROP TABLE tmp_keeper;
DROP TABLE tmp_dupes;

COMMIT;