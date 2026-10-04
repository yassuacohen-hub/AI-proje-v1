# UI-ADMIN-CRAWL-TASI-35 — Crawl Kontrolü Taşıma Raporu

| Alan | Değer |
| --- | --- |
| Görev | `UI-ADMIN-CRAWL-TASI-35` |
| Ajan | `utku` |
| Tarih | 2026-10-04 |
| Durum | ✅ Tamamlandı — teslimata hazır |
| Zincir | `UI-ADMIN-KAYNAKLAR-SAYFA-34` ✅ → **35** → `UI-ADMIN-SON-KAZIMA-KART-36` |
| SSOT | `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md` v2.8 → **v2.9** |

---

## 1. Ne yapıldı

Crawl tetikleme/durdur paneli `webhook_monitor.py`'den **Veri Kaynakları** sayfasına
taşındı. Kod taşındı, davranış **değişmedi**.

| Öğe | Önce | Sonra |
| --- | --- | --- |
| Panel | `webhook_monitor.py:236-302` | `admin_kaynaklar.py:359` `_render_crawl_kontrolu()` |
| Durum sabitleri | `webhook_monitor.py:30-33` | `admin_kaynaklar.py:76-79` |
| `CRAWL_ENABLED` | `webhook_monitor.py` | `admin_kaynaklar.py:81` |
| `CRAWL_DURUM_IKONLARI` | `webhook_monitor.py` | `admin_kaynaklar.py:83-89` |
| `_crawl_is_enabled()` | `webhook_monitor.py:38` | `admin_kaynaklar.py:91` |
| `_log_crawl_action()` | `webhook_monitor.py:42-50` | `admin_kaynaklar.py:96` |
| `import os` | `webhook_monitor.py` | kaldırıldı (kullanılmıyor) |
| Eski yer | — | `webhook_monitor.py:218-228` yönlendirme satırı |

### Yönlendirme (eski sayfada kalan tek iz)

```python
# web_dashboard/tabs/webhook_monitor.py:218-228
st.caption("🕷️ Crawl başlat/durdur → Veri Kaynakları sayfasında")
st.link_button(
    "🕷️ Veri Kaynakları",
    f"/{_kaynaklar_tab.url_path}" if _kaynaklar_tab else "/",
    width="stretch",
    help="Kazımayı tetikleme ve kaynak durumları bu sayfada.",
)
```

Adres `tab_getir("kaynaklar").url_path` üzerinden gelir; `SECTIONS` kaydı olmayan
durumda `/` fallback'i korunur. Döngüsel import yok — `tab_getir` fonksiyon içinde
çağrılır.

### Panel konumu ve seviyesi

`_render_crawl_kontrolu()` çağrısı **Durum Özeti**'nden sonra, **Son Çalışmalar**'dan
önce yer alır. Panel `Section("🕷️ Crawl Kontrolü", ..., seviye=3).render()` ile
çizilir; `BOLUMLER` listesine girmez → **D-213 menü tekliği** bozulmaz (ana menüde
ikinci bir "Crawl Kontrolü" girdisi oluşmaz).

### Korunan davranış (7 madde, birebir)

| # | Davranış | Durum |
| --- | --- | --- |
| 1 | 4 durum: `beklemede` / `calisiyor` / `basarisiz` / `durduruldu` | ✅ aynı değerler |
| 2 | `CRAWL_DURUM_IKONLARI` haritası | ✅ aynı ikonlar |
| 3 | `CRAWL_ENABLED` env kapısı (`os.getenv("CRAWL_ENABLED","0")=="1"`) | ✅ aynı |
| 4 | `admin_email` boşsa butonlar `disabled=True` | ✅ aynı |
| 5 | Başlat → `CRAWL_STATUS_CALISIYOR` + `_log_crawl_action("start")` | ✅ aynı |
| 6 | Durdur iki aşamalı (`crawl_stop_confirm` → `Evet, Durdur`) | ✅ aynı |
| 7 | `st.session_state` anahtarları (`crawl_status`, `crawl_stop_confirm`, `crawl_task_id`) | ✅ aynı |

Ek: butonlara `key=` eklendi (`kaynaklar_crawl_baslat`, `kaynaklar_crawl_durdur`,
`kaynaklar_crawl_evet`, `kaynaklar_crawl_env`) → D-213 anahtar çakışması önlenir,
Streamlit "DuplicateWidgetID" uyarısı engellendi.

---

## 2. Brief varsayımlarının doğrulanması

| Varsayım | Sonuç |
| --- | --- |
| Yardımcıların (`_crawl_is_enabled`, `_log_crawl_action`) dış çağıranı yok | ✅ Doğrulandı — çağrı yalnız panelin kendi içinde |
| Eski blok `webhook_monitor.py:236-302` | ✅ Doğrulandı |
| Sabitler `:30-33`, `_crawl_is_enabled` `:38`, `_log_crawl_action` `:42-50` | ✅ Doğrulandı |
| `webhook_monitor.py` `import os` yalnız crawl bloğu için kullanıyor | ✅ Doğrulandı → kaldırıldı |
| Davranış korunacak (kontrol mantığı değişmeyecek) | ✅ Doğrulandı → yalnız `key=` eklendi |

---

## 3. Test

### Yeni testler — `tests/test_admin_kaynaklar.py` (8 adet)

| Test | Kriter |
| --- | --- |
| `test_crawl_durum_sabitleri_tek_dosyada` | D-211: 3 sembolün tek tanımı, `admin_kaynaklar.py` |
| `test_webhook_monitorde_crawl_kontrolu_kalmadi` | `webhook_monitor.py`'de "Crawl Kontrol" / "Crawl Başlat" **0** |
| `test_webhook_monitor_veri_kaynaklarina_link_verir` | `tab_getir("kaynaklar")` + `st.link_button` |
| `test_crawl_kontrolu_son_calismalardan_once_cizilir` | sıra: crawl → son çalışmalar |
| `test_crawl_kontrolu_seviye3_alt_baslik_ile_cizilir` | `Section(..., seviye=3)`, `BOLUMLER`'de yok |
| `test_crawl_durumu_ve_yetki_korumasi` | yetkisiz `disabled=True`, admin `False` |
| `test_crawl_baslat_durdur_durum_gecisleri` | başlat → calisiyor → onay → durduruldu |
| `test_crawl_durum_ikonlari_dort_durumu_kapsar` | ikon haritası 4 durumu kapsar |

### Kabul seti

```
pytest tests/test_webhook_monitor_tab.py tests/test_admin_kaynaklar.py \
       tests/test_admin_kpi_kart.py tests/test_sekme_kapsama.py \
       tests/test_sayfa_iskeleti.py
→ 213 passed, 2 skipped
```

`tests/test_admin_kaynaklar.py` tek başına: **18 passed** (34'ten 10 + 35'ten 8).

### Statik kabul kontrolleri

| Kontrol | Sonuç |
| --- | --- |
| `"Crawl Kontrol"` → `webhook_monitor.py` (case-sensitive) | **0 satır** |
| `"Crawl Kontrol"` → `webhook_monitor.py` (case-insensitive) | **0 satır** |
| `def _log_crawl_action` repo geneli | tek: `admin_kaynaklar.py` |
| `def _crawl_is_enabled` repo geneli | tek: `admin_kaynaklar.py` |
| `CRAWL_STATUS_*` / `CRAWL_ENABLED` / `CRAWL_DURUM_IKONLARI` repo geneli | tek: `admin_kaynaklar.py:76-89` |

### Kodlama denetimi (`scripts/kodlama_denetim.py`)

Repo toplamı **47 ihlal** (38 `mojibake` + 9 `dosya_sonu`), çıkış kodu 1.

| Kapsam | Sonuç |
| --- | --- |
| Bu göreve ait dosyalar (`admin_kaynaklar.py`, `webhook_monitor.py`, `test_admin_kaynaklar.py`, SSOT, hub, rapor) | ✅ **0 ihlal** |
| Diğer ajanların dosyaları (`etl/nace_sozluk_yukle.py`, `etl/sozluk_baslik_duzelt.py`, `scripts/kazima_qwen_classify.py`, `tests/test_mojibake_bariyer.py`, …) | ⚠️ **47 ihlal, bu ajanların kilidinde** → dokunulmadı |

Task 34 teslimindeki taban 43 → şu an 47. Fark (`nace_sozluk_yukle.py`,
`sozluk_baslik_duzelt.py`, `test_mojibake_bariyer.py`, `dosya_sonu` scriptleri)
`SCRAPE-004-QWEN-SINIFLANDIRMA` / NACE sözlük çalışmalarına ait; bu görevin
dosyaları değil. Orkestratör bilgilendirildi (§6).

---

## 4. SSOT ve hub güncellemeleri

| Dosya | Değişiklik |
| --- | --- |
| SSOT §0 | Versiyon v2.8 → **v2.9**, tarih → 2026-10-04 |
| SSOT §7 (satır 123, Veri Ops) | `🟡 DLQ ✅, crawl kontrolü ❌` → `🟡 DLQ ✅, crawl tetikle/durdur ✅ (Veri Kaynakları), Kaynak Devre Dışı ❌` |
| SSOT §8.1 (satır 279, A8) | `webhook_monitor.py üzerine aksiyon katmanı gerekir` → `✅ admin_kaynaklar.py:359` |
| SSOT §12 (satır 232, §12 satırı) | `Kısmi` → `✅ Tam`, yol `webhook_monitor.py` → `admin_kaynaklar.py`, eski satır referansı kaldırıldı |
| SSOT §12 (satır 440, G8) | Zincir `34 → 35 → 36` → `34 ✅ → 35 ✅ → 36`; "Kalan" yalnız 36'ya indirildi |
| SSOT §14 | v2.9 değişiklik kaydı eklendi |
| `hubs/ADMIN_DASHBOARD_HUB.md:123` | 35 satırı öncelik `-19 (kapandi), -34` → `-19 (kapandi), -34 (kapandi)` |
| `hubs/ADMIN_DASHBOARD_HUB.md:226` | B-14 kapanış satırı eklendi |

§10 backlog satırı 10 ("A8 crawl tetikle/durdur") **değiştirilmedi**: D-197 kural 1-2
gereği maddenin güncel durumu §7'den okunur, backlog sıralaması korunur.

---

## 5. Bulgu / risk

| # | Bulgu | Etki | Karar |
| --- | --- | --- | --- |
| 1 | Taşıma sonrası `st.button` çağrılarında `key=` yoktu → aynı anda başka sekmede aynı etiket varsa Streamlit "DuplicateWidgetID" hatası | Düşük (şu an tek çağrı var, çalışmıyordu) | Görev kapsamında düzeltildi: 4 `key=` eklendi |
| 2 | `_log_crawl_action()` yalnız panel içinde çağrılıyor; crawl gerçekten **başlamıyor** — sadece `session_state` değişiyor ve log yazılıyor | Orta (brief kapsamı dışı; mevcut -19 davranışı korundu) | Orkestratöre `ihsan`'a soruldu: gerçek tetikleme `KazimaYazici`/crawler tarafında mı olmalı? Bkz. §6 |
| 3 | `CRAWL_ENABLED` import anında okunuyor; env değişikliği çalışma zamanında yansımıyor | Düşük (davranış korundu) | Bilinçli koruma — env yeniden yükleme bu görevin kapsamı dışı |
| 4 | `_render_crawl_kontrolu()` yalnız `admin_kaynaklar` içinde çağrılıyor | Yok | D-236 (tüketicisiz kod) riski yok, çağıran mevcut |

---

## 6. Orkestratöre açık soru (chat)

| Soru | Durum |
| --- | --- |
| `saglik_rozet_metni()` → `kaynak_guvenilirlik.py` taşınsın mı? (task 34 bulgusu; 0–1 ↔ 0–100 köprüsü modül içinde kalıyor) | ⏳ Cevap bekleniyor |
| Crawl tetikleme gerçek bir crawler çağrısı olmalı mı, yoksa mevcut "durum + log" davranışı yeterli mi? (§5 bulgu 2) | ⏳ Yeni soruldu |
| `kodlama_denetim.py` tabanı 43 → 47; NACE/QWEN dosyalarındaki artış hangi görev sahibine ait? | ⏳ Yeni soruldu |

---

## 7. Dosya listesi

| Dosya | İşlem |
| --- | --- |
| `web_dashboard/tabs/admin_kaynaklar.py` | sabitler + 2 yardımcı + `_render_crawl_kontrolu()` eklendi, `import os`, çağrı, giriş/rehber metni güncellendi |
| `web_dashboard/tabs/webhook_monitor.py` | `import os`, 6 sabit, 2 yardımcı, kontrol bloğu kaldırıldı → `st.caption` + `st.link_button` yönlendirmesi |
| `tests/test_admin_kaynaklar.py` | docstring + 8 yeni test |
| `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md` | §0, §7, §8.1 A8, §12, §14 |
| `hubs/ADMIN_DASHBOARD_HUB.md` | 35 satırı + B-14 kapanış satırı |
| `data/orchestrator/bulgu_defteri.md` | 2 kayıt |