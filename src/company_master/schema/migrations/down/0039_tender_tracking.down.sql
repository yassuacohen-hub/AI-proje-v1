-- Migration 0039 down: Tender/Ihale tracking tables drop

DROP TABLE IF EXISTS ihale_takip;
DROP TABLE IF EXISTS ihale_ekler;
DROP TABLE IF EXISTS ihale_katilimcilar;
DROP TABLE IF EXISTS ihale_ilanlari;
DROP TABLE IF EXISTS ihale_ilgilendirme_alanlari;
DROP TABLE IF EXISTS ihale_kaynaklari;

-- Indexler tablolarla birlikte silinir