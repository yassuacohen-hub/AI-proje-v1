# UI-ADMIN-SON-KAZIMA-KART-36 — Üretim Raporu (utku)

**Tarih:** 2026-10-04 · **Kit:** ADMIN-KİT · **Öncelik:** P2 · **Durum:** **KISMİ** (kod + test tamam, çizim kararı bekliyor)

## Ne yapıldı

- `web_dashboard/tabs/ana_kontrol.py:85` → `GIRIS_KARTLARI`'a beşinci kart eklendi:
  `("🕷️", "Veri Kaynakları", "kaynaklar")`. Tuple 4 → 5 kart.
- `tests/test_ana_kontrol_overview.py` → `test_giris_kartlari_bes_kart_ve_veri_kaynaklari_var`
  eklendi: kart sayısı 5, `"kaynaklar"` anahtarı tuple'da, `tab_getir("kaynaklar").url_path == "kaynaklar"`.
- Ölçülen üç bulgu `ajan_chat` + `chat_gonder` ile ihsan'a açıldı (`2026-10-04T01:24`).
- SSOT: §7'ye "Ana Kontrol giriş kartı → Veri Kaynakları (K1c)" satırı eklendi; §12 G8
  zinciri `34 ✅ → 35 ✅ → 36 🟡 (kısmi)`; §14'e **v2.10**; §0 sürümü v2.9 → v2.10.
- Hub `hubs/ADMIN_DASHBOARD_HUB.md`: B-14 kapanış satırı + görev tablosu `-34/-35 (kapandi)`.

### Neden kısmi (brif varsayımı tutmadı — D-217)

Brif: *"Giriş kartları `ana_kontrol.py:78-84` … 5. kart eklemek = tek satır."* Ölçüm:

| Ölçüm | Sonuç |
|---|---|
| Repo genelinde `GIRIS_KARTLARI` referansı | **2** — tanım `ana_kontrol.py:78`, test `test_ana_kontrol_overview.py:28` |
| `render_ana_kontrol()` içindeki `st.link_button` | **1** — aksiyon şeridi b1 "Firmalar" (`:488`) |
| `GIRIS_KARTLARI`'ı çizen fonksiyon | **0** |

Tuple **ölü kod**: hiçbir yerde render edilmiyor. Beşinci kart eklemek ekrana hiçbir şey
getirmiyor; "5. kart `/kaynaklar`'a gider" kriteri bu haliyle karşılanamaz.

İkinci sapma — kolon: brif `MAX(created_at)` diyor. `0050_scrape_audit_log.sql`
ölçüldü: `:20 timestamp TIMESTAMPTZ NOT NULL DEFAULT now()` (çekiş zamanı) ve
`:32 created_at` (satır ekleme) **ikisi de var**. `admin_kaynaklar.py:142` zaten
`MAX(timestamp)` kullanıyor; `created_at` ile ikinci bir "son kazıma" tanımı
(D-211 ikiz) ve iki sayfa arasında ayrışma riski doğardı.

## Değişen dosyalar

| Dosya | Değişiklik |
|---|---|
| `web_dashboard/tabs/ana_kontrol.py` | +2 satır (5. kart + yorum) |
| `tests/test_ana_kontrol_overview.py` | +8 satır (1 yeni test) |
| `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md` | §0 sürüm, §7 yeni satır, §12 G8, §14 v2.10 |
| `hubs/ADMIN_DASHBOARD_HUB.md` | B-14 kapanış satırı + görev tablosu |
| `data/orchestrator/ajan-chat.jsonl` | 1 sorun kaydı (ihsan) |
| `data/orchestrator/chat/messages.jsonl` | 1 soru mesajı (ihsan) |

Yeni bağımlılık, şema veya göç **yok**.

## Test sonuçları

| Komut | Sonuç |
|---|---|
| `pytest -q tests/test_ana_kontrol_overview.py tests/test_dashboard_nav.py tests/test_sekme_kapsama.py` | **204 passed, 3 skipped** |
| `pytest -q tests/test_taslak_sahte_veri.py tests/test_sayfa_iskeleti.py tests/test_admin_kaynaklar.py` | **130 passed** |
| `findstr /C:"kaynaklar" web_dashboard\tabs\ana_kontrol.py` | `("🕷️", "Veri Kaynakları", "kaynaklar"),` ✔ |

Bilinen ön-mevcut hata: **yok** (bu turun kabul seti tamamen yeşil).

## Bulgular

- 🟡 **Dikkat — `GIRIS_KARTLARI` ölü kod (brif varsayımı yanlış).** Tuple hiç çizilmiyor;
  5. kart ekranda görünmez. `tests/test_ana_kontrol_overview.py:27` yalnız `tab_getir`
  eşleşmesini doğruluyor, **görünürlüğü değil** — test yeşil, ekran boş (D-266:
  mandalın göremediği yer). Karar ihsan'a açıldı.
- 🟡 **Dikkat — "Firmalar" düğmesi zaten aksiyon şeridinde.** `ana_kontrol.py:488`
  (K3-10f kararı). Tuple'dan tam bir giriş kartı satırı çizilirse aynı ekranda
  ikinci "Firmalar" linki doğar (D-211 ikiz yasağı) — bu yüzden karar kendiliğinden
  verilmedi.
- 🔵 **Bilgi — `scrape_audit_log` iki zaman kolonu taşıyor.** `timestamp` (çekiş,
  NOT NULL) ve `created_at` (satır ekleme). "Son kazıma" tanımı tek yerde
  (`admin_kaynaklar.py:142`) kalmalı; ikinci yazım ikiz olur.
- 🔴 **Bulgu yok** (yukarıdakiler brif varsayımı düzeltmeleridir, ayrı görev konusu değildir).

## Eksik / erteleme

1. **Giriş kartlarının çizimi** — karar bekliyor (3 seçenek soruldu):
   (a) `GIRIS_KARTLARI`'dan 5 kartlı satır → "Firmalar" ikizi (D-211);
   (b) aksiyon şeridine 6. `link_button` → mevcut 4 buton / 4 renk (`_AKSIYON_RENK`) yapısı bozulur;
   (c) tuple'ı sil.
2. **`son_kazima_zamani()` yardımcısı + `st.caption`** — çizim kararından sonra yazılacak
   (tüketicisi olmayan kod yazılmaz, D-236). Kolon `timestamp` olacak (ölçüm yukarıda).
3. **Ekran görüntüsü** — (1) uygulanmadan alınamaz; kriter bilinçli olarak açık bırakıldı.
4. `_hareket_satiri` (`:292-301`) ile ilgili brif maddesi: ölçüm sonucu **değişiklik
   gerekmiyor** — "son kazıma" satırı kartın altına gider, `_hareket_satiri` dokunulmaz.

## İlgili Nodlar

- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]] — §7 / §12 G8 / §14
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]] — B-14 kapanış izi
- [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-SON-KAZIMA-KART-36]] — brif
- [[web_dashboard/tabs/ana_kontrol]] · [[tests/test_ana_kontrol_overview]]
- [[Huginn Data Insights/data/orchestrator/bulgu_defteri]] — bulgular (2 satır eklendi)