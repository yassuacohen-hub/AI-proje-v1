# RESEARCH-PONYTALE — Orkestratör Brief

**Görev:** Ponytail pattern araştırması  
**Ajan:** ihsan (Orkestratör)  
**Öncelik:** P0  
**Tarih:** 2026-09-22

## Özet

Gece zinciri sırasında görevler arasında veri taşıması (ponytail: bir görevin çıktısı sonrakine giriş olması) nasıl uygulanmalı? Posta kutusu (`data/orchestrator/triggers/{ajan}.jsonl`) talimat/çıktı mekanizmasının tasarımını araştır, best practice tanımla.

## Adımlar

1. **Mevcudu oku:** `trigger.py:teslim_et()` (satır 236-284) — çıktılar nasıl tutulmuş? `ciktilar` parametresi var mı?
2. **Posta kutusu şeması:** `_tetikleri_oku()`, `_tetikleri_yaz()` fonksiyonlarını inceле — tetik kaydında ne saklanabilir?
3. **Zincir çıktısı:** `zincir_devam_et()` sonraki göreve veri aktarıyor mu? Yoksa sadece tetik mi düşüyor?
4. **Design karar:** Çıktı şeması nedir? (JSON field, dosya path, embedding mi?)
5. **Teslim Not:** Araştırma bulguları, ponytail pattern için öneride bulunulan uygulamalar.

## Dosyalar

- `Huginn Data Insights/src/company_master/orchestrator/trigger.py` (referans)
- `Huginn Data Insights/data/orchestrator/triggers/` (örnek tetik dosyaları)

## Gözlemler

- `teslim_et()` `ciktilar: dict | None = None` parametresi alıyor — bu asıl ponytail mekanizması mı?
- Sonraki tetikler mevcut çıktılara erişebiliyor mu, yoksa sadece dosya yolları mı tutmuş?

**Teslim:** Ponytail pattern analizi, tetikler arası veri taşıması nasıl çalışıyor, best practice önerisi.
