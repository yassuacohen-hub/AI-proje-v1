"""VERI-TOBB2B-KESISIM-01 — TOBB2B teklifleri x kendi verimizin KESISIMI.

KAHIN 2026-09-29: "analizi genislet, tekrar bak daha iyi dusun,
VERI-TOBB2B-KESISIM-01 gorevi yasuya verilecek"

NEDEN VAR: Elimizdeki 8.987 kaydin NACE kodu sadece 12'sinde dolu
(%0.1) -> eslestirme NACE uzerinden KURULAMAZ; sektor METNI
uzerinden kurulur. Bu pilot OLAYI OLCER: kac teklif gelirse
kaci bizim verimizle eslesir?

POLITIKA: yalniz 20 teklif (VERI-TOBB2B-KESISIM-01). Toplu tarama YOK.
"""
from __future__ import annotations

import json
import pathlib
import re
import time

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
KOK = pathlib.Path(__file__).resolve().parents[1]
KOK_URL = "http://www.tobb2b.org.tr/"
PILOT = 20

#: NACE BOLUM kodu -> kendi sektor anahtarimiz. Bu, metin eslestirmesinden
#: GUVENLIDIR: "10" = gida; metin eslestirmesi "balikcilik" gibi
#: alakasiz sonuclari da yakaliyordu.
NACE_BOLUM_ESLESTIR = {
    "10": "gida", "11": "gida", "12": "gida", "13": "tekstil",
    "14": "tekstil", "15": "deri", "16": "tekstil", "17": "gida",
    "18": "tekstil", "19": "insaat",
    "20": "kimya", "21": "kimya", "22": "kimya", "23": "mineral",
    "24": "metal", "25": "metal", "26": "mineral",
    "27": "elektronik", "28": "makine", "29": "makine",
    "30": "makine", "31": "mobilya", "32": "makine", "33": "makine",
    "35": "enerji", "36": "insaat", "38": "cevre",
    "41": "insaat", "42": "insaat", "43": "insaat",
    "45": "ticaret", "46": "ticaret", "47": "ticaret",
    "49": "lojistik", "50": "lojistik", "51": "lojistik",
    "52": "depolama", "53": "lojistik",
    "55": "konaklama", "56": "gida", "61": "telekom",
    "62": "yazilim", "63": "veri", "70": "insaat",
    "71": "mimarlik", "72": "arastirma",
}

#: Kendi sektor metinlerimiz -> anahtar (yedek eslestirme)
SEKTOR_ESLESTIR = {
    "metal": ["metal", "metalurji", "demir", "celik"],
    "makine": ["makina", "makine", "makineci"],
    "mobilya": ["mobilya", "mobilya imalati"],
    "kimya": ["kimya", "kimyasal", "plastik", "lastik"],
    "gida": ["gida", "un ", "yem", "gida isletmesi"],
    "savunma": ["savunma", "silah"],
    "medikal": ["medikal", "saglik", "ilac", "tibbi"],
    "tekstil": ["tekstil", "kiyafet", "dokuma"],
    "elektronik": ["elektronik", "elektrikli", "elektro"],
    "insaat": ["insaat", "bina", "gayrimenkul", "yapi", "infaat"],
    "depolama": ["depolama", "lojistik", "nakliye"],
    "lojistik": ["lojistik", "nakliye", "depolama"],
    "deri": ["deri", "ayakkabi"],
}


def duz(html: str) -> str:
    t = re.sub(r"<script.*?</script>", " ", html, flags=re.S | re.I)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    # ONCE Turkce entity'ler, SONRA ASCII
    for a, b in (("&nbsp;", " "), ("&amp;", "&"), ("&#220;", "U"),
                 ("&#199;", "C"), ("&#246;", "o"), ("&#252;", "u"),
                 ("&#305;", "i"), ("&#351;", "s"), ("&#287;", "g")):
        t = t.replace(a, b)
    t = (t.replace("\u00dc", "U").replace("\u00c7", "C")
          .replace("\u00d6", "O").replace("\u00d1", "N")
          .replace("\u00dc", "U").replace("\u00e7", "C")
          .replace("\u00f6", "o").replace("\u00fc", "u")
          .replace("\u0131", "i").replace("\u015f", "s")
          .replace("\u011f", "g"))
    return re.sub(r"\s+", " ", t).strip()


def teklif_ayikla(m: str) -> dict:
    d = {}
    x = re.search(r"Teklif No\s*(\d+)", m)
    d["teklif_no"] = x.group(1) if x else ""
    x = re.search(r"Teklif Tarihi\s*([\d.]+)", m)
    d["tarih"] = x.group(1) if x else ""
    # 'Ulke TR' — Turkce U ve ASCII olabilir
    x = re.search(r"[U\u00dc]lke\s+([A-Z]{2})", m)
    d["ulke"] = x.group(1) if x else ""
    # NACE: 'NN - aciklama' tekrar ediyor. 'GTIP KODLARI' kirliligi var.
    nace = []
    for nk, ac in re.findall(
            r"\b(\d{2})\s*-\s*([^\n]{0,70}?)(?=\s+\d{2}\s*-|$)", m):
        ac = re.sub(r"GT\u0130P KODLARI", "", ac, flags=re.I).strip()
        if ac:
            nace.append([nk, ac])
    d["nace"] = nace[:8]
    d["ortak_arayan"] = bool(re.search(
        r"(seeking|looking for|arayan|searching for|distributors?|"
        r"importers?)", m, re.I))
    d["aciklama"] = m[:600]
    return d


def kendi_sektorler() -> dict:
    sonuc: dict = {}
    K = KOK / "data" / "osb"
    for d in sorted(K.iterdir()):
        f = d / "firmalar.jsonl"
        if not f.is_file():
            continue
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            s = json.loads(line)
            sek = (s.get("sektor") or "").strip().lower()
            if sek:
                sonuc.setdefault(sek, []).append(
                    (d.name, (s.get("unvan") or s.get("legal_name") or "")[:60]))
    return sonuc



def main() -> None:
    import httpx
    print("=" * 70)
    print(f"PILOT-{PILOT} — TOBB2B teklifleri x kendi verimiz")
    print("=" * 70)

    print("\n[1] Kendi sektor envanteri")
    kendi = kendi_sektorler()
    print(f"    farkli sektor metni : {len(kendi)}")
    print(f"    toplam kayit       : "
          f"{sum(len(v) for v in kendi.values())}")

    print(f"\n[2] TOBB2B'den {PILOT} teklif")
    teklifler = []
    with httpx.Client(headers={"User-Agent": UA}, timeout=25,
                      follow_redirects=True) as c:
        i = 21000
        denenen = 0
        while len(teklifler) < PILOT and denenen < 120:
            denenen += 1
            try:
                r = c.get(KOK_URL + f"teklif_goster.php?Id={i}",
                          timeout=15)
                m = duz(r.text)
                if "Teklif No" not in m:
                    i += 1
                    continue
                t = teklif_ayikla(m)
                t["id"] = i
                teklifler.append(t)
                print(f"    [{len(teklifler):2d}/{PILOT}] Id={i} | "
                      f"{t['teklif_no']:>10s} | {t['ulke']:>3s} | "
                      f"NACE {len(t['nace'])} | "
                      f"ortak={t['ortak_arayan']}")
                i += 1
                time.sleep(1.0)
            except Exception as e:
                print(f"    hata {type(e).__name__}")
                i += 1
    print(f"    toplam: {len(teklifler)} ({denenen} Id denendi)")

    print("\n[3] KESISIM (NACE bolum kodu ile - guvenli)")
    eslesme = []
    for t in teklifler:
        bulunan = set()
        for nk, _ac in t["nace"]:
            a = NACE_BOLUM_ESLESTIR.get(nk)
            if a:
                bulunan.add(a)
        # YEDEK: metin eslestirmesi yalniz NACE kodu bulunamadiginda
        ek = set()
        if not bulunan:
            for _nk, aciklama in t["nace"]:
                a = aciklama.lower()
                for anahtar, kws in SEKTOR_ESLESTIR.items():
                    if any(k in a for k in kws):
                        ek.add(anahtar)
            bulunan = ek
        for anahtar in bulunan:
            for sek, firmalar in kendi.items():
                if any(k in sek for k in SEKTOR_ESLESTIR.get(anahtar,
                                                              [anahtar])):
                    if not firmalar:
                        continue
                    eslesme.append({
                        "teklif_id": t["id"],
                        "teklif_no": t["teklif_no"],
                        "ulke": t["ulke"],
                        "ortak_arayan": t["ortak_arayan"],
                        "nace_bolum": anahtar,
                        "bizim_sektor": sek,
                        "bizim_osb": sorted({f[0] for f in firmalar}),
                        "bizim_firma_sayisi": len(firmalar),
                        "ornek_firma": firmalar[0][1],
                    })
    eslesen = ({t["id"] for t in teklifler}
               - {x["teklif_id"] for x in eslesme})
    ozet = []
    for t in teklifler:
        e = [x for x in eslesme if x["teklif_id"] == t["id"]]
        ozet.append({
            "id": t["id"], "no": t["teklif_no"], "ulke": t["ulke"],
            "nace": [n[0] for n in t["nace"]],
            "ortak_arayan": t["ortak_arayan"],
            "bizim_firma": sum(x["bizim_firma_sayisi"] for x in e),
            "sektorler": sorted({x["bizim_sektor"] for x in e}),
        })
    print(f"    teklif         : {len(teklifler)}")
    print(f"    ESLESEN teklif : {len(eslesen)}")
    print(f"    eslesme satiri: {len(eslesme)}")
    print(f"    toplam firma  : "
          f"{sum(x['bizim_firma_sayisi'] for x in eslesme)}")
    for o in ozet[:12]:
        print(f"      Id={o['id']} {o['no']:>10s} {o['ulke']:>3s} "
              f"NACE={','.join(o['nace'][:2]):<5s} "
              f"firma={o['bizim_firma']:4d} {str(o['sektorler'])[:28]}")

    cikti = KOK / "data" / "pilots" / "VERI-TOBB2B-KESISIM-01"
    cikti.mkdir(parents=True, exist_ok=True)
    (cikti / "teklifler.json").write_text(json.dumps(
        teklifler, ensure_ascii=False, indent=2), encoding="utf-8")
    (cikti / "kesisim.json").write_text(json.dumps(
        eslesme, ensure_ascii=False, indent=2), encoding="utf-8")
    (cikti / "ozet.json").write_text(json.dumps({
        "teklif": len(teklifler), "eslesen_teklif": len(eslesen),
        "eslesme": len(eslesme),
        "firma": sum(x["bizim_firma_sayisi"] for x in eslesme),
        "teklif_ozet": ozet,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\ncikti: {cikti}")


if __name__ == "__main__":
    main()
