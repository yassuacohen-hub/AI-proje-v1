-- 0048: Firma türü etiketi + KVKK kapsam bayrağı
--
-- Karar: KAHİN 2026-10-02 (ürün sahibi) — "Türkiye'de Türk Ticaret Kanunu ve
-- Kooperatifler Kanunu uyarınca toplam 7 ticaret şirketi ve türü vardır:
--   Sermaye: Limited Şirket / Anonim Şirket / Sermayesi Paylara Bölünmüş Komandit
--   Şahıs:   Şahıs Firması / Kollektif / Adi Komandit
--   Özel kanunlu: Kooperatif"
--   + "Her birine ... kimin şahıs şirketi kimin tüzel kişilik olduğunu
--      anlayabiliriz. Ayrıca işletme türlerine göre de tag atayabilirsin."
--
-- ÇELİŞKİ (bilinçli, kayda geçirildi): D-246/6 "Türetilmiş alan elle
-- yazılmaz; `tuzel_tip` yalnız sağlamadan geçmiş vkn/tckn kolonundan
-- türetilir. UNVANDAN TAHMİN YASAKTIR" diyor. Bu göç türü **unvandan**
-- türetir. KAHİN'in talebi ürün sahibi kararı olarak uygulanıyor; D-246/6'nın
-- itirazı (11 haneli 124 satırın 101'i unvanında LTD/A.Ş. taşıyor) kayda
-- geçmiştir. Orkestratör karar defterine yazmalıdır.
--
-- KANIT: canlı ölçüm 9412 firma (bkz. scripts/firma_turu_etiketle.py --dene,
-- 2026-10-02, KAHİN'in 4 kararından SONRA):
--   limited_sirket 4865 · anonim_sirket 1532 · sahis_isletmesi 2108
--   kooperatif 3 · payli/adi komandit 0 · kolektif 0
--   diger_tur 36 (TTK dışı: holding/vakıf) · belirsiz 868 (saf marka adı)
--
-- UYGULANAN KAHİN KARARLARI (2026-10-02) — sayıları yukarıda:
--   1. "vergi no eğer tc no ise kesin şahıs işletmesidir" → TC kontrolü
--      unvan elemesinin ÖNÜNE geçti. Canlıda geçerli TCKN = 0 olduğu için
--      ölçüm değiştirmedi, kural yazıldı.
--   2. "yabancı kayıtlarda LLC = limited şirket" → LLC deseni limited'e.
--   3. "şahıs işletmelerinde marka olmaz" → marka/faaliyet kelimesi taşıyan
--      kayıt şahıs DEĞİLDİR. Kısaltmalar kanonik sözlükten
--      (api/core/normalize.py) alınır; tam faaliyet kelimeleri
--      (_FAALIYET_KELIME) bu dosyanın kendi listesidir.
--   4. "k2 limited ama isimli olabilir" → "İSİM SOYİSİM-MARKA" kalıbı
--      (K2, ölçümde 155 kayıt) limited olarak etiketlenir.
--
-- KOLONLAR:
--   1. company_type   text  — ZATEN VAR (9412 satırda 0 dolu). Doldurulur.
--      Kanonik etiketler: limited_sirket | anonim_sirket | kooperatif
--      | kolektif_sirket | adi_komandit_sirket | payli_komandit_sirket
--      | sahis_isletmesi | diger_tur | belirsiz
--      `belirsiz` ayrı bir değerdir: "bilmiyorum" ile "tüzel" aynı şey
--      DEĞİLDİR (D-249).
--   2. kvkk_kapsam    boolean — YENİ. KAHİN: şahıs işletmelerine KVKK
--      etiketi. İkiz kolon değil: tür ile KVKK kapsamı iki AYRI olgudur —
--      vergi no kolonunda TC taşıyan bir limited şirket hukuken limited
--      kalır ama KVKK kapsamındadır (ölçümde bugün 0 kayıt).
--
-- D-251/5: göç idempotent. Aşağıdaki blok iki kez çalıştırılsa da aynı sonucu
-- verir. D-254 deseni: biçim kuralı VERİTABANINDA constraint olarak durur,
-- kodda değil — kod bir sonraki betiğin unutabileceği kuraldır.

-- 1) KVKK kapsam bayrağı
ALTER TABLE public.companies
    ADD COLUMN IF NOT EXISTS kvkk_kapsam boolean;

COMMENT ON COLUMN public.companies.kvkk_kapsam IS
    'KAHIN 2026-10-02: kayit KVKK kapsaminda mi? TRUE = sahis isletmesi VEYA '
    'vergi no kolonunda gecerli TCKN tasiyan tuzel kayit. Nihai deger '
    'firma_turu_etiketle.py tarafindan yazilir; elle yazilmaz.';

-- 2) company_type için değer kısıtı.
--    Kanonik sözlük: company_master.etl.firma_turu.TURLER
--    DB yeni bir etiketi kabul etmez; yeni tür önce göçle gelir.
DO $$
DECLARE
    mevcut_kisit text;
BEGIN
    SELECT conname INTO mevcut_kisit
    FROM pg_constraint
    WHERE conrelid = 'public.companies'::regclass
      AND conname = 'ck_companies_company_type_deger';

    IF mevcut_kisit IS NULL THEN
        ALTER TABLE public.companies
            ADD CONSTRAINT ck_companies_company_type_deger CHECK (
                company_type IS NULL OR company_type IN (
                    'limited_sirket',          -- Limited Sirket (Ltd. Sti.)
                    'anonim_sirket',           -- Anonim Sirket (A.S.)
                    'payli_komandit_sirket',   -- Sermayesi Paylara Bolunmus Komandit
                    'sahis_isletmesi',         -- Sahis Firmasi (ad + soyad)
                    'kolektif_sirket',         -- Kollektif Sirket
                    'adi_komandit_sirket',     -- Adi Komandit Sirket
                    'kooperatif',              -- Kooperatifler Kanunu
                    'diger_tur',               -- TTK disi: holding/vakif/dernek
                    'belirsiz'                 -- kanit yok ("bilmiyorum")
                )
            );
    END IF;
END $$;

COMMENT ON COLUMN public.companies.company_type IS
    'KAHIN 2026-10-02 (TTK + Kooperatifler Kanunu): firma hukuki turu. '
    'company_master.etl.firma_turu.firma_turu() tek kapidan yazar. '
    'D-246/6 ile celisiyor: karar unvandan tur turetir, o karar ise '
    'unvandan tahmin yasaklar. Kanit: yedekler/firma_turu_etiketle_*.jsonl';
