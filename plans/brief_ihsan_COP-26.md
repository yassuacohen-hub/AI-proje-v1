# COP-26: Müşteriler Ekranı — Firma Listesi + Filtre + Bildirim Blogu

## Görev Özeti
Müşteriler (firmalar) gösteren yeni bir sayfayı `web_dashboard/tabs/musteri_paneli.py` dosyasında oluştur. Temel özellikler: firma listesi (tablo), gelişmiş filtreleme, bildirim blogu feed'i.

## Bağımlılık
Bu görev **COP-25** tamamlandıktan sonra başlayabilir. COP-25 şunları sağlar:
- Müşteri veritabanı şeması ve query API'si
- Filtre parametreleri (endüstri, lokasyon, büyüklük)
- Backend bildirim servisi

## Çıktı
1. **Dosya:** `web_dashboard/tabs/musteri_paneli.py`
   - Firma listesi tablosu (tablo/dataframe)
   - Filtreleme araçu (sidebar dropdown'ları)
   - Bildirim feed'i (son 20 bildirim, statü renkleri)
   - Sayfalama (20 firma/sayfa)

2. **Stil:** `src/company_master/ui/styles.py` (mevcut tema)

3. **Test:** `tests/test_musteri_paneli.py` (fake data ile)

4. **Rapor:** `data/orchestrator/COP-26_rapor_<tarih>_roo.md` (D-55 formatı)

## Testler
```bash
# Frontend render (fake streamlit)
pytest tests/test_musteri_paneli.py -v

# API entegrasyon (COP-25 bağımlılık check)
python -c "from web_dashboard.tabs.musteri_paneli import get_firmalar; assert callable(get_firmalar)"
```

## Kurallar
- D-55: Rapor 5 başlık zorunlu, Bulgular zorunlu
- D-183: Dosya adı `_roo` sonekli
- D-184: Rapor'da `[[COP-25]]` wikilink (bağımlılık)
- D-57: Başlık `[UI] Müşteriler sayfası yaz → web_dashboard/tabs/musteri_paneli.py (3s)`

## Sahibi
**ROO** — manuel onay (P1)

## Teslim
```bash
python scripts/gorev_kutusu.py teslim \
  --task-id COP-26 \
  --rapor data/orchestrator/COP-26_rapor_2026-09-21_roo.md
```

## Başlama
COP-25 tamamlanınca otomatik tetiklenecek.
