# GÖREV BRIËFI: ORCH-03 — Görev Dağıtımı - Load Balancing

**Atanan:** orkestrator  
**Öncelik:** P0  
**Deadline:** 2026-10-01T23:59:59Z  
**Bağımlılıklar:** yok

## Özet
Görevleri worker'lara akıllıca dağıt. CPU/memory load, task priority, worker availability göz önüne alarak load balancing yap. Queue sistemi kur.

## Kabul Kriterleri
1. Load balancer modülü yazılmalı (orchestration/load_balancer.py)
2. Round-robin + weighted strategies uygulanmalı
3. Health check mekanizması

## Kaynaklar (SSOT)
- orchestration/load_balancer.py
- Worker pool management

## İmplantasyon Notları
- Task queue (RabbitMQ/Redis)
- Worker pool executor
- Dynamic scaling logic

## Proof-of-Work
File/Output: orchestration/load_balancer.py + queue implementation + load tests
