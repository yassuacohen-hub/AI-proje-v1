# GÖREV BRIËFI: ORCH-04 — Hata Toleransı - Retry Mekanizması

**Atanan:** orkestrator  
**Öncelik:** P1  
**Deadline:** 2026-10-02T23:59:59Z  
**Bağımlılıklar:** yok

## Özet
Başarısız görevler için retry mekanizması kur. Exponential backoff, max retry limiti, dead-letter queue ile hata yönetimi sağla.

## Kabul Kriterleri
1. Retry handler modülü yazılmalı (orchestration/retry_handler.py)
2. Exponential backoff stratejisi
3. Dead-letter queue entegrasyonu

## Kaynaklar (SSOT)
- orchestration/retry_handler.py
- Error handling patterns

## İmplantasyon Notları
- Jitter for thundering herd
- Circuit breaker pattern
- Error classification

## Proof-of-Work
File/Output: orchestration/retry_handler.py + circuit breaker + failure mode tests
