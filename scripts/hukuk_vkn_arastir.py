"""D-281 KAPSAM: (1) Hukuki uygunluk, (2) GIB VKN yolu — ikisini de olcer.

(1) OSTIM/ATO/ASO kullanim sartlari ve KVKK metinlerini BULUR ve ozetler.
    "Kullanim sartlari sayfasi var mi?" sorusu HTTP ile yanitlanir.
(2) GIB tarafinda halka acik VKN sorgu ucu var mi, e-Devlet zorunlu mu
    onu resmi sayfalardan dener.

Hicbir kaynak toplu INDIRILMEZ; sadece kosul metinleri okunur.

Kullanim: python scripts/hukuk_vkn_arastir.py
"""
from __future__ import annotations

import json
import pathlib
import re

import httpx

KOK = pathlib.Path(__file__).resolve().parents[1]
CIKTI = KOK / "data" / "hukuk_vkn_arastirma.json"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")

#: (etiket, url) — yasal metin adaylari.
HUKUK_URL = [
    ("OSTIM kullanim sartlari", "https://ostim.org.tr/kurumsal/portal-kullanim-sartlari"),
    ("OSTIM KVKK", "https://ostim.org.tr/kvkk-bilgilendirme-metni"),
    ("OSTIM gizlilik", "https://ostim.org.tr/gizlilik"),
    ("ATO kullanim sartlari", "https://www.atonet.org.tr/kullanim-sartlari"),
    ("ATO KVKK", "https://www.atonet.org.tr/kvkk"),
    ("ASO kullanim sartlari", "https://www.aso.org.tr/kullanim-sartlari"),
    ("ASO KVKK", "https://www.aso.org.tr/kvkk-aydinlatma-metni"),
    ("TicBakan KVKK", "https://ticaret.gov.tr/kvkk"),
]

#: (etiket, url) — GIB resmi VKN hizmetleri.
GIB_URL = [
    ("GIB VKN sorgulama", "https://www.gib.gov.tr/yardim-ve-kaynaklar/yararli-bilgiler/vergi-kimlik-numarasi-sorgulama"),
    ("GIB e-hizmetler", "https://www.gib.gov.tr/e-hizmetler"),
    ("GIB acik veri", "https://www.gib.gov.tr/acik-veri"),
    ("GIB VKN sorgu e-Devlet", "https://www.turkiye.gov.tr/gib-vergi-kimlik-numarasi-sorgulama"),
]


def duz(html: str) -> str:
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t)).strip()


def kontrol(etiket: str, url: str) -> dict:
    o = {"etiket": etiket, "url": url}
    try:
        r = httpx.get(url, timeout=25, headers={"User-Agent": UA},
                      follow_redirects=True)
        o["http"] = r.status_code
        o["bayt"] = len(r.content)
        o["erisim"] = r.status_code == 200
        if r.status_code == 200:
            m = duz(r.text)
            o["metin_uzunluk"] = len(m)
            # Kritik hukuki kavramlar var mi?
            o["anahtar_kavramlar"] = {
                k: bool(re.search(k, m, re.I))
                for k in (
                    r"ticari", r"kopyala", r"çeviri|ceviri", r"yeniden yayın|yayın",
                    r"izin", r"ücret|ucret", r"kişisel veri|kisisel veri",
                    r"KVKK", r"6698", r"otomasyon|robot|scrap|kazıma|kazima",
                )
            }
            o["ornek"] = m[:700]
    except Exception as e:
        o["hata"] = f"{type(e).__name__}: {e}"
        o["erisim"] = False
    return o


if __name__ == "__main__":
    hukuk = [kontrol(a, u) for a, u in HUKUK_URL]
    gib = [kontrol(a, u) for a, u in GIB_URL]
    rapor = {"hukuk": hukuk, "gib": gib}
    CIKTI.write_text(json.dumps(rapor, ensure_ascii=False, indent=2),
                     encoding="utf-8")

    print("=== HUKUK / KOSULLAR ===")
    for s in hukuk:
        print(f"  {s['etiket']:28s} {str(s.get('http')):5s} {s.get('bayt', 0):>7}")
    print("=== GIB / VKN ===")
    for s in gib:
        print(f"  {s['etiket']:28s} {str(s.get('http')):5s} {s.get('bayt', 0):>7}")
    print(CIKTI)
