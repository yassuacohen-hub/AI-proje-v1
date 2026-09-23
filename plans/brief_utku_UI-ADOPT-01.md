# UI-ADOPT-01: kpi_karti() → MetricCard Bileşen Benimsemesi

## Görev Özeti

Üç admin sekme dosyasında (`admin_auto_refresh.py`, `admin_api_analytics.py`, `admin_performance.py`) eski `web_dashboard.charts.kpi_karti()` fonksiyon çağrılarını yeni resmi `company_master.ui.MetricCard` bileşenine geçirmek. DASH-UX-01 renk kodlaması uygulanacak, tüm testler yeşil kalacak.

## Bağımlılıklar

- ✅ **MetricCard bileşen tanımı**: `src/company_master/ui/components/card.py` satır 88-178 — resmi/hazır
- ✅ **Eski kpi_karti() API**: `web_dashboard/charts.py` satır 405-445 — mevcut (temizleme aşamasında veri göçü için referans)
- ✅ **3 hedef dosya**:
  - `web_dashboard/tabs/admin_auto_refresh.py` (159 satır, kpi_karti() henüz KULLANMIYOR — safety check/noop)
  - `web_dashboard/tabs/admin_api_analytics.py` (229 satır, kpi_karti() YOĞUN — satır 121-128, 191-198)
  - `web_dashboard/tabs/admin_performance.py` (251 satır, kpi_karti() YOĞUN — satır 121-125, 136-141, 152-157, 189)

## Çıktı

1. **Kod değişiklikleri**:
   - `admin_api_analytics.py`: `kpi_karti()` çağrıları → `MetricCard()` bileşen render'ı
   - `admin_performance.py`: `kpi_karti()` çağrıları → `MetricCard()` bileşen render'ı
   - `admin_auto_refresh.py`: İnceleme ve safety check (mevcut durumda kpi_karti yok, test regresyonu kontrolü)

2. **Import güncellemeleri**:
   - `from company_master.ui import MetricCard` eklenmeli
   - Gerekirse eski `from web_dashboard.charts import kpi_karti` silinmeli

3. **Test çalıştırması**:
   - `pytest tests/ -q` — tüm testler yeşil (0 fail, 0 xfail)
   - Hedef dosyalarla ilgili test regresyonu yok

4. **Rapor**:
   - `[[Karar: UI bileşen standartlaştırması — MetricCard evrenselleştirme]]`
   - `[[Kod: admin_api_analytics.py / admin_performance.py kpi_karti geçişi]]`
   - `[[Test: pytest tests/ -q tüm yeşil]]`

## Kurallar

- **D-55**: Bu brief dosyası adı `brief_utku_UI-ADOPT-01.md` (ajan soneki `_utku`)
- **D-184**: Karar/Kod/Test wikilink'leri yukarıdaki Çıktı (Rapor) bölümünde verilmiştir
- **D-87**: Resmi atama sadece `python scripts/gorev_atama_otomatis.py --task-id UI-ADOPT-01 --ajan utku` ile yapılacak
- **Regresyon koruması**: Tüm testler yeşil kalmalı; `admin_auto_refresh.py` henüz kpi_karti kullanmadığı için noop olacak

## Sahibi

- **Sahip**: Utku (`utku`)
- **Görev Kimliği**: `UI-ADOPT-01`
- **Öncelik**: P1
- **Pano Durumu**: `beklemede` (atama tamamlanınca `aktif` olacak)

## Teslim

- Dosyalar: `web_dashboard/tabs/admin_auto_refresh.py`, `web_dashboard/tabs/admin_api_analytics.py`, `web_dashboard/tabs/admin_performance.py`
- Testler: `pytest tests/ -q` tüm yeşil
- Rapor dosyası: `data/orchestrator/UI-ADOPT-01_rapor_YYYY-MM-DD_utku.md` (orkestratör tarafından sonra oluşturulacak)

## Süre Tahmini

- **Kod geçişi**: ~30 min (kpi_karti çağrılarının say ve eşleştirilmesi, MetricCard yapı dönüşümü)
- **Test ve doğrulama**: ~15 min
- **Toplam**: ~45 min (P1 ivedilik)

## Tetik Zinciri

Sonraki görev: **P2 kategori sistemi birleştirme** (`web_dashboard/charts.py` satır 39-47 `KATEGORI_RENK` ↔ `KATEGORILER` uyumlaştırması).
