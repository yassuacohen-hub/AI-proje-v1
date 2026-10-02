# -*- coding: utf-8 -*-
"""VERI-TOBB2B-BUYUTME-01 — TOBB2B pilotunu genis Id araligina buyut (D-319).

NEDEN VAR: Pilot (VERI-TOBB2B-KESISIM-01) Id **21000-21049** araligini taradi,
20 teklif buldu (%40 doluluk), 11/20'si kendi OSB verimizle eslesti -> 1.575 firma.
KAHIN onayi (D-319): tobb2b.org.tr **ucretsiz**, duz `http://` erisim onaylandi ->
"pilot büyütme" gorevi acildi.

POLITIKA (R1 onlemi, buyutulmus olcekte de gecerli):
  * Istekler arasi **rate-limit** zorunlu (ASAGIDA `ARALIK_SN`, gorunur).
  * Ust sinir 150 Id — brif "ornek 500" dese de once olcum yapilir (D-238);
    buyutme karari olcumden SONRA ihsan'a gider (Faz C).
  * Pilot Id araligi **tekrar taranmaz** (brif varsayimi).

KÖPRÜ (D-184): temel pilot scripts/veri_tobb2b_kesisim.py ·
ozet data/pilots/VERI-TOBB2B-KESISIM-01/ozet.json ·
gorev plans/brief_yasu_VERI-TOBB2B-BUYUTME-01.md ·
hub hubs/OSINT_VERI_TOPLAMA_HUB.md
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
KOK = pathlib.Path(__file__).resolve().parents[1]
KOK_URL = "http://www.tobb2b.org.tr/"

#: Pilotun taradigi aralik — BURAYA DOKUNMA (brif: ayni Id'leri tekrar cekme).
PILOT_BAS = 21000
PILOT_BIT = 21049

#: Yeni aralik: pilotun ust sinirindan devam. 100 Id = kabul kriteri (>=100 yeni Id).
ID_BAS = 21050
ID_BIT = 21149

#: RATE-LIMIT: istekler arasi bekleme (sn). Brif kabul kriteri bunu kodda gormek ister.
ARALIK_SN = 1.0

#: NACE BOLUM -> kendi sektor anahtarimiz. Pilotun sozlugu (D-307) AYNI:
# bolum kodu kullanmak metin eslestirmesinden guvenlidir.
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

#: Kendi sektor metinlerimiz -> anahtar (yedek eslestirme, pilotla ayni)
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
}


def duz(html: str) -> str:
    """HTML bosluklarini sadelestirir (pilotla ayni)."""
    html = re.sub(r"<[^>]+>", " ", html)
    html = html.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", html)


def teklif_ayikla(m: str) -> dict:
    """Teklif sayfasindan alanlari ayiklar (pilotla ayni yontem)."""
    d: dict = {}
    x = re.search(r"Teklif No\s*(\d+)", m)
    d["teklif_no"] = x.group(1) if x else ""
    x = re.search(r"Teklif Tarihi\s*([\d.]+)", m)
    d["tarih"] = x.group(1) if x else ""
    x = re.search(r"[UÜ]lke\s+([A-Z]{2})", m)
    d["ulke"] = x.group(1) if x else ""
    nace = []
    for nk, ac in re.findall(
            r"\b(\d{2})\s*-\s*([^\n]{0,70}?)(?=\s+\d{2}\s*-|$)", m):
        ac = re.sub(r"GTİP KODLARI", "", ac, flags=re.I).strip()
        if ac:
            nace.append([nk, ac])
    d["nace"] = nace[:8]
    d["ortak_arayan"] = bool(re.search(
        r"(seeking|looking for|arayan|searching for|distributors?|importers?)",
        m, re.I))
    d["aciklama"] = m[:600]
    return d


def kendi_sektorler() -> dict:
    """Kendi OSB verimizdeki sektor metni -> [(klasor, unvan)] (pilotla ayni)."""
    sonuc: dict = {}
    for d in sorted((KOK / "data" / "osb").iterdir()):
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


def eslestir(teklif: dict, kendi: dict) -> tuple[int, list[str]]:
    """Teklifi kendi verimize baglar. Once NACE bolum kodu, yoksa sektor METNI.

    Doner: (eslesen_firma_sayisi, kullanilan_sektor_anahtarlari)
    """
    bolumler = {nk for nk, _ in teklif.get("nace", [])}
    anahtarlar = {NACE_BOLUM_ESLESTIR[b] for b in bolumler if b in NACE_BOLUM_ESLESTIR}
    # NACE bolum kodu tutmazsa metin eslestirmesi (pilotla ayni yedek yol)
    if not anahtarlar:
        aciklama = (teklif.get("aciklama") or "").lower()
        for anahtar, kelimeler in SEKTOR_ESLESTIR.items():
            if any(k in aciklama for k in kelimeler):
                anahtarlar.add(anahtar)

    bulunan = 0
    for anahtar in sorted(anahtarlar):
        if anahtar not in SEKTOR_ESLESTIR:
            continue
        for kelime in SEKTOR_ESLESTIR[anahtar]:
            bulunan += sum(1 for sek, _ in kendi.items() if kelime in sek)
    return bulunan, sorted(anahtarlar)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kuru", action="store_true",
                    help="yalniz olc; teklifler.json YAZMA")
    ap.add_argument("--ust", type=int, default=ID_BIT,
                    help=f"ust Id (varsayilan {ID_BIT}); brif '500' diyor, once olc")
    ap.add_argument("--bas", type=int, default=ID_BAS,
                    help=f"bas Id (varsayilan {ID_BAS}); 100 Id'lik ilk olcum "
                         f"tamamlandi, 500 Id icin 21150'den devam")
    a = ap.parse_args()
    id_bas = a.bas

    # Arka planda calisirken cikti tamponlanir; log dosyasinda anlik gorunmesi icin
    # flush (D-86: terminalden okunmayan cikti = kanitsiz).
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except AttributeError:  # pragma: no cover
        pass

    print("=" * 70)
    print("VERI-TOBB2B-BUYUTME-01 — pilot buyutme (D-319)")
    print("=" * 70)
    assert id_bas > PILOT_BIT, "yeni aralik pilotun ustunde olmali (brif varsayimi)"
    print(f"pilot araligi : {PILOT_BAS}-{PILOT_BIT} (TEKRAR TARANMAZ)")
    print(f"yeni aralik    : {id_bas}-{a.ust} ({a.ust - id_bas + 1} Id)")
    print(f"rate-limit     : {ARALIK_SN} sn (R1 onlemi)")

    print("\n[1] Kendi sektor envanteri")
    kendi = kendi_sektorler()
    print(f"    farkli sektor metni : {len(kendi)}")
    print(f"    toplam kayit        : {sum(len(v) for v in kendi.values())}")

    print(f"\n[2] TOBB2B taramasi (rate-limit'li)")
    teklifler: list[dict] = []
    denenen = bos = hata = 0
    baslangic = time.time()
    for i in range(id_bas, a.ust + 1):
        denenen += 1
        url = KOK_URL + f"teklif_goster.php?Id={i}"
        istek = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(istek, timeout=20) as yanit:
                kod = yanit.getcode()
                ham = yanit.read().decode("utf-8", "replace")
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as exc:
            hata += 1
            # R8: IP engeli belirtileri bu 3 denemede engellenirse DUR
            print(f"    [R8] erisim hatasi Id={i}: {type(exc).__name__} — "
                  f"toplam {hata}; 3'e ulasirsa DUR")
            if hata >= 3:
                print("    [R8] DUR: IP engeli. Chat'e yaz, veri bozulmadı.")
                break
            time.sleep(ARALIK_SN)
            continue

        m = duz(ham)
        if "Teklif No" not in m:
            bos += 1
            time.sleep(ARALIK_SN)          # R1: bos Id de yuk yem
            continue
        t = teklif_ayikla(m)
        t["id"] = i
        t["http"] = kod
        teklifler.append(t)
        print(f"    [{len(teklifler):3d}] Id={i} | {t['teklif_no']:>10s} | "
              f"{t['ulke']:>3s} | NACE {len(t['nace'])} | "
              f"ortak={int(t['ortak_arayan'])}")
        time.sleep(ARALIK_SN)               # R1: istekler arasi bekleme

    sure = time.time() - baslangic
    print(f"\n[3] Tarama ozeti")
    print(f"    denenen Id    : {denenen}")
    print(f"    dolu teklif   : {len(teklifler)}")
    print(f"    bos Id        : {bos}")
    print(f"    hata          : {hata}")
    doluluk = (len(teklifler) * 100) // denenen if denenen else 0
    print(f"    DOLULUK       : %{doluluk}  (pilot %40)")

    print(f"\n[4] Eslestirme (NACE bolum kodu)")
    eslesen_teklif = 0
    toplam_firma = 0
    for t in teklifler:
        adet, anahtarlar = eslestir(t, kendi)
        t["bizim_firma"] = adet
        t["sektorler"] = anahtarlar
        if adet:
            eslesen_teklif += 1
            toplam_firma += adet
    print(f"    eslesen teklif : {eslesen_teklif}/{len(teklifler)}"
          + (f" (pilot 11/20)" if teklifler else ""))
    print(f"    bulunan firma : {toplam_firma} (pilot 1.575)")

    if a.kuru:
        print("\n[5] KURU: dosya yazilmadi")
        return 0

    # Cikti
    hedef = KOK / "data" / "pilots" / "VERI-TOBB2B-BUYUTME-01"
    hedef.mkdir(parents=True, exist_ok=True)
    (hedef / "teklifler.json").write_text(
        json.dumps(teklifler, ensure_ascii=False, indent=1), encoding="utf-8")
    ozet = {
        "teklif": len(teklifler),
        "eslesen_teklif": eslesen_teklif,
        "eslesme": eslesen_teklif,
        "firma": toplam_firma,
        "denenen_id": denenen,
        "bos_id": bos,
        "hata": hata,
        "doluluk_yuzde": doluluk,
        "sure_sn": round(sure, 1),
        "rate_limit_sn": ARALIK_SN,
        "id_araligi": [id_bas, a.ust],
        "pilot_id_araligi": [PILOT_BAS, PILOT_BIT],
        "pilot_karsilastirma": {"teklif": 20, "eslesen": 11, "firma": 1575,
                                "doluluk_yuzde": 40},
    }
    (hedef / "ozet.json").write_text(
        json.dumps(ozet, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n[5] YAZILDI: {hedef.relative_to(KOK).as_posix()}/"
          f"{{teklifler,ozet}}.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())

