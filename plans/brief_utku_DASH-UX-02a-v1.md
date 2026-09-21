# DASH-UX-02a.v1: Sistem Sekmelerini Dosyada Yaz (SECTIONS Kayıtsız)

## Görev Özeti

`web_dashboard/tabs/admin_sistem.py` dosyasını oluştur. 5 sekmeyi (Cost/Performance/API Analytics/DLQ/Webhook) bir sayfa içinde aynı anda göster.

**Kısıt:** `web_dashboard/tabs/__init__.py`'ye **DOKUNMA**. SECTIONS kaydı v2'de (MENUTREE bitince).

## Bağımlılık

SENTEZ-01 tamamlandıktan sonra başlayabilir.

## Çıktı

1. **Dosya:** `web_dashboard/tabs/admin_sistem.py`
   - 5 sekmeyi Streamlit tab container içinde düzenle
   - Her sekme: veri kaynağı + placeholder + 1 satır açıklama (K2/K3)
   - Durum management (sidebar veya session_state)
   - Sekme değişim animasyonu (fade/slide)
   - **K1 Kalibrasyonu (tanımı + yapı):** Bu görevde bir kez yazılır, raporda detaylandırılır

2. **Stil:** Mevcut `src/company_master/ui/styles.py` kullan

3. **Rapor:** `data/orchestrator/DASH-UX-02a-v1_rapor_<tarih>_utku.md` (D-55 formatı)
   - K1 kalibrasyonunun yapısı, seçimler, eşikler
   - Veri kaynakları ve placeholder stratejileri
   - Test sonuçları

## Testler

```bash
# Local import
python -c "from web_dashboard.tabs.admin_sistem import render_admin_sistem"

# Sekme render mock
pytest tests/test_dash_ux_tabs.py::test_admin_sistem_sekmeleri_v1 -v

# K1 tanımı doğrulama
pytest tests/test_dash_ux_k1_calibration.py::test_k1_definition_v1 -v
```

## Kurallar

- D-55: Rapor 5 başlık zorunlu
- D-183: Dosya adı `_utku` sonekli
- D-184: Rapor'da mimari köprü `[[SENTEZ-01]]`, `[[D-185]]`
- D-57: Başlık standardı
- **D-185 Split:** v1 `__init__.py`'ye hiç dokunmaz

## Sahibi

**UTKU** — SENTEZ-01'den sonra başlama (P1, paralel MENUTREE ile)

## Teslim

```bash
python scripts/gorev_kutusu.py teslim \
  --ajan utku \
  --task-id DASH-UX-02a \
  --ozet "admin_sistem.py: 5 sekme (cost/perf/api_analytics/dlq/webhook), K1 kalibrasyonu tanımı. Tests yeşil. __init__.py'ye dokunulmadi." \
  --cikti "web_dashboard/tabs/admin_sistem.py,tests/test_dash_ux_tabs.py"
```

## Süre Tahmini

4–5 saat (orijinal 8h'dan 3-4h kayıt işi çıkarıldı)
