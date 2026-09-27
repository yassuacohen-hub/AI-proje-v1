# Brif — VERI-HAYALET-TEMIZ-01 (P0)

**Sahip:** utku · **Mod:** code · **Süre:** 3s · **Kaynak:** ihsan (KAHİN denetimi 2026-09-27)

## Sorun

`companies` tablosunda **14003 satır var, gerçek tekil firma 9412**. Aradaki **4591 satır hayalet** — kazıyıcı aynı firmayı defalarca yazmış.

### Kanıt (canlı Supabase, ölçüldü)

```
companies toplam      : 14003
companies tekil ad    :  9412
tekrarli ad grubu     :   494
fazlalik satir        :  4591   <-- silinecek
vergi_no dolu         :   774
ivedik kayitli firma  :  3134
```

Kaynak bazında:

| kaynak | satır | tekil | oran |
|--------|-------|-------|------|
| ostim.org.tr | 9513 | 8740 | %91.9 |
| **ivedik.org.tr** | **3134** | **14** | **%0.4** |
| baskentosb.org.tr | 761 | 481 | %63.2 |
| aso.org.tr | 592 | 592 | %100 |

İvedik'te 14 firma **224'er kez** yazılmış:

```
228 x FATIH BAĞBAŞI
224 x EGEMEN PANO
224 x ARAD BRANDING
224 x ALİ EŞREF ERKANİ
... (14 ünvan, her biri ~224 kopya)
```

## Kök neden — ZATEN DÜZELTİLDİ

WordPress tabanlı OSB siteleri geçersiz `?page/N/` isteğine **sayfa 1'i** döndürür. Eski kazıyıcıdaki "liste boşalınca dur" koşulu hiç gerçekleşmez → sonsuz döngü.

Koruma [`base_osfb_scraper.sayfa_dongusu()`](../src/company_master/etl/scrapers/base_osfb_scraper.py:101) içinde mevcut (D-235): `MAX_SAYFA=500` sert tavan + `TEKRAR_TOLERANSI=2` imza karşılaştırması + ünvan tekilleştirme. 14 test yeşil.

**Yani kod güvende — kirli olan sadece veritabanı.**

## Yapılacak

`src/company_master/etl/hayalet_kayit_temizle.py`

1. **Önce yedek**: silinecek satırları `data/backup/hayalet_YYYYMMDD.jsonl`'e yaz.
2. Aynı `legal_name` grubunda **hangi satırın kalacağını** şu sıraya göre seç:
   - `vergi_no`/`tax_number` dolu olan öncelikli (774 satır bu bilgiye sahip),
   - sonra en çok alanı dolu olan,
   - eşitlikte en küçük `company_id`.
3. Kalan satırın eksik alanlarını kopyalardan **birleştir** — veri kaybı olmasın (telefon, e-posta, adres, web sitesi).
4. Silmeden önce bağlı satırları kalan kayda taşı: `company_industries`, `nace_validity`, `source_records` bağları.
5. Sil.
6. Tekrar oluşmasın diye: `companies.legal_name` üzerine **UNIQUE kısıt** ekle (migration).

## Kabul ölçütleri

- `select count(*) from companies` = `select count(distinct legal_name) from companies`
- Silmeden önceki `vergi_no` dolu sayısı korunur: **774** (düşerse iş reddedilir)
- Yedek dosyası mevcut ve satır sayısı = silinen satır sayısı
- UNIQUE kısıt migration dosyası var
- Test: `tests/test_hayalet_kayit_temizle.py` — sahte veriyle birleştirme + seçim sırası doğrulanır

## Uyarı

Bu iş **geri alınamaz**. Yedek yazılmadan tek satır silinmeyecek. Adım 3 (birleştirme) atlanırsa kopyalarda duran iletişim bilgisi kaybolur — silme değil, **toplama** işi bu.
