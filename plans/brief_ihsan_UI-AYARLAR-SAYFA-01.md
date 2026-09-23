# UI-AYARLAR-SAYFA-01: Kullanıcı Ayarları Sayfası UI Yazma

## Görev Özeti

`web_dashboard/tabs/admin_kullanici_ayarlari.py` dosyasında Kullanıcı Ayarları sayfası UI bileşenlerini yaz. Hesap/Güvenlik/Tercihler 3 bölüm.

## Bağımlılıklar

- ✅ **company_master.ui bileşenler** — Button, Card, MetricCard, stil_enjekte
- ✅ **Streamlit** — st.columns, st.form, st.session_state
- ✅ **Test test_admin_kullanici_ayarlari.py** — mevcut (P2 TEST-AYARLAR-KAPSAM-01)

## Çıktı

1. **UI bileşenleri**:
   - Hesap bölümü: e-posta, profil, kimlik doğrulama
   - Güvenlik bölümü: şifre, iki faktörlü kimlik doğrulama
   - Tercihler bölümü: dil, tema, bildirimler

2. **Kod yapısı**:
   - `web_dashboard/tabs/admin_kullanici_ayarlari.py` yazıldı
   - SECTIONS kaydı güncellendi (admin_kullanici_ayarlari dahil)
   - 9+ test geçiş (test_admin_kullanici_ayarlari.py)

3. **Rapor**:
   - `[[Karar: Kullanıcı ayarları UI merkezi yönetimi]]`
   - `[[Kod: admin_kullanici_ayarlari.py yazma]]`
   - `[[Test: 9 test PASSED]]`

## Kurallar

- **D-55**: Brief dosyası adı `brief_ihsan_UI-AYARLAR-SAYFA-01.md`
- **D-87**: Resmi atama `python scripts/gorev_atama_otomatis.py --task-id UI-AYARLAR-SAYFA-01 --ajan ihsan`
- **Zincir**: ALTYAPI-KILIT-TEMIZLE-01 → UI-AYARLAR-SAYFA-01

## Sahibi

- **Sahip**: İhsan (`ihsan`)
- **Görev Kimliği**: `UI-AYARLAR-SAYFA-01`
- **Öncelik**: P1
- **Pano Durumu**: `aktif`

## Teslim

- Dosya: `web_dashboard/tabs/admin_kullanici_ayarlari.py`
- Testler: `pytest tests/test_admin_kullanici_ayarlari.py -v` — 9+ yeşil
- Rapor dosyası: `data/orchestrator/UI-AYARLAR-SAYFA-01_rapor_YYYY-MM-DD_ihsan.md`

## Süre Tahmini

- **UI yazma + bileşen entegrasyonu**: ~1 saat

## Tetik Zinciri

Sonraki: **Utku'nun kendi görevleri** (UI-ADOPT-01 → CHART-KATEGORI-02 → TEST-DASHBOARD-REGRESYON-01).
