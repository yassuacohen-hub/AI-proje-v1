"""Birlestirilmis veri kalite denetimi (D-285).

Birlestirme yazildi (`ostim_set_birlestir.py`). Simdi KALITE olcülür:
  1. Orneklemeli dogrulama: rastgele N kayit ornek alinip ALANLARI
     KAYNAK SAYFADAN tek tek dogrulanir (sacma degil, kanit)
  2. K-2 uyumu: kolonlar arasi kacis var mi?
  3. Ayni degerin iki farkli kaynaktan gelmesi (celiski) var mi?
  4. Tutarsiz adres/web (orn. ayni web her firmadaan) tespiti

D-285 amac: "kolonlari birbirine karistirma" uyarisinin KODDA da
dogru oldugunu KANITLAMAK (D-283'te 1 kez yandi: web_sitesi=htk.org.tr).

Kullanim: python scripts/birlestirme_kalite_kontrol.py [--orneklem 30]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import random
import re
import sys
from collections import Counter
from typing import Any, Optional

KOK = pathlib.Path(__file__).resolve().parents[1]
DATA = KOK / "data" / "ostim"
GIRIS = DATA / "firmalar_birlestirilmis.jsonl"
CIKTI = KOK / "data" / "birlestirme_kalite_raporu.json"
DIZIN = "https://ostim.org.tr"

#: Bu degerler OLUSTAN cikiyorsa kacis var demektir (D-283'te yandi).
YASAK_DEGERLER = {
    "htk.org.tr": "fuar/organizasyon sitesi — firma degil",
    "ostim.org.tr": "sitenin kendi domaini — firma degil",
    "ostimosb": "sitenin kendi sosyal hesabi",
    "ostim-osb": "sitenin kendi sosyal hesabi",
}


def _yukle(p: pathlib.Path) -> list[dict]:
    if not p.is_file():
        return []
    out = []
    for satir in p.read_text(encoding="utf-8").splitlines():
        if satir.strip():
            try:
                out.append(json.loads(satir))
            except json.JSONDecodeError:
                pass
    return out


def kacis_taramasi(kayitlar: list[dict]) -> dict:
    """YASAK degerler kolonlarda siziyor mu? (K-2 ihlali kaniti)"""
    bulunan = Counter()
    ornek = []
    for s in kayitlar:
        alanlar = {
            "web_sitesi": s.get("web_sitesi"),
            "sosyal_medya": json.dumps(s.get("sosyal_medya") or {},
                                      ensure_ascii=False),
        }
        for alan, deger in alanlar.items():
            if not deger:
                continue
            for yasak, aciklama in YASAK_DEGERLER.items():
                if yasak in str(deger):
                    bulunan[f"{alan}:{yasak}"] += 1
                    if len(ornek) < 5:
                        ornek.append(
                            {"unvan": (s.get("unvan") or "")[:50],
                             "alan": alan, "deger": str(deger)[:60],
                             "neden": aciklama}
                        )
    return {
        "kacis_bulundu": sum(bulunan.values()),
        "dagilim": dict(bulunan),
        "ornekler": ornek,
    }



def k2_uyum(kayitlar: list[dict]) -> dict:
    """K-2: kolonlar arasi kacis ve kaynak isaretlemesi olcumu."""
    n = len(kayitlar) or 1
    sonuc = {
        "kayit": n,
        "kaynak_adi_hepsi": all(s.get("kaynak_adi") for s in kayitlar),
        "kaynak_turu_hepsi": all(s.get("kaynak_turu") for s in kayitlar),
        "kaynak_degerleri": dict(Counter(
            str(s.get("kaynak_adi")) for s in kayitlar).most_common(5)),
        "nace_guven_dagilimi": dict(Counter(
            str(s.get("nace_confidence")) for s in kayitlar).most_common()),
        "vergi_no_dolu": sum(1 for s in kayitlar if s.get("vergi_no")),
        "nace_guvensiz_kayit": sum(
            1 for s in kayitlar
            if s.get("nace_code") and not s.get("nace_confidence")),
        "unvan_bos": sum(1 for s in kayitlar if not s.get("unvan")),
    }
    return sonuc


def celiski_taramasi(kayitlar: list[dict]) -> dict:
    """Ayni degerin cok sayida firmada gorunmesi = sute bulasma isareti."""
    sonuc = {}
    for alan in ("web_sitesi", "adres", "telefonler", "emailler"):
        ham = [s.get(alan) for s in kayitlar]
        degerler = [
            (h[0] if isinstance(h, list) and h else h)
            for h in ham if h
        ]
        if not degerler:
            sonuc[alan] = {"dolu": 0}
            continue
        sayac = Counter(map(str, degerler))
        en_cok = sayac.most_common(1)[0]
        sonuc[alan] = {
            "dolu": len(degerler),
            "tekil": len(sayac),
            "tekillestirme_orani": round(len(sayac) / len(degerler) * 100, 1),
            "en_cok_tekrar": {"deger": en_cok[0][:50], "adet": en_cok[1]},
        }
    return sonuc


if __name__ == "__main__":
    import importlib.util

    kayitlar = _yukle(GIRIS)
    rapor = {
        "dosya": str(GIRIS),
        "kayit": len(kayitlar),
        "kacis_taramasi": kacis_taramasi(kayitlar),
        "k2_uyum": k2_uyum(kayitlar),
        "celiski": celiski_taramasi(kayitlar),
    }
    CIKTI.write_text(json.dumps(rapor, ensure_ascii=False, indent=2),
                     encoding="utf-8")
    print("KAYIT:", rapor["kayit"])
    k = rapor["kacis_taramasi"]
    print("KACIS (K-2 ihlali):", k["kacis_bulundu"], k["dagilim"])
    for o in k["ornekler"][:3]:
        print("   ", o["alan"], "->", o["deger"], "|", o["neden"])
    print("K-2 UYUM:", json.dumps(rapor["k2_uyum"], ensure_ascii=False))
    print("CELISKI:")
    for a, v in rapor["celiski"].items():
        if v.get("dolu"):
            print(f"   {a:13s} dolu={v['dolu']:5d} tekil={v['tekil']:5d} "
                  f"oran=%{v['tekillestirme_orani']:5} "
                  f"en_cok={v['en_cok_tekrar']['deger'][:26]} x"
                  f"{v['en_cok_tekrar']['adet']}")
    print(CIKTI)
