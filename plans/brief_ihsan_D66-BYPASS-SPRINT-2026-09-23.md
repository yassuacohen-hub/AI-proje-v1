# Brief: İhsan — D-66 Bypass (SPRINT 2026-09-23)

## Görev: D-66 BYPASS — Tetikleme Bypass Mekanizması

**Status:** plan → aktif  
**Başlama:** 2026-09-23T13:00:00Z  
**Hedef:** Acil tetikleme bypass (override) mekanizması kurgusu

---

## Sorun Tanımı
- Tetik_senk cron zamanlayıcısı saat uyuşmazlığı
- 14 sapma gözlendi (hata log'unda)
- Manual override gerekli (D-66)
- UTKU test görevleri bekliyor (TEST-ADMIN-PERF-01 başlayamıyor)
- YASU altyapı görevleri zarflı (ACİL TRIGGER-LOGGING, 30 min)

---

## Çözüm (D-66)

### 1. Bypass Flag Ekle
```python
# scripts/tetik_senk.py
--bypass-override: Force trigger now (skip cron check)
--bypass-reason: "D-66 — Saat uyuşmazlığı 2026-09-23"
```

**Dosya:** [`scripts/tetik_senk.py`](Huginn Data Insights/scripts/tetik_senk.py:1)

### 2. Logging Güçlendir
```python
# src/company_master/orchestrator/trigger.py
logger.info(f"D-66 bypass tetikleme: reason={bypass_reason}, timestamp={now()}")
```

**Dosya:** [`src/company_master/orchestrator/trigger.py`](Huginn Data Insights/src/company_master/orchestrator/trigger.py:1)

### 3. Durum Kaydı
- task_board.json → D-66 bypass tetiklemesi kaydı
- tetik_senk_log.jsonl → bypass event

---

## Adımlar (15 min)

1. **bypass-override** flag ekle (5 min)
2. **Logging** ekle (5 min)
3. **test_d190_mimir_rapor.py** regresyon check (5 min)

**Toplam:** 15 min

---

## Teslim Kriteri
- ✅ bypass flag aktif
- ✅ logging kaydı açık
- ✅ test geçmiş (regresyon yok)
- ✅ task_board.json güncellendi

---

## Bağlantılar
- YASU ACİL TRIGGER-LOGGING-CLEANUP: [`brief_yasu_SPRINT-2026-09-23-ALTYAPI-GOREVLER.md`](Huginn Data Insights/plans/brief_yasu_SPRINT-2026-09-23-ALTYAPI-GOREVLER.md)
- UTKU TEST-ADMIN-PERF-01: [`brief_utku_SPRINT-2026-09-23-TEST-GOREVLER.md`](Huginn Data Insights/plans/brief_utku_SPRINT-2026-09-23-TEST-GOREVLER.md)

---

## İletişim
- Acil sorun? → Orchestrator kontrol
- Bypass log: `tetik_senk_log.jsonl`
