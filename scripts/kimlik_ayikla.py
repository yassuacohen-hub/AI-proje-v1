# -*- coding: utf-8 -*-
"""Kimlik defteri araci (D-254).

companies uzerindeki serbest kimlik alanlarini tipler, kaynagiyla birlikte
company_identifiers defterine yazar. Hicbir degeri silmez, hicbirini
dogrulanmis gibi gostermez.

  python scripts/kimlik_ayikla.py            # sadece olcer, yazmaz
  python scripts/kimlik_ayikla.py --yaz      # deftere yazar (idempotent)

Tipler:
  vkn / tckn          -> D-246 kapisini gecti, confidence 1.00
  chamber_member_no   -> oda uye numarasi (aso.org.tr), vergi no DEGIL
  osb_member_no       -> OSB uye numarasi (ostim.org.tr vb.)
  unverified_legacy   -> kaynakta izi yok, confidence 0.00, karantina
"""
import sys
from collections import Counter

sys.path.insert(0, "src")

from sqlalchemy import text  # noqa: E402

from company_master.db.connection import get_engine  # noqa: E402
from company_master.etl.kimlik_no import kimlik_dogrula  # noqa: E402

# Kaynak adi -> (uye numarasi tipi, guven). Oda ve OSB numaralari vergi
# numarasi degildir; kaynagin yetkisi sadece "bu numara bende var" der.
UYE_TIPI = {
    "aso.org.tr": ("chamber_member_no", 0.80),
    "ostim.org.tr": ("osb_member_no", 0.90),
    "ivedik.org.tr": ("osb_member_no", 0.90),
    "baskentosb.org.tr": ("osb_member_no", 0.90),
}

OKU = text("""
    SELECT c.company_id, c.vergi_no, c.tax_number,
           sr.source_id, s.source_name,
           (sr.raw_tax_number IS NOT NULL
            AND sr.raw_tax_number = COALESCE(c.vergi_no, c.tax_number)) AS ham_izli
    FROM companies c
    LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
    LEFT JOIN sources s ON s.source_id = sr.source_id
    WHERE (c.vergi_no IS NOT NULL AND c.vergi_no <> '')
       OR (c.tax_number IS NOT NULL AND c.tax_number <> '')
""")

# ON CONFLICT bu kisiti gerektirir. Goc 0027 ayni indeksi IF NOT EXISTS ile
# tekrar tanimlar; sira bagimliligi olmasin diye burada da aciyoruz.
KISIT = text("""
    CREATE UNIQUE INDEX IF NOT EXISTS uq_company_identifiers_deger
        ON company_identifiers (company_id, identifier_type, identifier_value)
""")

YAZ = text("""
    INSERT INTO company_identifiers
        (company_id, identifier_type, identifier_value, source_id, confidence)
    VALUES (:company_id, :identifier_type, :identifier_value, :source_id, :confidence)
    ON CONFLICT (company_id, identifier_type, identifier_value) DO NOTHING
""")


def siniflandir(deger, kaynak_adi, ham_izli):
    """Bir kimlik degerini (tip, guven) ciftine cevirir.

    Once D-246 kapisi: gecerli VKN/TCKN ise tip kesindir.
    Gecmiyorsa kaynagin ne vaat ettigine bakilir; kaynakta izi yoksa
    deger karantinaya alinir (D-245: kaynaksiz deger kabul edilemez).
    """
    norm, tip = kimlik_dogrula(deger)
    if tip in ("vkn", "tckn"):
        return norm, tip, 1.00

    haneli = "".join(ch for ch in (deger or "") if ch.isdigit())
    if ham_izli and 3 <= len(haneli) <= 6 and kaynak_adi in UYE_TIPI:
        uye_tipi, guven = UYE_TIPI[kaynak_adi]
        return haneli, uye_tipi, guven

    return (deger or "").strip(), "unverified_legacy", 0.00


def topla(satirlar):
    """Satirlardan yazilacak defter kayitlarini uretir."""
    kayitlar = []
    for r in satirlar:
        for deger in (r.vergi_no, r.tax_number):
            if not deger or not deger.strip():
                continue
            norm, tip, guven = siniflandir(deger, r.source_name, r.ham_izli)
            if not norm:
                continue
            kayitlar.append({
                "company_id": r.company_id,
                "identifier_type": tip,
                "identifier_value": norm,
                "source_id": r.source_id,
                "confidence": guven,
            })
    # Ayni firma icin ayni tip+deger iki kolondan da gelebilir
    benzersiz = {(k["company_id"], k["identifier_type"], k["identifier_value"]): k
                 for k in kayitlar}
    return list(benzersiz.values())


def calistir(yaz: bool) -> int:
    motor = get_engine()
    with motor.connect() as conn:
        satirlar = conn.execute(OKU).all()

    kayitlar = topla(satirlar)
    sayim = Counter(k["identifier_type"] for k in kayitlar)

    print(f"okunan firma: {len(satirlar)}")
    print(f"uretilen kimlik: {len(kayitlar)}")
    for tip, adet in sayim.most_common():
        print(f"  {adet:>5}  {tip}")

    if not yaz:
        print("\n(kuru calisma - yazmak icin --yaz)")
        return 0

    with motor.begin() as conn:
        conn.execute(KISIT)
        conn.execute(YAZ, kayitlar)  # tek seferde toplu yazim (D-249)
        toplam = conn.execute(text("SELECT count(*) FROM company_identifiers")).scalar()
    print(f"\ndefterdeki toplam kimlik: {toplam}")
    return len(kayitlar)


def _kendini_dene():
    """Siniflandirma kurallarinin kosulabilir denetimi."""
    assert siniflandir("9380023742", "aso.org.tr", True)[1] == "vkn"
    assert siniflandir("51692509524", "ostim.org.tr", False)[1] == "tckn"
    # ASO'nun 6 haneli uye numarasi vergi numarasi olarak sayilmaz
    assert siniflandir("540030", "aso.org.tr", True) == ("540030", "chamber_member_no", 0.80)
    assert siniflandir("443473", "ostim.org.tr", True)[1] == "osb_member_no"
    # Kaynakta izi olmayan deger karantinaya girer
    assert siniflandir("540030", "aso.org.tr", False)[1] == "unverified_legacy"
    # Gecersiz 11 hane TCKN degil -> karantina
    assert siniflandir("85334148121", "ostim.org.tr", False)[1] == "unverified_legacy"
    print("kendini-dene: tamam")


if __name__ == "__main__":
    if "--dene" in sys.argv:
        _kendini_dene()
    else:
        calistir("--yaz" in sys.argv)
