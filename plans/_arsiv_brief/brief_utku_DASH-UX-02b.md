# DASH-UX-02b: Tek Sayfa İçinde 4 Sekmeyi Yönet

## Görev Özeti
`web_dashboard/tabs/admin_yonetim.py` dosyasını oluştur veya genişlet. DASH-UX-02a'dan farklı olarak, 4 sekmeyi (Admin Paneli, Kullanıcı Yönetimi, Sistem Kaydı, Raporlar) bir sayfa içinde aynı anda göster. Sekme değişim animasyonu ve durum saklaması.

## Bağımlılık
Bu görev **SENTEZ-01** ve **DASH-UX-02a** tamamlandıktan sonra başlayabilir:
- SENTEZ-01: Mimari sentez raporu (bileşen hiyerarşisi)
- DASH-UX-02a: Bireysel sekme UI'ları (yeniden kullanılacak)

## Çıktı
1. **Dosya:** `web_dashboard/tabs/admin_yonetim.py`
   - 4 sekmeyi Streamlit tab container içinde düzenle
   - Durum management (sidebar veya session_state)
   - Sekme değişim animasyonu (fade veya slide)

2. **Stil:** Mevcut `src/company_master/ui/styles.py` kullan

3. **Rapor:** `data/orchestrator/DASH-UX-02b_rapor_<tarih>_utku.md` (D-55 formatı)

## Testler
```bash
# Sekme yapısı doğrulaması
python -c "import web_dashboard.tabs; g=web_dashboard.tabs.__dict__; assert 'admin_yonetim' in str(g)"

# Render testi (fake streamlit context)
pytest tests/test_dash_ux_tabs.py::test_admin_yonetim_sekmeleri -v
```

## Kurallar
- D-55: Rapor 5 başlık zorunlu
- D-183: Dosya adı `_utku` sonekli
- D-184: Rapor'da mimari köprü `[[SENTEZ-01]]` `[[DASH-UX-02a]]`
- D-57: Başlık standardı `[UI] N sekmeyi bir sayfada yönet → web_dashboard/tabs/admin_yonetim.py (2s)`

## Sahibi
**UTKU** — manuel onay (P1)

## Teslim
```bash
python scripts/gorev_kutusu.py teslim \
  --task-id DASH-UX-02b \
  --rapor data/orchestrator/DASH-UX-02b_rapor_2026-09-21_utku.md
```

## Başlama
Bağımlılıklar çözüldükten sonra otomatik tetiklenecek (zincir kuralı).
