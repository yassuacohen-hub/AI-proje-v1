-- 0047: Firma ilişki ağı v0 — company_edges tablosu
--
-- Karar: D-238 (ölçüm), D-245 (kolon adı ölçerek bulunur), D-249 (NULL != 0),
--        D-253 (göç defteri), D-256 (tek yazma kapısı), D-260 (kanıtsız beyan yasak)
-- SSOT: yedekler/Huginn Data Insights (HUGIns).txt:756-774 (10 düğüm türü),
--       :779 ("Şirket ekosistemini görselleştirmek."),
--       :837-839 (Nihai çıktılar: "Entity Graph - Şirket ağ haritası."),
--       :859-861 (Faz 3 = Entity Graph)
--
-- NEDEN YENİ GÖÇ: Bugün ne kenar tablosu ne de kenar üretici var. Faz 3 ilk adım.
--
-- FK KOLONU D-245 İLE ÖLÇÜLDÜ (brif "companies.id" varsayıyordu — diskte YANLIŞ):
--   companies tablosunun birincil anahtarı `id` DEĞİL, `company_id`'dir.
--   Kanıt: 0001_core.sql:35 -> company_id UUID PRIMARY KEY
--   Kanıt: tests/test_schema_validation.py:141 -> PK kontrolü `company_id` bekliyor
--   Bu dosyada companies(id) yazılsaydı migration UYGULANAMAZDI.
--
-- OSB KOLONU D-245 İLE ÖLÇÜLDÜ (brif "osb_slug gibi bir kolon" varsayıyordu):
--   companies tablosunda `osb_slug` YOKTUR. Var olanlar:
--     0001_core.sql:51 -> osb_id UUID REFERENCES osbs(osb_id)   <-- FK, metin değil
--     0001_core.sql:50 -> is_osb_member BOOLEAN DEFAULT FALSE
--     0001_core.sql:19 -> osbs(osb_id, name, city, ...) master tablosu
--   `osb_name` yalnız ihale tablosunda (0043_sector_columns.sql:30); companies'ta YOK.
--   Sonuç: `same_osb` kenarı companies.osb_id = companies.osb_id ile kurulur;
--          `evidence` alanına osbs.name yazılır.
--
-- company_industries VARSAYIMI DOĞRULANDI:
--   0002_relations.sql:70 (tablo), :76 (is_primary), :72 (company_id FK)
--
-- strength: NUMERIC(5,2) ve DEFAULT YOK. Ölçülemiyorsa NULL yazılır, 0 yazılmaz
--           (D-249: "veri yok" ile "0" aynı şey değildir).
--
-- evidence: BOŞ BIRAKILAMAZ. Kenarın NEDEN kurulduğunu yazar. Boş evidence
--           ile kenar yazmak kanıtsız iddiadır (D-260). Yazıcı bunu DB'de
--           değil, tek yazma kapısında Python tarafında reddeder.
--
-- YÖNSÜZ KENAR: (a_id, b_id) çiftinde a_id < b_id kısıtı tek temsili garanti eder.
--
-- v0 KAPSAMI (brif): yalnız 2 kenar türü ÜRETİLİR — same_osb, nace_complementary.
--   Kalan türler şemada KANONİK LİSTEDE vardır ama BOŞ kalır (D-249: boş ≠ yok sayılmaz).
--
-- KÖPRÜ (D-184 — karar ↔ kod ↔ test):
--   Kod    : src/company_master/graph/kenarlar.py  (kenar üreticileri + tek yazma kapısı)
--   Test   : tests/test_entity_graph.py           (9 test; mandal kırıldı/geri alındı)
--   Görev  : plans/brief_yasu_VERI-ENTITY-GRAPH-01.md
--   SSOT   : yedekler/Huginn Data Insights (HUGIns).txt:756-774, :779, :837-839, :859-861
--   Rapor  : data/orchestrator/osb_temizlik_raporu_2026-10-01.md (benzer "beyan ≠ veri" dersi)

BEGIN;

-- 1) company_edges tablosu
CREATE TABLE IF NOT EXISTS company_edges (
    company_a_id UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    company_b_id UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    edge_type     TEXT NOT NULL,
    -- strength ölçülemiyorsa NULL. DEFAULT 0 YASAK (D-249).
    strength      NUMERIC(5,2),
    -- kenarın neden kurulduğu; BOŞ BIRAKILAMAZ (D-260)
    evidence      TEXT NOT NULL,
    source        TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Yönsüz kenarın tek temsili
    CONSTRAINT ck_company_edges_yonsuz CHECK (company_a_id < company_b_id),
    -- Boş evidence yazılamaz
    CONSTRAINT ck_company_edges_evidence_bos CHECK (btrim(evidence) <> ''),

    PRIMARY KEY (company_a_id, company_b_id, edge_type)
);

-- 2) COMMENT'ler — SSOT satır numarası + Türkçe resmi ad (D-259/1 deseni, 0046 ile aynı)
COMMENT ON TABLE company_edges IS 'Firma ilişki ağı — Faz 3 Entity Graph. SSOT: HUGIns.txt:779 (Şirket ekosistemini görselleştirmek), :837-839 (Şirket ağ haritası), :859-861 (Faz 3). Kenar yönsüzdür; a_id < b_id tek temsildir.';

COMMENT ON COLUMN company_edges.company_a_id IS 'Kenarın düğüm A ucu — companies(company_id) FK. Kanonik kolon adı 0001_core.sql:35 ile ölçüldü; brifin "companies.id" varsayımı yanlıştı (D-245).';

COMMENT ON COLUMN company_edges.company_b_id IS 'Kenarın düğüm B ucu — companies(company_id) FK. company_a_id < company_b_id olacak şekilde normalize edilir.';

COMMENT ON COLUMN company_edges.edge_type IS 'Kenar türü — kanonik liste (ck_company_edges_edge_type). v0da yalnız same_osb ve nace_complementary ÜRETİLİR; kalan türler SSOT satırına dayanır ama kaynak veri yoktur, boş bırakılır (D-249).';

COMMENT ON COLUMN company_edges.strength IS 'Kenar gücü 0-100. ÖLÇÜLEBİLİYORSA yazılır; ölçülemiyorsa NULL. DEFAULT 0 YOK — veri yok ile 0 aynı şey değildir (D-249).';


-- 3) edge_type CHECK — kanonik liste
--
--   v0 ÜRETİLEN (2):
--     same_osb           — aynı OSB'de komşu        (kaynak: companies.osb_id, 0001_core.sql:51)
--     nace_complementary — NACE tamamlayıcılığı      (kaynak: company_industries, 0002_relations.sql:70)
--
--   SSOT'TAN TÜRETİLEN, v0'DA BOŞ (9):
--     SSOT 10 düğüm türünden "Şirket" (SSOT:756) kök düğümdür; iki firma arasında
--     kenar üretmez. Geri kalan 9 attribute tipi ikili kenar türetir:
--     Domain(SSOT:758) Telefon(:760) E-posta(:761) Sosyal Medya(:762)
--     Yönetici(:763) Ortak(:765) Şube(:767) Marka(:769) Grup Şirketleri(:771)
--
--   SAYI NOTU (D-260): brif Faz A madde 1 "10 tür" yazıyor; burada 11 değer var.
--   Sebep: SSOT'un 10 türünün 1'i (Şirket) kök düğümdür ve kenar türü değildir;
--   2 v0 kenar türü SSOT düğüm listesinden değil, mevcut VERİ tablolarından türer.
--   Kural "10 sayısı" değil "kanonik liste"dir; liste kanıta dayanır.
ALTER TABLE company_edges
    ADD CONSTRAINT ck_company_edges_edge_type
    CHECK (
        edge_type IN (
            -- v0 üretilen
            'same_osb',
            'nace_complementary',
            -- SSOT'tan türetilen (v0'da boş)
            'shared_domain',
            'shared_phone',
            'shared_email',
            'shared_social_media',
            'shared_officer',
            'shared_partner',
            'same_branch',
            'same_brand',
            'same_group_company'
        )
    );

-- 4) İndeksler
-- Komşu kenar araması: A ucundan çıkan kenarlar
CREATE INDEX IF NOT EXISTS idx_company_edges_a
    ON company_edges(company_a_id);
-- Komşu kenar araması: B ucundan çıkan kenarlar
CREATE INDEX IF NOT EXISTS idx_company_edges_b
    ON company_edges(company_b_id);
-- Tür bazlı filtre: "bu firmayı hangi türlerde bağlılar"
CREATE INDEX IF NOT EXISTS idx_company_edges_type
    ON company_edges(edge_type);

COMMIT;

COMMENT ON COLUMN company_edges.evidence IS 'Kenarın neden kurulduğu — kanıt metni. Boş bırakılamaz (ck_company_edges_evidence_bos + yazıcı tarafı kontrol). Örn. "aynı OSB: Başkent OSB" (D-260: kanıtsız iddia yok).';

COMMENT ON COLUMN company_edges.source IS 'Kenaryn kaynağı — üreticinin adı ve/veya veri kaynağı. Örn. "kenarlar.py:osb_komsulari", "companies.osb_id".';

COMMENT ON COLUMN company_edges.created_at IS 'Kenaryn yazılma zamanı (UTC).';
