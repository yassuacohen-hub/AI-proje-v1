# utku_project_context.md — Oturum Hafızası (D-219)

Şablon: [[Huginn Data Insights/_ajan_context_sablon]] · Tavan 200 satır.

## KALDIĞIM YER

- **Konum:** aktif iş yok — 5 görev onay bekliyor (review), 6 aktif/plan
- **Yapılanlar:** 
  - TEST-BACKLOG-20: 6 faz tamamlandı (A=9 migration down, B=3 sayfa iskeleti, C=3 log altyapısı, D=2 API rotası, E=2 denetim, F=1 kullanıcı ayarı) — tam suite 20 failed → 0
  - VERI-HAYALET-TEMIZ-01: 4591 hayalet kayıt silindi, companies.legal_name UNIQUE kısıtı (migration 0022), vergi_no korundu (774), alanlar birleştirildi, yedek alındı
  - VERI-KAYNAK-BAG-01: company_id kolonu eklendi (migration 0023), 5252 eşleşme (37.5%), FK doğrulandı, nace_codes 3319 yüklendi (4 kaynak birleşimi)
  - VERI-NACE-SOZLUK-01: 3319 NACE kodu yüklendi (4 kaynak birleşimi), seviye korundu (6/4/2/1), eşleşme %92.9
  - VERI-NACE-TEMIZ-01: 7614 NN.NN format düzeltildi (raw_nace'ten türetildi), 675 altı haneli kırpıldı, 25 iki haneli NULL'a çekildi, 1 yetim kod düzeltildi
- **Kritik bağlam:** 5 görev onay bekliyor (review), 2 P0 task onaylandığında VERI-02 ve VERI-NACE-COKLU-01 başlanabilir
- **Aktif görevler:** VERI-02 (P1, bloke VERI-KAYNAK-BAG-01), VERI-NACE-COKLU-01 (P1, bloke VERI-NACE-SOZLUK-01), VERI-NACE-KOLON-01 (P2)
- **Plan görevler:** VERI-SEKTOR-01 (P1), VERI-KAYNAK-SIZINTI-01 (P2), VERI-IVEDIK-YENIDEN-01 (P1)
- **Sonraki adım:** ihsan onayını bekle / posta kutusunu kontrol et
- **Görev:** `TEST-BACKLOG-20` (review), `VERI-HAYALET-TEMIZ-01` (review), `VERI-KAYNAK-BAG-01` (review), `VERI-NACE-SOZLUK-01` (review), `VERI-NACE-TEMIZ-01` (review) · **Son okunan karar:** `D-268`

> **2026-09-29 notu (D-268):** Kökten 130 tek kullanımlık dosya `_ARSIV_tek_kullanimlik/`'a
> taşındı. **Senin 6 görevinin hiçbir dosyası taşınanlarla çakışmıyor** (brif taraması:
> 0 eşleşme). Senin kilitli dosyaların (`nace_coklu_ata.py`, `kaynak_firma_bagla.py`,
> `sektor_normalize.py`, `kaynak_sizinti_duzelt.py`, `ivedik_scraper.py`) **yerinde**.
> D-220 gereği `_ARSIV*` arama kapsamı dışıdır — aramana girmesi gerekmez.

## Oturum Açılış (60 saniye, bu sırayla)

1. **§KALDIĞIM YER** — yukarıdaki blok.
2. **§Tuzaklar** + **§Sabitler** — okumazsan aynı hatayı tekrar ödersin.
3. `python scripts/gorev_kutusu.py liste --ajan utku`
4. `python scripts/ajan_chat.py oku --ajan utku` (D-210 cevap süresi: P0 5-10dk, P1 10-15dk, P2 15-30dk)
5. [[Huginn Data Insights/AGENTS]] son karar no ≠ `D-219` ise aradakileri oku (D-168).
6. Brifin **§Doğrulanacak varsayım** maddelerini koda karşı doğrula; tutmuyorsa chat aç, **uydurma**.

**§KALDIĞIM YER pano ile çelişiyorsa pano üstündür.**

## Kimlik

- **Ajan:** `utku` (araç: kilo)
- **Rol:** Üretim/hacim ajanı — kod yazma, refactoring, test, CI/CD. Kilitli dosyalarda çalışır.
- **Kit:** `ADMIN-KİT` (D-196)
- **Mülkü:** `src/**`, `web_dashboard/**`, `tests/**` — kilit aldığım dosyalar
- **Mülkü değil:** `AGENTS.md` (yalnız KAHİN), SSOT dökümanı §7 dışı bölümler, başka ajanın açık kilidi
- **Rapor hattı:** teslim → `ihsan` onayı (P0/P1 elle, P2 ve altı `oto_nobetci.py` — D-46)

## Proje Temel Bilgileri

- **SSOT:** `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md` (görev başı oku, görev sonu §7'ye işle)
- **Kural kaynağı:** [[Huginn Data Insights/AGENTS]] — tek SSOT, kural kopyalamak yasak
- **Test:** `python -m pytest tests/ -q` → **son bilinen: 20 failed / 4260 passed / 12 skipped** (2026-09-26)
- **Hedef:** `TEST-BACKLOG-20` ile 20 → 0

## Sabitler (doğrulanmış gerçekler)

- Migration dizini `src/company_master/schema/migrations/` — `migrate.py` **burada**; `schema/migrate.py` **yok**, `db/migrate.py` ayrı dosya
- `0016_users_last_login.down.sql` + `0017_user_activity_log.down.sql` migrations **kökünde**, `down/` alt dizininde değil
- `down/` dizininde 16 dosya var, en az 19 bekleniyor
- Admin menü kökleri (D-214/D-215): 6 kök — Gelir Kapısı + Güvenlik Kapısı dahil

## Tuzaklar (aynı hatayı iki kez yapma)

- Pano görevi kod tabanında karşılığı olmayan dosyaya işaret ediyor → şablon/placeholder sızıntısı → **çapraz kontrol et, kod yazma**, chat aç (D-216: 8 görev bu yüzden arşivlendi)
- `migrate.py` üç ayrı yolda aranıyor → yanlış dosyayı düzenleme riski → yalnız `schema/migrations/migrate.py`
- İkiz dosya/şablon üretmek → D-211 ihlali → önce `glob` ile ara, varsa mevcut olanı düzenle

## Bilinen Açıklar (kapsam dışı backlog)

- Tam suite 20 failed — görev `TEST-BACKLOG-20` (6 faz, tek brif — D-217)

## Sık Komutlar

```bash
python scripts/gorev_kutusu.py liste --ajan utku
python scripts/gorev_kutusu.py al --ajan utku --task-id <TASK_ID>
python scripts/ajan_chat.py ac utku <TASK_ID> "<sorun>" --cozum "<oneri>"
python scripts/gorev_kutusu.py teslim --ajan utku --task-id <TASK_ID> --ozet "<özet>"
```

## Oturum Günlüğü

### 2026-09-27 — VERI-KAYNAK-BAG-01 + VERI-NACE-SOZLUK-01 + VERI-NACE-TEMIZ-01 + TEST-BACKLOG-20 + VERI-HAYALET-TEMIZ-01 tamamlandı (onay bekliyor)

- **Görevler:** `VERI-KAYNAK-BAG-01` (P0), `VERI-NACE-SOZLUK-01` (P0), `VERI-NACE-TEMIZ-01` (P1), `TEST-BACKLOG-20` (P1), `VERI-HAYALET-TEMIZ-01` (P0)
- **Yapılan VERI-KAYNAK-BAG-01:**
  - Migration 0023: source_records.company_id kolonu eklendi + FK
  - 5252 eşleşme (37.5%): 34 vergi_no + 5218 isim birebir
  - FK doğrulandı (0 ihlal)
- **Yapılan VERI-NACE-SOZLUK-01:**
  - 4 kaynak birleşimi: xlsx_resmi (1547), turkiye_nace_json (2142), nace-rev-2-1.json (1562), nace-rev-2.json (1482)
  - 3319 NACE kodu yüklendi, seviye 6/4/2/1 dolu
  - Eşleşme %92.9 (4252/4574), 47.79.04 ve 47.79 var
- **Yapılan VERI-NACE-TEMIZ-01:**
  - 7614 NN.NN format düzeltildi (raw_nace'ten türetildi)
  - 675 altı haneli kırpıldı (valid 4 haneli parent'a)
  - 25 iki haneli NULL'a çekildi (98/71/16/78 - çoklu child)
  - 1 yetim kod düzeltildi (13.92.11)
  - Sonuç: NN.NN 8289 (valid), 6-digit 0, 2-digit 0, yetim 0
- **Yapılan TEST-BACKLOG-20:** 6 faz, 20 failed → 0, 348 test passed
- **Yapılan VERI-HAYALET-TEMIZ-01:** 4591 hayalet kayıt silindi, UNIQUE INDEX (migration 0022), vergi_no 761 korundu
- **Doğrulama:** Tüm 5 görev `review` durumunda, onay bekliyor
- **Kalan / bloke:** VERI-02 ve VERI-NACE-COKLU-01 bloke (P0 onayı bekliyor)
- **Öğrenilen tuzak:** 5 görev tek seferde onay kuyruğuna girdi, tek tek onaylanmalı

### 2026-09-26 — D-215/D-216 menü kaydı

- **Görev:** `UI-ADMIN-MENU-D215216`
- **Yapılan:** D-215 (Gelir Kapısı, paket_kredi taşıma, maliyet→Metrikler, Güvenlik Kapısı kök) + D-216 hayalet arşivleme geriye dönük panoya işlendi
- **Doğrulama:** `pytest tests/test_naming_audit.py -q` → 9 passed
- **Commit:** `9650bf1`
- **Kalan / bloke:** yok
- **Öğrenilen tuzak:** pano kaydı ile kod tabanı çapraz kontrol edilmeden görev alınmamalı (→ §Tuzaklar)

> **Oturumu kapatmadan:** §KALDIĞIM YER'i güncelle + **Son okunan karar** no'yu tazele.

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/_ajan_context_sablon]]
- [[plans/_brief_sablon]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
