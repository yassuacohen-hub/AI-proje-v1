# UI-ADMIN-CRAWL-TASI-35 — Brief (utku)

**Başlık:** [ADMIN-KİT] Crawl Kontrolü bloğunu Webhook'tan "Veri Kaynakları" sayfasına taşı → tek OSINT adresi (2 saat)
**Öncelik:** P1 · **Kit:** `ADMIN-KİT` (AGENTS.md D-196)
**Kilitli dosya:** `web_dashboard/tabs/webhook_monitor.py`, `web_dashboard/tabs/admin_kaynaklar.py`, `tests/test_webhook_monitor_tab.py`
**Bağımlılık:** `UI-ADMIN-KAYNAKLAR-SAYFA-34` (sayfa var olmalı), `UI-ADMIN-SAYFA-ISKELET-19` (kapandı)
**Hub:** `hubs/ADMIN_DASHBOARD_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

> **Tek brif kuralı (D-217):** Zincir 34 → **35** → 36. 34 teslim edilmeden başlama.

## Neden
- KK-12 K1b: Crawl başlat/durdur "Webhook Monitor" altında gömülü; admin bunu "kazıma" olarak arar, "webhook" olarak değil. `docs/ADMIN_8SAYFA_VIZYON_KAPSAM.md:40-44`.
- Mevcut yer: `web_dashboard/tabs/webhook_monitor.py:236-302` (`# --- Crawl Kontrolü ---` … `st.caption(f"Mevcut durum: ...")`).
- SSOT §7 "Crawl yönetimi" satırı adres değişikliği ister (v2.8).

## Doğrulanacak varsayım
- Blok sınırı `webhook_monitor.py:236` (`# --- Crawl Kontrolü ---`) → `:302`; `:303` `# --- Istatistik Kartları ---` ile başlar. Kaymışsa satırı ölç, uydurma.
- Taşınacak yardımcılar: sabitler `CRAWL_STATUS_BEKLEMEDE/CALISIYOR/BASARISIZ/DURDURULDU` (`:30-33`), `_crawl_is_enabled()` (`:38`), `_log_crawl_action(action, task_id=None)` (`:42-50`). Başka çağıranı varsa (`findstr /S`) **dur**, sorun aç.
- `is_admin = st.session_state.get("admin_email","") != ""` deseni korunur; yetki daraltılmaz/genişletilmez.
- `tests/test_webhook_monitor_tab.py` `st.columns` mock'u sabit tuple döner; blok gidince çağrı sayısı değişir → test güncellenir, **gevşetilmez**.
- `tests/test_admin_kpi_kart.py:84` webhook_monitor'da `st.metric` yok kuralı yeşil kalmalı.
- `tests/test_sayfa_iskeleti.py:51` muaf listesinde `webhook_monitor` var; taşıma sonrası dokunulmaz.

## Adımlar
1. `webhook_monitor.py:30-50` sabit + 2 yardımcı → `admin_kaynaklar.py` üst kısmına taşı (kopya değil, **taşı**; D-211 ikiz yasağı).
2. `webhook_monitor.py:236-302` bloğunu kes → `admin_kaynaklar.py` "Son Çalışmalar" bölümünün üstüne "Crawl Kontrolü" alt başlığı olarak yapıştır (`Section(..., seviye=3)` deseni `ana_kontrol.py:679`).
3. Webhook'ta yerine tek satır: `st.caption("🕷️ Crawl başlat/durdur → Veri Kaynakları sayfasında")` + `st.link_button("Veri Kaynakları", f"/{tab_getir('kaynaklar').url_path}")` (desen `ana_kontrol.py:487-490`).
4. `tests/test_webhook_monitor_tab.py` columns/subheader/caption beklentilerini yeni sayıya göre düzelt; crawl testlerini `tests/test_admin_kaynaklar.py`'ye taşı.
5. `findstr /S /C:"_log_crawl_action" /C:"_crawl_is_enabled" /C:"CRAWL_STATUS_"` → webhook_monitor dışında çağıran kalmadı kanıtı rapora.
6. SSOT §7 "Crawl yönetimi" satırı: yeni adres `admin_kaynaklar.py:NN`.

## Kabul kriteri
- [ ] `python -m pytest -q tests/test_webhook_monitor_tab.py tests/test_admin_kaynaklar.py tests/test_admin_kpi_kart.py tests/test_sekme_kapsama.py tests/test_sayfa_iskeleti.py` yeşil.
- [ ] `findstr /C:"Crawl Kontrolü" web_dashboard\tabs\webhook_monitor.py` → 0 satır; `admin_kaynaklar.py` → 1 satır.
- [ ] `_log_crawl_action` tek tanım, tek dosya (`findstr /S /N` çıktısı raporda).
- [ ] Webhook sayfasında link butonu `/kaynaklar`'a gider (manuel: `streamlit run app.py`, ekran görüntüsü yolu raporda).
- [ ] SSOT §7 satırı + hub "Kapanan işler" yazıldı.

## Kurallar (ADMIN-KİT · D-196)
- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`.
- **Görev sonunda** ilerlemeyi SSOT §7 satırına işle.
- Kanıtsız durum beyanı yasak.
- Yeni bağımlılık yok; davranış değişikliği yok (yalnız yer değişir).
- **Teslimden önce** hub "Kapanan işler" satırı (B-14).

## Ajan chat zorunlu (D-210 · D-217)
- Varsayım tutmuyorsa → `ac`, uydurma.
- Tıkandıysa → sorun aç, sonraki adıma geç.
- @mention → P1 10-15 dk.

```bash
python scripts/ajan_chat.py ac utku UI-ADMIN-CRAWL-TASI-35 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id UI-ADMIN-CRAWL-TASI-35
python scripts/chat_gonder.py --to ihsan --type hata --task-id UI-ADMIN-CRAWL-TASI-35 --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id UI-ADMIN-CRAWL-TASI-35 --ozet "<özet>"
```

**Teslimden sonra DURMAK YASAK (D-312 · D-335).**

```bash
python scripts/gorev_kutusu.py nobet --ajan utku
```

- Çıkış `0` = İŞ VAR → sıradaki `UI-ADMIN-SON-KAZIMA-KART-36`.
- Çıkış `3` → ihsan'a kısa rapor, kapat.

## Ilgili Nodlar
- [[Huginn Data Insights/docs/ADMIN_8SAYFA_VIZYON_KAPSAM]] — K1b
- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]] — §7 Crawl yönetimi
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
- [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-KAYNAKLAR-SAYFA-34]] — öncül
- [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-SON-KAZIMA-KART-36]] — sonraki
- [[Huginn Data Insights/AGENTS]]
- [[plans/_brief_sablon]]
