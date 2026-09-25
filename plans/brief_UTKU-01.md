# GÖREV BRIËFI: UTKU-01 — Veri Şeması Doğrulama - Core Modülü

**Atanan:** utku  
**Öncelik:** P0  
**Deadline:** 2026-09-30T23:59:59Z  
**Bağımlılıklar:** yok

## Özet
Core modülü için veri şeması doğrulama sistemi oluştur. Gelen veri tiplerini ve yapılarını kontrol et, hatalı formatları reddet ve detaylı hata mesajları döndür.

## Kabul Kriterleri
1. Schema validator modülü oluşturulmalı (src/core/schema_validator.py)
2. 5+ veri tipi için test case'leri yazılmalı
3. Hata mesajları JSON formatında döndürülmeli

## Kaynaklar (SSOT)
- src/core/schema_validator.py
- Huginn Data Insights/AGENTS.md:D-48

## İmplantasyon Notları
- Pydantic kullan (stdlib alternatif)
- Type hints zorunlu
- Performans: <50ms/validation

## Proof-of-Work
File/Output: src/core/schema_validator.py + test coverage ≥80%
