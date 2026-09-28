-- 0035: ticaret sicil numarasini ham arsivden semaya cikarir.
--
-- BORCUN ADI YANLISTI (D-265/D-266 deseni). Devir notu "620 firmanin sicil
-- degeri YANLIS ALANDA, tasinmali" diyordu. Olculen:
--   companies.trade_registry_number = 0 / 9412
--   companies.trade_registry_office = 0 / 9412
--   tax_number icinde 3-6 haneli sicil deseni = 0 satir
-- Deger yanlis kolonda DEGIL, HIC KOLONDA DEGIL. Tek bulundugu yer ham arsiv:
--   source_records.raw_payload ->> 'ticaretSicilNo' = 620 kayit
-- Yani bu bir kolon->kolon TASIMA degil, arsiv->sema CIKARMA'dir.
--
-- KOK NEDEN: etl/normalize.py payload'dan 'ticaret_sicil_no' (snake_case)
-- okuyordu; gercek anahtar 'ticaretSicilNo' (camelCase). Ustelik _map_row()
-- INSERT listesinde trade_registry_number hic YOKTU — ETL bu kolonu hic
-- yazmiyordu. Bu goc gecmisi onarir; gelecegi normalize.py duzeltmesi onarir.
-- Ikisi birlikte olmazsa yarim goc olur (D-258/4).
--
-- OLCUM (D-260: iki oran birden):
--   kayit kapsamasi : 620 / 9401 source_records
--   firma kapsamasi : 619 / 9412 companies   (1 kayit firmaya bagli degil)
--   ayni firmaya iki FARKLI sicil degeri     : 0 (cakisma yok)
--   sicil_dogrula() tek kapisi (D-247)       : 619 gecerli, 0 gecersiz
--   asagidaki SQL ifadesi ile sicil_dogrula() farki : 0 satir (olculdu)
--
-- DURUSTLUK NOTU — TAVAN NEDEN YUKSELIYOR:
--   D-250 puan icin sicil no VE sicil dairesi'ni BIRLIKTE ister.
--   Daire tasiyan firma sayisi 25 / 9412 = binde 2.7.
--   Yani 619 firma degeri kazanir, sadece 25'i PUAN kazanir. Tavan yukseliyorsa
--   bunun sebebi "620 firma puan aldi" degil; D-258'de "kilitli" tanimi
--   "sifir firma puan aliyor" oldugu icin, 25 > 0 olmasi kilidi acar.
--   Ortalama puan bu goc ile kayda deger artmaz. Acilan sey TAVAN'dir.
--
-- KAYNAK KOLON (D-254/D-263 ikiz yasagi): ikiz kolon OLUSMUYOR. Kaynak bir
-- kolon degil, raw_payload — ve D-246/4 raw_payload'u kalici ham arsiv olarak
-- tanimlar. Arsivden okumak ikizlik degildir; dusurulecek kolon yoktur.

BEGIN;

UPDATE companies c
SET trade_registry_number = v.sicil_no,
    trade_registry_office = v.sicil_daire
FROM (
    SELECT c2.company_id,
           CASE WHEN x.n ~ '^[0-9]{3,6}$' THEN x.n END AS sicil_no,
           CASE WHEN x.n ~ '^[0-9]{3,6}$' THEN x.d END AS sicil_daire
    FROM source_records sr
    JOIN companies c2 ON c2.source_record_id = sr.source_record_id
    CROSS JOIN LATERAL (
        SELECT nullif(btrim(split_part(
                   btrim(sr.raw_payload ->> 'ticaretSicilNo'), '-', 1)), '') AS n,
               nullif(upper(rtrim(btrim(split_part(
                   btrim(sr.raw_payload ->> 'ticaretSicilNo'), '-', 2)), '.')), '') AS d
    ) x
    WHERE nullif(btrim(sr.raw_payload ->> 'ticaretSicilNo'), '') IS NOT NULL
) v
WHERE c.company_id = v.company_id
  AND v.sicil_no IS NOT NULL;

COMMENT ON COLUMN companies.trade_registry_number IS
    'Ticaret sicil no. Kaynak: source_records.raw_payload->>ticaretSicilNo (aso.org.tr + ostim.org.tr). Dogrulama tek kapisi: etl/kimlik_no.sicil_dogrula() — 3-6 hane. TOBB/TSG kapali (D-257), bu yuzden tek kaynak ham arsivdir (D-267).';

COMMENT ON COLUMN companies.trade_registry_office IS
    'Sicil dairesi (ilce). Ham metin; "BEYP." ile "BEYPAZARI" ayri deger kalir. D-250: puan icin no ile BIRLIKTE dolu olmasi gerekir (D-267).';

-- Mandal: beklenen sayilar tutmuyorsa goc kendini durdurur.
-- Sayilar ustteki olcumden gelir; degisirlerse once olcum yenilenmeli.
DO $$
DECLARE
    no_sayisi    int;
    daire_sayisi int;
    firma_sayisi int;
BEGIN
    SELECT count(trade_registry_number), count(trade_registry_office), count(*)
      INTO no_sayisi, daire_sayisi, firma_sayisi
      FROM companies;

    IF no_sayisi <> 619 THEN
        RAISE EXCEPTION USING MESSAGE =
            'GOC 0035 DURDU: sicil no dolu firma = ' || no_sayisi || ', beklenen 619';
    END IF;
    IF daire_sayisi <> 25 THEN
        RAISE EXCEPTION USING MESSAGE =
            'GOC 0035 DURDU: sicil dairesi dolu firma = ' || daire_sayisi || ', beklenen 25';
    END IF;
    IF firma_sayisi <> 9412 THEN
        RAISE EXCEPTION USING MESSAGE =
            'GOC 0035 DURDU: firma sayisi = ' || firma_sayisi || ', beklenen 9412 (satir kaybi)';
    END IF;
END $$;

COMMIT;
