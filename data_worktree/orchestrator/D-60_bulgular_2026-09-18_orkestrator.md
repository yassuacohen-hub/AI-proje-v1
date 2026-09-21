[[Huginn Data Insights/data/orchestrator/D-60_bulgular_2026-09-18_orkestrator.md]]

# D-60/D-61 Ad Geçişi — Kapsam Dışı Bulgular

Tarih: 2026-09-18 · Rol: orkestratör

## Özet

| # | Bulgu | Renk | Durum |
|---|-------|------|-------|
| B-1 | `nobetci.py` ajan adını normalize etmiyordu | 🔴 | ✅ düzeltildi (kapsam içi) |
| B-2 | `musteri_yonetimi.py` 5 adet `st.subheader` bırakmış | 🟡 | ⏳ düzeltilmedi (kapsam dışı) |
| B-3 | `webhook_monitor.py` artık `st.metric` çağırmıyor, testi bayat | 🟡 | ⏳ düzeltilmedi (kapsam dışı) |

---

## B-1 — Normalize sızıntısı (düzeltildi)

`src/company_master/orchestrator/nobetci.py` tetik dosyası yolunu **ham** ajan adıyla kuruyordu:

```python
dosya = _data_dir(data_dir) / "triggers" / f"{ajan}.ALARM.json"   # satır 67
yol   = _data_dir(data_dir) / "triggers" / f"{ajan}.jsonl"        # satır 136
```

`trigger.tetik_ekle` ise `ajan_normalize()` uyguluyor. Sonuç: `kilo` ile yazılan kayıt
`utku.jsonl`'a düşüyor, nöbetçi `kilo.jsonl` arıyor → 7 test `assert 0 == 1`.

**Düzeltme:** `ajan_normalize` import edildi, iki yol `f"{ajan_normalize(ajan) or ajan}..."` oldu.
`tests/test_gorev_nobetci.py` içindeki `"kilo"` → `"utku"`. **17/17 yeşil.**

**Ders:** tetik dosya yolu kuran **her** nokta `ajan_normalize()` çağırmalı. Bu bir sınıf hatası;
benzer noktalar taranmalı (`TEST-NORMALIZE-TARAMA-01` önerilir).

---

## B-2 — `musteri_yonetimi.py` subheader kalıntısı

```
FAILED tests/test_sayfa_iskeleti.py::test_ekranda_subheader_kalmaz[musteri_yonetimi]
AssertionError: musteri_yonetimi: 5 adet `st.subheader` kaldı.
```

ADMIN-UI-10 sayfa iskeleti dönüşümü yarım kalmış. 5 `st.subheader` → `Section` olmalı.
Ad geçişiyle **ilgisiz**, önceden vardı.

Önerilen görev: `[UI] Subheader'ları Section'a taşı → web_dashboard/tabs/musteri_yonetimi.py (30d)`

---

## B-3 — `webhook_monitor` testi bayat

```
FAILED tests/test_webhook_monitor_tab.py::test_render_webhook_monitor_tab_renders_metrics
assert metric.called → False
```

`ADMIN-KPI-KART-02` görevinde tüm `st.metric` çağrıları `kpi_karti` ile değiştirildi.
Test hâlâ `st.metric` mock'unun çağrıldığını bekliyor. **Test bayat, kod doğru.**

Önerilen görev: `[TEST] Metric mock'unu kpi_karti'na çevir → tests/test_webhook_monitor_tab.py (30d)`

---

## Kapı durumu

| Kapı | Sonuç |
|------|-------|
| `python scripts/kodlama_denetim.py` | 🟢 temiz |
| `pytest tests/test_gorev_nobetci.py -q` | 🟢 17 passed |
| `pytest -q` (tam süit) | 🟡 2 failed / 3911 passed — ikisi de yukarıdaki B-2, B-3 |
