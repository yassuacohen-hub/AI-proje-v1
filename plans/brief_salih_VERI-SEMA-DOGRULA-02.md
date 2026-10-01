# VERI-SEMA-DOGRULA-02 — Brief (salih)

## Neden

**SEMA-DENETIM-01 (V21):** `0021_missing_tables.sql` migrasyonunda kodun sorgulattığı 5 tablo belirtildi, fakat hâlâ 2'si eksik:
- ✅ `audit_logs` — var
- ✅ `admin_audit_log` — var
- ❌ `entity_matches` — **EKSIK**
- ✅ `campaign_packages` — var
- ❌ `api_usage_daily` — **EKSIK**

Bu tablolar UTKU'nun VERI-TSG-04-YAZICI-01 ve diğer ETL görevlerinin ön koşulu. Şema eksikse kod hata verir (D-260: teslim özeti kanıt değildir).

## Doğrulanacak varsayım

1. `entity_matches` ve `api_usage_daily` tabloları kodda nerede sorgulanıyor?
2. Şema tanımları neler olmalı (sütunlar, tipler, kısıtlar)?
3. Migration dosyaları oluşturulup `schema_versions.json`'a eklenmeli mi?

## Adımlar

1. **Kod taraması:** Tüm Python dosyalarında `entity_matches` ve `api_usage_daily` sorgusu bul:
   ```
   grep -r "entity_matches\|api_usage_daily" src/
   ```

2. **Şema tasarımı:** Her tablo için sütun tanımı yaz (tabloların amacına göre):
   - `entity_matches`: Hangi varlıkları karşılaştırıyor? (firma/kaynak eşleştirmesi mi?)
   - `api_usage_daily`: API kullanım istatistikleri (tarih, endpoint, count vb.)

3. **Migration dosyası oluştur:** `0046_missing_tables_fix.sql` dosyası yaz (CREATE TABLE)

4. **Defter güncelle:** `schema_versions.json`'a V24 ve V25 satırları ekle

5. **Doğrulama:** `migrate.py --esitle` çalıştır, sonra `migrate.py up` ile canlı şemaya uygula

6. **Kanıt:** 
   ```sql
   SELECT COUNT(*) FROM entity_matches;
   SELECT COUNT(*) FROM api_usage_daily;
   PRAGMA table_info(entity_matches);
   PRAGMA table_info(api_usage_daily);
   ```

## Kabul kriteri

- [ ] `entity_matches` ve `api_usage_daily` tabloları canlı DB'de var
- [ ] Her tablo için en az 3 test satırı INSERT edildi
- [ ] `migrate.py --esitle` defter ile şema senkron
- [ ] `schema_versions.json` V24 ve V25 kaydedildi
- [ ] Chat'e kanıt (SELECT COUNT(*)) yollandı

## Kurallar (VERI-KİT · D-196)

- **D-251:** Göc defteri tek anlaticıdır. Sema tasarımı → göc dosyası → defter kaydı sırasıyla.
- **D-260:** Teslim özeti kanıt değildir. Canlı DB'de ölçüm yapılır.
- **D-238:** Canlı veritabanında ölçüm yapılır — belge değil, SQL sonucu.

## Ajan chat zorunlu (D-210 · D-217)

Tamamlandığında:

```bash
python scripts/chat_gonder.py \
  --ajan salih \
  --task-id VERI-SEMA-DOGRULA-02 \
  --durum cozuldu \
  --mesaj "2 tablo oluşturuldu: entity_matches (row count), api_usage_daily (row count). V24/V25 deftere yazıldı."
```

## Teslim

- Dosya: `src/company_master/schema/migrations/0046_missing_tables_fix.sql`
- Dosya: `src/company_master/schema/migrations/schema_versions.json` (V24/V25 eklenmeli)
- Kanıt: Canlı DB SELECT COUNT(*) çıktısı
- Chat: Tamamlanma raporu

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]] (D-251, D-260, D-238)
- [[Huginn Data Insights/scripts/goc_defteri.py]]
- [[Huginn Data Insights/src/company_master/schema/migrations/schema_versions.json]]
- [[Huginn Data Insights/src/company_master/schema/migrations/0021_missing_tables.sql]]
