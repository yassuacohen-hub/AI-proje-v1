# -*- coding: utf-8 -*-
"""VERI-LONCA-FIRMA-01 — /FirmaBilgisi ucunu olcum (KAHIN'in verdigi TAM Id).

GOREV: 1 Id ile 7 alani cikarmak, POST WAF durumunu yeniden olcmek,
/Sektor sayfasinda Id var mi bakmak. Supabase'e YAZMA YOK.
Bilinmeyen 'bilinmiyor' yazilir (D-217).
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

import httpx

KOK = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

TABAN = "https://lonca.gov.tr"
CIKTI = KOK / "data" / "pilots" / "VERI-LONCA-FIRMA-01"
CIKTI.mkdir(parents=True, exist_ok=True)

#: KAHIN'in ekran goruntusunden kopyaladigi TAM Id (URL-kodlu haliyle).
ID_TAM = ("GUlaiBriA%2BpzS%2FLpqr6uYKPmeSqOSPYFlh3E5OjL5tlhbihfLlr0VvuqySlFUOW7e"
          "kyZcaf3tzXUOXSik827xVYC286iPnapNecagyOWGfmbbbNxVi6WbytSGLQgDZQkuXq1Oco%3D")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
HDR = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
}


def _metin(h: str) -> str:
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", h, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", s).strip()


def _cx() -> httpx.Client:
    return httpx.Client(timeout=40, follow_redirects=True, headers=HDR)


def _tek(gid: str) -> dict:
    """Tarayici benzeri akis: once ana sayfa (oturum), sonra FirmaBilgisi."""
    with _cx() as cx:
        cx.get(TABAN)
        r = cx.get(f"{TABAN}/FirmaBilgisi?Id={gid}")
    return {"http": r.status_code, "bayt": len(r.text),
            "html": r.text, "metin": _metin(r.text),
            "tablo": len(re.findall(r"<table", r.text, re.I)),
            "tr": len(re.findall(r"<tr", r.text, re.I))}


def _coz(h: str) -> str:
    """HTML entity'lerini coz (sayfa &#x130; &#xC7; gibi kod kullaniyor)."""
    import html as _h
    return _h.unescape(h)


def alanlari(d: str) -> dict:
    """7 alan: sicil_no, unvan, adres, telefon, faks, eposta, web."""
    out = {}
    d = _coz(d)

    # Unvan: 'SİNCAN / ANKARA' ibaresinden onceki buyuk harfli blok
    m = re.search(r"([A-ZÇĞİÖŞÜ][A-ZÇĞİÖŞÜ0-9 .'\-]{8,70})\s+S[İI]NCAN", d)
    if m:
        out["unvan"] = re.sub(r"\s+", " ", m.group(1)).strip()

    # Sicil: '12132 / SİNCAN / ANKARA' veya 'SİNCAR / ANKARA' oncesi rakam
    m = re.search(r"(\d{4,7})\s*/\s*S[İI]NCAN", d)
    if m:
        out["sicil_no"] = m.group(1)

    m = re.search(r"Adres\s*(.{0,160})", d, re.I)
    if m:
        v = re.split(r"(?=(?:Telefon|Faks|E-Posta|Web)\b)", m.group(1))[0].strip()
        v = re.sub(r"^Adres\s*:?\s*", "", v).strip()
        if v:
            out["adres"] = v[:130]

    for et, anahtar in (("Telefon", "telefon"), ("Faks", "faks")):
        m = re.search(rf"{et}\s*(.{{0,24}})", d, re.I)
        if m:
            v = m.group(1).strip()
            if v.startswith("0") or "(" in v:
                out[anahtar] = v[:24]

    for m in re.findall(r"[\w.\-]+@[\w.\-]+\.\w{2,}", d):
        out["eposta"] = m
        break
    m = re.search(r"(www\.[\w.\-]+\.\w{2,4})", d)
    if m:
        out["web"] = m.group(1)

    return out


def urunler(d: str) -> list[str]:
    """Firma urun gruplari: 'NN.NN - Ad' kalibi, satir sonu sinirli."""
    return sorted(set(m.strip() for m in re.findall(
        r"\b(\d{2}\.\d{2}\s*-\s*[^|]{3,60}?)(?=\s{2,}\d{2}\.\d{2}|$)", d)))


def html_urunleri(html: str) -> list[list[str]]:
    """#tbl satirlari: firmanin URUN KATALOGU (NACE listesi DEGIL).

    Sayfa #tbl icinde DataTables ile gosteriyor; ornege gore buradaki
    satirlar URETIM URUNLERI (orn. 'UCUS KONTROL SISTEMI').
    """
    out = []
    h = _coz(html)
    m = re.search(r'id="tbl".*?</table>', h, re.S | re.I)
    if not m:
        return out
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", m.group(0), re.S | re.I):
        hucreler = [re.sub(r"\s+", " ", _metin(x)).strip()
                    for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S | re.I)]
        hucreler = [x for x in hucreler if x]
        if hucreler:
            out.append(hucreler)
    return out


def sektor_tablosu(kod: str) -> dict:
    """/Sektor sayfasindaki tablo gercekten firma listesi mi? Cikar."""
    with _cx() as cx:
        r = cx.get(f"{TABAN}/Sektor?sektorKodu={kod}")
    h = r.text
    tablo = []
    for tb in re.findall(r"<table[^>]*>(.*?)</table>", h, re.S | re.I):
        satirlar = []
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", tb, re.S | re.I):
            hucreler = [re.sub(r"\s+", " ", _metin(x)).strip()
                        for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>",
                                            tr, re.S | re.I)]
            hucreler = [x for x in hucreler if x]
            if hucreler:
                satirlar.append(hucreler)
        tablo.append(satirlar)
    return {"kod": kod, "tablo_sayisi": len(re.findall(r"<table", h, re.I)),
            "tablolar": tablo,
            "firma_link": sorted(set(re.findall(r"FirmaBilgisi", h)))[:5],
            "id_benzeri": sorted(set(re.findall(r"[?&]Id=([A-Za-z0-9%+/_-]{20,})", h)))[:5]}


def post_dene(etiket: str, hdr: dict, veri_ek: dict | None = None) -> tuple[int, int, bool]:
    """POST /Ara -> (http, bayt, waf_reddi)."""
    with _cx() as cx:
        ana = cx.get(TABAN)
        blk = re.search(r"""<input[^>]*__RequestVerificationToken[^>]*>""",
                        ana.text, re.I)
        tok = re.search(r"""value="([^"]+)""", blk.group(0), re.I) if blk else None
        v = {"search": etiket, "sec": "2", "araIller": ""}
        if tok:
            v["__RequestVerificationToken"] = tok.group(1)
        if veri_ek:
            v.update(veri_ek)
        r = cx.post(TABAN + "/Ara", data=v, headers=hdr)
    return r.status_code, len(r.text), "Rejected" in r.text




if __name__ == "__main__" and "--yapilari" in sys.argv:
    """HAM HTML yapısını incele — regex değil, GERÇEK yapı."""
    with _cx() as cx:
        cx.get(TABAN)
        r = cx.get(f"{TABAN}/FirmaBilgisi?Id={ID_TAM}")
    h = _coz(r.text)
    (CIKTI / "ham.html").write_text(h, encoding="utf-8")
    print("kaydedildi, bayt:", len(h))

    print("\n--- unvan bolgesi (AKARNA) ---")
    m = re.search(r"AKANA", h, re.I)
    if m:
        a = max(0, m.start() - 700)
        print(re.sub(r"\s+", " ", h[a:m.end() + 500])[:1100])

    print("\n--- rakam + SİNCAN cevresi (sicil no) ---")
    for m in list(re.finditer(r"SİNCAN", h))[:3]:
        a = max(0, m.start() - 320)
        print("  >>", re.sub(r"\s+", " ", h[a:m.end() + 120])[:460], "\n")

    print("\n--- 'Adres' etiketinin tam HTML'i ---")
    m = re.search(r"Adres", h)
    if m:
        a = max(0, m.start() - 300)
        print(re.sub(r"\s+", " ", h[a:m.end() + 700])[:900])

if __name__ == "__main__":


    o = _tek(ID_TAM)
    print("== 1) /FirmaBilgisi TAM Id ile ==")
    print("HTTP %d | %d bayt | tablo=%d tr=%d"
          % (o["http"], o["bayt"], o["tablo"], o["tr"]))
    d = o["metin"]
    a = alanlari(d)
    uh = html_urunleri(o["html"])
    print("\n--- 7 ALAN ---")
    for k in ("sicil_no", "unvan", "adres", "telefon", "faks", "eposta", "web"):
        print("   %-9s %s" % (k, a.get(k, "(BULUNAMADI)")))
    print("\n--- FIRMA URUN GRUPLERI: %d adet (html tablosu) ---" % len(uh))
    for x in uh:
        print("   ", " | ".join(x)[:112])
    (CIKTI / "firma_ornek.txt").write_text(d, encoding="utf-8")
    (CIKTI / "firma_ornek.html").write_text(o["html"], encoding="utf-8")
    (CIKTI / "firma_ornek_alanlar.json").write_text(
        json.dumps(a, ensure_ascii=False, indent=2), encoding="utf-8")
    (CIKTI / "firma_urun_katalogu.json").write_text(
        json.dumps(uh, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n== 2) /Sektor tablosu firma listesi mi? ==")
    st = sektor_tablosu("24.10")
    print("tablo sayisi:", st["tablo_sayisi"], "| FirmaBilgisi link:",
          len(st["firma_link"]), "| id_benzeri:", len(st["id_benzeri"]))
    for i, tb in enumerate(st["tablolar"]):
        print("  TABLO %d: %d satir" % (i, len(tb)))
        for s in tb[:4]:
            print("     ", " | ".join(s)[:120])

    print("\n== 3) POST /Ara WAF varyantlari (KAHIN izin verdi, nokta nokta) ==")
    temel = {"Referer": TABAN, "Origin": TABAN,
             "Content-Type": "application/x-www-form-urlencoded"}
    varyantlar = [
        ("temel", {**temel}),
        ("fetch-meta", {**temel, "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin",
                        "X-Requested-With": "XMLHttpRequest"}),
        ("navigate", {**temel, "Sec-Fetch-Dest": "document",
                      "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "same-origin"}),
    ]
    for ad, h in varyantlar:
        try:
            code, bayt, waf = post_dene("AKARNA", h)
            print("   %-12s HTTP %d | %6d bayt | %s"
                  % (ad, code, bayt, "WAF REDDI" if waf else "GECTI"))
        except Exception as e:
            print("   %-12s HATA %s" % (ad, type(e).__name__))

