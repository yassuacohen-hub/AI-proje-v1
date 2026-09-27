# UI-SUBHEADER-MUSTERI-01 — musteri_yonetimi 5 st.subheader kaldı

## Görev Özeti
`tests/test_sayfa_iskeleti.py::test_ekranda_subheader_kalmaz[musteri_yonetimi]` kırık:
5 adet `st.subheader` çağrısı duruyor. Sayfa iskeleti kuralı: başlıklar
`PageHeader` / `Section` ile çizilir.

## Kök Neden (doğrulandı)
Test AST ile `st.subheader(` çağrılarını sayıyor, `musteri_yonetimi` modülünde 5 tane var.
Diğer tüm sayfalar geçişi tamamlamış; bu sayfa atlanmış.

## Çıktı
- `web_dashboard/tabs/musteri_yonetimi.py` (test hangi modülü işaret ediyorsa o):
  5 `st.subheader` → `Section(...)` ya da `PageHeader(...)`
- Görsel hiyerarşi bozulmasın: alt başlık `Section`, sayfa başlığı `PageHeader`
- Mevcut sayfalardaki kalıbı kopyala (`web_dashboard/tabs/pazarlama.py` iyi örnek)

## Kabul Kriteri
```
set PYTHONIOENCODING=utf-8 && python -m pytest tests/test_sayfa_iskeleti.py -q
# 1 failed -> 0 failed
set PYTHONIOENCODING=utf-8 && python -m pytest tests/ -q --tb=line
# yeni kirik yok
```

## Kurallar
- D-86 / D-66
- Testi parametreden çıkararak geçirmek YASAK

## Süre Tahmini
2 saat

## Ilgili Nodlar
- [[Huginn Data Insights/AGENTS]]
