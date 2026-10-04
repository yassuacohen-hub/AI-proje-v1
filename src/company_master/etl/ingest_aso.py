# -*- coding: utf-8 -*-
"""ASO (Ankara Sanayi Odası) ham kaydını companies + source_records alır.

Tek giriş noktası: `data/aso/aso_full.jsonl` (JSONL).
Rapor/özet dosyaları ASLA firma kaydı sanılmaz.

D-211: tek yol. Eski `scripts/ingest_aso_data.py` ikizi silindi; kayıt izi
       yalnız `source_records.raw_payload` içindedir.
D-233: eşleşme YALNIZ kesindir. Fuzzy `LIKE '%unvan[:20]%'` taşınmadı —
       ölçüldü: 722 unvanın 673'ünde ilk 20 karakter birden fazla yanlış
       aday üretiyor (ortak tasfiye öneki). Yanlış firmayı zenginleştirmek
       kesin eşleşmeden daha kötüdür.
D-244: yazma idempotenttir; `ON CONFLICT (legal_name)` +
       `ON CONFLICT (source_id, external_id)`.
D-246: `tax_number` ve `raw_tax_number` bu yoldan YAZILMAZ. ASO'nun
       `ticaretSicilNo` alanı VKN değildir; ham değer `raw_payload` içinde
       durur (D-267).
D-259: `data_quality_score` bu yoldan yazılmaz (puanı tek kapı yazar).
D-261: `content_hash` yalnız kayıt içeriğinden türetilir; zaman damgası ya da
       satır kimliği karışmaz (aksi halde her koşu yeni satır açar).
D-263: `companies.source_record_id` A yönü KAYNAKTIR. Dolu bir A yönü
       ezilmez; bağ yalnız eksikse doldurulur.
D-264: "(IFLAS NEDENIYLE) TASFİYE HALİNDE" oneki ayri bir firma degil,
        bir haldir; unvan oldugu gibi yazilir, onek soyulmez.
D-233: `data/aso/aso_full_clean.jsonl` SILINMEDI ve bu modulle iliskilendirilmez.
        Brif "tum turetilmis dosyalari tasi" diyordu; olcum yanlisladi.
        Bu dosya 716 tekil unvan / 781 `?` isaretli (kanonik dosyada 722 unvan,
        0 `?`) ve `scripts/osb_tarama.py` KORUNAN listesinde (SHA-256 kilidi
        `data/osb_tarama/_kaynak_kilidi.json`), ayrica
        `scripts/osb_veri_seti_uret.py` 9 `kaynaklar` referansi uretiyor.
        Yani bu bir ikiz yukleme yolu degil, OSB'nin **kendi kalite filtresinden
        gecmis girdisi**. Canli kod bu yola bakiyorsa yol kopyadir, bagimliliktir.
        Kaldirilma isi: OSB tuketicisi once kanonik dosyaya gecirilir, sonra
        bu dosya tuketici olmadan (D-236) silinir.
"""

import hashlib
import json
from pathlib import Path

from sqlalchemy import text

from ..db.connection import get_engine
from .kimlik_no import sicil_dogrula

ROOT = Path(__file__).resolve().parents[3]
ASO_DATA_DIR = ROOT / "data" / "aso"

# D-211: tek dosya. Rapor/ozet dosyalari glob ile hic karistirilmaz.
KAYNAK_DOSYA = "aso_full.jsonl"

# D-267: `sources.source_name` degeridir (0032'de ayni yol kullanildi).
KAYNAK_ADI = "aso.org.tr"

#: D-246: bu kolonlara yazilacak deger yok. ASO sicil numarasi VKN degildir.
YAZILMAZ_KOLONLAR = ("tax_number", "raw_tax_number", "data_quality_score")

#: Ham kaydin korundugu alanlar; ham deger kaybolmaz (D-246/4).
HAM_ALANLAR = (
    "unvan",
    "adres",
    "eposta",
    "telefonlar",
    "naceKod",
    "naceDetay",
    "meslekGrubu",
    "ticaretSicilNo",
    "detailToken",
    "yetkililer",
)

INSERT_SQL = text(
    "INSERT INTO companies "
    "(legal_name, address, primary_phone, primary_email, nace_code, "
    " is_ankara, is_osb_member, created_at, updated_at) "
    "VALUES (:legal_name, :address, :primary_phone, :primary_email, :nace_code, "
    " TRUE, TRUE, NOW(), NOW()) "
    "ON CONFLICT (legal_name) DO NOTHING "
    "RETURNING company_id"
)

#: D-233: kesin eslesme. `LIKE` iceren bir eslesme YAZILMAZ.
ESLES_SQL = text(
    "SELECT company_id FROM companies "
    "WHERE LOWER(TRIM(legal_name)) = LOWER(TRIM(:unvan)) LIMIT 1"
)

#: D-245: dolu alan ezilmez; yalnizca bos olan doldurulur.
ZENGINLESTIR_SQL = text(
    "UPDATE companies SET "
    " address       = COALESCE(NULLIF(address, ''), :adres), "
    " primary_phone = COALESCE(NULLIF(primary_phone, ''), :phone), "
    " primary_email = COALESCE(NULLIF(primary_email, ''), :email), "
    " updated_at = NOW() "
    "WHERE company_id = :cid"
)

#: D-263: A yonu kaynaktir; doluysa ezilmez.
BAGLA_SQL = text(
    "UPDATE companies SET source_record_id = COALESCE(source_record_id, :sid), "
    "updated_at = NOW() WHERE company_id = :cid"
)

#: D-244 + D-261: ayni `(source_id, external_id)` ikilisi ikinci kosuda
#: yeni satir acmaz; ham alanlar yalniz eksikse doldurulur.
KAYNAK_SQL = text(
    "INSERT INTO source_records "
    "(source_id, external_id, raw_name, raw_address, raw_phone, raw_email, "
    " raw_tax_number, raw_nace, raw_payload, content_hash, company_id) "
    "VALUES (:source_id, :external_id, :raw_name, :raw_address, :raw_phone, "
    " :raw_email, NULL, :raw_nace, (:payload)::jsonb, :content_hash, :company_id) "
    "ON CONFLICT (source_id, external_id) DO UPDATE SET "
    " raw_address = COALESCE(source_records.raw_address, EXCLUDED.raw_address), "
    " raw_phone   = COALESCE(source_records.raw_phone, EXCLUDED.raw_phone), "
    " raw_email   = COALESCE(source_records.raw_email, EXCLUDED.raw_email), "
    " raw_payload = COALESCE(source_records.raw_payload, '{}'::jsonb) "
    "              || COALESCE(EXCLUDED.raw_payload, '{}'::jsonb), "
    " content_hash = EXCLUDED.content_hash, "
    " company_id  = COALESCE(source_records.company_id, EXCLUDED.company_id) "
    "RETURNING source_record_id"
)

KAYNAK_ID_SQL = text(
    "SELECT source_id FROM sources WHERE source_name = :ad LIMIT 1"
)


def kaynak_dosya(veri_disi=None):
    """Yalniz ham JSONL dosyasini secer; rapor/ozet dosyalarini dislar."""
    dizin = Path(veri_disi) if veri_disi else ASO_DATA_DIR
    aday = dizin / KAYNAK_DOSYA
    return aday if aday.is_file() else None


def kayitlari_oku(dosya):
    """JSONL satirlarini okur. Bozuk satir atlanir."""
    kayitlar = []
    with open(dosya, "r", encoding="utf-8") as f:
        for satir in f:
            satir = satir.strip()
            if not satir:
                continue
            try:
                kayitlar.append(json.loads(satir))
            except json.JSONDecodeError:
                continue
    return kayitlar


def _metin(deger):
    if deger is None:
        return None
    metin = str(deger).strip()
    return metin or None


def _telefon(kayit):
    """`telefonlar` listesi sozluk ya da duz metin olabilir."""
    liste = kayit.get("telefonlar") or []
    if isinstance(liste, (str, int)):
        return _metin(liste)
    for giris in liste:
        deger = giris.get("no") or giris.get("numara") if isinstance(giris, dict) else giris
        if deger and str(deger).strip():
            return str(deger).strip()
    return None


def _external_id(kayit):
    """D-262: UNIQUE kisit NULL'a baglanmaz; kimlik uretilmezse atlanir."""
    return _metin(kayit.get("ticaretSicilNo")) or _metin(kayit.get("detailToken"))


def _raw_payload(kayit):
    """Ham kaydin korundugu JSONB. Kaynak sizintisi alanlari da durur."""
    ham = {alan: kayit.get(alan) for alan in HAM_ALANLAR if alan in kayit}
    ham["kaynak"] = KAYNAK_ADI
    if kayit.get("meslekGrubu"):
        ham["sektor"] = kayit.get("meslekGrubu")
    return ham


def _content_hash(kayit):
    """D-261: yalniz kayit icerigi. Zaman damgasi/satir kimligi karismaz."""
    kanonik = json.dumps(kayit, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(kanonik.encode("utf-8")).hexdigest()


def satirlari_hazirla(kayitlar):
    """Ham kayitlari yazilabilir satirlara cevirir; batch ici mukerreri tekillestirir."""
    satirlar = []
    gorulen = set()
    for kayit in kayitlar:
        unvan = _metin(kayit.get("unvan"))
        if not unvan:
            continue
        anahtar = unvan.casefold()
        if anahtar in gorulen:
            continue
        gorulen.add(anahtar)
        satirlar.append(
            {
                "legal_name": unvan,
                "address": _metin(kayit.get("adres")),
                "primary_phone": _telefon(kayit),
                "primary_email": _metin(kayit.get("eposta")),
                "nace_code": _metin(kayit.get("naceKod")),
                "external_id": _external_id(kayit),
                "raw_nace": _metin(kayit.get("naceKod")),
                "raw_payload": _raw_payload(kayit),
                "content_hash": _content_hash(kayit),
            }
        )
    return satirlar


def gecersiz_sicil_sayisi(kayitlar):
    """D-267: ticaret sicili KENDI kapisindan gecer.

    Eski ölçüm `kimlik_dogrula()` (VKN/TCKN kapısı) kullanıyordu ve
    1091/1091 "geçersiz kimlik" diyordu. Bu bir alarm değil, kapının yanlış
    seçildiğinin işaretiydi: 3-6 haneli sicil numarası zaten VKN değildir
    (D-245: doluluk geçerlilik değildir).
    """
    sayi = 0
    for kayit in kayitlar:
        ham = _metin(kayit.get("ticaretSicilNo"))
        if ham and sicil_dogrula(ham)[0] is None:
            sayi += 1
    return sayi


def _zenginlestirilebilir(satir):
    return any(satir.get(a) for a in ("address", "primary_phone", "primary_email"))


def yaz(engine, satirlar, dry_run=False):
    """Kesin eslesme + kaynak izi + bos alan zenginlestirme. D-233/D-244/D-263."""
    sonuc = {
        "eklenen": 0,
        "eslesen": 0,
        "zenginlestirilen": 0,
        "kaynak_yazilan": 0,
        "kaynak_atlanan": 0,
    }
    if not satirlar:
        return sonuc

    if dry_run:
        # D-243: prova diske/DB'ye yazmaz.
        sonuc["kaynak_atlanan"] = sum(1 for s in satirlar if not s["external_id"])
        return sonuc

    with engine.begin() as c:
        satir = c.execute(KAYNAK_ID_SQL, {"ad": KAYNAK_ADI}).first()
        if satir is None:
            raise RuntimeError(
                "sources tablosunda " + KAYNAK_ADI + " kaynagi yok; "
                "kaynak kaydi olusturulmadan ingest calismaz."
            )
        source_id = satir[0]

        # D-243: tek `engine.begin()` — yarim yazim olmaz. Hata olursa
        # istisna yukselir; sessizce kismi kalan bir kosu birakilmaz.
        for s in satirlar:
            mevcut = c.execute(ESLES_SQL, {"unvan": s["legal_name"]}).first()
            if mevcut is None:
                yeni = c.execute(INSERT_SQL, s).first()
                company_id = yeni[0] if yeni else None
                if company_id is None:
                    # ON CONFLICT yarisi: satir baska bir kosuda eklendi.
                    eslesen = c.execute(ESLES_SQL, {"unvan": s["legal_name"]}).first()
                    company_id = eslesen[0] if eslesen else None
                    sonuc["eslesen"] += 1
                else:
                    sonuc["eklenen"] += 1
            else:
                company_id = mevcut[0]
                sonuc["eslesen"] += 1

            if company_id is None:
                continue

            if _zenginlestirilebilir(s):
                c.execute(
                    ZENGINLESTIR_SQL,
                    {
                        "cid": company_id,
                        "adres": s["address"],
                        "phone": s["primary_phone"],
                        "email": s["primary_email"],
                    },
                )
                sonuc["zenginlestirilen"] += 1

            if not s["external_id"]:
                # D-262: kimliksiz kayit UNIQUE ile korunamaz.
                sonuc["kaynak_atlanan"] += 1
                continue

            sid = c.execute(
                KAYNAK_SQL,
                {
                    "source_id": source_id,
                    "external_id": s["external_id"],
                    "raw_name": s["legal_name"],
                    "raw_address": s["address"],
                    "raw_phone": s["primary_phone"],
                    "raw_email": s["primary_email"],
                    "raw_nace": s["raw_nace"],
                    "payload": json.dumps(s["raw_payload"], ensure_ascii=False, default=str),
                    "content_hash": s["content_hash"],
                    "company_id": company_id,
                },
            ).first()
            if sid is not None:
                c.execute(BAGLA_SQL, {"cid": company_id, "sid": sid[0]})
                sonuc["kaynak_yazilan"] += 1
    return sonuc


def ingest_aso_data(veri_disi=None, engine=None, dry_run=False):
    """ASO ham kaydini companies + source_records tablosuna alir. Olcum doner."""
    dosya = kaynak_dosya(veri_disi)
    if dosya is None:
        print("ASO veri dosyasi bulunamadi: " + KAYNAK_DOSYA)
        return {"dosya": None, "okunan": 0, "yazilabilir": 0, "eklenen": 0}

    kayitlar = kayitlari_oku(dosya)
    satirlar = satirlari_hazirla(kayitlar)
    gecersiz = gecersiz_sicil_sayisi(kayitlar)
    # D-243: kuruda engine HIC kurulmaz; `get_engine()` canliya baglanir.
    olcum = yaz(None, satirlar, dry_run=True) if dry_run else yaz(
        engine or get_engine(), satirlar
    )

    print(f"Isleniyor: {dosya}" + ("  [KURU]" if dry_run else ""))
    print(f"  okunan satir      : {len(kayitlar)}")
    print(f"  yazilabilir satir : {len(satirlar)}")
    print(f"  eklendi           : {olcum['eklenen']}")
    print(f"  kesin eslesme     : {olcum['eslesen']}")
    print(f"  zenginlestirilen  : {olcum['zenginlestirilen']}")
    print(f"  kaynak kaydi      : {olcum['kaynak_yazilan']} (kimliksiz: {olcum['kaynak_atlanan']})")
    print(f"  gecersiz sicil    : {gecersiz} (hicbir kimlik kolonuna yazilmadi, D-246)")
    sonuc = {
        "dosya": str(dosya),
        "okunan": len(kayitlar),
        "yazilabilir": len(satirlar),
        "kuru": dry_run,
    }
    sonuc.update(olcum)
    return sonuc


if __name__ == "__main__":
    import sys

    ingest_aso_data(dry_run="--kuru" in sys.argv)
