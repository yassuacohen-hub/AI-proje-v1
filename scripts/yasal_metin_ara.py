"""D-282: YASAL METIN ICERIGINI ARA (sart/KVKK/otomasyon yasagi).

D-281'de adresler tahmin edildi ve bulunamadi. Bu tur **icerik** arar:
her kaynagin tum menulerini gezip sart/KVKK/otomasyon metni olan sayfayi
bulur ve KRITIK cumleleri (ticari kullanim, kopyalama yasagi, izin) cikarir.

Kullanim: python scripts/yasal_metin_ara.py
"""
from __future__ import annotations

import json
import pathlib
import re

import httpx

KOK = pathlib.Path(__file__).resolve().parents[1]
CIKTI = KOK / "data" / "yasal_metin_sonuc.json"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")

KOKLER = {
    "OSTIM": "https://ostim.org.tr/",
    "ATO": "https://www.atonet.org.tr/",
    "ASO": "https://www.aso.org.tr/",
    "ATB": "https://www.atb.org.tr/",
}

#: Yasal metin sayfasi olabilecek linkler.
HEDEF = re.compile(
    r"(?:kullanim-sart|kullanım-şart|kosullar|koşullar|sartlar|şartlar"
    r"|kvkk|aydinlatma|aydınlatma|gizlilik|r[üu]h[üu]s[sz]|uyum"
    r"|cerez|uyum-politika|dis-politika|d[uü]s-politika)",
    re.I,
)

#: Kritik hukuki kavramlar — bulunmasi riski, bulunmaması serbestiyi gösterir.
KAVRAM = {
    "ticari_kullanim": r"ticari\s+(?:amaç|amac|kullanım|kullanim|olarak|faydalan)",
    "kopyalama_yasagi": r"(?:kopyalam|copy|çeviri|ceviri|yeniden\s+yayın|yayin)",
    "izin_gerekir": r"(?:önceden\s+izin|izni\s+(?:al|gerekir)|yazılı\s+izin)",
    "ucret": r"(?:ücret|ucret|bedel|ödeme|odeme)",
    "otomasyon_yasagi": r"(?:otomasyon|robot|scrap|kazıma|kazima|bots?)\b",
    "kvkk_6698": r"(?:6698|KVKK|kişisel\s+veri|kisisel\s+veri)",
    "sorumluluk": r"(?:sorumlu|sorumluluk|zarar|ceza)",
}


def duz(html: str) -> str:
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t)).strip()


def tara(kok: str) -> dict:
    o = {"kok": kok, "hedef": [], "bulunan_sayfalar": []}
    try:
        r0 = httpx.get(kok, timeout=30, headers={"User-Agent": UA},
                       follow_redirects=True)
        h0 = r0.text
        tum = re.findall(r'href="([^"#]+)"', h0, re.I)
        adaylar = set()
        for u in tum:
            if not HEDEF.search(u):
                continue
            adaylar.add(u if u.startswith("http") else kok.rstrip("/") + u)
        o["hedef"] = sorted(adaylar)[:20]
        for tam in sorted(adaylar)[:20]:
            try:
                r = httpx.get(tam, timeout=20, headers={"User-Agent": UA},
                              follow_redirects=True)
                t = duz(r.text)
                kav = {k: bool(re.search(p, t, re.I)) for k, p in KAVRAM.items()}
                if sum(kav.values()) >= 2:
                    # Kritik cumleleri cikar
                    cumleler = []
                    for k, p in KAVRAM.items():
                        for m in re.finditer(r"[^.]{0,120}" + p + r"[^.]{0,120}\.",
                                             t, re.I):
                            cumleler.append(m.group(0).strip()[:220])
                    o["bulunan_sayfalar"].append(
                        {
                            "url": tam,
                            "http": r.status_code,
                            "metin_uzunluk": len(t),
                            "kavramlar": kav,
                            "cumleler": cumleler[:8],
                        }
                    )
            except Exception:
                pass
    except Exception as e:
        o["hata"] = str(e)[:120]
    return o


if __name__ == "__main__":
    rapor = {}
    for ad, kok in KOKLER.items():
        r = tara(kok)
        rapor[ad] = r
        print("=" * 55)
        print(f"{ad}: {len(r['hedef'])} hedef, "
              f"{len(r['bulunan_sayfalar'])} yasal sayfa")
        for s in r["bulunan_sayfalar"][:3]:
            print("   ", s["url"][:90])
            print("      kavramlar:",
                  [k for k, v in s["kavramlar"].items() if v])
    CIKTI.write_text(json.dumps(rapor, ensure_ascii=False, indent=2),
                     encoding="utf-8")
    print(CIKTI)
