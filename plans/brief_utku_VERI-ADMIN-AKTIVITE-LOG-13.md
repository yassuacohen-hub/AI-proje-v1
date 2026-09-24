# VERI-ADMIN-AKTIVITE-LOG-13 — Brief (utku)

**Başlık:** [VERI] Kullanıcı aktivite log tablosunu yaz → migration 0017 (2s)
**Öncelik:** P0 · **Kit:** `ADMIN-KİT` (AGENTS.md D-196)
**Kilitli dosya:** `src/company_master/schema/migrations/0017_user_activity_log.sql` (+ `.down.sql`)

## Neden
SSOT §8.4 EK BULGU-8 (satır 322) ve §10 sıra 3 (satır 366): giriş/arama/AI kullanım log tablosu DB'de **hiç yok** (30 tablo tarandı). Bu tek eksik 3 ayrı açık maddeyi bloke ediyor: K1 Churn 3-sinyal (§9 satır 340), K9 Arama Boşluğu (§9 satır 348), G4 gerçek DAU (§12 satır 417). Önce girdi, sonra algoritma.

## Doğrulanacak varsayım
- `src/company_master/schema/migrations/0016_users_last_login.sql` dosyası var ve numaralı migration deseni kullanılıyor varsayıldı; sıradaki boş numara `0017`. Numara doluysa **dur**, panoya sorun aç, uydurma.
- `schema_migrations` tablosu mevcut ve migration koşucusu onu okuyor varsayıldı. Yoksa **dur**, önce koşucuyu doğrula.
- Hedef veritabanı PostgreSQL ve `JSONB` + `TIMESTAMPTZ` tipleri destekliyor varsayıldı. SQLite/başka motor çıkarsa **dur**, tip seçimini KAHİN'e sor.
- `users` tablosu var ve `user_id` FK verilebilir varsayıldı; PK adı `users.id`. Farklıysa **dur**.
- `user_activity_log` adında tablo **yok** varsayıldı (SSOT §8.4:322 "30 tablo tarandı" bulgusu). `inspect().get_table_names()` ile bizzat doğrula; varsa **dur**, görev yeniden tanımlanır.
- `olay_tipi` değer kümesi `giris`/`arama`/`ai_kullanim` yeterli varsayıldı — `-14`, `-20`, `-17` bu üç değeri yazacak/okuyacak. Dördüncü tip gerekirse **dur**, panoya sorun aç.

## Adımlar
1. `0016_users_last_login.sql` desenini örnek al (aynı migration klasörü, `schema_migrations` zaten var).
2. Tek tablo `user_activity_log`: `id` (PK), `user_id` (FK users), `olay_tipi` (`giris`/`arama`/`ai_kullanim`), `olay_zamani TIMESTAMPTZ NOT NULL DEFAULT NOW()`, `detay JSONB NULL` (arama terimi, sonuç adedi vb.), `basarili BOOLEAN NOT NULL DEFAULT TRUE`.
3. İndeks: `idx_activity_user_zaman (user_id, olay_zamani DESC)` ve `idx_activity_tip_zaman (olay_tipi, olay_zamani DESC)`.
4. `.down.sql` ile tam geri alma (DROP INDEX + DROP TABLE).
5. Ayrı arama/AI tablosu **açma** — tek tablo + `olay_tipi` ayrımı yeterli (SSOT §12 G2 "sıfır yeni tablo" ilkesine en yakın çözüm).

## Kabul kriteri
- [ ] Migration up uygulanıyor, `inspect().get_table_names()` içinde `user_activity_log` görünüyor.
- [ ] Down çalıştırılınca tablo ve indeksler tamamen kalkıyor.
- [ ] `detay` alanı NULL geçilebiliyor (giriş olayında detay yok).

## Kurallar (ADMIN-KİT · D-196)
- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) + §14 (Revizyon Tablosu) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni bağımlılık ekleme; mevcut şema/araç ile çöz.
- Bitince `python scripts/gorev_kutusu.py teslim --ajan utku --task-id VERI-ADMIN-AKTIVITE-LOG-13 --ozet "<özet>"`

## Ilgili Nodlar
- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/AGENTS]]
