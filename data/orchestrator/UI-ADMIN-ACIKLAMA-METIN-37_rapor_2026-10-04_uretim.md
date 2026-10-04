# UI-ADMIN-ACIKLAMA-METIN-37 — Üretim Raporu

**Ajan:** utku (Üretim/Hacim) · **Tarih:** 2026-10-04 · **Öncelik:** P2 · **Kit:** ADMIN-KİT
**Durum:** `review` (onay bekliyor)

## Ne yapıldı

`web_dashboard/tabs/__init__.py` içindeki menü ipuçları (`TabTanimi.aciklama`)
teknik jargondan arındırıldı. Yalnız metin değişti; hiçbir gezinme alanı
(`anahtar`, `url_path`, `sira`, `ust`, `grup`, `min_rol`) dokunulmadı.

**Ölçüm (brif varsayımı değil):**

| Ölçüt | Değer |
|---|---|
| `aciklama=` satırı | **37** (brif "~38" demişti) |
| 60 karakteri aşan | **0** (brif "kısalt" öneriyordu, ama hepsi zaten sınırdaydı) |
| Jargonlu satır | **13** |
| Yeniden yazılan metin | **24** |
| Yazım aracı | `data/_tmp/aciklama_metni_guncelle.py` (tek seferlik, idempotent — **iş bitince silindi**, D-166) |

### Eski → yeni (rapor tablosu, sayı eşit: 37 girdi, 37 çıktı)

| # | Eski | Yeni |
|---|---|---|
| 173 | KPI'lar, müşteri ve sistem sağlığı tek bakışta | Müşteri ve sistem sağlığı, ana göstergeler tek bakışta |
| 185 | Firma listesi, filtreler ve kalite bildirimleri | *değişmedi* (jargon yok) |
| 196 | Kampanyalar, segmentler ve segment kapsama analizi | *değişmedi* |
| 208 | 9Router tabanlı AI sohbet ve analiz asistanı | Yapay zekâ asistanı: sohbet ve analiz |
| 224 | MRR/ARR, churn oranı ve tenant sağlık dağılımı — yönetici özeti | Aylık gelir, müşteri kaybı ve sağlık dağılımı |
| 236 | Ticket listesi, olusturma ve durum degistirme | Destek talepleri: açma ve durum değiştirme |
| 248 | Hatalar, webhook olayları ve ölü harf kuyruğu (DLQ) | Hatalar, dış sistemden gelen haberler, takılan işler |
| 260 | Kullanıcı yönetimi ve izin denetimi | *değişmedi* |
| 272 | Sistem kararları ve denetim kayıtları | *değişmedi* |
| 285 | D-192: Ajan sorun takibi — açık/çözündürülmüş/çözüldü metrikler ve son sorunlar | Ajan sorunları: açık, önerilen çözüm ve kapananlar |
| 298 | ALTYAPI-ADMIN-PANO-01: Ajan görevlerinin 4 bölümlü panosu | Ajan görevlerinin dört bölümlü panosu |
| 312 | MIMIR architect raporları — otomatik oluşturuldu, tüm agentle açık | MIMIR mimari raporları: otomatik üretilir, herkese açık |
| 323 | Veri kalitesi ve uyum skoru | *değişmedi* |
| 336 | Global arama ve filtreleme | *değişmedi* |
| 348 | Veri dışa aktarma ve raporlar | *değişmedi* |
| 360 | AI ve sistem maliyeti analizi | Yapay zekâ ve sistem maliyeti analizi |
| 373 | Kazıma kaynakları: son çalışma, hata ve toplanan sayfa | *değişmedi* |
| 385 | Süreç diyagramı, servis haritası ve performans metrikleri | *değişmedi* |
| 398 | Sistem performansı ve gecikme metriği | *değişmedi* |
| 410 | API analitiği ve kullanım | Sunucu isteği analizi ve kullanımı |
| 422 | Webhook izleme ve durum | Dış sistemden gelen haberlerin durumu |
| 435 | Otomatik yenileme ayarları | *değişmedi* |
| 447 | Performans, maliyet, webhook, DLQ ve denetim izi | Performans, maliyet, takılan işler ve denetim izi |
| 459 | Gerçek zamanlı sinyal akışı (SSE) | Gerçek zamanlı sinyal akışı |
| 472 | Denetim izi, KVKK modu ve MFA yönetimi — erişim ve uyum kontrolleri | Denetim izi, kişisel veri ve giriş güvenliği ayarları |
| 485 | KVKK strict/lenient mode toggle, gecmis ve trend analizi | Kişisel veri modu, geçmiş ve eğilim analizi |
| 499 | Maskeli/açık alanlar, tier dağılımı, trend ve mode geçişleri | Maskeli alanlar, paket dağılımı ve eğilimler |
| 513 | Sistem feature flag'lerini yönetin (admin only) | Sistem özellik anahtarlarını yönetin (yalnız admin) |
| 526 | Müşteri yaşam boyu değeri (LTV) ve kazanım maliyeti (CAC) analizi | Müşteri kazandırma maliyeti ve yaşam boyu değeri |
| 539 | Kredi yükleme, paket kategorileri ve tier yönetimi | Kredi yükleme, paket kategorileri ve paket yönetimi |
| 553 | Çok faktörlü kimlik doğrulama (TOTP) ayarları | İki adımlı giriş doğrulama ayarları |
| 566 | Görünüm, veri, bildirim ve bölgesel kullanıcı tercihleri (P7-46) | Görünüm, veri, bildirim ve bölge tercihleri |
| 579 | Loading state örnekleri ve skeleton gosterim (P7-42) | Yükleniyor göstergesi ve iskelet ekran örnekleri |
| 591 | Müşteri yönetim, paket, giriş ve destek ana sayfa | *değişmedi* |
| 604 | Karar defteri, açık işler, denetim izi ve hatalar | *değişmedi* |
| 617 | KPI, kalite, arama ve executive özeti | Ana göstergeler, kalite, arama ve yönetici özeti |
| 630 | Paketler ve pazarlama müşteri ekranı (Huginn önizleme) | Paketler ve müşteri ekranı önizlemesi (Huginn) |

## Değişen dosyalar

| Dosya | Değişiklik |
|---|---|
| `web_dashboard/tabs/__init__.py` | 24 `aciklama` string'i |
| `tests/test_dashboard_nav.py` | `import re` + 2 test + `JARGON`/`_JARGON_DESEN` sabitleri |
| `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md` | §0 v2.11 · §7 yeni "Menü ipucu teknik jargonsuz (K2)" satırı · §14 v2.11 kaydı · §12 G8 ve §7 36 satırında `:488 → :490` düzeltmesi |
| `AGENTS.md` | D-196 kit tablosu v2.8 → **v2.11** |
| `hubs/ADMIN_DASHBOARD_HUB.md` | B-14 kapanan işler satırı + 36 satırı `:490` düzeltmesi |
| `data/_tmp/aciklama_metni_guncelle.py` | tek seferlik yazım betiği — teslimden önce **silindi** (D-166) |

### Kodlama denetimi

`python scripts/kodlama_denetim.py` → `dosya_sonu` **10** (9 değil; başka ajanların
dosyaları), `mojibake` listesi de büyüdü. **Bu görevin iki dosyası
(`tabs/__init__.py`, `tests/test_dashboard_nav.py`) taramada çıkmadı** — temiz.
Tam repo tabanı başka ajanlara ait; düzeltilmedi (D-260: sahibi olmayan borca
dokunulmaz).

## Test sonuçları

| Komut | Sonuç |
|---|---|
| `pytest -q tests/test_dashboard_nav.py tests/test_tabs_ia.py tests/test_sekme_kapsama.py` | **208 passed, 3 skipped** (4.57 s) |
| `pytest -q tests/test_dashboard_nav.py -k aciklama` (bozuk hali) | **1 failed** — `assert not [('executive', 'DLQ kuyrugu ve KPI dağılımı')]` |
| `pytest -q tests/test_dashboard_nav.py -k aciklama` (geri alındı) | **2 passed** |

**Kırma kanıtı (D-256/4 zorunlu):** `executive` satırına geçici
`aciklama="DLQ kuyrugu ve KPI dağılımı"` yazıldı → mandal kırmızı verdi ve
hangi `anahtar`'da olduğunu raporladı → metin geri alındı → yeşil. Mandal
gerçekten kırılabiliyor; yeşil sonuç bir tesadüf değil.

## Bulgular

| Renk | Bulgu | Kanıt | Karar |
|---|---|---|---|
| 🟡 | **Düz alt-dize jargon kontrolü meşru Türkçeyi yasaklar.** "Paketler" kelimesi `Pak`+`etl`+`er` → "ETL" alt-dizesi taşıyor. Brifin istediği düz `in` kontrolü 1 yanlış pozitif üretirdi. | Ölçüldü: 37 metinden 1'i (`L630`) "ETL" ile eşleşiyordu. | Mandal `\b` (kelime sınırı) ile yazıldı; negatif kontrol `assert not _JARGON_DESEN.search("Paketler ve musteri ekrani")` teste gömüldü. Düz `in` yazılırsa mandal kırılır. |
| 🔵 | **Tüketici zaten vardı, ikinci tüketici yazılmadı.** `app.py:render_topbar` `:616-618` `st.caption` ile `tanim.aciklama` basıyor. | `tests/test_dashboard_nav.py:207` zaten `tanim.aciklama` doluluğunu zorunlu kılıyor. | D-211 gereği yeni render noktası açılmadı; yalnız veri kaynağı metni değişti. |
| 🔵 | **Brif "~38" dedi, ölçüm 37.** | `Select-String 'aciklama='` → 37. | Raporda ve SSOT'ta gerçek sayı yazıldı (D-224). |
| 🔵 | **D-210 teslim kapısı kendi kaydını sayıyordu (task 36).** `UI-ADMIN-SON-KAZIMA-KART-36` teslimi `kimden=utku` olmasına rağmen "açık sorun var" ile reddedildi; D-321/2 `ajan_acik_sorulari` filtresinin `kimden != ajan` olması gerektiğini yazıyor. | `gorev_kutusu.py teslim` → `HATA: Acik sorun var — kimden: utku`. Kayıt `cokundurmus` yapılınca teslim geçti. | `bulgu_defteri.md`'ye yazıldı. Orkestratör (ihsan) kararına bırakıldı: filtre düzeltmeli ya da kural "kendi sorununu çözüm önerisiyle kapat" olarak yazılmalı. |

## Eksik / erteleme

- **Eksik yok.** Brifin dört maddesi de yapıldı: metin dönüşümü, tek assert,
  kırma kanıtı, SSOT §7 + hub kaydı.
- **Ertelenen (kapsam dışı, bu görevin kilidi değil):**
  - `aciklama` metinlerinin **görsel** doğrulaması (ekran görüntüsü) yapılmadı;
    60 karakter sınırı ölçüldü ama topbar satır kaydı gözle doğrulanmadı.
  - `docs/ADMIN_8SAYFA_VIZYON_KAPSAM.md:44` (KK-12 K2) metin listesi SSOT ile
    eşitlenmedi — o belge kaynak değil, boşluk kaydı; D-220 Kural 1 gereği
    kanonik yol SSOT §7'dir.
  - `aciklama` alanında teknik kısaltma **ölçümü sonrası 2** kaldı ve ikisi de
    **bilinçli**: `MIMIR mimari raporları…` (MIMIR bir ajan adı — marka/marka
    kuralı: yasak yazımlar `Munin/Muginn`; kanonik `MIMIR` duruyor) ve
    `(yalnız admin)` (hedef kitle tanımı — paneldeki rol). `KVKK`, `MFA`, `API`,
    `SSE`, `TOTP`, `LTV`, `CAC` **0** çıktı (ölçüldü, kelime sınırıyla).
    Bunları da çözmek isteyen varsa karar ihsana aittir.

## İlgili Nodlar

- [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-ACIKLAMA-METIN-37]] — brif
- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]] — ADMIN-KİT SSOT §7
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]] — B-14 kapanan işler
- [[Huginn Data Insights/docs/ADMIN_8SAYFA_VIZYON_KAPSAM]] — KK-12 K2 kaynağı
- [[tests/test_dashboard_nav]] — yeni mandal
- [[web_dashboard/tabs/__init__]] — değişen kaynak
- [[Huginn Data Insights/AGENTS]] — D-196 / D-211 / D-224 / D-256