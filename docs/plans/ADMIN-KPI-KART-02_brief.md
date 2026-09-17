# ADMIN-KPI-KART-02 — Kalan st.metric kartları → kpi_karti (webhook_monitor, tenant_health) (kilo, P2)

Ortak kurallar: `docs/plans/GECE-ZINCIR-03_ortak_kurallar.md` (UTF-8, test, restart, commit YOK, rapor).

## Sorun
ADMIN-KPI-KART-01 sekiz admin sekmesini kapsıyor; iki dosya kapsam dışı kaldı ve hâlâ ham `st.metric` kullanıyor (tek KPI dili ihlali):
- `web_dashboard/tabs/webhook_monitor.py`: L165-189 (6 kart: Durum/Secret/Rate Limit/DLQ/Cache/Prometheus), L208-216 (5 kart: olay istatistikleri), L313-314 (latency döngüsü).
- `web_dashboard/tabs/tenant_health_dashboard.py`: L20-24 (genel skor), L33-34 (4 bileşen döngüsü, `cols[i].metric`).
- `web_dashboard/tabs/ana_kontrol.py` L11 docstring hâlâ `st.metric` referansı veriyor.

## Amaç
Admin panelde `st.metric` çağrısı kalmasın; tüm kartlar `web_dashboard.charts.kpi_karti` (+ `sayi_formatla`).

## Yapılacaklar
| # | İş | Not |
|---|----|-----|
| 1 | `webhook_monitor.py` 11 kart → `kpi_karti(baslik, deger, kategori=..., aciklama=...)`; kategori eşlemesi: Durum/Secret/Rate Limit → `sistem`; DLQ/Hatalı → `hata`; Başarılı/Toplam → `musteri` | Mevcut kategori adlarını `charts.KATEGORI_RENK` anahtarlarından seç; **yeni kategori YASAK** |
| 2 | Latency döngüsü (L313-314): en fazla 4 sütun, `st.columns(min(4, len(latency_keys)))`; her metrik `kpi_karti`; değer `sayi_formatla(v, ondalik=3, birim="s")` | 4'ten fazla anahtar varsa kalanı `st.dataframe` |
| 3 | `tenant_health_dashboard.py`: genel skor + 4 bileşen → `kpi_karti`; `help=` bilgisi `aciklama` parametresine | `cols[i].metric` yerine `with cols[i]: kpi_karti(...)` |
| 4 | `ana_kontrol.py` L11 docstring: `st.metric` → `kpi_karti` | Yalnız docstring; kod satırı değişmez |
| 5 | Test: `tests/test_webhook_monitor_tab.py` mock'ları `kpi_karti`'ye çevir; `tests/test_admin_kpi_kart.py`'ye (KART-01'de oluşturuldu) AST tabanlı kontrol: `web_dashboard/tabs/*.py` içinde `st.metric(` / `.metric(` çağrısı **0** | `ast.walk` ile `Attribute(attr="metric")` tarama; `admin_loading.py` demo iskeleti muaf tutulacaksa listede açıkça yaz |

## Kilitli dosyalar
- `web_dashboard/tabs/webhook_monitor.py`
- `web_dashboard/tabs/tenant_health_dashboard.py`
- `web_dashboard/tabs/ana_kontrol.py` (yalnız docstring)
- `tests/test_webhook_monitor_tab.py`
- `tests/test_admin_kpi_kart.py`

## Kurallar
- `charts.kpi_karti` imzası **değişmez**; `charts.py`'ye dokunma.
- ADMIN-KPI-KART-01 teslim edilmeden bu göreve başlama (zincir sırası).
- `web_dashboard/tabs/__init__.py` yasak.

## Teslim
- `python scripts/gorev_kutusu.py teslim --ajan kilo --task-id ADMIN-KPI-KART-02 --ozet "..."`
- Rapor: `data/orchestrator/ADMIN-KPI-KART-02_rapor_<tarih>_kilo.md`
- Kapsam dışı bulgu: `data/orchestrator/ADMIN-KPI-KART-02_bulgular_<tarih>_kilo.md` (düzeltme YOK)
- `python scripts/streamlit_restart.py` + `python scripts/kodlama_denetim.py` temiz.

## Tahmin
~1.5 saat.
