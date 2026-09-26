# utku_project_context.md — Oturum Hafızası (D-219)

Şablon: [[Huginn Data Insights/_ajan_context_sablon]] · Tavan 200 satır.

## KALDIĞIM YER

- **Konum:** aktif iş yok — son teslim `UI-ADMIN-MENU-D215216` (done)
- **Yapılanlar:** D-215/D-216 menü düzenlemesi geriye dönük panoya işlendi (commit `9650bf1`)
- **Kritik bağlam:** yeni görev `TEST-BACKLOG-20` bekliyor → SADECE brifte yazılı dosyalar
- **Sonraki adım:** `plans/brief_utku_TEST-BACKLOG-20.md` oku, Faz A'dan başla (migration down, veri kaybı riski)
- **Görev:** `TEST-BACKLOG-20` (bekliyor) · **Son okunan karar:** `D-219`

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
