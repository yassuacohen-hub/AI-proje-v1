# UI-ADMIN-SON-KAZIMA-KART-36 — Brief (utku)

**Başlık:** [ADMIN-KİT] Ana Kontrol'e "Veri Kaynakları" giriş kartı ekle → son kazıma tek tıkla görünür (1 saat)
**Öncelik:** P2 · **Kit:** `ADMIN-KİT` (AGENTS.md D-196)
**Kilitli dosya:** `web_dashboard/tabs/ana_kontrol.py`, `tests/test_ana_kontrol_overview.py`
**Bağımlılık:** `UI-ADMIN-KAYNAKLAR-SAYFA-34` (`kaynaklar` sekmesi SECTIONS'ta olmalı)
**Hub:** `hubs/ADMIN_DASHBOARD_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

> **Tek brif kuralı (D-217):** Zincir 34 → 35 → **36**. 34 teslim edilmeden başlama (35 ile paralel olabilir, dosya çakışmaz).

## Neden
- KK-12 K1c: Ana Kontrol'de "son kazıma ne zaman, kaç sayfa" sorusuna cevap yok; admin Webhook'a inmek zorunda. `docs/ADMIN_8SAYFA_VIZYON_KAPSAM.md:42`.
- Giriş kartları `ana_kontrol.py:78-84` `GIRIS_KARTLARI` tuple'ı — 4 kart var (`("📊","Metrikler","veri_kalite")` dahil). 5. kart eklemek = tek satır.
- SSOT §7 "Ana Kontrol giriş kartları" satırı.

## Doğrulanacak varsayım
- `GIRIS_KARTLARI: tuple[tuple[str, str, str], ...]` biçimi `(ikon, etiket, tab_anahtar)`; `tests/test_ana_kontrol_overview.py:27` bu tuple'ı `tab_getir` ile doğrular. Kaymışsa satırı ölç.
- Kart çizimi `st.link_button(..., f"/{tanim.url_path}")` deseni (`ana_kontrol.py:487-490`); 5 kart kolon sayısını bozuyorsa `st.columns(len(GIRIS_KARTLARI))` zaten dinamik mi ölç — sabit `st.columns(4)` ise dinamiğe çevir.
- `_hareket_satiri` (`:292-301`) genel yardımcı; "son kazıma" satırı **buraya değil** karta gider (boşluk belgesi :42/:59 yanlış yazmıştı, düzeltildi).
- Kart altına opsiyonel `st.caption` ile son kazıma zamanı: `scrape_audit_log` `MAX(created_at)` — `@st.cache_data(ttl=60)`, D-238 canlı ölçüm, DB yoksa `"—"`.

## Adımlar
1. `GIRIS_KARTLARI`'na `("🕷️", "Veri Kaynakları", "kaynaklar")` ekle.
2. Kolon sayısı sabitse `len(GIRIS_KARTLARI)` yap.
3. Kart altı caption: `son_kazima_zamani()` küçük yardımcı (tek sorgu, try/except → `"—"`), D-213 veri etiketi `_veri_etiketi(gercek=["scrape_audit_log"], sahte=[])`.
4. `tests/test_ana_kontrol_overview.py` kart sayısı 4→5; `tab_getir("kaynaklar")` ile anahtar doğrulaması zaten var — yeşil kalmalı.
5. SSOT §7 satırı güncelle.

## Kabul kriteri
- [ ] `python -m pytest -q tests/test_ana_kontrol_overview.py tests/test_dashboard_nav.py tests/test_sekme_kapsama.py` yeşil.
- [ ] `findstr /C:"kaynaklar" web_dashboard\tabs\ana_kontrol.py` → `GIRIS_KARTLARI` satırı görünür.
- [ ] Ana Kontrol ekranında 5. kart `/kaynaklar`'a gider (ekran görüntüsü yolu raporda).
- [ ] SSOT §7 + hub "Kapanan işler".

## Kurallar (ADMIN-KİT · D-196)
- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`.
- **Görev sonunda** ilerlemeyi SSOT §7 satırına işle.
- Kanıtsız durum beyanı yasak.
- Yeni bağımlılık, şema, göç yok.
- **Teslimden önce** hub "Kapanan işler" satırı (B-14).

## Ajan chat zorunlu (D-210 · D-217)
- Varsayım tutmuyorsa → `ac`, uydurma.
- Tıkandıysa → sorun aç, sonraki adıma geç.
- @mention → P1 10-15 dk.

```bash
python scripts/ajan_chat.py ac utku UI-ADMIN-SON-KAZIMA-KART-36 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id UI-ADMIN-SON-KAZIMA-KART-36
python scripts/chat_gonder.py --to ihsan --type hata --task-id UI-ADMIN-SON-KAZIMA-KART-36 --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id UI-ADMIN-SON-KAZIMA-KART-36 --ozet "<özet>"
```

**Teslimden sonra DURMAK YASAK (D-312 · D-335).**

```bash
python scripts/gorev_kutusu.py nobet --ajan utku
```

- Çıkış `0` = İŞ VAR → sıradaki `UI-ADMIN-ACIKLAMA-METIN-37`.
- Çıkış `3` → ihsan'a kısa rapor, kapat.

## Ilgili Nodlar
- [[Huginn Data Insights/docs/ADMIN_8SAYFA_VIZYON_KAPSAM]] — K1c
- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]] — §7
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
- [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-KAYNAKLAR-SAYFA-34]] — öncül
- [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-CRAWL-TASI-35]] — kardeş
- [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-ACIKLAMA-METIN-37]] — sonraki
- [[Huginn Data Insights/AGENTS]]
- [[plans/_brief_sablon]]
