# UI-ADMIN-KAYNAKLAR-SAYFA-34 — Brief (utku)

**Başlık:** [ADMIN-KİT] "Veri Kaynakları" sayfası ekle → 0050 kazıma tablolarını tek yerde göster (4 saat)
**Öncelik:** P1 · **Kit:** `ADMIN-KİT` (AGENTS.md D-196)
**Kilitli dosya:** `web_dashboard/tabs/admin_kaynaklar.py` (YENİ), `web_dashboard/tabs/__init__.py`
**Bağımlılık:** `UI-ADMIN-SAYFA-ISKELET-18` (kapandı — ADMIN-UI-10 kalıbı hazır)
**Hub:** `hubs/ADMIN_DASHBOARD_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

> **Tek brif kuralı (D-217):** Bir görev = bir brif. Zincir: 34 → 35 → 36. Bu brif 34'tür; 35 ve 36 ayrı brif.

## Neden
- Vizyon "Veri Kaynakları (OSINT)" sayfası kodda yok: `docs/ADMIN_8SAYFA_VIZYON_KAPSAM.md:21-35` (ölçüldü: SECTIONS'ta `kaynaklar` anahtarı yok).
- KK-12 = A′ kararı K1/K6: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md` §11 KK-12 (v2.8).
- 0050 tabloları (`scrape_audit_log`, `scrape_errors`, `scrape_pages`) yazılıyor ama **hiç okunmuyor**: tek yazıcı `src/company_master/etl/scrape_kayit.py:87` `KazimaYazici`; reader yok (D-236: tüketicisi olmayan çıktı).
- Admin genç/düşük teknik; "kazıma ne durumda?" sorusunun tek adresi olmalı (SSOT §2 soru envanteri).

## Doğrulanacak varsayım
- `web_dashboard/tabs/__init__.py:106` `TabTanimi` frozen dataclass alanları: `anahtar, baslik, ikon, grup, aciklama, url_path, ust, sira, modul, fonksiyon, hazir, bekleyen_gorev, min_rol, yuzey`. Farklıysa **dur**, sorun aç.
- `veri_kalite` kökü `__init__.py:599-605`; çocukları sira 0-4 dolu (`kalite`=0 :325, `executive`=1 :226, `arama`=2 :338, `kontrol-panosu`=3 :488, `maliyet`=4 :362). **sira=5 boş** varsayıldı.
- `🕷️` ikonu SECTIONS içinde başka menü öğesinde yok varsayıldı (`tests/test_tabs_ia.py` ikon tekilliği). Varsa başka ikon seç, test kırma.
- 0050 tablo adları ve kolonları `scrape_kayit.py:101-220` içindeki INSERT'lerden okunur; **canlı DB'de `inspect` ile doğrula (D-238)**, uydurma.
- `src/company_master/kaynak_guvenilirlik.py:161` `hesapla(kaynak_id, kaynak_adi, toplam_cekis, basarili_cekis, son_cekis_zaman, son_n_cekisler=None) -> KaynakSaglik`; `:321 saglik_rozeti(oran) -> str`. İmza farklıysa **dur**.
- `web_dashboard/charts.py:416` `kpi_karti(...)` mevcut; yeni kart bileşeni yazılmaz.
- `admin_kpi.py:222 load_source_health()` `sources`+`source_records` okur, 0050 **okumaz** — bu görev ona dokunmaz.

## Adımlar
1. `admin_musteriler.py:1-60` ADMIN-UI-10 kalıbını kopyala → `web_dashboard/tabs/admin_kaynaklar.py`, `render_kaynaklar_tab()`.
   `BOLUMLER = (Section("Durum Özeti",…,kimlik="durum-ozeti"), Section("Son Çalışmalar",…,"son-calismalar"), Section("Hatalar",…,"hatalar"), Section("Toplanan Sayfalar",…,"toplanan-sayfalar"))`.
   `PageHeader("Veri Kaynakları", giris=…, ust_etiket="Metrikler · Veri Kaynakları", ikon="🕷️")`.
2. Okuma fonksiyonları (`@st.cache_data(ttl=60)`, salt `SELECT`, `get_engine()`): kaynak başına `scrape_audit_log` toplam/başarılı/son zaman; `scrape_errors` son 20; `scrape_pages` kaynak başına adet. Yazma yok — `KazimaYazici` tek yazıcı kalır.
3. "Durum Özeti": kaynak başına `kaynak_guvenilirlik.hesapla(...)` → `kpi_karti` + `saglik_rozeti`. Veri yoksa "Henüz kazıma yapılmadı" (D-249: veri yok ≠ 0).
4. Her blokta veri kaynağı etiketi (D-213 VERI-ETIKET-01): `st.caption("Kaynak: scrape_audit_log · canlı")`.
5. `__init__.py` SECTIONS'a ekle:
   `TabTanimi(anahtar="kaynaklar", baslik="Veri Kaynakları", ikon="🕷️", grup=GRUP_IS, aciklama="Kazıma kaynakları: son çalışma, hata ve toplanan sayfa", url_path="kaynaklar", ust="veri_kalite", sira=5, modul="web_dashboard.tabs.admin_kaynaklar", fonksiyon="render_kaynaklar_tab", min_rol="admin")`.
   `grup` sabiti `veri_kalite` kökü ile aynı olsun (`:599-605`'teki değeri kullan).
6. Hazır olmayan bölüm bırakma: Crawl butonları **bu görevde yok** (35'te taşınır); "Son Çalışmalar" altında yalnız okuma.
7. SSOT §7 "Kaynak sağlığı" satırını `dosya:satır` ile güncelle.

## Kabul kriteri
- [ ] `python -m pytest -q tests/test_dashboard_nav.py tests/test_tabs_ia.py tests/test_sekme_kapsama.py tests/test_sayfa_iskeleti.py` yeşil.
- [ ] `python -c "from web_dashboard.tabs import tab_getir; t=tab_getir('kaynaklar'); print(t.url_path, t.ust, t.sira)"` → `kaynaklar veri_kalite 5`.
- [ ] Canlı ölçüm (D-238): 0050 üç tablonun `COUNT(*)` çıktısı raporda; sayfa aynı sayıları gösterir.
- [ ] `tests/test_admin_kaynaklar.py` (yeni, ≤10 test): boş tablo → "Henüz kazıma yapılmadı"; 1 kaynak → rozet metni; `st.metric` kullanılmaz (`test_admin_kpi_kart.py:84` deseni).
- [ ] SSOT §7 satırı güncel; hub "Kapanan işler" satırı yazıldı.

## Kurallar (ADMIN-KİT · D-196)
- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md` (§11 KK-12, §12 G8, §9 K4).
- **Görev sonunda** ilerlemeyi SSOT §7 satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni bağımlılık yok; şema/migration yok; stdlib + Streamlit + mevcut `charts.py`.
- `_hg_rehber`, K3-10g footer toggle, mevcut sekme ağacı bozulmaz.
- **Teslimden önce** `hubs/ADMIN_DASHBOARD_HUB.md` "Kapanan işler" bölümüne `UI-ADMIN-KAYNAKLAR-SAYFA-34` satırı yaz (B-14).

## Ajan chat zorunlu (D-210 · D-217)
Sessiz çalışma yasak:
- Brifteki varsayım kodda tutmuyorsa → `ac` ile sorun aç, **uydurma, durma**.
- Bir adım tıkandıysa → sorun aç, sonraki adıma geç.
- @mention → P1 10-15 dk içinde cevap.

```bash
python scripts/ajan_chat.py ac utku UI-ADMIN-KAYNAKLAR-SAYFA-34 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id UI-ADMIN-KAYNAKLAR-SAYFA-34
python scripts/chat_gonder.py --to ihsan --type hata --task-id UI-ADMIN-KAYNAKLAR-SAYFA-34 --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id UI-ADMIN-KAYNAKLAR-SAYFA-34 --ozet "<özet>"
```

**Teslimden sonra DURMAK YASAK (D-312 · D-335).**

```bash
python scripts/gorev_kutusu.py nobet --ajan utku
```

- Çıkış `0` = İŞ VAR → hemen yap (sıradaki: `UI-ADMIN-CRAWL-TASI-35`).
- Çıkış `3` = 60 dk iş gelmedi → ihsan'a kısa rapor, kapat.

## Ilgili Nodlar
- [[Huginn Data Insights/docs/ADMIN_8SAYFA_VIZYON_KAPSAM]] — kaynak belge (K1/K6)
- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]] — §11 KK-12 · §7 Kaynak sağlığı
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]] — Tur 2026-10-03 brief tablosu
- [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-CRAWL-TASI-35]] — zincirde sonraki
- [[Huginn Data Insights/AGENTS]]
- [[plans/_brief_sablon]]
