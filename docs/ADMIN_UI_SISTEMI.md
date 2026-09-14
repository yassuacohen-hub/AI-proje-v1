# Admin Panel UI Sistemi (ADMIN-UI)

> **Kapsam:** Streamlit admin paneli (`http://localhost:8501`, `app.py`).
> **Kaynak kod:** `src/company_master/ui/`
> **Durum:** Uygulandı ve testle korunuyor (1411 test geçiyor).
> **Amaç:** Bu belge yalnız "ne yaptık" değil, **"kullanıcı paneli sıraya gelince aynı çerçeve nasıl uygulanır"** sorusunun cevabıdır.

---

## 0. Mimari Sınır (sahip kararı)

| Sunucu | Teknoloji | Rol | Bu sistemin kapsamı |
|---|---|---|---|
| `:8501` | Streamlit (`app.py`) | İç operasyon / Süper Admin | ✅ **Bu belge burayı anlatır** |
| `:8000` | FastAPI + HTML/CSS (`web_app.py`) | Müşteri paneli | ⛔ Sıraya alındı, dokunulmadı |

**Karar:** Müşteri paneli Streamlit'e taşınmayacak. İki panel **tasarım token'larını ortaklaşır**, kod tabanını değil. Kullanıcı paneli sıraya gelince `tokens.py` çıktısı CSS değişkeni olarak köprülenir (bkz. `web_dashboard/css/theme.css` bridge kalıbı).

---

## 1. Katman Haritası

```
src/company_master/ui/
├── tokens.py       ← Ham değerler (renk, punto, boşluk, yarıçap, gölge)
├── styles.py       ← Token'ları tüketen CSS blokları
├── base.py         ← Bilesen ABC, kaçış (escape), sınıf birleştirme
└── components/
    ├── page.py     ← PageHeader, Section, SectionNav   (sayfa iskeleti)
    ├── button.py   ← Button, ButtonGroup               (tek buton sistemi)
    ├── topbar.py   ← TopBar, ThemeToggle, ChatBubble   (çerçeve)
    ├── card.py     ← Card, MetricCard
    ├── input.py / dropdown.py / table.py / badge.py / modal.py / tooltip.py
```

**Tek yönlü bağımlılık:** `components → base → styles → tokens`. Bileşen asla ham renk/punto yazmaz; test bunu zorlar (`test_bilesenlerde_hardcoded_renk_yok`).

---

## 2. Tasarım Token'ları — Rol Ayrımı (en kritik ders)

Renk token'ları **üç role** ayrıldı. Bu ayrım yapılmadan önce 9 ayrı WCAG hatası vardı; ayrımdan sonra sıfır.

| Rol | Örnek | Nerede kullanılır | Kontrast hedefi |
|---|---|---|---|
| **Dolgu** | `success`, `warning`, `danger`, `info`, `primary` | Buton/rozet arka planı | — (zemin kendisi) |
| **Yüzey üstü metin** | `success-text`, `danger-text` … | `bg`/`surface` üzerine yazı | **≥ 4.5:1** |
| **Dolgu üstü metin** | `on-success`, `on-primary` … | Dolgu rengi üzerine yazı | **≥ 4.5:1**, tema bağımsız |

**Yanlış kullanım:** `color: var(--hg-color-success)` ile açık zemine yazı yazmak.
**Doğru kullanım:** `color: var(--hg-color-success-text)`.

### Sınır token'ları
| Token | Anlam | Eşik |
|---|---|---|
| `border` / `border-strong` | Dekoratif ayraç | eşik yok |
| `border-interactive` | Etkileşimli bileşen sınırı (input, buton) | **≥ 3:1** |

### ⚠️ Kontrast ölçümünde en sık yapılan hata
Kontrastı **saf beyaza (#fff) karşı ölçmeyin.** Gerçek zemin token'ı neyse ona karşı ölçün:
- Aydınlık tema sayfa zemini `bg = #f6f7fb` (beyaz değil!)
- Kart zemini `surface`

Bu fark, aydınlık temada `border-interactive`'i `#8b93a7` (2.87:1 ❌) yerine `#7e869b` (3.40:1 ✅) yapmayı gerektirdi.

**Formül (WCAG 2.1):**
```
kanal = c/12.92           , c ≤ 0.03928
kanal = ((c+0.055)/1.055)^2.4 , aksi halde
L     = 0.2126·R + 0.7152·G + 0.0722·B
oran  = (L_üst + 0.05) / (L_alt + 0.05)
```
Bekçi test: `tests/test_ui_kontrast.py` — **her iki temayı** ayrı ayrı tarar.

---

## 3. Tipografi Ölçeği

İki katmanlı: **ham ölçek** (boyut sözlüğü) + **semantik ölçek** (kullanım niyeti).

| Ham | px | | Semantik | px | Kullanım |
|---|---|---|---|---|---|
| `size-xs` | 11 | | `size-h1` | 32 | Sayfa başlığı (ekranda **1 tane**) |
| `size-sm` | 13 | | `size-h2` | 22 | Bölüm başlığı |
| `size-md` | 14 | | `size-h3` | 17 | Alt bölüm |
| `size-lg` | 16 | | `size-body` | 14 | Gövde metni |
| `size-xl` | 20 | | `size-lead` | 16 | Giriş paragrafı |
| `size-2xl` | 26 | | `size-label` | 12 | Form etiketi |
| `size-3xl` | 32 | | `size-help` | 12 | Yardım metni |

- Ağırlık: `400 / 500 / 600 / 700`
- Satır yüksekliği: `1.25` (başlık) · `1.5` (gövde) · `1.7` (uzun metin)
- Harf aralığı: `-0.02em` (başlık) · `0.06em` (üst etiket, büyük harf)
- Font: **Inter** (metin) + **JetBrains Mono** (kod/sayı)

**Kural:** CSS'te `font-size: 14px` yazmak **yasak**; `font-size: var(--hg-font-size-body)` yazılır. Bekçi: `test_bilesen_css_hardcoded_punto_icermez`.

> Sahip kuralı gereği font ailesi ve renk paleti **yeniden icat edilmedi** — sadece disiplinli bir hiyerarşiye oturtuldu.

---

## 4. Sayfa İskeleti — Playground Kalıbı

Her ekran **aynı üç adımı** izler (referans: Streamlit Playground dokümantasyon düzeni).

```python
from company_master.ui import PageHeader, Section, SectionNav

GIRIS_METNI = "Bu ekranda ne yapılır, tek paragrafta."

BOLUMLER: tuple[Section, ...] = (
    Section("Webhook & DLQ", "Kuyruk sağlığı.", kimlik="webhook-dlq", ikon="🔌"),
    Section("Performans & Maliyet", "Kaynak tüketimi.", kimlik="performans-maliyet", ikon="⚡"),
)

def render_sistem_tab() -> None:
    # 1) Üst etiket → H1 → giriş paragrafı
    PageHeader("Sistem", giris=GIRIS_METNI,
               ust_etiket="Sistem · Operasyon", ikon="⚙️").render()

    # 2) Aksiyon şeridi — ekranda TEK birincil buton
    col_btn, col_zaman = st.columns([1, 3], vertical_alignment="center")
    with col_btn:
        yenile = st.button("🔄 Yenile", type="primary", use_container_width=True,
                           help="Önbelleği temizler ve panelleri yeniden yükler.")
    with col_zaman:
        st.caption(f"Son güncelleme: {datetime.now():%H:%M}")

    # 3) Sayfa içi gezinme + bölümler
    SectionNav(BOLUMLER, yatay=True).render()
    _bolum("webhook-dlq").render()
    ...
```

### Zorunlu kurallar
1. **Ekranda tam olarak bir `<h1>`.** `PageHeader` üretir; `st.subheader` **yasaktır**.
2. **Elle `st.markdown("## ...")` yasaktır.** Başlık = `Section`.
3. Her `Section` bir `kimlik` taşır; `SectionNav` bu kimliğe anchor verir.
4. Aynı ekranda **birden fazla birincil buton olamaz** — `PageHeader` ve `ButtonGroup` bunu `ValueError` ile reddeder.
5. Kaynak dosyalar **BOM'suz UTF-8**.

**Bekçi test:** `tests/test_sayfa_iskeleti.py` — tüm ekranları AST ile tarar, muaf listesi gerekçe zorunlu.

---

## 5. Buton Sistemi

Tek giriş noktası; görsel varyant yerine **rol** konuşulur.

```python
ROLLER = {
    "birincil":  "primary",    # ekranda en fazla 1
    "ikincil":   "secondary",
    "tehlikeli": "danger",     # geri alınamaz işlem
    "sessiz":    "ghost",
}
```

| Durum | Davranış |
|---|---|
| `hover` | Yüzey bir kademe açılır |
| `focus-visible` | 2px `focus-ring` halkası (klavye erişilebilirliği) |
| `pasif` | `opacity` + `pointer-events:none` + `aria-disabled` |
| `yukleniyor` | Spinner + **otomatik olarak pasif** (`pasif = pasif or yukleniyor`) |

`ButtonGroup` hizalamaları: `sol` · `sag` · `arali`. Boş liste veya >1 birincil → `ValueError`. Grup `role="group"` yazar.

**Bekçi test:** `tests/test_ui_tipografi.py` (buton sözleşmesi bölümü, 12 test).

---

## 6. Çerçeve Bileşenleri (sahip talebi — 3 unsur)

| Bileşen | Konum | Durum |
|---|---|---|
| `ThemeToggle` | — | ⛔ **Streamlit panelinden kaldırıldı (U-01)** — bileşen `topbar.py`'de duruyor, HTML müşteri paneli (8000) kullanmaya devam eder |
| Arama alanı | Sağ üst | ✅ Bölüm adına göre canlı süzme |
| `ChatBubble` "AI Abrakadabra" | Sağ alt | ⚠️ **UI kabuğu hazır, AI motoru bağlı değil** — panel başlığında **"Yakında" durum rozeti** gösterilir |

### 6.0 Streamlit'in kendi araç çubuğuna devredilen kontroller (2026-09-14)

Sahip tespiti: *"zaten Streamlit gece/gündüz teması var sağ üst ⋮ menüde, sen sayfada tekrar koymuşsun"* ve *"cache temizleme de bu menüde var zaten"*. Mükerrer kontroller kaldırıldı; ⋮ menüsü `toolbarMode = "auto"` ile geri açıldı.

| Kontrol | Eskiden | Şimdi |
|---|---|---|
| **Tema (gece/gündüz)** | Sayfa içi `ThemeToggle` + `?tema=` URL parametresi | Sağ üst ⋮ › **Settings › Appearance**. `app.py::aktif_tema()` bunu `st.context.theme.type` ile okur, `STREAMLIT_TEMA_ESLEME` ile iç anahtarlara (`aydinlik`/`karanlik`) çevirir |
| **Genişlik (Wide mode)** | `set_page_config(layout="wide")` sabitti, menüde seçenek yoktu | `layout` verilmiyor → ⋮ › **Wide mode** geçişi kullanıcıda |
| **Önbellek temizleme** | Footer'da "Cache Temizle" butonu | Sağ üst ⋮ › **Clear cache**. Footer yalnız yönlendirici bir caption gösterir |

**Kural:** Streamlit'in araç çubuğunda zaten bulunan bir kontrolü sayfa içinde tekrarlamayın. İki ayrı kaynak senkronsuz kalır ve kullanıcı hangisinin geçerli olduğunu bilemez. Tema için **tek doğru kaynak** `st.context.theme`'dir.

**Durum rozeti sözleşmesi (`hg-chat-rozet`):**

| Durum | Çağrı | Sonuç |
|---|---|---|
| Motor bağlı değil (varsayılan) | `ChatBubble(acik=True)` | Başlıkta `ChatBubble.VARSAYILAN_ROZET` = **"Yakında"** rozeti çizilir |
| Motor bağlandı | `ChatBubble(acik=True, rozet_metni="")` | Rozet tamamen kaldırılır |
| Özel etiket | `ChatBubble(acik=True, rozet_metni="Beta")` | Metin `guvenli_metin()` kaçışından geçer (XSS koruması) |

Rozet yalnız **açık panel başlığına** aittir; kapalı durumdaki FAB rozet çizmez. Renkler `--hg-color-warning` / `--hg-color-warning-soft` tokenlarından gelir (hardcoded renk yok).

> **Açık iş:** Sohbet balonuna gerçek bir sohbet modeli bağlanacak (soru cevaplama, analiz, rehberlik). Sahip talimatı: *"iş yükü çoksa not alırsın sonra yaparız."* → Ayrı görev olarak kayıtlı. Motor devreye alındığında `app.py::render_chat` çağrısına `rozet_metni=""` eklenerek rozet kapatılır; başka değişiklik gerekmez.

**Korunanlar (değiştirilmedi):** sol menü ikon dizilimi ve sırası, renk paleti, font seçimi, daraltılabilir dinamik sol menü.

---

## 7. Responsive Kırılma Noktaları

| Genişlik | Davranış |
|---|---|
| `≤ 900px` | `SectionNav` dikeyden yatay sarmalı listeye döner |
| `≤ 640px` | `PageHeader` tek sütuna iner · `TopBar` yığılır · `ChatBubble` tam genişliğe yayılır · `ButtonGroup` %100 genişlik |
| `prefers-reduced-motion` | Tüm geçiş/animasyonlar kapatılır |

---

## 8. Test Sahteleme Sözleşmesi (yeni ekran testi yazacaklar için)

İskelet `st.markdown(..., unsafe_allow_html=True)` üzerinden yayın yapar. Bu yüzden eski `st.subheader` beklentileri **geçersizdir**. Yeni ekran testi şu kalıbı kullanır:

```python
def _markdown_metni(mock: MagicMock) -> str:
    """Tüm st.markdown çağrılarının ilk konumsal argümanını birleştirir."""
    return "\n".join(str(c.args[0]) for c in mock.call_args_list if c.args)

def _columns_sahte(spec, **_kwargs):
    """vertical_alignment gibi kwarg'ları SESSİZCE YUTMALI."""
    adet = spec if isinstance(spec, int) else len(spec)
    return [MagicMock() for _ in range(adet)]

@pytest.fixture
def st_sahte(monkeypatch):
    kaydedilen = {ad: MagicMock() for ad in ("markdown", "caption", "divider", "info")}
    for ad, mock in kaydedilen.items():
        monkeypatch.setattr(modul.st, ad, mock)
    monkeypatch.setattr(modul.st, "button", lambda *a, **k: False)
    monkeypatch.setattr(modul.st, "columns", _columns_sahte)
    return kaydedilen

def test_sayfa_iskeleti_h1_uretir(st_sahte):
    modul.render_x_tab()
    metin = _markdown_metni(st_sahte["markdown"])
    assert metin.count("<h1") == 1
    assert modul.GIRIS_METNI in metin
```

> **Tuzak:** `lambda n: [...]` şeklinde kolon sahtesi yazmayın — `st.columns(..., vertical_alignment="center")` çağrısı `TypeError` verir. Mutlaka `**kwargs` yutun.

---

## 9. Test Bekçileri Özeti

| Dosya | Neyi korur |
|---|---|
| `tests/test_ui_components.py` | Bileşen HTML sözleşmesi, XSS kaçışı, ölü CSS seçici yok |
| `tests/test_ui_tipografi.py` | Punto ölçeği monotonluğu, hardcoded punto yasağı, buton rolleri |
| `tests/test_ui_kontrast.py` | WCAG 4.5:1 / 3:1 — **her iki temada** |
| `tests/test_sayfa_iskeleti.py` | Tek H1, `st.subheader` yasağı, Section kullanımı, BOM yok |
| `tests/test_sekme_kapsama.py` | Öksüz render fonksiyonu kalmasın |

---

## 10. Kullanıcı Paneli Sıraya Gelince (yol haritası)

1. `tokens.py` çıktısını CSS değişkeni olarak köprüle → `web_dashboard/css/theme.css`
2. Tipografi ölçeğini (bölüm 3) birebir aktar — punto değerleri tek kaynaktan gelmeli
3. Sayfa iskeletini (bölüm 4) HTML şablonunda karşıla: `<header class="page-head">` → `<nav class="section-nav">` → `<section id="...">`
4. Buton rollerini (bölüm 5) CSS sınıfı olarak karşıla; **tek birincil buton** kuralını koru
5. Kontrast bekçisini (bölüm 2) müşteri CSS'i için de koştur — zemin token'ı `bg`/`surface` olsun, beyaz değil

---

## 11. Navigasyon Bölümleri (`web_dashboard/tabs/__init__.py::SECTIONS`)

Toplam **11 bölüm**. Her kayıt bir `TabTanimi`; `hazir=False` olanlar `render_placeholder` ile "bekleyen görev" bildirir.

| # | Anahtar | Render fonksiyonu | Not |
|---|---|---|---|
| 1 | `ana_kontrol` | `ana_kontrol.render_ana_kontrol_tab` | KPI özeti |
| 2 | `musteriler` | `admin_musteriler.render_musteriler_tab` | |
| 3 | `paketler` | `paketler.render_paketler_tab` | |
| 4 | `pazarlama` | `pazarlama.render_pazarlama_tab` | |
| 5 | `abrakadabra` | — | `hazir=False` — AI motoru ayrı görev |
| 6 | `sistem` | `admin_sistem.render_sistem_tab` | |
| 7 | `canli_veri` | `admin_realtime.render_admin_realtime_tab` | |
| 8 | `denetim` | `admin_audit.render_audit_tab` | **DASH-08** — öksüzdü, bağlandı |
| 9 | `yonetim` | `admin_yonetim.render_yonetim_tab` | Karar defteri dahil (`render_decision_tab`) |
| 10 | `ayarlar` | `admin_panel.render_ayarlar_tab` | |
| 11 | `yukleme` | `admin_loading.render_loading_tab` | **P7-42** — öksüzdü, bağlandı |

**Bekçi test:** `tests/test_dashboard_nav.py` (bölüm sayısı + anahtar/URL benzersizliği) ve `tests/test_sekme_kapsama.py` (öksüz render fonksiyonu kalmasın — `BILINEN_ACIK` artık boş).

---

## 12. Bilinen Açık Kayıtlar

| Kayıt | Durum |
|---|---|
| AI Abrakadabra sohbet motoru | Ayrı görev — UI kabuğu hazır, başlıkta "Yakında" rozeti gösteriliyor |
| `test_api_integration.py::test_companies_liste_sozlesme` | UI dışı; gerçek DB'ye bağlı (`total == 1` bekliyor, 14000 geliyor) → izole fixture DB ayrı görev |
| ~~3 öksüz sekme~~ | ✅ **Kapandı** — `render_audit_tab` + `render_loading_tab` SECTIONS'a eklendi, `render_decision_tab` yönetim sekmesine delege edildi |
