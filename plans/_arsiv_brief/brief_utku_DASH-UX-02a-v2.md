# DASH-UX-02a.v2: Sistem Sekmesi SECTIONS Kaydını Yap

## Görev Özeti

DASH-UX-02a.v1'in `admin_sistem.py` dosyası + ADMIN-UX-MENUTREE-01'in yeni SECTIONS yapısı üzerine, SECTIONS registry'sine "Sistem" sekmesi kaydını yaz ve tüm testleri çalıştır.

**D-185 Karar:** DASH-UX-02a split v2 — dosya çakışmasını seri yapma ile çöz.

## Bağımlılıklar

1. ✅ DASH-UX-02a.v1 = **done** (review onaylandı)
2. ✅ ADMIN-UX-MENUTREE-01 = **done** (review onaylandı)

## Çıktı

1. **Dosya:** `web_dashboard/tabs/__init__.py` (SECTIONS tuple güncelle)
   - v1'in `admin_sistem.py` için `TabTanimi` kaydı ekle
   - MENUTREE'nin "Ayarlar" silme + grup düzenlemesi üzerine yaz
   - URL pattern: `/admin/sistem`
   - Role: `min_rol="admin"`
   - K1 kalibrasyonu: v1 raporundan al, uyumlu yapı kullan

2. **Rapor:** `data/orchestrator/DASH-UX-02a-v2_rapor_<tarih>_utku.md` (D-55 formatı)
   - v1 raporuna referans (K1 yapısı alma)
   - SECTIONS eklenen satır + context
   - Tüm testler yeşil onayı
   - Merge detayları (MENUTREE + v1 üzerine)

## Testler

```bash
# SECTIONS import ve parse
python -c "from web_dashboard.tabs import SECTIONS; admin_sistem = next((s for s in SECTIONS if 'sistem' in s.id), None); assert admin_sistem is not None"

# URL yönlendirme
pytest tests/test_dashboard_routing.py::test_admin_sistem_url -v

# Regresyon (tüm testler)
pytest tests/ -q
```

## Kurallar

- D-55: Rapor 5 başlık zorunlu
- D-183: Dosya adı `_utku` sonekli
- D-184: Rapor'da `[[DASH-UX-02a-v1]]`, `[[ADMIN-UX-MENUTREE-01]]`, `[[D-185]]`
- **D-85:** Seri yapma — v1 onay → v2 → 02b tetik
- **K1 Tutarlılığı:** v1 raporundan K1 yapısını doğru al ve uygula

## Sahibi

**UTKU** — MENUTREE bitince başlama (P1, seri uygulanma D-85)

## Teslim

```bash
python scripts/gorev_kutusu.py teslim \
  --ajan utku \
  --task-id DASH-UX-02a-SECTIONS \
  --ozet "SECTIONS: admin_sistem TabTanimi ekle (MENUTREE'nin yeni struct uzerine). K1 v1 raporundan. Tum testler yeşil. Merge __init__.py bitirdi." \
  --cikti "web_dashboard/tabs/__init__.py"
```

## Süre Tahmini

1–2 saat (registry düzeltmesi + full test)

## Tetik Zinciri

```
DASH-UX-02a.v1 (done) → (onay) → DASH-UX-02a-SECTIONS tetikle (blocked, MENUTREE bitmesini bekle)
ADMIN-UX-MENUTREE-01 (done) → (onay) → DASH-UX-02a-SECTIONS blokaj çözül (otomatik başla)
DASH-UX-02a-SECTIONS (done) → (onay) → DASH-UX-02b tetikle
```
