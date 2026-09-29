"""D-305: Her OSB icin AYRI TEMIZ VERI SETI uretir.

KAHIN (2026-09-29): "osb'ler icin ayri ayri tek bir veri seti istiyorum,
senden ayri ayri veri setleri istiyorum osb'leri icin, sonra hepsi
birles-tirilecek."

DUZEN (supabase uyumu):
  - Her OSB icin AYRI klasor: data/osb/<slug>/firmalar.jsonl
  - Ortak alan adlari supabase `companies` tablosunun kavramsal
    alanlariyla ayni (legal_name, adres, phones, emails ...).
  - Kaynak dosyalara DOKUNULMAZ; yalniz okunur, yeni dosya yazilir.
  - Hicbir kayit SILINMEZ. Birles-tirme AYRI adimdir (KAHIN onayi).

DIKKAT - kaynak kod ASCII harflerle yazilmistir. Turkce OSB adlari
asagidaki Unicode kaci sabitleriyle tutulur; editor/terminal kodlamasi
metni bozdugu icin kaynak kodda dogrudan Turkce harf bulundurulmaz.
D-300'de ayni tuzak yazim hatasi nedeniyle bir testi sessizce gecersiz
kilmustu.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
from collections import Counter
from datetime import datetime

KOK = pathlib.Path(__file__).resolve().parents[1]
CIKTI = KOK / "data" / "osb"

#: Turkce harfler (Unicode kacisi) - tek kaynak
I_DOT = "\u0131"
S_CEDIL = "\u015f"
S_UML = "\u015e"
G_BREVE = "\u011f"
U_UML = "\u00fc"
U_UML_U = "\u00dc"
O_DIA = "\u00f6"
O_UML = "\u00d6"
C_CEDIL = "\u00e7"
I_UML = "\u0130"

#: slug -> tanim
OSB_TANIM: dict[str, dict] = {
    "ostim": {
        "ad": "Ostim OSB", "ilce": "Yenimahalle", "tur": "Karma",
        "kaynaklar": ["data/ostim/OSTIM_TEMIZ.jsonl"],
        "anahtar": ["ostim"], "uyari": None,
    },
    "ivedik": {
        "ad": I_UML + "vedik OSB", "ilce": "Yenimahalle", "tur": "Karma",
        "kaynaklar": ["data/ivedik/firmalar.jsonl"],
        "anahtar": ["ivedik"],
        "uyari": ("KAYNAK LISTESINDEN DUSURULDU (D-301): 14 tekil firma, "
                  "alan dolulugu %0. KULLANILAMAZ."),
    },
    "baskent": {
        "ad": "Ba" + S_CEDIL + "kent OSB",
        "ilce": "Sincan (Mal" + I_DOT + "k" + O_UML + "y)", "tur": "Karma",
        "kaynaklar": ["data/baskent/firmalar.jsonl"],
        "anahtar": ["baskent"], "uyari": None,
    },
    "aso": {
        "ad": "Ankara Sanayi Odas" + I_DOT + " 1. OSB",
        "ilce": "Sincan (T" + O_UML + "rekent)", "tur": "Karma",
        "kaynaklar": ["data/aso/aso_full_clean.jsonl"],
        "anahtar": ["aso"], "uyari": None,
    },
    "anadolu": {
        "ad": "Anadolu OSB",
        "ilce": "Sincan (Mal" + I_DOT + "k" + O_UML + "y)", "tur": "Karma",
        "kaynaklar": ["data/aso/aso_full_clean.jsonl",
                      "data/ostim/OSTIM_TEMIZ.jsonl"],
        "anahtar": ["anadolu"], "uyari": None,
    },
    "polatli": {
        "ad": "Polatl" + I_DOT + " OSB", "ilce": "Polatl" + I_DOT,
        "tur": "Karma",
        "kaynaklar": ["data/aso/aso_full_clean.jsonl",
                      "data/merged/multi_osb_merged.jsonl"],
        "anahtar": ["polatli"], "uyari": None,
    },
    "sereflikochisar": {
        "ad": S_UML + "erefliko" + C_CEDIL + "hisar OSB",
        "ilce": S_UML + "erefliko" + C_CEDIL + "hisar", "tur": "Karma",
        "kaynaklar": ["data/aso/aso_full_clean.jsonl",
                      "data/merged/multi_osb_merged.jsonl"],
        "anahtar": ["sereflikochisar"], "uyari": None,
    },
    "kazan_hab": {
        "ad": ("Ankara Uzay ve Havac" + I_DOT + "l" + I_DOT + "k "
               + I_UML + "htisas OSB (HAB)"),
        "ilce": "Kahramankazan", "tur": I_UML + "htisas",
        "kaynaklar": ["data/aso/aso_full_clean.jsonl",
                      "data/ostim/OSTIM_TEMIZ.jsonl"],
        "anahtar": ["habosb", "kazan"], "uyari": None,
    },
    "dokumcu": {
        "ad": ("Ankara D" + O_UML + "k" + U_UML + "mc" + U_UML + "ler "
               + I_UML + "htisas OSB"),
        "ilce": "Sincan (Alc" + I_DOT + ")", "tur": I_UML + "htisas",
        "kaynaklar": ["data/aso/aso_full_clean.jsonl",
                      "data/merged/multi_osb_merged.jsonl"],
        "anahtar": ["dokumcu"], "uyari": None,
    },
    "elmadag": {
        "ad": ("Elmada" + G_BREVE + " Mobilyac" + I_DOT + "lar "
               + I_UML + "htisas OSB"),
        "ilce": "Elmada" + G_BREVE, "tur": I_UML + "htisas",
        "kaynaklar": ["data/aso/aso_full_clean.jsonl",
                      "data/ostim/OSTIM_TEMIZ.jsonl"],
        "anahtar": ["elmadag"], "uyari": None,
    },
    "cubuk": {
        "ad": "Ankara-" + C_CEDIL + "ubuk TD" + I_UML + " (Besi) OSB",
        "ilce": C_CEDIL + "ubuk", "tur": I_UML + "htisas",
        "kaynaklar": ["data/aso/aso_full_clean.jsonl",
                      "data/merged/multi_osb_merged.jsonl"],
        "anahtar": ["cubuk"], "uyari": None,
    },
    "aso2": {
        "ad": "ASO 2. ve 3. OSB", "ilce": "Sincan (Alc" + I_DOT + ")",
        "tur": "Karma",
        "kaynaklar": ["data/aso/aso_full_clean.jsonl",
                      "data/merged/multi_osb_merged.jsonl"],
        "anahtar": ["aso2osb"],
        "uyari": "Kaynakta net '2. OSB' ayrimi yok; dogrulanmali.",
    },
    "polatli_ticaret": {
        "ad": "Polatl" + I_DOT + " Ticaret Odas" + I_DOT + " OSB",
        "ilce": "Polatl" + I_DOT, "tur": "Karma",
        "kaynaklar": [], "anahtar": ["ptoosb"],
        "uyari": "KAYNAK YOK - CSV'de web sitesi var, taranmali.",
    },
}

#: OSTIM semasi -> ortak sema (supabase `companies` kavramsal alanlari)
ALAN_ADI = {
    "unvan": "legal_name",
    "unvan_anahtari": "name_key",
    "adres": "adres",
    "telefonler": "phones",
    "emailler": "emails",
    "web_sitesi": "website_domain",
    "sektor": "sektor",
    "vergi_no": "tax_number",
    "nace_kod": "nace_code",
    "nace_detay": "nace_detail",
    "osb_parsel": "parsel",
    "slug": "company_slug",
    "kaynak_adi": "source_name",
    "kaynak_turu": "source_type",
    "kaynaklar": "sources",
    "yetkililer": "officials",
    "sosyal_medya": "social_media",
    "osb": "osb_slug",
}


def norm(s) -> str:
    """Turkce harfleri ASCII'ye indirger, kucultur, sadelestirir."""
    if not s:
        return ""
    t = str(s).lower()
    for a, b in ((I_DOT, "i"), (S_CEDIL, "s"), (S_UML, "s"),
                 (G_BREVE, "g"), (U_UML, "u"), (U_UML_U, "u"),
                 (O_DIA, "o"), (O_UML, "o"), (C_CEDIL, "c"),
                 (I_UML, "i")):
        t = t.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "", t)


def _oku(yol: pathlib.Path):
    for satir in yol.read_text(encoding="utf-8").splitlines():
        if satir.strip():
            try:
                yield json.loads(satir)
            except json.JSONDecodeError:
                continue


def donustur(kayit: dict, osb_slug: str, kaynak_dosya: str) -> dict:
    """OSTIM semasi -> ortak sema. Kaynak alanlari KORUNUR."""
    out: dict = {}
    for eski, yeni in ALAN_ADI.items():
        if eski in kayit:
            out[yeni] = kayit[eski]
    out["osb_slug"] = osb_slug
    out["source_file"] = kaynak_dosya
    out.setdefault("status", "active")
    out.setdefault("is_ankara", 1)
    out.setdefault("is_osb_member", 1)
    return out


def osb_iceren(kayit: dict, anahtarlar: list[str]) -> bool:
    """Kayit bu OSB'ye ait mi? YALNICA kaynak alanlarindan eslesir."""
    parcalar = [str(kayit.get(k, "")) for k in
                ("osb", "osb_slug", "kaynak_adi", "kaynaklar",
                 "adres", "unvan", "legal_name", "source_name")]
    n = norm(" ".join(parcalar))
    return any(norm(a) and norm(a) in n for a in anahtarlar)


def uret(slug: str, kontrol: bool) -> dict:
    t = OSB_TANIM[slug]
    kayitlar: list[dict] = []
    gorulen: set = set()
    for yol in t["kaynaklar"]:
        p = KOK / yol
        if not p.is_file():
            continue
        for k in _oku(p):
            if not osb_iceren(k, t["anahtar"]):
                continue
            d = donustur(k, slug, p.name)
            anahtar = d.get("company_slug") or d.get("legal_name")
            if anahtar and anahtar in gorulen:
                continue          # ayni OSB icinde ikinci kez geldi
            if anahtar:
                gorulen.add(anahtar)
            kayitlar.append(d)

    doluluk: Counter = Counter()
    for d in kayitlar:
        for alan in ("legal_name", "adres", "phones", "emails",
                     "website_domain", "tax_number", "nace_code"):
            if d.get(alan) not in (None, "", [], {}):
                doluluk[alan] += 1

    sonuc = {
        "osb_slug": slug, "ad": t["ad"], "ilce": t["ilce"], "tur": t["tur"],
        "kaynak_dosyalar": t["kaynaklar"], "kayit": len(kayitlar),
        "doluluk_yuzde": {a: (doluluk[a] * 100 // len(kayitlar)
                             if kayitlar else 0) for a in doluluk},
        "uyari": t["uyari"],
        "zaman": datetime.now().isoformat(timespec="seconds"),
    }
    if kontrol or not kayitlar:
        return sonuc

    hedef = CIKTI / slug
    hedef.mkdir(parents=True, exist_ok=True)
    gecici = hedef / "firmalar.jsonl.tmp"
    with gecici.open("w", encoding="utf-8") as f:
        for d in kayitlar:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    gecici.replace(hedef / "firmalar.jsonl")     # atomik (K-3)
    (hedef / "meta.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")
    sonuc["yazildi"] = str((hedef / "firmalar.jsonl").relative_to(KOK))
    return sonuc


def main() -> int:
    ay = argparse.ArgumentParser()
    ay.add_argument("--osb", default=None)
    ay.add_argument("--kontrol", action="store_true")
    ns = ay.parse_args()

    print("=" * 74)
    print("OSB BAZINDA AYRI TEMIZ VERI SETI (D-305)")
    print("=" * 74)
    sluglar = [ns.osb] if ns.osb else list(OSB_TANIM)
    toplam = 0
    rapor = []
    for slug in sluglar:
        if slug not in OSB_TANIM:
            print(f"  bilinmeyen slug: {slug}")
            return 1
        r = uret(slug, ns.kontrol)
        toplam += r["kayit"]
        rapor.append(r)
        durum = "YAZILDI" if r.get("yazildi") else (
            "KONTROL" if ns.kontrol else "KAYIT YOK")
        dol = " ".join(f"{a}:{v}" for a, v in
                       list(r["doluluk_yuzde"].items())[:4])
        print(f"\n  [{durum:8s}] {slug:18s} {r['kayit']:6d} kayit")
        print(f"              {r['ad']} ({r['ilce']}, {r['tur']})")
        if dol:
            print(f"              doluluk %: {dol}")
        if r["uyari"]:
            print(f"              UYARI: {r['uyari']}")

    print("\n" + "=" * 74)
    print(f"TOPLAM: {toplam} kayit / {len(sluglar)} OSB")
    print(f"Cikti: {CIKTI}")
    print("NOT: Birles-tirme AYRI adimdir - bu script birlestirmez.")
    print("=" * 74)
    (KOK / "data" / "_tmp").mkdir(parents=True, exist_ok=True)
    (KOK / "data" / "_tmp" / "osb_veri_seti_raporu.json").write_text(
        json.dumps(rapor, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
