# GÖREV BRIËFI: UTKU-04 — Veritabanı Migration - Index Optimizasyon

**Atanan:** utku  
**Öncelik:** P1  
**Deadline:** 2026-09-29T23:59:59Z  
**Bağımlılıklar:** yok

## Özet
Veritabanı index'lerini optimize et. Sık sorgulanan kolonlarda composite index'ler oluştur, eski/kötü performans index'lerini kaldır.

## Kabul Kriterleri
1. Migration dosyası yazılmalı (0020_index_optimization.sql)
2. Rollback script hazırlanmalı
3. Query performance ≥30% iyileşme

## Kaynaklar (SSOT)
- src/company_master/schema/migrations/0020_index_optimization.sql
- Query execution plans

## İmplantasyon Notları
- EXPLAIN ANALYZE kullan
- Foreign key constraints kontrol et
- Downtime <1 saat

## Proof-of-Work
File/Output: 0020_index_optimization.sql + rollback + perf_report.json
