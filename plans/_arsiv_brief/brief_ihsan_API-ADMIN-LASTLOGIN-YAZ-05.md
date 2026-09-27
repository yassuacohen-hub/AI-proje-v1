# API-ADMIN-LASTLOGIN-YAZ-05 — Brief (ihsan)

**Başlık:** [API] Giriş anında last_login değerini yaz → auth akışı (1s)
**Öncelik:** P1 · **Kit:** `ADMIN-KİT` (AGENTS.md D-196)
**Kilitli dosya:** (kilit yok — kapsam brifte)

## Neden

Churn zincirinin 2. halkası. Kolon açıldı ama kimse doldurmazsa hâlâ veri yok.

## Adımlar

1. **Bağımlılık:** VERI-ADMIN-LASTLOGIN-MIGRATION-04 bitmeden başlama.
2. Başarılı giriş anında `UPDATE users SET last_login = NOW() WHERE id = :id`.
3. Giriş yolu: `web_dashboard/tabs/admin_auth.py` + ilgili auth servisi — tek yerden geçtiğinden emin ol, iki kopya varsa raporla.

## Kabul kriteri

- [ ] Giriş yapan kullanıcının `last_login` değeri güncelleniyor (1 test).
- [ ] Başarısız girişte kolon güncellenMİYOR.

## Kurallar (ADMIN-KİT · D-196)

- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) + §14 (Revizyon Tablosu) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni tablo/bağımlılık ekleme; mevcut şema ile çöz.
- Bitince `python scripts/gorev_kutusu.py teslim --ajan <ajan> --task-id <TASK> --ozet "<özet>"`

## Ilgili Nodlar

- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/AGENTS]]
