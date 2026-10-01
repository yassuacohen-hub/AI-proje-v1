# brief_yasu_VERI-SEMA-DOGRULA-03 — Kod Denetimi: NACE Dil Kolonları

## Neden

**VERI-NACE-SOZLUK-DIL-01:** UTKU'nun bu görevinde NACE kodlarının dil açılımları (İngilizce, Fransızca vb.) gerekli.

Fakat:
1. `0006_nace_details.sql` migrasyonu NACE tablosunu oluştururken dil sütunları tanımladı mı?
2. `sunum.py` içindeki `acilim_getir()` fonksiyonu dil parametresini destekliyor mu?

Bu sorulara cevap veremeden SALIH şema güncellemesi yapamaz. YASU'ya: kod + migration denetim yap, rapor yaz.

## Doğrulanacak varsayım

1. `0006_nace_details.sql` dosyasında CREATE TABLE nace_codes kaç sütun tanımlı?
2. Dil sütunları (name_en, name_fr, name_de vb.) var mı?
3. `sunum.py:acilim_getir()` fonksiyonu kaç parametre alıyor?
4. Dil seçimi var mı (örn: lang="en" parametresi)?

## Adımlar

### 1. Migration Denetim

Dosya: `src/company_master/schema/migrations/0006_nace_details.sql`

```sql
-- Bu dosyayı aç ve oku:
-- CREATE TABLE nace_codes (...) içindeki tüm sütunları list yap
-- Aradığın sütunlar: name (Türkçe), name_en (İngilizce), name_fr (Fransızca), name_de (Almanca)
-- Her sütun için: tür (VARCHAR?), NULL izni var mı, default değer?
```

Rapora yaz:
```
### 0006_nace_details.sql Denetim

**Tanımlı sütunlar:**
- name (VARCHAR(255), NOT NULL) ✅
- name_en (VARCHAR(255), NULL) ❌ EKSIK
- name_fr (VARCHAR(255), NULL) ❌ EKSIK

**Sonuç:** 2 dil sütunu eksik. Migration güncellenmeli.
```

### 2. Kod Denetim

Dosya: `src/company_master/sunum.py`

Satırlar 250-276, `acilim_getir()` fonksiyonunu oku:

```python
def acilim_getir(nace_code: str | None) -> str:
    # Fonksiyon imzasını kontrol et: kaç parametre?
    # nace_code + lang parametresi var mı?
    # SQL sorgusunda hangi sütun kullanılıyor? (name mi, name_en mi?)
```

Raporda yaz:
```
### sunum.py:acilim_getir() Denetim

**Fonksiyon imzası:**
- acilim_getir(nace_code: str | None) -> str

**Parametreler:** 1 (nace_code sadece)
**Dil desteği:** ❌ EKSIK (lang parametresi yok)

**SQL Sorgusu:** SELECT name FROM nace_codes WHERE code = nace_code
**Kullanılan sütun:** name (Türkçe sadece)

**Sonuç:** Dil parametresi eklenmeli (func imzası + SQL query güncelle).
```

### 3. Rapor Oluştur

Dosya: `plans/rapor_yasu_VERI-SEMA-DOGRULA-03.md` içine yaz:

```markdown
# NACE Dil Kolonları — Kod Denetim Raporu

## Özet
- Migration (0006): 2 sütun eksik
- Kod (sunum.py): Dil parametresi yok

## Risk
- VERI-NACE-SOZLUK-DIL-01 görevinde dil açılımları yazılamaz
- acilim_getir() her zaman Türkçe dönüş yapar

## Önerilen Aksiyon
1. 0006_nace_details.sql güncelle: name_en, name_fr sütunları ekle
2. sunum.py:acilim_getir() güncelle: lang parametresi ekle
3. SQL: SELECT name_<lang> FROM nace_codes olacak şekilde

## Ek Not
- Dil verisinin kaynağı? (Turkish, Wikipedia, API?)
- Veri doluluk kontrolü gerekli (D-238 canlı ölçüm)
```

### 4. Chat Bildirimi

```bash
python scripts/chat_gonder.py \
  --ajan yasu \
  --task-id VERI-SEMA-DOGRULA-03 \
  --durum cozuldu \
  --mesaj "NACE dil denetim bitti. Sonuç: Migration 2 sütun eksik, Kod dil parametresi yok. Rapor: plans/rapor_yasu_VERI-SEMA-DOGRULA-03.md"
```

## Kabul kriteri

- [ ] 0006_nace_details.sql denetim yapıldı (tüm sütunlar listelendi)
- [ ] sunum.py:acilim_getir() fonksiyonu analiz edildi
- [ ] Eksik sütunlar/parametreler tespit edildi
- [ ] Rapor dosyası oluşturuldu (`plans/rapor_yasu_VERI-SEMA-DOGRULA-03.md`)
- [ ] Chat'e bildirim gönderildi

## Kurallar

- **D-238:** Canlı doğrulama kuralı. Rapor tamamlandıktan sonra SALIH canlı DB'ye veri yazacak.
- **D-260:** Beyan değil, kod. Migration + Python kodu gerçek kanıt.

## Teslim

- Dosya: `plans/rapor_yasu_VERI-SEMA-DOGRULA-03.md` (denetim bulguları)
- Chat: Bildirim mesajı
- Bağımlılık: VERI-SEMA-DOGRULA-02 sonra

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]] (D-238, D-260)
- [[Huginn Data Insights/src/company_master/schema/migrations/0006_nace_details.sql]]
- [[Huginn Data Insights/src/company_master/sunum.py:250-276]]
- [[Huginn Data Insights/plans/brief_utku_VERI-NACE-SOZLUK-DIL-01.md]]
