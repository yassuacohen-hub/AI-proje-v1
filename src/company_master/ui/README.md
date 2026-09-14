# UX-01 — Huginn UI Bileşen Kütüphanesi (Design System)

Streamlit tabanlı admin panelleri için yeniden kullanılabilir, bağımsız
test edilebilir HTML/CSS bileşen kütüphanesi.

## Neden bu kütüphane?

- **Streamlit'ten bağımsız:** Her bileşen saf HTML string üretir
  (`.html()`). `import streamlit`, yalnızca `.render()` / `.streamlit()`
  metotları içinde, yerel (lazy) olarak yapılır. Bu sayede bileşenler
  Streamlit kurulu olmadan da test edilebilir (bkz. `tests/test_ui_components.py`).
- **Token SSOT:** Hiçbir bileşende ham hex renk/px değeri yoktur. Her şey
  `tokens.py` içindeki CSS değişkenlerine (`var(--hg-*)`) bağlanır. Bu,
  UX-03'ün tema değişimini tek noktadan (`:root` bloğu) yapmasını sağlar.
- **Güvenlik:** Kullanıcı verisi `guvenli_metin()` (`html.escape`) ile
  kaçışlanır. Yalnızca bilinçli `ham_html=True` parametresiyle ham HTML
  gömülebilir (örn. ikon SVG'leri için).
- **Erişilebilirlik:** `role`, `aria-*`, `scope="col"`, `for`/`id`
  eşleşmesi, `prefers-reduced-motion` desteği bileşenlere gömülüdür.
- **Çakışma önleme:** Tüm sınıflar `hg-` önekini taşır; Streamlit'in
  kendi iç sınıfları ve `web_dashboard/css/style.css` ile çakışmaz.

## Hızlı kullanım

```python
from company_master.ui import Button, MetricCard, Table, stil_enjekte

stil_enjekte()  # sayfa başında bir kez çağrılır (Streamlit)

Button("Kaydet", varyant="primary", ikon="💾").render()

MetricCard(
    "Toplam Firma", 8313,
    kategori="customer",
    aciklama="Veritabanındaki doğrulanmış firma sayısı",
    soru="Bu hafta kaç yeni firma eklendi?",
).render()

Table([{"ad": "Acme A.Ş.", "aktif": True, "puan": 87}]).render()
```

Streamlit olmadan (örn. testte veya CLI önizlemede) yalnızca HTML almak
için `.html()` kullanılır:

```python
from company_master.ui import Button
print(Button("Gönder").html())
# <button type="button" class="hg-btn hg-btn-primary hg-btn-md">Gönder</button>
```

## Bileşenler

| Bileşen | Modül | Amaç |
|---|---|---|
| `Button` | `components/button.py` | Aksiyon butonu; varyant/boyut/ikon/yükleniyor/href desteği |
| `Input` | `components/input.py` | Etiketli form giriş alanı (text/textarea/vb.), hata/yardım mesajı |
| `Dropdown` | `components/dropdown.py` | Tekli/çoklu seçim alanı |
| `Badge` | `components/badge.py` | Küçük durum/etiket rozeti; `Badge.durumdan(durum)` ile otomatik varyant |
| `Card` | `components/card.py` | Genel amaçlı kart kapsayıcısı (başlık/içerik/altbilgi) |
| `MetricCard` | `components/card.py` | KPI metrik kartı (DASH-UX-01 renk kodlaması, delta oku) |
| `Table` | `components/table.py` | Veri tablosu; DataFrame/`to_dict(orient="records")` uyumlu, kırpma desteği |
| `Modal` | `components/modal.py` | Diyalog penceresi; `role="dialog"`, aksiyon butonları |
| `Tooltip` | `components/tooltip.py` | İpucu balonu; `role="tooltip"`, klavye erişimi |

Tüm bileşenler `company_master.ui` üst modülünden tek noktadan import edilir.

## Tasarım token'ları

`tokens.py` renk, boşluk, yarıçap, tipografi, gölge ve z-index
ölçeklerini tanımlar. Öne çıkanlar:

- **Marka rengi (accent):** Indigo `#6366F1` — `docs/UX_ADMIN_PANEL_REVIEW_2026-09-14.md`
  denetimiyle hizalıdır. `RENKLER["accent"]` ve `RENKLER["primary"]` aynı
  değeri taşır (semantik takma ad).
- **Durum renkleri:** `success #22C55E`, `warning #F59E0B`, `danger #EF4444`.
- **Semantik yarıçaplar:** `button` 8px, `card` 12px, `modal` 16px —
  denetim raporundaki bantlarla (`8-10 / 12-16 / 16-20px`) uyumludur.
- **z-index katmanları:** `base 1 < dropdown 1000 < tooltip 1100 <
  modal-backdrop 1200 < modal 1201` (çakışmayı önler).

```python
from company_master.ui import kok_css, token

print(kok_css())          # :root { --hg-color-primary: #6366f1; ... }
print(token("color", "accent"))  # var(--hg-color-accent)
```

## Test / regresyon garantisi

`tests/test_ui_components.py` (82 test) şunları makine ile denetler:

- Her bileşenin ürettiği HTML sınıflarının CSS'te karşılığı olduğunu
  (`test_her_uretilen_sinifin_css_karsiligi_var`).
- CSS'te tanımlı olup hiçbir bileşenin üretmediği "ölü" seçici olmadığını
  (`test_olu_css_secici_yok`).
- Bileşen CSS'inde hardcoded hex renk olmadığını
  (`test_bilesenlerde_hardcoded_renk_yok`).
- Copilot UX denetiminin renk paleti (`accent/success/warning/danger`)
  ve yarıçap bandı (`button/card/modal`) sözleşmesinin korunduğunu.
- XSS kaçışlama, erişilebilirlik nitelikleri, geçersiz girdilerde
  `BilesenHatasi` fırlatıldığını.

Çalıştırma:

```bash
python -m pytest tests/test_ui_components.py -q
```

## Yeni bileşen ekleme kontrol listesi

1. `components/<isim>.py` içinde `Bilesen` alt sınıfı oluştur;
   `html()` metodu saf HTML döndürsün, `streamlit()`/`render()` içinde
   yerel `import streamlit` yap.
2. Tüm renk/boşluk/yarıçap değerlerini `tokens.token(...)` üzerinden al
   — asla ham hex/px yazma.
3. Kullanıcı verisini `guvenli_metin()` ile kaçışla.
4. `styles.py`'a bileşenin CSS bloğunu ekle (yalnızca `var(--hg-*)`
   referanslarıyla).
5. `components/__init__.py` ve `ui/__init__.py`'a dışa aktar.
6. `tests/test_ui_components.py`'daki `_tum_ornekler()` listesine yeni
   varyant/boyut permütasyonlarını ekle (ölü CSS / stilsiz sınıf testleri
   otomatik doğrular).
