# UI-ADMIN-REHBER-ALAN-38 — Brief (utku)

**Başlık:** [ADMIN-KİT] `TabTanimi.rehber` alanı ekle → 6 dağınık `_hg_rehber` okuyucusu tek kapıdan geçer (3 saat)
**Öncelik:** P2 · **Kit:** `ADMIN-KİT` (AGENTS.md D-196)
**Kilitli dosya:** `web_dashboard/tabs/__init__.py` (`TabTanimi` + SECTIONS `rehber=`), `app.py` (`render_icerik`), 6 okuyucu: `admin_realtime.py`, `admin_panel.py`, `admin_musteriler.py`, `paketler.py`, `pazarlama.py`, `ana_kontrol.py`
**Bağımlılık:** `UI-ADMIN-ACIKLAMA-METIN-37` (aynı `__init__.py` kilidi; 37 teslim edilmeden başlama)
**Hub:** `hubs/ADMIN_DASHBOARD_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

> **Tek brif kuralı (D-217):** Sıra 37 → **38**. Zincir 34-36 ile `app.py` çakışmaz; `ana_kontrol.py` 36 ile çakışır → 36 da kapanmış olmalı.

## Neden
- KK-12 K3: "Rehber" açıklaması 6 dosyada ayrı ayrı `st.session_state.get("_hg_rehber")` ile çizilir; yeni sayfa açan unutuyor (34'te `admin_kaynaklar.py` 7. kopya olacaktı). `docs/ADMIN_8SAYFA_VIZYON_KAPSAM.md:46`. D-211 ikiz yasağı, D-212 tek adres.
- Tek kapı: `app.py:render_icerik` (`:693-724`), `fn()` çağrısı `:712`.
- SSOT §7 "Rehber modu" satırı.

## Doğrulanacak varsayım
- Okuyucular: `admin_realtime.py:205`, `admin_panel.py:408`, `admin_musteriler.py:53`, `paketler.py:245`, `pazarlama.py:339`, `ana_kontrol.py:731`. `findstr /S /N /C:"_hg_rehber"` ile **yeniden ölç**; 7. varsa listeye ekle.
- Footer toggle `app.py:749-751` `_hg_rehber`'i yazar; **dokunulmaz**.
- `TabTanimi` `frozen=True` dataclass (`__init__.py:106`); yeni alan `rehber: str = ""` varsayılanlı → mevcut 38+ `TabTanimi(...)` çağrısı kırılmaz. `__post_init__` (`:144-154`) doğrulama ekliyorsa `rehber` için ekleme.
- Her okuyucunun bastığı metin farklı (`st.info` / `st.caption` / expander?) — ölç; tek kalıp `st.info(tanim.rehber)` seçildi, farklı kalıp varsa chat'te sor.
- `tests/test_dashboard_nav.py`, `tests/test_tabs_ia.py` `TabTanimi` alan sayısına bağlı değil (ölç: `findstr /C:"fields(" tests\*.py`).

## Adımlar
1. `__init__.py` `TabTanimi`'ye `rehber: str = ""` ekle (alan sırası sona).
2. 6 okuyucudaki rehber metnini ilgili `TabTanimi(... rehber="...")` satırına taşı (kopya değil, **taşı**).
3. `app.py:render_icerik` `fn()` sonrası (`:712` civarı, try içinde):
   ```python
   if tanim.rehber and st.session_state.get("_hg_rehber"):
       st.info(tanim.rehber)
   ```
4. 6 okuyucudaki `_hg_rehber` bloklarını sil; `findstr /S /C:"_hg_rehber"` → yalnız `app.py` (footer + render_icerik) kalır.
5. Test: `tests/test_tabs_ia.py`'ye assert — `ust is None` olan her bölümün `rehber` boş değil (kök sayfalar rehbersiz kalmaz).
6. SSOT §7 satırı.

## Kabul kriteri
- [ ] `python -m pytest -q tests/test_dashboard_nav.py tests/test_tabs_ia.py tests/test_sekme_kapsama.py tests/test_sayfa_iskeleti.py tests/test_ana_kontrol_overview.py` yeşil.
- [ ] `findstr /S /N /C:"_hg_rehber" web_dashboard\tabs\*.py` → 0 satır; `app.py` → footer + render_icerik (çıktı raporda).
- [ ] Rehber toggle açıkken her kök sayfada `st.info` görünür (manuel, ekran görüntüsü yolu raporda).
- [ ] SSOT §7 + hub "Kapanan işler".

## Kurallar (ADMIN-KİT · D-196)
- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`.
- **Görev sonunda** ilerlemeyi SSOT §7 satırına işle.
- Kanıtsız durum beyanı yasak.
- Davranış aynı kalır (metin aynı, yer aynı); yalnız kaynak tekleşir.
- **Teslimden önce** hub "Kapanan işler" satırı (B-14).

## Ajan chat zorunlu (D-210 · D-217)
- Varsayım tutmuyorsa → `ac`, uydurma.
- Tıkandıysa → sorun aç, sonraki adıma geç.
- @mention → P1 10-15 dk.

```bash
python scripts/ajan_chat.py ac utku UI-ADMIN-REHBER-ALAN-38 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id UI-ADMIN-REHBER-ALAN-38
python scripts/chat_gonder.py --to ihsan --type hata --task-id UI-ADMIN-REHBER-ALAN-38 --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id UI-ADMIN-REHBER-ALAN-38 --ozet "<özet>"
```

**Teslimden sonra DURMAK YASAK (D-312 · D-335).**

```bash
python scripts/gorev_kutusu.py nobet --ajan utku
```

- Çıkış `0` = İŞ VAR → sıradaki görev.
- Çıkış `3` → ihsan'a kısa rapor, kapat.

## Ilgili Nodlar
- [[Huginn Data Insights/docs/ADMIN_8SAYFA_VIZYON_KAPSAM]] — K3
- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]] — §7
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
- [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-ACIKLAMA-METIN-37]] — öncül
- [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-KAYNAKLAR-SAYFA-34]] — rehber alanını kullanacak ilk yeni sayfa
- [[Huginn Data Insights/AGENTS]]
- [[plans/_brief_sablon]]
