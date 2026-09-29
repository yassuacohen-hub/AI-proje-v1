"""D-279: Abonelik kapsamini olcer.

KAHIN'in itirazi (2026-09-29):
  "1 aylik ucret odemekle firma bilgilerini tam toplanmaz; ucret sadece o
   ayin sirket bilgilerini gosterir, acilis kapanis vs; aradigimiz veri orada degil."

Dogrulanmasi gerekenler:
  1. Abonelik SURESI yillik mi aylik mi? (sayfada yazili)
  2. Kapsam: gecmis yillar kapsaniyor mu?
  3. Empirik: 448217 (AKANA) icin 4 ilanin yil dagilimi.
"""
import json
import pathlib
import re

KOK = pathlib.Path(__file__).resolve().parents[1]
HAM = KOK / "data" / "kesif_abonelik_ham.html"
KANIT = KOK / "data" / "kanit" / "448217_tobb_ilanlari.json"
CIKTI = KOK / "data" / "kesif_abonelik_kapsam.json"


def duz_metin(html: str) -> list[str]:
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S)
    t = re.sub(r"<[^>]+>", "\n", t)
    sat = [re.sub(r"\s+", " ", x).replace("&nbsp;", " ").strip() for x in t.split("\n")]
    return [x for x in sat if x]


def olc() -> dict:
    html = HAM.read_text(encoding="utf-8")
    sat = duz_metin(html)

    sure_kanit = [x for x in sat if "251" in x or "Yıllık" in x or "yıllık" in x]
    gunluk_kanit = [x for x in sat if "2.730" in x or "Günlük" in x]
    fihrist_kanit = [x for x in sat if "fihrist" in x.lower()]
    gecmis_kanit = [x for x in sat if re.search(r"20(1|2)\d", x) and "yıl" in x.lower()]

    kanit = json.loads(KANIT.read_text(encoding="utf-8"))
    yillar = [int(k["yayin_tarihi"][-4:]) for k in kanit["ilanlar"]]

    return {
        "abonelik_suresi_kaniti": sure_kanit[:6],
        "gunluk_gazete_kaniti": gunluk_kanit[:4],
        "fihrist_kaniti": fihrist_kanit[:4],
        "gecmis_yil_kaniti": gecmis_kanit[:4],
        "empirik_448217": {
            "ilan_sayisi": len(yillar),
            "yillar": sorted(yillar),
            "2026_adet": sum(1 for y in yillar if y == 2026),
            "2026_disi_adet": sum(1 for y in yillar if y != 2026),
            "yil_kapsam_yuzde": round(
                100 * sum(1 for y in yillar if y == 2026) / len(yillar)
            ),
        },
    }


if __name__ == "__main__":
    r = olc()
    CIKTI.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(r["empirik_448217"], ensure_ascii=False, indent=2))
    print("SURE:", len(r["abonelik_suresi_kaniti"]), "GUNLUK:", len(r["gunluk_gazete_kaniti"]))
    print(CIKTI)
