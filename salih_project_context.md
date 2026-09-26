# salih_project_context.md — Oturum Hafızası (D-219)

Şablon: [[Huginn Data Insights/_ajan_context_sablon]] · Tavan 200 satır.

## KALDIĞIM YER

- **Konum:** aktif iş yok
- **Yapılanlar:** —
- **Kritik bağlam:** mekanik görev — SADECE ölçüm/plan çıktısı üret, kod değiştirme
- **Sonraki adım:** `python scripts/gorev_kutusu.py liste --ajan salih` ile pano kontrolü
- **Görev:** — · **Son okunan karar:** `D-219`

## Oturum Açılış (60 saniye, bu sırayla)

1. **§KALDIĞIM YER** — yukarıdaki blok.
2. **§Tuzaklar** + **§Sabitler**.
3. `python scripts/gorev_kutusu.py liste --ajan salih`
4. `python scripts/ajan_chat.py oku --ajan salih` (D-210 cevap süresi: P0 5-10dk, P1 10-15dk, P2 15-30dk)
5. [[Huginn Data Insights/AGENTS]] son karar no ≠ `D-219` ise aradakileri oku (D-168).
6. Brifin **§Doğrulanacak varsayım** maddelerini koda karşı doğrula.

**§KALDIĞIM YER pano ile çelişiyorsa pano üstündür.**

## Kimlik

- **Ajan:** `salih` (araç: continue)
- **Rol:** Test Danışman — mekanik görevler: test planlama, benchmark, bilgi tabanı, uyum denetimi.
- **Kit:** `ADMIN-KİT` (D-196)
- **Mülkü:** test planları, benchmark çıktıları, bilgi tabanı notları
- **Mülkü değil:** üretim kodu ve test kodu implementasyonu (utku) — plan üretirsin, yazmazsın
- **Rapor hattı:** **rapor → YASU** (doğrudan ihsan'a değil)

## Proje Temel Bilgileri

- **SSOT:** `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Kural kaynağı:** [[Huginn Data Insights/AGENTS]] — tek SSOT, kural kopyalamak yasak
- **Test:** `python -m pytest tests/ -q` → **son bilinen: 20 failed / 4260 passed / 12 skipped** (2026-09-26)

## Sabitler (doğrulanmış gerçekler)

- Test kökü `tests/`; tam suite ~4292 test
- Denetim testleri: `tests/test_naming_audit.py` (D-57), `tests/test_brief_sablon_denetim.py` (D-217/D-218)

## Tuzaklar (aynı hatayı iki kez yapma)

- Plan üretirken var olmayan dosyaya atıf → hayalet görev doğurur (D-216) → her atıf `dosya:satır` doğrulanır
- Ölçüm sayısı brifteki sayı ile tutmuyor → **dur**, chat aç; sayıyı brife uydurma

## Bilinen Açıklar (kapsam dışı backlog)

- Tam suite 20 failed — görev `TEST-BACKLOG-20` (utku'da)

## Sık Komutlar

```bash
python scripts/gorev_kutusu.py liste --ajan salih
python scripts/gorev_kutusu.py al --ajan salih --task-id <TASK_ID>
python scripts/ajan_chat.py ac salih <TASK_ID> "<sorun>" --cozum "<oneri>"
python scripts/gorev_kutusu.py teslim --ajan salih --task-id <TASK_ID> --ozet "<özet>"
```

## Oturum Günlüğü

### <YYYY-MM-DD> — <oturum konusu>

- **Görev:** `<TASK_ID>`
- **Yapılan:** <madde madde, `dosya:satır` referanslı>
- **Doğrulama:** `<komut>` → `<sonuç>`
- **Commit:** `<sha>`
- **Kalan / bloke:** <yoksa "yok">
- **Öğrenilen tuzak:** <varsa §Tuzaklar'a ekle>

> **Oturumu kapatmadan:** §KALDIĞIM YER'i güncelle + **Son okunan karar** no'yu tazele.

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/_ajan_context_sablon]]
- [[Huginn Data Insights/yasu_project_context]]
- [[plans/_brief_sablon]]
