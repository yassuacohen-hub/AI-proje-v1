# VERI-SEMA-DOGRULA-01 — Brief (salih)

## Neden

**MIGRATE-EXEC-02:** `schema_versions.json` defterde V7 satırı `0007_add_address_column.sql` dosyasını işaret ediyor, ancak gerçek dosya `0013_job_intelligence.sql` olabilir. Bu tutarsızlık `migrate.py` koşturulurken hata veya sessiz başarısızlık oluşturabilir.

UTKU'nun 4 aktif görevinin şema bağımlılığı vardır. Bu görev kapanmadan diğerleri ilerleyemez (D-251: goc defteri tek anlatıcı; D-253: iz doğrulanır).

## Doğrulanacak varsayım

1. `schema_versions.json` dosyasındaki V7 kaydı — gerçek dosya adı hangisi?
2. `0007_add_address_column.sql` dosyası mevcut mu?
3. `0013_job_intelligence.sql` dosyası mevcut mi?
4. `migrate.py --validate` sırasında hatalar yok mu?

## Adımlar

1. **Defter okuma:** `src/company_master/schema/migrations/schema_versions.json` dosyasında version 7 satırını aç.
2. **Dosya tarama:** `src/company_master/schema/migrations/` dizininde hem `0007_*.sql` hem de `0013_*.sql` dosyalarını kontrol et.
3. **Validate çalıştırma:** `python scripts/goc_defteri.py calistir --esitle` (kuru koşu) sonra `migrate.py --validate` ile hata kontrolü.
4. **Tutarlılık kurma:** Defter dosya adıyla eşleş; uyumsuzsa defter güncelle.
5. **Kanıt kaydı:** `migrate.py --validate` çıktısı (stderr boş olmalı) ve migrate.log dosyasını chat'e yaz.

## Kabul kriteri

- [ ] `schema_versions.json` V7 satırı gerçek dosya adıyla eşleşti
- [ ] `migrate.py --validate` stderr boş dönüyor
- [ ] `migrate.log` tutarlılık kontrol raporu içeriyor
- [ ] Brief'teki varsayımlar kanıt dosyasıyla doğrulandı

## Kurallar (ADMIN-KİT · D-196)

- **D-251:** Şema migrasyon defteridir; tek anlaticıdır. Kod yol alır, defter ölçer ve kaydeder.
- **D-253:** Migrasyon izleri kaydedilir; beyan değil, iz doğrulanır.
- **D-238:** Canlı veritabanında ölçüm yapılır — kanıt beyanı değildir.

## Ajan chat zorunlu (D-210 · D-217)

Görev tamamlandığında chat_gonder kullanarak result mesajı gönder:

```bash
python scripts/chat_gonder.py \
  --ajan salih \
  --task-id VERI-SEMA-DOGRULA-01 \
  --durum cozuldu \
  --mesaj "Tutarlılık sağlandı. V7 → $(gerçek dosya adı). migrate.py --validate: 0 hata."
```

## Teslim

- Dosya: `src/company_master/schema/migrations/schema_versions.json` (güncellenmiş)
- Kanıt: `migrate.log` (doğrulama çıktısı)
- Chat: Tamamlanma raporu

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]] (D-251, D-253, D-238)
- [[Huginn Data Insights/scripts/goc_defteri.py]]
- [[Huginn Data Insights/src/company_master/schema/migrations/schema_versions.json]]
