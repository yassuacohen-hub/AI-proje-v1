# VERI-ADMIN-LASTLOGIN-MIGRATION-04 — Brief (ihsan)

**Başlık:** [VERI] users.last_login kolonunu yaz → schema migration (1s)
**Öncelik:** P1 · **Kit:** `ADMIN-KİT` (AGENTS.md D-196)
**Kilitli dosya:** (kilit yok — kapsam brifte)

## Neden

Churn zincirinin 1. halkası. `users` tablosunda 28 kolon tarandı, `last_login`/`last_seen` **yok** (SSOT §11 KK-3 doğrulandı). Girdisiz algoritma yazılamaz.

## Adımlar

1. `schema_migrations` altyapısı zaten var — tek migration yeter.
2. `users` tablosuna `last_login TIMESTAMP NULL` ekle.
3. Geri alınabilir olsun (down migration).
4. Bu görev **veri yazmaz**, yalnız şema açar. Yazma işi VERI-... -05'te.

## Kabul kriteri

- [ ] Migration uygulandı, `inspect(engine).get_columns('users')` içinde `last_login` görünüyor.
- [ ] SSOT §11 KK-3 satırına 'kolon eklendi' kanıtı işlendi.

## Kurallar (ADMIN-KİT · D-196)

- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) + §14 (Revizyon Tablosu) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni tablo/bağımlılık ekleme; mevcut şema ile çöz.
- Bitince `python scripts/gorev_kutusu.py teslim --ajan <ajan> --task-id <TASK> --ozet "<özet>"`

## Ilgili Nodlar

- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/AGENTS]]
