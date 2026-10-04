# -*- coding: utf-8 -*-
"""OSTIM `web_sitesi` alanindaki sayfa-sablonu sizintisini temizler (D-292).

Olcum (2026-10-03, `data/ostim/firmalar_detailed.jsonl`): `web_sitesi` dolu
1555 kaydin **tamami** iki portal adresine bakiyordu
(1415 x nsosyal.com/ostim_osb, 140 x ostimonline.com/Home/OstimMain).
Gercek firma sitesi sayisi **0**. OSTIM detay sayfalarinda firma web sitesi
bulunmuyor; yalnizca OSB portalinin kendi ayaklari var.

Neden ayri betik: `run_scraper()` slug'i `completed_slugs` icinde gördugu icin
bozuk satirlari ASLA yeniden cekmez. Filtre duzeltmesi tek basina yeterli
degildir; diskteki degerler de NULL'a cekilmelidir (D-267/6: yazan yol ile
yazan gecmisi ayni turda duzelt).

Kullanim:
    python -X utf8 scripts/ostim_websitesi_temizle.py            # prova (varsayilan, yazmaz)
    python -X utf8 scripts/ostim_websitesi_temizle.py --yaz      # yedek alip uygular

Idempotent: `--yaz` ikinci kez calistirilirsa 0 satir degisir, yeni yedek alinmaz.
"""
import argparse
import io
import json
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
VARSAYILAN = ROOT / "data" / "ostim" / "firmalar_detailed.jsonl"
YEDEK_DIZIN = ROOT / "yedekler"

# Canli sayfa taramasiyla olculmus portal/ajan adresleri (2026-10-03).
SIZINTI_DESEN = (
    "nsosyal.com", "ostimonline.com", "ostim.org.tr", "ostimradyo.com",
    "ostimkooperatifi.com", "ostimsavunma.org", "ostimvakfi.org",
    "ostimyatirim.com.tr", "ostimistihdam.com", "htk.org.tr",
    "isim.org.tr", "osp.com.tr", "odtuteknokent.com.tr",
    "kaucukteknolojileri.com", "ostimteknik.edu.tr",
)


def sizinti_mi(deger) -> bool:
    if not deger:
        return False
    low = str(deger).strip().lower()
    return any(d in low for d in SIZINTI_DESEN)


def tara(yol: Path) -> tuple[list[dict], int, int, int]:
    """(kayitlar, dolu, sizinti, bozuk_satir)"""
    kayitlar, bozuk = [], 0
    with io.open(yol, encoding="utf-8-sig", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                kayitlar.append(json.loads(line))
            except json.JSONDecodeError:
                bozuk += 1
    dolu = sum(1 for k in kayitlar if (k.get("web_sitesi") or "").strip())
    sizinti = sum(1 for k in kayitlar if sizinti_mi(k.get("web_sitesi")))
    return kayitlar, dolu, sizinti, bozuk


def uygula(yol: Path, yaz: bool) -> int:
    kayitlar, dolu, sizinti, bozuk = tara(yol)
    print(f"dosya            : {yol}")
    print(f"satir            : {len(kayitlar)}  (bozuk: {bozuk})")
    print(f"web_sitesi dolu  : {dolu}")
    print(f"SIZINTI (silinecek): {sizinti}")
    print(f"kalacak gercek   : {dolu - sizinti}")

    if not yaz:
        print("\n[PROVA] hicbir dosya degismedi. Uygulamak icin: --yaz")
        return 0
    if sizinti == 0:
        print("\n[TEMIZ] silinecek satir yok; dosyaya dokunulmadi.")
        return 0

    YEDEK_DIZIN.mkdir(parents=True, exist_ok=True)
    damga = datetime.now().strftime("%Y%m%d_%H%M%S")
    yedek = YEDEK_DIZIN / f"ostim_firmalar_detailed_{damga}.jsonl"
    yedek.write_bytes(yol.read_bytes())
    print(f"\n[YEDEK] {yedek}  ({len(kayitlar)} satir)")

    degisen = 0
    with io.open(yol, "w", encoding="utf-8", newline="\n") as out:
        for k in kayitlar:
            if sizinti_mi(k.get("web_sitesi")):
                k["web_sitesi"] = None
                degisen += 1
            out.write(json.dumps(k, ensure_ascii=False) + "\n")

    # D-244: yedek satiri silinen satir sayisiyla esit olmali, degilse dur.
    yedek_satir = sum(1 for _ in io.open(yedek, encoding="utf-8-sig") if _.strip())
    if yedek_satir != len(kayitlar):
        print(f"[HATA] yedek satir sayisi esit degil ({yedek_satir} != {len(kayitlar)})")
        return 2

    _, yeni_dolu, yeni_sizinti, _ = tara(yol)
    print(f"[YAZILDI] {degisen} satir web_sitesi -> NULL")
    print(f"[DOGRULAMA] dolu={yeni_dolu} sizinti={yeni_sizinti}")
    if yeni_sizinti != 0:
        print("[HATA] sizinti kalmadi, hedef tutulmadi.")
        return 2
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="OSTIM web_sitesi sizinti temizligi")
    ap.add_argument("--dosya", default=str(VARSAYILAN))
    ap.add_argument("--yaz", action="store_true", help="varsayilan: sadece prova")
    a = ap.parse_args()
    return uygula(Path(a.dosya), a.yaz)


if __name__ == "__main__":
    raise SystemExit(main())
