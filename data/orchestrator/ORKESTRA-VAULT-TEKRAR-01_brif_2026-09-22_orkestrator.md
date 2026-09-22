# ORKESTRA-VAULT-TEKRAR-01 — Orkestratör Brief

**Görev:** Vault mekanizması gözden geçir  
**Ajan:** ihsan (Orkestratör)  
**Öncelik:** P2  
**Tarih:** 2026-09-22

## Özet

Gece zinciri boyunca görev çıktıları ve geçici veriler nereye saklanıyor? Vault mekanizması şu anda net değil. Tasarımı gözden geçir, gerekli iyileştirmeleri tanımla.

## Adımlar

1. **Mevcudu oku:**
   - `Huginn Data Insights/data/orchestrator/` altında vault/cache dizinleri var mı?
   - `trigger.py` çıktı tutma mekanizmasını kontrol et (`ciktilar` parametresi).
   - Geçici dosyalar nerede? (`data/_tmp/`, `.kilo/`, `.roo/` gibi).

2. **Akış:** Görev çıktısı → hangi aj ana → sonraki görevden erişilebilir mi?

3. **Sorunlar:** Stale dosyalar var mı? Kilit süresi sınırlı mı? Disk space?

4. **Öneriler:** Vault mekanizması için best practice önerileri yaz.

5. **Teslim Not:** Mevcut durum, sorunlar, öneride bulunulan iyileştirmeler.

## Dosyalar

- `Huginn Data Insights/src/company_master/orchestrator/trigger.py` (referans)
- `Huginn Data Insights/data/orchestrator/` (audit)
- `Huginn Data Insights/data/_tmp/` (geçici veriler)

## Gözlemler

- Vault P2 işaretli — kritik değil ama gerekli.
- Çıktı saklama: JSON, dosya path, embedding mi?

**Teslim:** Vault mekanizması analizi, mevcut sorunlar, improvement önerileri.
