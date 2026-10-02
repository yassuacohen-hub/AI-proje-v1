# -*- coding: utf-8 -*-
"""SSOT Ilerleme Matrisi veritabanini kurar ve gunceller.

Mevcut olcum her sayi dosyadan gelir; elle yazim YOK (D-260).
Idempotans: 'Alan' degeriyle eslesir, sadece degisen alanlar PATCH edilir.
"""
from __future__ import annotations

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from notion_pano import istek                    # noqa: E402
from notion_senkron import _degisen, _duzle      # noqa: E402
from notion_matris import ilerleme_satirlari, ajan_satirlari   # noqa: E402

PANO_SAYFA = "3ed279b7-9d9d-8127-82d7-f78a2177eae3"
ISARET = "\u2934ssot-matrisi\u2935"

ILK_SUTUN = "Alan"


def _metin(v: str) -> dict:
    return {"rich_text": [{"text": {"content": str(v)[:1900]}}]}


def _sayi(v: int) -> dict:
    return {"number": v}


def _baslik(v: str) -> dict:
    return {"title": [{"text": {"content": v}}]}


def ilerleme_sema() -> dict:
    return {
        ILK_SUTUN: {"title": {}},
        "Olcum ne diyor": {"rich_text": {}},
        "Simdi nerede": {"rich_text": {}},
        "Toplam": {"number": {"format": "number"}},
        "Nerede olculuyor": {"rich_text": {}},
    }


def ajan_sema() -> dict:
    return {
        "Ajan": {"title": {}},
        "Toplam is": {"number": {"format": "number"}},
        "Su anda calisiyor": {"number": {"format": "number"}},
        "Onay bekliyor": {"number": {"format": "number"}},
        "Yapilacak": {"number": {"format": "number"}},
    }


def _veritabani_bul(sayfa_id: str) -> str | None:
    for b in istek(f"/blocks/{sayfa_id}/children?page_size=100")["results"]:
        if b.get("type") == "child_database":
            return b.get("id")
    return None


def _db_ac(etiket: str, sema: dict) -> str:
    """Notion 2022-06-28: veritabani POST /databases ile acilir."""
    return istek("/databases", {
        "parent": {"type": "page_id", "page_id": PANO_SAYFA},
        "title": [{"type": "text", "text": {"content": etiket}}],
        "properties": sema,
    })["id"]


def _satirlar(db_id: str, anahtar: str) -> dict[str, dict]:
    r = istek(f"/databases/{db_id}/query", yontem="POST", govde={"page_size": 100})["results"]
    out = {}
    for s in r:
        pr = s["properties"].get(anahtar, {})
        k = "".join(x.get("plain_text", "") for x in pr.get("title", []))
        out[k] = s
    return out


def kur() -> None:
    """Iki veritabanini ac ve olculmus satirlarla doldur (yoksa olustur)."""
    for etiket, sema, anahtar in (
        ("Ilerleme Matrisi", ilerleme_sema(), ILK_SUTUN),
        ("Ajan Ilerlemesi", ajan_sema(), "Ajan"),
    ):
        db = _veritabani_bul_by_name(etiket)
        if not db:
            db = _db_ac(etiket, sema)
            print(f"veritabani acildi: {etiket}")
        mevcut = _satirlar(db, anahtar)

        veriler = ([{"Alan": _baslik(x["alan"]),
                     "Olcum ne diyor": _metin(x["olcu"]),
                     "Simdi nerede": _metin(x["ilerleme"]),
                     "Toplam": _sayi(x["toplam"]),
                     "Nerede olculuyor": _metin(x["not"])}
                    for x in ilerleme_satirlari()]
                   if anahtar == ILK_SUTUN else
                   [{"Ajan": _baslik(a["ajan"]),
                     "Toplam is": _sayi(a["toplam"]),
                     "Su anda calisiyor": _sayi(a["calisiyor"]),
                     "Onay bekliyor": _sayi(a["onay"]),
                     "Yapilacak": _sayi(a["plan"])}
                    for a in ajan_satirlari()])

        eklendi = guncellendi = 0
        for v in veriler:
            # v[anahtar] artik SARIMALI sozluk; eslesme anahtari duz metin olmali.
            parca = v[anahtar]
            kimlik = "".join(y.get("text", {}).get("content", "")
                             for y in parca.get("title", []))
            if kimlik in mevcut:
                eski = mevcut[kimlik]["properties"]
                degisen = _degisen(eski, v)
                if degisen:
                    istek(f"/pages/{mevcut[kimlik]['id']}",
                          {"properties": degisen}, yontem="PATCH")
                    guncellendi += 1
            else:
                istek("/pages", {"parent": {"database_id": db},
                                 "properties": v})
                eklendi += 1
        print(f"  {etiket}: eklendi {eklendi}, guncellendi {guncellendi}, "
              f"toplam {len(veriler)}")


def _veritabani_bul_by_name(ad: str) -> str | None:
    for x in istek("/search", {"page_size": 100})["results"]:
        if x.get("object") != "database":
            continue
        bas = "".join(y.get("plain_text", "") for y in x.get("title", []))
        if bas == ad:
            return x["id"]
    return None


def bagla() -> None:
    """Matris sayfasini panoya baglar (link_blogu)."""
    sayfa = istek("/search", {"page_size": 100})["results"]
    del sayfa
    # pano sayfasina link ekle
    once = istek(f"/blocks/{PANO_SAYFA}/children?page_size=100")["results"]
    for b in once:
        t = b.get("type", "")
        rt = b.get(t, {}).get("rich_text", []) if t != "divider" else []
        if ISARET in "".join(x.get("plain_text", "") for x in rt):
            return
    istek(f"/blocks/{PANO_SAYFA}/children", {"children": [{
        "object": "block", "type": "paragraph",
        "paragraph": {"rich_text": [{"text": {"content": ISARET +
            "  Ayni sayfanin altindaki 'Ilerleme Matrisi' ve "
            "'Ajan Ilerlemesi' tablolarina bak."}}]}}]}, yontem="PATCH")
    print("pano -> matris baglantisi eklendi")


if __name__ == "__main__":
    kur()
    bagla()