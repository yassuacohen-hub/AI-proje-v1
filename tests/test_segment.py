# -*- coding: utf-8 -*-
"""PO-BACK-02 — Segment Eligibility Skoru + Onay Akışı testleri."""

from __future__ import annotations

from company_master.segment import (
    aggregate_eligibility,
    calculate_segment_eligibility,
    onay_aciklama,
    segment_eligibility_skoru,
    segment_onay_durumu,
)


SEGMENTLER = [
    {
        "segment_id": "SEG-001",
        "name": "B2B Teknoloji",
        "criteria": {"sektor": "teknoloji", "firma_tipi": "B2B", "min_hacim": 1000000},
    },
    {
        "segment_id": "SEG-002",
        "name": "E-ticaret",
        "criteria": {"sektor": "e-ticaret", "min_hacim": 5000000},
    },
    {
        "segment_id": "SEG-003",
        "name": "Enerji",
        "criteria": {"sektor": "enerji", "min_hacim": 5000000},
    },
    {
        "segment_id": "SEG-004",
        "name": "Turizm",
        "criteria": {"sektor": "turizm", "turu": "premium"},
    },
    {
        "segment_id": "SEG-005",
        "name": "İnşaat",
        "criteria": {"sektor": "inşaat", "min_hacim": 10000000},
    },
]


def test_uygun_firma_tum_kriterleri_eslesir():
    firma = {
        "company_id": "c1",
        "company_name": "Ankara Yazılım A.Ş.",
        "sektor": "teknoloji",
        "firma_tipi": "B2B",
        "revenue": 2000000,
    }

    sonuc = calculate_segment_eligibility(firma, SEGMENTLER)
    b2b = next(s for s in sonuc if s.segment_id == "SEG-001")

    assert b2b.eligible is True
    assert b2b.score == 100.0
    assert b2b.matched_criteria == ["sektor", "firma_tipi", "min_hacim"]
    assert b2b.missing_fields == []


def test_hacim_altinda_firma_eligible_olmaz():
    firma = {
        "company_id": "c2",
        "company_name": "Küçük Yazılım",
        "sektor": "teknoloji",
        "firma_tipi": "B2B",
        "revenue": 900000,
    }

    sonuc = calculate_segment_eligibility(firma, SEGMENTLER)
    b2b = next(s for s in sonuc if s.segment_id == "SEG-001")

    assert b2b.eligible is False
    assert b2b.score == 66.67
    assert b2b.missing_fields == ["min_hacim"]


def test_eksik_alan_eksikler_listesinde_gosterilir():
    firma = {
        "company_id": "c3",
        "company_name": "Enerji Firması",
        "sektor": "enerji",
        "revenue": 6000000,
    }

    sonuc = calculate_segment_eligibility(firma, SEGMENTLER)
    enerji = next(s for s in sonuc if s.segment_id == "SEG-003")

    # SEG-003 kriterleri: {sektor, min_hacim} — firma_tipi yok
    assert enerji.eligible is True
    assert enerji.score == 100.0
    assert enerji.missing_fields == []


def test_aggregate_eligibility_ozet_verir():
    firma = {
        "company_id": "c4",
        "company_name": "Turizm Premium A.Ş.",
        "sektor": "turizm",
        "turu": "premium",
        "revenue": 3000000,
    }

    ozet = aggregate_eligibility(firma, SEGMENTLER)

    assert ozet["toplam_segment"] == 5
    assert ozet["uygun_segment_sayisi"] == 1
    assert ozet["genel_skor"] == 26.67
    assert ozet["onay_durumu"] == "eksik alan"


def test_onay_aciklama_etiketleri_icerir():
    firma = {
        "company_id": "c5",
        "company_name": "Yapı Merkezi A.Ş.",
        "sektor": "inşaat",
        "firma_tipi": "B2B",
        "revenue": 15000000,
    }

    metin = onay_aciklama(firma, SEGMENTLER)

    assert "📋 Yapı Merkezi A.Ş." in metin
    assert "✅ İnşaat" in metin
    assert "❌" in metin
    assert "eksik" in metin


def test_kolaylik_fonksiyonlari():
    firma = {
        "company_id": "c6",
        "company_name": "E-ticaret",
        "sektor": "e-ticaret",
        "firma_tipi": "B2B",
        "revenue": 6000000,
    }

    assert segment_eligibility_skoru(firma, SEGMENTLER) == 43.33
    assert segment_onay_durumu(firma, SEGMENTLER) == "eksik alan"
# ---------------------------------------------------------------------------
# PO-BACK-02: eligibility_skoru + onay_durumu testleri
# ---------------------------------------------------------------------------

from company_master.segment import eligibility_skoru, onay_durumu


def test_eligibility_skoru_bos_firma():
    """Boş firma → 0.0"""
    assert eligibility_skoru({}) == 0.0


def test_eligibility_skoru_none_firma():
    """None firma → 0.0"""
    assert eligibility_skoru(None) == 0.0  # type: ignore[arg-type]


def test_eligibility_skoru_zorunlu_alan_yok():
    """company_name veya sector yok → 0.0"""
    firma = {"company_name": "Test", "revenue": 1000000}
    assert eligibility_skoru(firma) == 0.0

    firma2 = {"sektor": "teknoloji", "revenue": 1000000}
    assert eligibility_skoru(firma2) == 0.0


def test_eligibility_skoru_tam_uygun():
    """Tüm alanlar mevcut, sector eşleşmesi var, employee aralığında → 1.0"""
    firma = {
        "company_name": "Tam Yazılım",
        "sektor": "teknoloji",
        "firma_tipi": "B2B",
        "revenue": 10000000,  # ~1000 employees → 10-5000 aralığında
    }
    skor = eligibility_skoru(firma)
    assert skor > 0.95  # Yaklaşık 1.0


def test_eligibility_skoru_yuksek_revenue():
    """Çok yüksek revenue → employee aralığına uygun"""
    firma = {
        "company_name": "Dev Şirket",
        "sektor": "teknoloji",
        "firma_tipi": "B2B",
        "revenue": 50000000,  # ~5000 employees → tam aralıkta
    }
    skor = eligibility_skoru(firma)
    assert skor == 1.0


def test_eligibility_skoru_dusuk_revenue():
    """Çok düşük revenue → employee aralığına uygun değil"""
    firma = {
        "company_name": "Küçük İş",
        "sektor": "teknoloji",
        "firma_tipi": "B2B",
        "revenue": 10000,  # ~1 employee → aralık dışarı
    }
    skor = eligibility_skoru(firma)
    assert skor == 0.67  # Sektör(0.33) + veri tamlılığı(0.34)


def test_onay_durumu_otomatik():
    """Skor >= 0.6 → 'otomatik'"""
    assert onay_durumu(0.6) == "otomatik"
    assert onay_durumu(1.0) == "otomatik"
    assert onay_durumu(0.75) == "otomatik"


def test_onay_durumu_manuel():
    """0.4 <= skor < 0.6 → 'manuel'"""
    assert onay_durumu(0.4) == "manuel"
    assert onay_durumu(0.5) == "manuel"
    assert onay_durumu(0.59) == "manuel"


def test_onay_durumu_red():
    """skor < 0.4 → 'red'"""
    assert onay_durumu(0.0) == "red"
    assert onay_durumu(0.3) == "red"
    assert onay_durumu(0.39) == "red"


def test_onay_durumu_ozel_esik():
    """Özel esik değeri ile çalışır"""
    assert onay_durumu(0.8, esik=0.7) == "otomatik"
    assert onay_durumu(0.6, esik=0.7) == "manuel"
    assert onay_durumu(0.3, esik=0.7) == "red"


def test_onay_durumu_gecersiz_girdi():
    """None veya sayısal olmayan girdi → 'red'"""
    assert onay_durumu(None) == "red"  # type: ignore[arg-type]
    assert onay_durumu("abc") == "red"  # type: ignore[arg-type]


def test_onay_durumu_aralik_klip():
    """Geçersiz aralık (0-1 dışarı) → 0-1'e klipla"""
    assert onay_durumu(1.5) == "otomatik"  # 1.0'e kliplendi
    assert onay_durumu(-0.5) == "red"  # 0.0'a kliplendi
