# UI-MIMARI-02 — Admin panel UI mimari borçları (kilo, P2)

> Ortak kurallar: `docs/plans/GECE-ZINCIR-03_ortak_kurallar.md`. Zincir halkası 2/4.
> Kaynak bulgular: `docs/ROO_ELESTIRI_NOTLARI.md` M-03, M-05 (+ K-04 KVKK tüketimi). **M-04 bu görevde YOK** (`web_dashboard/tabs/__init__.py` cline kilidinde; SEC-AUTH-01 bitince ayrı görev).

## Kapsam
- `web_dashboard/tabs/ana_kontrol.py`, `web_dashboard/tabs/musteri_yonetimi.py`, `web_dashboard/charts.py`,
  `src/company_master/ui/tokens.py` (yalnız CSS sınıfı gerekiyorsa), ilgili testler.
- DOKUNMA: `web_dashboard/tabs/__init__.py`, `app.py`.

## İş
1. **M-03 ölü CSS:** `ana_kontrol.py` `_get_metric_color()` `metric-blue/metric-orange` döndürüyor; bu sınıflar hiçbir CSS'te tanımlı değil ve kartlar zaten `kpi_karti(..., kategori=...)` ile renkleniyor. Karar: fonksiyon ve çağrıları **kaldırılır**; docstring'deki "CSS via _get_metric_color" kuralı `kpi_karti kategori` olarak güncellenir. Eğer hâlâ `st.metric` kullanan yer varsa `kpi_karti`'ye çevrilir (K4 renk kuralı: müşteri=mavi, sistem=turuncu).
2. **M-05 inline import:** `musteri_yonetimi.py` `_paket_kredi()` içindeki `from web_dashboard.tabs.admin_extras import get_api, post_api` modül başına taşınır. Döngüsel import çıkarsa `admin_extras` yerine `scripts/dash04_api_client.py`'deki `get_api/post_api` kullanılır (aynı imza).
3. **KVKK tüketimi (K-04 devamı):** `musteri_yonetimi.py` login/search olay tablolarında `kvkk_maske_acik(kullanici_id)` False ise (ADMIN-AYAR-01 yardımcısı) e-posta/IP sütunları için `st.caption("Maskeleme kapalı — yetki gerektirir")` uyarısı gösterilir; veri tarafı zaten maskeli (`email_masked`), ham veri GÖSTERİLMEZ. Amaç: ayarın görünür etkisi olsun.
4. Testler: `_get_metric_color` yok; modül import düzeni; maske uyarısı caption'ı (MagicMock st ile).

## Teslim kriteri
- Tam süit yeşil; `kodlama_denetim` temiz; `streamlit_restart.py` çalıştırıldı.
- Rapor: `data/orchestrator/UI-MIMARI-02_rapor_<tarih>_kilo.md`. M-04 için not: "SEC-AUTH-01 sonrası UI-MIMARI-03".
