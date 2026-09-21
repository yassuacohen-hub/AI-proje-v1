# DASH-UX-02a: Tek Sayfa İçinde 5 Sistem Sekmesini Yönet

## Görev Özeti
`web_dashboard/tabs/admin_sistem.py` dosyasını oluştur. 5 sekmeyi (Cost/Performance/API Analytics/DLQ/Webhook) bir sayfa içinde aynı anda göster. Sekme değişim animasyonu, durum saklaması, **K1 kalibrasyonu bu görevde yapılır** ve DASH-UX-02b aynı kalibrasyonu uygular.

## Bağımlılık
Bu görev **SENTEZ-01** tamamlandıktan sonra başlayabilir:
- SENTEZ-01: Mimari sentez raporu (bileşen hiyerarşisi, veri kaynakları)

## Çıktı
1. **Dosya:** `web_dashboard/tabs/admin_sistem.py`
   - 5 sekmeyi Streamlit tab container içinde düzenle (Cost/Performance/API Analytics/DLQ/Webhook)
   - Her sekme: veri kaynağı + boş-veri placeholder + 1 satır açıklama (K3)
   - Durum management (sidebar veya session_state)
   - Sekme değişim animasyonu (fade veya slide)
   - **K1 Kalibrasyonu:** İlk kez bu dosyada tanımlanır (yapısı, ölçümler, limitler), DASH-UX-02b'ye aktarılır

2. **Stil:** Mevcut `src/company_master/ui/styles.py` kullan

3. **Rapor:** `data/orchestrator/DASH-UX-02a_rapor_<tarih>_utku.md` (D-55 formatı)
   - K1 kalibrasyonunun detayları (yapı, eşikler, test sonuçları)
   - Veri kaynakları ve placeholder stratejileri
   - Alt-sekme yapısı (varsa)

## Testler
```bash
# Sekme yapısı doğrulaması
python -c "import web_dashboard.tabs; g=web_dashboard.tabs.__dict__; assert 'admin_sistem' in str(g)"

# Render testi (fake streamlit context)
pytest tests/test_dash_ux_tabs.py::test_admin_sistem_sekmeleri -v

# K1 kalibrasyonu doğrulama
pytest tests/test_dash_ux_k1_calibration.py -v
```

## Kurallar
- D-55: Rapor 5 başlık zorunlu (Özet, Çıktı, Testler, Riskler, İlk Adımlar)
- D-183: Dosya adı `_utku` sonekli
- D-184: Rapor'da mimari köprü `[[SENTEZ-01]]`
- D-57: Başlık standardı `[DASH-UX] DASH-UX-02a: 5 sistem sekmesini tek 'admin_sistem.py' icinde birlest`
- **K1/K2/K3/K5:** 
  - K1 = Kalibrasyonu bu görevde yapılır (K2 = tekrar etmez; K5 = test)
  - K2 = Veri kaynağı + placeholder (dikey dilim)
  - K3 = 1 satır açıklama per grafik
  - K5 = Test birlikte gelsin

## Sahibi
**UTKU** — SENTEZ-01'den sonra manuel başlama (P1)

## Teslim
```bash
python scripts/gorev_kutusu.py teslim \
  --task-id DASH-UX-02a \
  --rapor data/orchestrator/DASH-UX-02a_rapor_2026-09-21_utku.md
```

## Başlama
Bağımlılıklar (SENTEZ-01) çözüldükten sonra başla.

## D-85 Notu (Seri Uygulanma Stratejisi)
Bu görev ve DASH-UX-02b aynı sahip (UTKU) tarafından seri yapılır:
1. DASH-UX-02a: 5 sistem sekmesi + K1 kalibrasyonu (ilk kez)
2. DASH-UX-02b: 4 yönetim sekmesi + K1'i uygula (tekrar)
Aynı K1 yapısı ve ölçümleri her iki dosyada kullanılır — böylece tutarlılık sağlanır.
