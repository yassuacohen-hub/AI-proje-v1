# TEST-DASHBOARD-REGRESYON-01: Dashboard Test Regresyonu Araştırması

## Görev Özeti

Rebase sonrası dashboard testlerinde 8 kırık + 71 kayıp test tespit edildi. Kök nedenleri araştırıp düzeltmeleri apply etmek.

## Bağımlılıklar

- ✅ **Git rebase** — tamamlandı (chore/monorepo-merge)
- ✅ **CHART-KATEGORI-02** (önceki) — kategori sistemi birleştirilecek (P2)
- ✅ **Test dosyaları**: `tests/test_dashboard_nav.py`, `tests/test_dash_ux_tabs.py`, vb.

## Çıktı

1. **Kök neden analizi**:
   - 8 kırık test — hangi dosyalarda, neden (import hata / state yönetimi / mock sorunu)
   - 71 kayıp test — hangi dosyalar test edilemiyor, neden

2. **Düzeltmeler**:
   - Kırık testler için fix commit
   - Kayıp test dosyalarını tekrar aktifleştir
   - `pytest tests/ -q` → tüm yeşil (0 fail, 0 xfail, minimal skip)

3. **Rapor**:
   - `[[Karar: Dashboard test regresyonu kök neden belirleme]]`
   - `[[Kod: tests/ dizininde kırık/kayıp test düzeltmeleri]]`
   - `[[Test: pytest tests/ -q 179/179 PASSED]]`

## Kurallar

- **D-55**: Brief dosyası adı `brief_utku_TEST-DASHBOARD-REGRESYON-01.md`
- **D-184**: Karar/Kod/Test wikilink'leri yukarıda
- **D-87**: Resmi atama `python scripts/gorev_atama_otomatis.py --task-id TEST-DASHBOARD-REGRESYON-01 --ajan utku`
- **Zincir**: CHART-KATEGORI-02 → TEST-DASHBOARD-REGRESYON-01

## Sahibi

- **Sahip**: Utku (`utku`)
- **Görev Kimliği**: `TEST-DASHBOARD-REGRESYON-01`
- **Öncelik**: P1
- **Pano Durumu**: `beklemede`

## Teslim

- Testler: `pytest tests/ -q` — tüm yeşil
- Rapor dosyası: `data/orchestrator/TEST-DASHBOARD-REGRESYON-01_rapor_YYYY-MM-DD_utku.md`

## Süre Tahmini

- **Kök neden analizi**: ~30 min
- **Düzeltmeler**: ~45 min
- **Toplam**: ~1 saat (P1, kritik)

## Tetik Zinciri

Sonraki: **AGENTS.md UU merge çakışması** (kütüphaneci/orchestrator) — kullanıcı onayı gerekli.
