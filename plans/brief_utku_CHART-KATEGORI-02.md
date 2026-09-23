# CHART-KATEGORI-02: KATEGORI_RENK ↔ KATEGORILER Uyumlaştırması

## Görev Özeti

`web_dashboard/charts.py` dosyasında iki paralel kategori sistemi birleştirilecek:
- Satır 39-47: `KATEGORI_RENK: dict[str, str]` — 12 kategori rengi
- İmplisit/dağınık: `KATEGORILER` — mevcut kategori listesi (başka yerde tanımlanmış veya kullanımda çıkıyor)

Amaç: Tek, otoriter kategori listesi + renk haritalanması. Kod tekrarı ve bakım yükü azalacak.

## Bağımlılıklar

- ✅ **web_dashboard/charts.py** — KATEGORI_RENK satır 39-47 (mevcut)
- ✅ **Kategori kullanan dosyalar**: admin_api_analytics.py (satır 121-128), admin_performance.py (satır 121-125)
- ✅ **UI-ADOPT-01** (önceki) — tamamlandı (P1, beklemede)

## Çıktı

1. **Kod değişiklikleri**:
   - `KATEGORILER` canonic tanımını web_dashboard/charts.py satır 39'da merkezi hale getir
   - `KATEGORI_RENK` ve `KATEGORILER` tek yapı olarak birleştir (dict veya namedtuple)
   - Tüm kategori referanslarını bu merkezi tanımdan al

2. **Regresyon koruması**:
   - `pytest tests/ -q` — tüm testler yeşil (0 fail)
   - admin_api_analytics.py + admin_performance.py kategori kullanımı sağlamlaşacak

3. **Rapor**:
   - `[[Karar: Kategori sistemi merkezi standartlaştırması]]`
   - `[[Kod: web_dashboard/charts.py KATEGORI_RENK + KATEGORILER birleşimi]]`
   - `[[Test: pytest tests/ -q tüm yeşil]]`

## Kurallar

- **D-55**: Brief dosyası adı `brief_utku_CHART-KATEGORI-02.md` (ajan soneki `_utku`)
- **D-184**: Karar/Kod/Test wikilink'leri yukarıda verilmiştir
- **D-87**: Resmi atama sadece `python scripts/gorev_atama_otomatis.py --task-id CHART-KATEGORI-02 --ajan utku` ile yapılacak
- **Zincir**: UI-ADOPT-01 → CHART-KATEGORI-02 → (sonrası TBD)

## Sahibi

- **Sahip**: Utku (`utku`)
- **Görev Kimliği**: `CHART-KATEGORI-02`
- **Öncelik**: P2
- **Pano Durumu**: `beklemede` (atama tamamlanınca `aktif` olacak)

## Teslim

- Dosya: `web_dashboard/charts.py`
- Testler: `pytest tests/ -q` tüm yeşil
- Rapor dosyası: `data/orchestrator/CHART-KATEGORI-02_rapor_YYYY-MM-DD_utku.md`

## Süre Tahmini

- **Kod birleştirme**: ~20 min (refactor + test)
- **Toplam**: ~20 min (P2, hızlı)

## Tetik Zinciri

Sonraki görev: **TEST-DASHBOARD-REGRESYON-01** (tüm dashboard testleri kontrol, 8 kırık + 71 kayıp test araştırması).
