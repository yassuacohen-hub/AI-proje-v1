-- 0038: Sorgu talebi kuyrugu (TSG-05).
--
-- ustunden-gecen: 0041_tsg_kolon_adlari_ingilizce.sql
-- Bu dosyanin TEK amaci sorgu_talepleri tablosuydu; tablo + tum kolonlar +
-- indeksler + kisit 0041'de query_requests'e RENAME edildi (D-251/1 Ingilizce
-- sema kurali). Baska gecerli iz kalmadigi icin dosya-bazli ustunden-gecen
-- kullanildi (0038'in tamami, 0037'nin sadece bir kolonu degil).
--
-- NEDEN: Musteri "bu firmayi sorgula" dedigi anda is bir yere DUSMELI. Olculdu
-- (2026-09-29): `sorgu_talepleri` benzeri hicbir tablo semada YOK, kodda da
-- `grep sorgu_talep` -> 0 sonuc. Talep su an hicbir yerde durmuyor; kim istedi,
-- ne zaman istedi, teslim edildi mi sorularinin cevabi kayitsiz.
--
-- DURUM SUTUNU: degerler `src/company_master/talep_durum.py` TEK KAPISINDAN
-- gelir (`db_deger()`); CHECK kisiti ayni dort degeri semada da baglar.
-- Iki yerde yazili olmasi kopya degil ZORLAYICI: Python kapisi atlanirsa
-- (elle SQL, baska servis) sema hala tutar. D-303 dersi: TEKILLIK/GECERLILIK
-- KOLONDA OLMAZSA KODDA TUTMAZ.
--
-- SLA: `son_teslim` HESAPLANMIS deger olarak yazilir, `talep_durum.sla_son_teslim()`
-- uretir. Kolonu generated yapmadik cunku mesai/tatil takvimi SQL'de degil
-- Python'da; iki yere yazmak iki gercek olurdu (BORC-GOC-IKI-DEFTER-01 dersi).
--
-- TAVAN (ponytail): oncelik/kuyruk siralamasi kolonu YOK. Pilotta (TSG-PILOT-20)
-- gunluk talep hacmi olculecek; hacim tek siraya sigmiyorsa oncelik o zaman eklenir.

BEGIN;

CREATE TABLE IF NOT EXISTS sorgu_talepleri (
    id            BIGSERIAL PRIMARY KEY,
    -- Olculdu (2026-09-29): `companies` birincil anahtari `company_id UUID`;
    -- `id BIGINT` diye bir kolon YOK. Ilk yazimda varsayilmisti, goc
    -- `UndefinedColumn: column "id" referenced in foreign key` ile dustu.
    -- Ders (D-268): sema tipi de olculur, hatirlanmaz.
    company_id    UUID REFERENCES companies(company_id) ON DELETE SET NULL,
    -- Serbest metin: musteri henuz DB'de olmayan bir firmayi da sorabilir.
    -- company_id NULL olabilir, sorulan sey kaybolmasin.
    sorgu_metni   TEXT NOT NULL,
    talep_eden    TEXT NOT NULL,
    durum         TEXT NOT NULL DEFAULT 'reserved'
                  CHECK (durum IN ('reserved', 'processing', 'done', 'refunded')),
    gelis_zamani  TIMESTAMPTZ NOT NULL DEFAULT now(),
    son_teslim    TIMESTAMPTZ,
    teslim_zamani TIMESTAMPTZ,
    iade_sebebi   TEXT,
    olusturuldu   TIMESTAMPTZ NOT NULL DEFAULT now(),
    guncellendi   TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE sorgu_talepleri IS
    'Musteri sorgu talebi kuyrugu. Durum degerleri talep_durum.py tek kapisindan (TSG-05).';
COMMENT ON COLUMN sorgu_talepleri.sorgu_metni IS
    'Musterinin sordugu sey (unvan/MERSIS/sicil). company_id NULL olsa da kaybolmaz.';
COMMENT ON COLUMN sorgu_talepleri.durum IS
    'reserved/processing/done/refunded. CHECK kisiti Python kapisi atlanirsa da tutar.';
COMMENT ON COLUMN sorgu_talepleri.son_teslim IS
    'SLA son ani. talep_durum.sla_son_teslim() uretir: mesai ici 10 dk, mesai disi ertesi is gunu.';
COMMENT ON COLUMN sorgu_talepleri.iade_sebebi IS
    'Iade edildiyse neden. Bos iade kabul edilmez - asagidaki CHECK zorlar.';

-- Iade sessiz olmaz: sebep yazilmadan iade edilemez (D-216 gorunurluk).
ALTER TABLE sorgu_talepleri
    DROP CONSTRAINT IF EXISTS ck_sorgu_talepleri_iade_sebepli;
ALTER TABLE sorgu_talepleri
    ADD CONSTRAINT ck_sorgu_talepleri_iade_sebepli
    CHECK (durum <> 'refunded' OR (iade_sebebi IS NOT NULL AND iade_sebebi <> ''));

-- Acik talepleri bulmak icin: kuyrugun tamami taranmaz.
CREATE INDEX IF NOT EXISTS ix_sorgu_talepleri_acik
    ON sorgu_talepleri(son_teslim)
    WHERE durum IN ('reserved', 'processing');

CREATE INDEX IF NOT EXISTS ix_sorgu_talepleri_company
    ON sorgu_talepleri(company_id)
    WHERE company_id IS NOT NULL;

COMMIT;
