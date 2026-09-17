# ADMIN-HATA-01 — Hata Yönetimi sekmesi gerçek veriye bağlansın (kilo, P2)

Ortak kurallar: `docs/plans/GECE-ZINCIR-03_ortak_kurallar.md` (UTF-8, test, restart, commit YOK, rapor).

## Sorun (mevcut `web_dashboard/tabs/admin_errors.py`)
1. L146-152: sabit sahte istatistik ("5 bugün" vb.) — canlı sistemde yanıltıcı.
2. L113-119: "demo" düğmesi gerçek exception fırlatıyor → Streamlit çalışma zamanını kırıyor.
3. L124-141: hata bildirim formu sadece `st.json` gösteriyor, hiçbir yere kaydetmiyor.

## Yapılacaklar
| # | İş | Not |
|---|---|---|
| 1 | Sahte istatistikleri kaldır | Kaynak: `logs/` altındaki uygulama logu (varsa) veya `data/errors/*.jsonl` sayımı; kaynak yoksa `—` göster (`sayi_formatla(None)`), asla uydurma sayı yok |
| 2 | Demo raise'i kaldır | Yerine `render_error_page("500", details=...)` önizlemesi; `st.error` ile göster, exception fırlatma |
| 3 | Rapor formunu kaydet | `data/errors/reports.jsonl` (append, UTF-8, `atomic_write_text` gerekmiyorsa `open(..., "a")`); alanlar: `ts`, `kullanici`, `sayfa`, `aciklama`, `onem`; başarı mesajı + form temizle |
| 4 | Kayıtları listele | Son 20 raporu `st.dataframe` ile göster; boşsa bilgi kutusu |
| 5 | KPI kartları | `kpi_karti` kullan (ADMIN-KPI-KART-01 ile aynı standart), `st.metric` yok |
| 6 | Test | `tests/test_admin_errors.py` (YENİ): form kaydı tmp_path'e yazılıyor, sahte sayı yok, demo raise yok (kaynakta `raise` araması), `render_error_page` çıktısı |

## Kilitli dosyalar
- `web_dashboard/tabs/admin_errors.py`
- `tests/test_admin_errors.py`

`tests/test_proje_yonetimi.py` içindeki `admin_errors.render_errors_tab` mock'u kırılmamalı (imza aynı kalsın: parametresiz).

## Teslim
- `python scripts/gorev_kutusu.py teslim --ajan kilo --task-id ADMIN-HATA-01`
- Rapor: `data/orchestrator/ADMIN-HATA-01_rapor_<tarih>_kilo.md`
- `python scripts/streamlit_restart.py` + `python scripts/kodlama_denetim.py` temiz.

## Tahmin
~2 saat.
