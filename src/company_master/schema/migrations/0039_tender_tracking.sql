-- Migration 0039: Tender/Ihale tracking tables
-- VERI-02: OSB ihale izleyicisi icin tablo yapilari

-- ihale_kaynaklari: Kaynak OSB portaileri
CREATE TABLE IF NOT EXISTS ihale_kaynaklari (
    kaynak_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    isim VARCHAR(255) NOT NULL,
    base_url VARCHAR(500) NOT NULL,
    liste_url_sablonu VARCHAR(500), -- {sayfa} placeholder ile
    detay_url_sablonu VARCHAR(500),
    aktif BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ihale_ilgilendirme_alanlari: OSB'de ilan edilen ihale kategorileri
CREATE TABLE IF NOT EXISTS ihale_ilgilendirme_alanlari (
    alan_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kaynak_id UUID NOT NULL REFERENCES ihale_kaynaklari(kaynak_id),
    kaynak_alan_kodu VARCHAR(100),
    alan_adi VARCHAR(255) NOT NULL,
    aktif BOOLEAN DEFAULT true
);

-- ihale_ilanlari: Ana ihale ilanlari tablosu
CREATE TABLE IF NOT EXISTS ihale_ilanlari (
    ilan_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kaynak_id UUID NOT NULL REFERENCES ihale_kaynaklari(kaynak_id),
    kaynak_ilan_id VARCHAR(100) NOT NULL, -- OSB portailindeki orijinal ID
    ilan_basligi VARCHAR(500) NOT NULL,
    ilan_turu VARCHAR(50), -- 'yapim', 'tedarik', 'hizmet', 'danismanlik'
    usul VARCHAR(50), -- 'acik', 'sinirli', 'dogrudan_temin', 'yatirimci_secimi'
    
    -- Onemli tarihler
    duyuru_tarihi DATE,
    soru_cevap_son_tarihi DATE,
    teklif_verme_son_tarihi DATE,
    acilis_tarihi DATE,
    
    -- Yer
    il VARCHAR(100),
    ilce VARCHAR(100),
    osb_adi VARCHAR(255),
    
    -- Butce ve maliyet
    tahmini_maliyet NUMERIC(18,2),
    birim VARCHAR(10),
    
    -- Detay
    aciklama TEXT,
    belge_url TEXT,
    
    -- Durum
    durum VARCHAR(50) DEFAULT 'aktif', -- 'aktif', 'iptal', 'sonuclandi', 'duyuru_cekildi'
    kaynak_ilan_url TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    
    UNIQUE(kaynak_id, kaynak_ilan_id)
);

-- ihale_katilimcilar: Ihaleye katilan firmalar
CREATE TABLE IF NOT EXISTS ihale_katilimcilar (
    katilimci_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ilan_id UUID NOT NULL REFERENCES ihale_ilanlari(ilan_id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(company_id), -- companies tablosuna bagli
    aday_firma_adi VARCHAR(255) NOT NULL, -- Ilanda gecen firma adi (company_id yoksa)
    vergi_no VARCHAR(20),
    siralama INTEGER, -- Teklif sirasi
    teklif_tutari NUMERIC(18,2),
    kazandi BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ihale_ekler: Ilanla ilgili belgeler
CREATE TABLE IF NOT EXISTS ihale_ekler (
    ek_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ilan_id UUID NOT NULL REFERENCES ihale_ilanlari(ilan_id) ON DELETE CASCADE,
    dosya_adi VARCHAR(255),
    dosya_turu VARCHAR(50), -- 'teklif_mektubu', 'sozlesme', 'ozel_sartname', 'teknik_sartname', 'diger'
    dosya_url TEXT NOT NULL,
    dosya_boyutu BIGINT,
    yukleyen VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ihale_takip: Kullanici/ajanim takip listesi
CREATE TABLE IF NOT EXISTS ihale_takip (
    takip_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ajan_id VARCHAR(100) NOT NULL, -- ajan kimligi (utku, ihsan, vb.)
    ilan_id UUID NOT NULL REFERENCES ihale_ilanlari(ilan_id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(ajan_id, ilan_id)
);

-- Indexler
CREATE INDEX IF NOT EXISTS idx_ihale_ilanlari_kaynak ON ihale_ilanlari(kaynak_id);
CREATE INDEX IF NOT EXISTS idx_ihale_ilanlari_tarih ON ihale_ilanlari(teklif_verme_son_tarihi);
CREATE INDEX IF NOT EXISTS idx_ihale_ilanlari_durum ON ihale_ilanlari(durum);
CREATE INDEX IF NOT EXISTS idx_ihale_ilanlari_il ON ihale_ilanlari(il, ilce);
CREATE INDEX IF NOT EXISTS idx_ihale_katilimcilar_ilan ON ihale_katilimcilar(ilan_id);
CREATE INDEX IF NOT EXISTS idx_ihale_katilimcilar_company ON ihale_katilimcilar(company_id);
CREATE INDEX IF NOT EXISTS idx_ihale_ekler_ilan ON ihale_ekler(ilan_id);