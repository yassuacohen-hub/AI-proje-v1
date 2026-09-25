-- Migration 0001 down: Uzantılar ve çekirdek tabloları geri al
-- Migration 0001_core.sql'in tersidir

-- Önce verileri temizle (FK constraint'ler için)
DELETE FROM osbs WHERE name IN (
    'OSTİM OSB', 'İvedik OSB', 'ASO 1. OSB', 'ASO 2-3 OSB',
    'Başkent OSB', 'HAB OSB (Havaalanı)', 'Dökümcüler OSB',
    'Anadolu OSB', 'Polatlı OSB'
);

-- Tabloları sil (FK dependency sırasına göre)
DROP TABLE IF EXISTS source_records;
DROP TABLE IF EXISTS sources;
DROP TABLE IF EXISTS quarantine_firms;
DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS osbs;

-- Extensions (dikkat: diğer veritabanları etkilenebilir, sadece bu migration'un eklediği varsayıyorum)
-- DROP EXTENSION IF EXISTS pg_trgm;
-- DROP EXTENSION IF EXISTS pgcrypto;

-- Not: Extensions drop edilmez, diğer migration'lar kullanıyor olabilir
-- Sadece bu migration'un oluşturduğu objeler silinir