# UI Modal + Chart Arastirma — Admin Panel (2026-09-15)

> SADECE DOKUMAN, KOD YOK. UI-CHART-01 (kilo, charts.py) ile cakisma yok:
> bu dosya oneri yazar; `charts.py` ve `web_dashboard/**` dosyalarina dokunulmaz.
> Olcutlenmis surumler: Streamlit **1.62.0**, plotly **7.0.0**, altair **6.2.2**,
> `streamlit-echarts` **kurulu degil** (`pip show` NOT FOUND).

---

## 1) Streamlit modal secenekleri

| Secenek | Arti | Eksi | Surum gereksinimi |
|---|---|---|---|
| `st.dialog` | Yerlesik, dekorator API, ekran kilitler, form destegi | 1.33+ gerekir; ic ice dialog yok | 1.33+ (mevcut 1.62.0 OK) |
| `st.popover` | Hafif, tek dugme + icerik; kucuk aksiyonlar icin ideal | Gercek modal degil (disari tiklayinca kapanir) | 1.32+ (mevcut OK) |
| `st.expander` | Sifir maliyet, her surumde var | Sayfa ici genisler; odak kilitlemez | tum surumler |
| `streamlit-modal` (3. parti) | Eski surumlerde modal taklidi | Bakimsiz kalma riski; ek bagimlilik | kurulum gerekir — ONERILMEZ |
| Custom CSS overlay | Tam kontrol (tema, animasyon) | Bakim yuku, erisilebilirlik riski | sifir bagimlilik |

**Oneri:** Birincil `st.dialog` (kurulu 1.62.0 destekliyor), kucuk hizli
aksiyonlarda `st.popover`, salt-bilgi icin `st.expander`. 3. parti modal
paketi eklenmesin.

---

## 2) Admin panelde 5 somut modal senaryosu

### S1 — Kullanici onayi + tier secimi
- **Tetik:** Kullanicilar tablosunda satir secimi → "Onayla" dugmesi.
- **Alanlar:** tier secici (terminal/operator/admin — bkz. REV-MVP-ADMIN-01 K-1),
  not alani (opsiyonel), onay kutusu ("Eminim").
- **Kapanma:** `post_api` basarili ise `st.success` + `st.rerun`;
  hata ise dialog acik kalir, hata dialog icinde gosterilir.
- **Dosya:** `web_dashboard/tabs/admin_extras.py`.

### S2 — Kredi yukleme
- **Tetik:** Musteri/paket satirinda "Kredi Yukle" dugmesi.
- **Alanlar:** miktar (min 1), aciklama, odeme referansi (opsiyonel).
- **Kapanma:** Basarili → success + rerun; vazgec → sessiz kapanma.
- **Dosya:** `paketler.py` / `admin_cost.py`.

### S3 — Kategori duzenle
- **Tetik:** Kategori listesinde "Duzenle".
- **Alanlar:** ad, renk (color picker), aktif/pasif anahtari.
- **Kapanma:** Kaydet → rerun; Iptal → degisiklik yok.

### S4 — Sifre degistir
- **Tetik:** Ayarlar/kullanici menusunde "Sifre Degistir".
- **Alanlar:** mevcut sifre, yeni sifre, yeni sifre (tekrar).
- **Kapanma:** Basarili → session temizlenir, login ekranina yonlenir;
  hata → dialog icinde hata, alanlar korunur.
- **Dosya:** `admin_auth.py` + backend endpoint.


### S5 — Firma detay karti
- **Tetik:** Firma listesindeki satira tiklama / "Detay" dugmesi.
- **Icerik (salt-okunur + aksiyon):** unvan, VKN maskeli, NACE, sehir,
  kalite skoru, son guncelleme; altinda "Duzenle" ve "Kapat".
- **Kapanma:** Kapat / disari tiklama (bilgi modalı, veri kaybi riski yok).

**Ortak kapanma kurali:** Veri yazan dialoglarda basarisiz islemde dialog
ACIK kalir (girdi korunur); salt-okunur dialoglarda disari tiklama serbesttir.

---

## 3) Grafik/chart karsilastirma

| Kutuphane | Arti | Eksi | Admin KPI uygunlugu |
|---|---|---|---|
| plotly (+ `st.plotly_chart`) | Etkilesimli, tema ozellestirme, kurulu (7.0.0) | Buyuk veride agir | YUKSEK — birincil oneri |
| altair | Deklaratif, yerlesik destek, vega-lite tabanli | Cok buyuk veride yavas | YUKSEK |
| `st.bar_chart` / `st.line_chart` | Sifir kod, hizli | Ozel tema kontrolu sinirli | ORTA — sparkline ve basit seriler |
| vega-lite (ham JSON) | Maksimum esneklik | Bakim maliyeti | DUSUK — altair uzerinden kullan |
| `streamlit-echarts` | Guclu galeri | **Kurulu degil**, ek bagimlilik | DUSUK — su an eklenmesin |

**Admin KPI icin 5 chart onerisi:**

| # | Chart | Veri kaynagi (endpoint) | Tema uyumu |
|---|---|---|---|
| 1 | KPI sparkline (mini cizgi) | `/api/kpi` (gunluk ozet) | `st.line_chart`; koyu/acik otomatik |
| 2 | Kaynak dagilimi donut | `/api/sources` | plotly `pie(hole=0.5)`; renkler `tokens.py` paletinden |
| 3 | Kalite skoru histogram | `/api/quality-trend` | plotly histogram; esik cizgisi sabit renk |
| 4 | NACE top10 yatay bar | `/api/nace-distribution` | plotly yatay bar; etiketler Turkce |
| 5 | Zaman serisi trend | `/api/quality-trend` + `/api/kpi` | plotly cizgi + alan; koyu temada dusuk kontrast grid |

Tema notu: tum oneriler `src/company_master/ui/tokens.py` renk jetonlarini
kullanir; chart icinde sabit renk kodu yazilmaz.

---

## 4) 2026 admin dashboard tasarim referanslari

1. Tremor — https://tremor.so
2. shadcn/ui dashboard bloklari — https://ui.shadcn.com/blocks
3. Vercel Geist — https://vercel.com/geist/introduction
4. Linear metod — https://linear.app/method
5. Grafana dashboard dokumantasyonu — https://grafana.com/docs/grafana/latest/dashboards/
6. Refine admin desenleri — https://refine.dev

---

## 5) Sonuc — MVP oncelik tablosu

| Oneri | Oncelik | Tahmini efor | Dokunulacak dosya |
|---|---|---|---|
| S1 kullanici onayi + tier secici (`st.dialog`) | **P1** | 0.5 gun | `web_dashboard/tabs/admin_extras.py` |
| S5 firma detay karti (`st.dialog` salt-okunur) | **P1** | 0.5 gun | ilgili liste sekmesi + dialog yardimcisi |
| 1–2: sparkline + kaynak donut (plotly) | **P1** | 1 gun | `admin_kpi.py`, `admin_executive.py` |
| S4 sifre degistir dialogu | **P2** | 0.5 gun | `admin_auth.py` + backend endpoint |
| 3–5: histogram + NACE bar + trend (plotly) | **P2** | 1.5 gun | `admin_kpi.py`, `admin_quality.py` |
| S2 kredi yukleme dialogu | **P2** | 0.5 gun | `paketler.py` / `admin_cost.py` |
| S3 kategori duzenle dialogu | **P3** | 0.5 gun | ilgili sekme |
| `st.popover` kucuk aksiyonlar | **P3** | 0.5 gun | ihtiyac duyulan sekmeler |
| `streamlit-echarts` ekleme | **P3 (simdilik YOK)** | — | bagimlilik karari gerekir |

**Toplam P1:** ~2 gun. **P2:** ~3 gun. **P3:** ~1 gun + degerlendirme.

---

## Ek: kapsam disi gozlem (duzeltme YOK)

- `src/company_master/ui/styles.pyX` uzantili gorunuyor (dizin listelemede
  `styles.pyX`): gercek uzanti `.pyX` ise import/discovery disi kalir;
  teyit edilmeden dokunulmadı.
- `web_dashboard/tabs/` altinda `admin_audit.pyX`, `pazarlama.pyX`,
  `admin_extras.pyX` benzer sekilde `X` sonekli gorunuyor; ayni suphe gecerli.
- `src/company_master/ui/__pycache__` ve `web_dashboard/tabs/__pycache__`
  calisma ortami artiklaridir.
- Detay: `data/orchestrator/UI-MODAL-01_bulgular_20260915_cline.md`

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]]

- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
