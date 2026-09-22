# Admin Panel — Ana Sayfa (Ana Kontrol) Wireframe / UX
**Tarih:** 2026-09-18 · **Durum:** KAHİN onayı bekliyor · **Kod yazılmadı**
**Referans:** Claude Console dashboard ekran görüntüsü · `docs/UI_MODAL_CHART_ARASTIRMA_2026-09-15.md`
**Kural (KAHİN, 2026-09-18):** Her sayfa yapılmadan önce wireframe/UX görüntüsü çıkarılır, onay alınır.

---

## 1) AS-IS — Bugün ekranda ne var

Kaynak: `web_dashboard/tabs/ana_kontrol.py` (275 satır)

```
┌──────────────────────────────────────────────────────────────────┐
│ İŞ · OPERASYON                                     (üst etiket)  │
│ Ana Kontrol                                        (H1)          │
│ Hoş geldin metni…                                  (giriş)       │
├──────────────────────────────────────────────────────────────────┤
│ [Veriyi Yenile] [Sekme rehberi ⃝]   Son güncelleme 14:32 · 30 sn │
├──────────────────────────────────────────────────────────────────┤
│ Bu sayfada: Müşteri · Sistem · Uyarılar · Webhook Akışı          │
├──────────────────────────────────────────────────────────────────┤
│ ## Müşteri                                                       │
│ ┌────────┬────────┬────────┬────────┐                            │
│ │Toplam  │Aktif   │Sinyal  │API     │  4 kart · mavi · sparkline │
│ │Firma   │Kullanıcı│Sayısı │Çağrı24h│                            │
│ └────────┴────────┴────────┴────────┘                            │
│ ## Sistem                                                        │
│ ┌────────┬────────┬────────┬────────┐                            │
│ │Sistem  │DLQ     │Cache   │Query   │  4 kart · gri/turuncu      │
│ │Durumu  │Kuyruk  │Hit %   │Latency │                            │
│ └────────┴────────┴────────┴────────┘                            │
│ ## Uyarılar                                                      │
│ [ tek satır st.success / st.warning ]                            │
│ ## Webhook Akışı                                                 │
│ [ donut — veri yok, hep boş state ]                              │
└──────────────────────────────────────────────────────────────────┘
```

### Problem tablosu

| # | Bulgu | Sınıf | Oran / Etki |
|---|-------|-------|-------------|
| 1 | `load_webhook_stats()` **sahte veri** döner — hepsi sıfır. Webhook Akışı donut'u hiç çizilmez, "Uyarılar" hep yeşil | 🔴 | Ekranın **%50'si (4 bölümün 2'si) ölü** |
| 2 | Ekranda **para/gelir yok**. Claude Console'un ilk kartı "credits + spend" | 🔴 | Ticari karar desteği **%0** |
| 3 | 8 kartın 8'i **tek satır sayı**. Trend/eşik/karşılaştırma yok, sparkline yalnız 3 kartta | 🟡 | Kartların **%62'si bağlamsız** |
| 4 | Kartlar tıklanamaz — ilgili sayfaya derin link yok | 🟡 | Sıfır gezinme, her şey sidebar'dan |
| 5 | `st.columns(4)` sabit; 640 px altında kartlar sıkışır | 🟡 | Mobil/tablet **kırılıyor** |
| 6 | "Sekme rehberi" toggle 9 satır metin açıyor, ekranı iter | 🔵 | Yardım içeriği popover olmalı |
| 7 | `PageHeader` + `SectionNav` yapısı sağlam, ton doğru | 🟢 | Korunacak |

---

## 2) TO-BE — Wireframe

Ana sayfanın işi tek soru: **"Bugün her şey yolunda mı, değilse nereye tıklayacağım?"**
Claude Console kalıbı: *para → kullanım → sağlık → kaynaklar*.

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║ İŞ · OPERASYON                                                                ║
║ Ana Kontrol                                            [Veriyi Yenile] [ ? ]  ║
║ Bugünün özeti — 18 Eyl 2026, 14:32 · veri 30 sn'de bir tazelenir              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ ŞERİT 0 — DURUM ÇUBUĞU (tam genişlik, tek satır, koşullu)                     ║
║ ┌───────────────────────────────────────────────────────────────────────────┐ ║
║ │ ● Sistem sağlıklı · 0 kritik uyarı          son olay 12 dk önce  [Detay →] │ ║
║ └───────────────────────────────────────────────────────────────────────────┘ ║
║   yeşil=sağlıklı · sarı=dikkat · kırmızı=blokaj (renk + ● ikon, renk tek başına değil) ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ ŞERİT 1 — TİCARİ (12 kolon → 4 + 4 + 4)                                       ║
║ ┌──────────────────┐┌──────────────────┐┌──────────────────┐                  ║
║ │ Aylık Gelir      ││ Kredi Bakiyesi   ││ Bekleyen Onay    │                  ║
║ │ ₺124.500         ││ 2.480 kredi      ││ 7 başvuru        │                  ║
║ │ ▁▂▃▅▆▇  ▲ %12    ││ ▇▆▅▃▂▁  ▼ %8     ││ en eskisi 2 gün  │                  ║
║ │ geçen aya göre   ││ 14 gün yeter     ││ [Onay kuyruğu →] │                  ║
║ └──────────────────┘└──────────────────┘└──────────────────┘                  ║
║   kaynak: /api/kpi · /api/admin/pending                                        ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ ŞERİT 2 — MÜŞTERİ & KULLANIM (4 kolon x 3)                                     ║
║ ┌────────┐┌────────┐┌────────┐┌────────┐                                       ║
║ │Toplam  ││Aktif   ││Sinyal  ││API 24s │  kompakt kart: sayı + sparkline + Δ%  ║
║ │Firma   ││Kullanıcı││        ││        │  hepsi tıklanabilir → ilgili sayfa    ║
║ │48.210  ││ 312    ││ 1.904  ││ 8.442  │                                       ║
║ │▁▃▅▆ ▲3%││▁▂▂▃ ▲7%││▂▄▃▅ ▬  ││▃▅▇▆ ▲9%│                                       ║
║ └────────┘└────────┘└────────┘└────────┘                                       ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ ŞERİT 3 — GRAFİK (8 kolon + 4 kolon)                                           ║
║ ┌──────────────────────────────────┐┌────────────────────────┐                 ║
║ │ Firma Büyümesi — son 30 gün      ││ Veri Kaynakları        │                 ║
║ │      ╱╲    ╱                     ││      ╭───╮             │                 ║
║ │   ╱─╯  ╲──╯                      ││   ╱ 48.2K ╲   donut    │                 ║
║ │ ╱                                ││  │  firma  │  hole=.5  │                 ║
║ │ plotly area · /api/kpi/history   ││   ╲       ╱            │                 ║
║ │ [7g][30g][90g] segment           ││      ╰───╯             │                 ║
║ └──────────────────────────────────┘│ OSTİM %41 · ASO %33 …  │                 ║
║                                     └────────────────────────┘                 ║
║                                       kaynak: /api/sources                     ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ ŞERİT 4 — SAĞLIK & KALİTE (6 + 6)                                              ║
║ ┌────────────────────────────┐┌────────────────────────────┐                   ║
║ │ Sistem Sağlığı             ││ Veri Kalitesi              │                   ║
║ │ DLQ          0      ✓      ││ ▁▃▇▇▅▂  histogram          │                   ║
║ │ Cache hit    %87    ✓      ││ ortalama 74 / 100          │                   ║
║ │ Query ort.   42 ms  ✓      ││ %68'i 60 puan üstü         │                   ║
║ │ Webhook      12/12  ✓      ││ /api/quality-trend         │                   ║
║ │ [Sistem sağlığı →]         ││ [Kalite raporu →]          │                   ║
║ └────────────────────────────┘└────────────────────────────┘                   ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ ŞERİT 5 — KAYNAKLAR (3 x 4 kolon, sade, ikonlu, link listesi)                  ║
║  📘 Dokümantasyon      🔑 API anahtarları      💬 Destek talepleri              ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### Kart envanteri

| Şerit | Kart | Endpoint | Görsel | Tıkla → |
|-------|------|----------|--------|---------|
| 0 | Durum çubuğu | `/api/kpi` + DLQ | ● nokta + metin | Sistem Sağlığı |
| 1 | Aylık Gelir | `/api/kpi` | sayı + sparkline + Δ% | Gelir & Paketler |
| 1 | Kredi Bakiyesi | `/api/kpi` | sayı + sparkline + "X gün yeter" | Gelir & Paketler |
| 1 | Bekleyen Onay | `/api/admin/pending` | sayı + en eski süre | Kullanıcılar |
| 2 | Toplam Firma | `/api/kpi` + history | sparkline | Müşteriler |
| 2 | Aktif Kullanıcı | `/api/kpi` + history | sparkline | Kullanıcılar |
| 2 | Sinyal Sayısı | `/api/kpi` + history | sparkline | KPI |
| 2 | API Çağrı 24s | `/api/kpi` | sparkline | API Kullanımı |
| 3 | Firma Büyümesi | `/api/kpi/history` | plotly area | KPI |
| 3 | Veri Kaynakları | `/api/sources` | plotly `pie(hole=0.5)` | Teknik Altyapı |
| 4 | Sistem Sağlığı | `/metrics` | 4 satır liste + ✓/⚠ | Sistem Sağlığı |
| 4 | Veri Kalitesi | `/api/quality-trend` | plotly histogram | Veri Kalitesi |
| 5 | Kaynaklar | statik | ikon + link | — |

**Kaldırılan:** Webhook Akışı donut'u (`load_webhook_stats()` sahte veri). Webhook durumu Şerit 4'te tek satıra iner; ayrıntı Sistem Sağlığı sayfasında.

---

## 3) Değişim özeti

| Ölçü | AS-IS | TO-BE | Fark |
|------|-------|-------|------|
| Ekrandaki kart | 8 | 12 | +%50 |
| Gerçek veriye bağlı kart | 8/8 ama 2 bölüm ölü | 12/12 canlı | ölü alan %50 → **%0** |
| Grafik | 1 (hiç çizilmiyor) | 4 (hepsi çizilir) | +%300 |
| Tıklanabilir kart | 0 | 9 | 0 → **%75** |
| Ticari metrik | 0 | 3 | yeni |
| Dikey kaydırma (1440 px) | ~2.1 ekran | ~1.6 ekran | −%24 |

---

## 4) Kurallar

**Chart** — `UI_MODAL_CHART_ARASTIRMA` kararına uyar: plotly 7.0.0 birincil, altair ikincil, yeni paket **yok**. Chart içinde sabit renk kodu yazılmaz; `src/company_master/ui/tokens.py` jetonları kullanılır.

**Responsive**
| Genişlik | Şerit 1 | Şerit 2 | Şerit 3 | Şerit 4 |
|----------|---------|---------|---------|---------|
| ≥1440 px | 3 kolon | 4 kolon | 8+4 | 6+6 |
| 1024 px | 3 kolon | 2x2 | alt alta | 6+6 |
| ≤640 px | alt alta | alt alta | alt alta | alt alta |

**Durumlar** — her kartın 3 hali tanımlı:
- *yükleniyor* → `st.skeleton` yoksa gri placeholder yükseklik sabit (zıplama yok)
- *boş* → "Veri gelince burada görünecek" + ne zaman geleceği
- *hata* → kart içinde tek satır ⚠ + "Yenile" ; sayfa çökmez

**Erişilebilirlik**
- Durum **renk + ikon + metin** ile anlatılır, renk tek başına anlam taşımaz
- Kart kontrastı ≥4.5:1, tıklanabilir kart `role="link"` + görünür odak halkası
- Sekme sırası: üst şerit → durum çubuğu → kartlar (soldan sağa, yukarıdan aşağı)
- `prefers-reduced-motion` açıkken sparkline animasyonu kapalı

---

## 5) Uygulama planı (onay sonrası)

1. `load_webhook_stats()` sahte verisi kaldırılır → gerçek DLQ okuması veya kart düşer
2. `ana_kontrol.py` şerit yapısına göre yeniden dizilir (`BOLUMLER` 4 → 5 şerit)
3. `kpi_karti()` bileşenine `hedef_url` parametresi eklenir (tıklanabilirlik)
4. Şerit 1 ticari kartlar `/api/kpi` + `/api/admin/pending` ile bağlanır
5. Şerit 3 grafikleri `web_dashboard/charts` içine (area + donut + histogram)
6. Test: kart sayısı, boş/hata durumu, endpoint mock — `tests/test_ana_kontrol_ui.py`

**Garanti:** `url_path` ve endpoint sözleşmeleri değişmez; yalnız yerleşim ve görselleştirme değişir.

---

## 6) Figma sorusu — değerlendirme

KAHİN'in sorusu: *"Figma desteği alabilirsin, entegrasyona Figma katabiliriz, ne dersin?"*

### Kısa cevap: **şimdi hayır, Faz 2'de evet.**

| Kriter | Durum | Sınıf |
|--------|-------|-------|
| Arayüz teknolojisi | Streamlit — bileşen seti sabit, Figma'dan kod üretimi **çalışmaz** | 🔴 |
| Mevcut tasarım altyapısı | `tokens.py` + `styles.py` + 11 bileşen **zaten var ve çalışıyor** | 🟢 |
| Figma'nın getirisi | Görsel onay hızı (KAHİN wireframe'i resim olarak görür) | 🟡 |
| Figma'nın maliyeti | Tasarım ile kod **iki ayrı doğruluk kaynağı** olur, senkron bakım yükü | 🔴 |
| MCP/entegrasyon | Figma MCP kurulu değil, lisans + kurulum + öğrenme eğrisi | 🟡 |

**Gerekçe:** Streamlit'te bir Figma ekranını piksel piksel uygulamak mümkün değil; `st.columns`, `st.metric`, `st.dialog` kendi kalıbını dayatır. Figma çizimi kodla örtüşmezse tasarım "yalan doküman" olur — bu, V9 SSOT kuralına aykırı.

**Önerilen ara yol (maliyetsiz, bugün çalışır):**
1. ASCII wireframe → onay (şu anki yöntem, 0 maliyet, kodla %100 örtüşür)
2. Onay sonrası kod → `scripts/streamlit_restart.py` → **canlı ekran** KAHİN'e gösterilir
3. Gerçek ekran görüntüsü = tek doğruluk kaynağı; ayrı tasarım dosyası yok

**Figma ne zaman mantıklı olur:** Streamlit'ten React/Next.js müşteri paneline geçildiğinde (Huginn 🦅 dış yüz). O gün Figma + shadcn/ui + Figma MCP birlikte anlamlı. Şu an iç panel (Muninn 🛡️) için **erken**.

Karar KAHİN'de: "Figma'yı yine de kur" derse görev açılır, itiraz kaydı düşülür.

---

## 7) KAHİN (Ürün Sahibi) özeti

| Renk | Bulgu | Rakam |
|------|-------|-------|
| 🔴 | Ana sayfanın yarısı ölü — Webhook bölümü sahte veri gösteriyor, hiç çizilmiyor | 4 bölümün 2'si, **%50** |
| 🔴 | Para ile ilgili hiçbir bilgi yok. Gelir, kredi, bekleyen onay ekranda görünmüyor | **0** ticari kart |
| 🟡 | Kartların hiçbiri tıklanmıyor; ilgili sayfaya gitmek için hep sol menü gerekiyor | tıklanabilirlik **%0 → %75** |
| 🟡 | Ekran dar ekranda bozuluyor (tablet/telefon) | 640 px altı **kırık** |
| 🟢 | Başlık düzeni ve renk dili doğru, korunuyor | değişiklik **yok** |
| 🔵 | Yeni düzen: 12 kart, 4 grafik, dikey kaydırma **%24 azalıyor** | 8 → 12 kart |
| 🔵 | Figma önerisi: **şimdilik gerek yok** — Streamlit'te karşılığı yok, çift bakım yükü getirir. React paneline geçince değerlendirilir | maliyet **0 TL** ile aynı sonuç |

**Onay verilirse:** 6 adımlık uygulama başlar, ekran testleriyle teslim edilir.
**Onay verilmezse:** hangi şerit değişsin denirse wireframe güncellenir, kod yazılmaz.

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]]

- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
