# UI-ADMIN-ACIKLAMA-METIN-37 — Brief (utku)

**Başlık:** [ADMIN-KİT] SECTIONS `aciklama` metinlerini admin diline çevir → menü ipucu teknik jargonsuz (2 saat)
**Öncelik:** P2 · **Kit:** `ADMIN-KİT` (AGENTS.md D-196)
**Kilitli dosya:** `web_dashboard/tabs/__init__.py` (yalnız `aciklama=` string'leri), `tests/test_dashboard_nav.py`
**Bağımlılık:** yok (34-36'dan bağımsız; `kaynaklar` sekmesi eklendiyse onu da kapsa)
**Hub:** `hubs/ADMIN_DASHBOARD_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

> **Tek brif kuralı (D-217):** Bağımsız iş. Zincir 34-36 ile aynı anda `__init__.py` kilidi çakışır → 34 teslim edilmeden **başlama**.

## Neden
- KK-12 K2: ~38 `aciklama` string'i ("DLQ", "webhook", "ETL", "KPI", "latency") — admin genç/düşük teknik; menü ipucu okunmuyor. `docs/ADMIN_8SAYFA_VIZYON_KAPSAM.md:44`.
- Tüketici: `app.py:render_topbar` (`:616-618`), `IPUCU_KEY="_hg_menu_ipucu_ac"` (`:92`), footer toggle `:749-751`. **`_nav_ipucu` (`:370-379`) None döner, tüketici değil** — boşluk belgesi yanlış yazmıştı, düzeltildi.
- SSOT §7 "Menü ipucu" satırı.

## Doğrulanacak varsayım
- `aciklama` alanı `TabTanimi` (`__init__.py:106-164`) içinde `str`; `tests/test_dashboard_nav.py:205-207` boş olmamasını ister, uzunluk sınırı var mı ölç (`findstr /N "aciklama" tests\test_dashboard_nav.py`).
- `render_topbar :616-618` `tanim.aciklama`'yı `st.caption` ile basar; kalıp değişmez.
- `sekme_kapsama` / `tabs_ia` testleri `aciklama` içeriğine bağlı değil (ölç: `findstr /S /C:"aciklama" tests\*.py`).
- Sayı: `findstr /C:"aciklama=" web_dashboard\tabs\__init__.py | find /C "aciklama"` → raporda gerçek sayı.

## Adımlar
1. Ölç: tüm `aciklama=` satırlarını listele (`findstr /N`), rapora tablo: eski → yeni.
2. Kural: ≤ 60 karakter, fiil + sonuç, kısaltma yok ("DLQ" → "takılan işler", "webhook" → "dış sistemden gelen haber", "ETL" → "veri yükleme", "latency" → "gecikme süresi").
3. Yalnız string'leri değiştir; `anahtar`, `url_path`, `sira`, `ust` **dokunulmaz** (ESKI_URL `:631-638` bozulmaz).
4. `tests/test_dashboard_nav.py`'ye tek assert: hiçbir `aciklama` `("DLQ","ETL","KPI","webhook","latency")` içermez (küçük/büyük harf duyarsız).
5. SSOT §7 satırı.

## Kabul kriteri
- [ ] `python -m pytest -q tests/test_dashboard_nav.py tests/test_tabs_ia.py tests/test_sekme_kapsama.py` yeşil.
- [ ] Yeni jargon-yok assert'ü yeşil; **kırılarak** doğrulandı (D-256/4: bir tane geçici "DLQ" koy, kırmızı gör, kaldır — çıktı raporda).
- [ ] Eski → yeni tablo raporda (sayı eşit).
- [ ] SSOT §7 + hub "Kapanan işler".

## Kurallar (ADMIN-KİT · D-196)
- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`.
- **Görev sonunda** ilerlemeyi SSOT §7 satırına işle.
- Kanıtsız durum beyanı yasak.
- Metin dışı değişiklik yok; Türkçe karakter korunur (`# -*- coding: utf-8 -*-`).
- **Teslimden önce** hub "Kapanan işler" satırı (B-14).

## Ajan chat zorunlu (D-210 · D-217)
- Varsayım tutmuyorsa → `ac`, uydurma.
- Tıkandıysa → sorun aç, sonraki adıma geç.
- @mention → P1 10-15 dk.

```bash
python scripts/ajan_chat.py ac utku UI-ADMIN-ACIKLAMA-METIN-37 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id UI-ADMIN-ACIKLAMA-METIN-37
python scripts/chat_gonder.py --to ihsan --type hata --task-id UI-ADMIN-ACIKLAMA-METIN-37 --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id UI-ADMIN-ACIKLAMA-METIN-37 --ozet "<özet>"
```

**Teslimden sonra DURMAK YASAK (D-312 · D-335).**

```bash
python scripts/gorev_kutusu.py nobet --ajan utku
```

- Çıkış `0` = İŞ VAR → sıradaki `UI-ADMIN-REHBER-ALAN-38`.
- Çıkış `3` → ihsan'a kısa rapor, kapat.

## Ilgili Nodlar
- [[Huginn Data Insights/docs/ADMIN_8SAYFA_VIZYON_KAPSAM]] — K2
- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]] — §7
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
- [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-SON-KAZIMA-KART-36]] — önceki
- [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-REHBER-ALAN-38]] — sonraki
- [[Huginn Data Insights/AGENTS]]
- [[plans/_brief_sablon]]
