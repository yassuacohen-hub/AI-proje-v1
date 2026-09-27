# UI-ADMIN-MAU-08 — Brief (ihsan)

**Başlık:** [UI] Yanlış DAU etiketini düzelt → admin_kpi.py gerçek MAU (2s)
**Öncelik:** P1 · **Kit:** `ADMIN-KİT` (AGENTS.md D-196)
**Kilitli dosya:** (kilit yok — kapsam brifte)

## Neden

`admin_kpi.py:65` bugün yalnız `status IN ('onayli','aktif')` sayıyor — bu **kayıtlı kullanıcı**, DAU değil. Etiket yalan söylüyor (SSOT §12 G4).

## Adımlar

1. **Bağımlılık:** API-ADMIN-LASTLOGIN-YAZ-05.
2. `last_login` üzerinden MAU tek sorguyla çıkar (son 30 gün).
3. Gerçek DAU için ayrı olay tablosu gerekir — **bu görevde yapılmaz**, kartı MAU olarak doğru etiketle.

## Kabul kriteri

- [ ] Kart adı gerçeği söylüyor, MAU `last_login` üzerinden hesaplanıyor.

## Kurallar (ADMIN-KİT · D-196)

- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) + §14 (Revizyon Tablosu) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni tablo/bağımlılık ekleme; mevcut şema ile çöz.
- Bitince `python scripts/gorev_kutusu.py teslim --ajan <ajan> --task-id <TASK> --ozet "<özet>"`

## Ilgili Nodlar

- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/AGENTS]]
