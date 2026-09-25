-- Migration 0002 down: Şirket ilişki tablolarını geri al
-- Migration 0002_relations.sql'in tersidir

-- FK dependency sırasına göre ters sırada sil
DROP TABLE IF EXISTS company_contacts;
DROP TABLE IF EXISTS company_products;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS product_categories;
DROP TABLE IF EXISTS company_industries;
DROP TABLE IF EXISTS company_locations;
DROP TABLE IF EXISTS nace_codes;
DROP TABLE IF EXISTS company_identifiers;
DROP TABLE IF EXISTS company_names;
DROP TABLE IF EXISTS company_locations;
DROP TABLE IF EXISTS nace_codes;
DROP TABLE IF EXISTS company_industries;

-- Not: company_contacts, company_products, products, product_categories,
-- company_industries, company_locations, nace_codes, company_identifiers,
-- company_names tabloları 0001_core.sql'in companies, osbs, sources tablolarına
-- FK bağımlılığına sahip, bu yüzden önce silinmeli.