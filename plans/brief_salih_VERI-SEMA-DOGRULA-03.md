# VERI-SEMA-DOGRULA-03 — Brief (salih)

## Neden

**VERI-NACE-SOZLUK-DIL-01** görevinde NACE kodlarının dil açılımları (İngilizce, Fransızca vb.) gerekli. [`src/company_master/sunum.py`](src/company_master/sunum.py:250-276) içindeki `acilim_getir()` fonksiyonu NACE açılımlarını veritabanından çekiyor. 

Fakat `nace_codes` tablosunda dil kolonları (name_en, name_fr, name_de vb.) mevcut mu? V6 (`0006_nace_details.sql`) migrasyonu bu tabloyu oluştururken dil desteği vardı mı?

## Doğrulanacak varsayım

1. `nace_codes` tablosunda minimum 3 dil kolonu var mı? (name, name_en, name_fr)
2. `acilim_getir()` fonksiyonu dil parametresini destekliyor mu?
3. Şemada dil sütunları eksikse V6 güncellenmeli mi?

## Adımlar

1. **Schema kontrol (canlı DB):**
   ```sql
   PRAGMA table_info(nace_codes);
   ```
   Çıktıda sütun listesini kontrol et. Aranacak sütunlar: name, name_en, name_fr, name_de

2. **Kod analizi:** `src/company_master/sunum.py` dosyasında `acilim_getir()` fonksiyonunu oku:
   - Kaç parametresi var?
   - Dil parametresi destekliyor mu?
   - SQL sorgusunda hangi sütun kullanılıyor?

3. **Migration taraması:** `0006_nace_details.sql` dosyasını aç:
   - CREATE TABLE nace_codes içinde dil sütunları tanımlı mı?
   - Eksikse → migration güncelleme gerekli

4. **Eksik sütun ekleme (gerekirse):**
   - Yeni migration: `0047_nace_dil_kolonlari.sql`
   - ALTER TABLE nace_codes ADD COLUMN name_en VARCHAR(255);
   - ALTER TABLE nace_codes ADD COLUMN name_fr VARCHAR(255);
   - schema_versions.json'a V26 ekle

5. **Test çalıştırma:** `src/company_master/sunum.py` içinde doctest varsa:
   ```bash
   python -m doctest src/company_master/sunum.py -v
   ```

6. **Canlı ölçüm (D-238):**
   ```sql
   SELECT COUNT(*) FROM nace_codes WHERE name_en IS NOT NULL;
   SELECT COUNT(*) FROM nace_codes WHERE name_fr IS NOT NULL;
   ```

## Kabul kriteri

- [ ] PRAGMA table_info(nace_codes) en az 3 dil sütununu gösteriyor
- [ ] `acilim_getir()` fonksiyonu dil parametresini destekliyor (parametre varsa)
- [ ] doctest çalışıyor (hata yok)
- [ ] Canlı ölçüm: name_en ve name_fr sütunlarında veri var (COUNT > 0)
- [ ] Schema_versions.json güncel

## Kurallar (VERI-KİT · D-196)

- **D-238:** Canlı veritabanında ölçüm yapılır — belge/beyan değil
- **D-251:** Göc defteri tek anlaticıdır
- **D-260:** Teslim özeti kanıt değildir — canlı doğrulama şart

## Ajan chat zorunlu (D-210 · D-217)

Tamamlandığında:

```bash
python scripts/chat_gonder.py \
  --ajan salih \
  --task-id VERI-SEMA-DOGRULA-03 \
  --durum cozuldu \
  --mesaj "nace_codes dil kolonları doğrulandı: name_en (N satır), name_fr (N satır). acilim_getir() test passed."
```

## Teslim

- Dosya: `src/company_master/schema/migrations/0006_nace_details.sql` (güncellenmiş, gerekirse)
- Dosya: `src/company_master/schema/migrations/schema_versions.json` (V26 eklenmeli, gerekirse)
- Kanıt: PRAGMA table_info çıktısı + doctest sonucu + SELECT COUNT(*) canlı ölçüm
- Chat: Tamamlanma raporu

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]] (D-238, D-251, D-260)
- [[Huginn Data Insights/src/company_master/sunum.py:250-276]]
- [[Huginn Data Insights/src/company_master/schema/migrations/0006_nace_details.sql]]
- [[Huginn Data Insights/plans/brief_utku_VERI-NACE-SOZLUK-DIL-01.md]]
