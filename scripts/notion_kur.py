# -*- coding: utf-8 -*-
"""Pano olusturma ve doldurma. Calistirmak icin: python scripts/notion_pano.py kur"""
from __future__ import annotations

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from notion_pano import (  # noqa: E402
    AJAN_AD, API, BEKLEME, DURUM_AD, ONCELIK_AD, aciklama_getir,
    istek, pano_gorevleri,
)

# SUTUNLAR: (notion adi, tur)
# tur: title | rich_text | select
SUTUNLAR = [
    ("Gorev", "title"),
    ("Ne yapti", "rich_text"),
    ("Bunu ne etkiledi", "rich_text"),
    ("Kim yapiyor", "select"),
    ("Oncelik", "select"),
    ("Durum", "select"),
    ("Gorevi ne acar", "rich_text"),
    ("Kanit (dosya)", "rich_text"),
]

RENK = {"P0": "red", "P1": "orange", "P2": "yellow", "P3": "gray"}
DURUM_RENK = {"YAPILACAK": "gray", "SU ANDA YAPILIYOR": "blue",
              "ONAY BEKLIYOR": "yellow", "BITTI": "green"}


def _s(baslik: str, tur: str, secenekler: list[str] | None = None,
       sec_renk: dict | None = None) -> dict:
    if tur == "title":
        return {"title": {}}
    if tur == "select":
        return {"select": {"options": [
            {"name": s, "color": (sec_renk or {}).get(s, "default")} for s in secenekler]}}
    return {"rich_text": {}}


def _metin(deger: str) -> dict:
    return {"rich_text": [{"text": {"content": deger[:1900]}}]}


def _tek(s: str) -> dict:
    return {"select": {"name": s}}


def sema() -> dict:
    """Veritabani semasini kurar."""
    return {ad: _s(ad, tur, _secenekler(ad, tur), _renkler(ad, tur))
            for ad, tur in SUTUNLAR}


def _secenekler(ad: str, tur: str) -> list[str] | None:
    if tur != "select":
        return None
    if ad == "Kim yapiyor":
        return ["yasu", "utku", "ihsan", "salih"]
    if ad == "Oncelik":
        return [ONCELIK_AD[k] for k in ["P0", "P1", "P2", "P3"]]
    return list(DURUM_RENK.keys())


def _renkler(ad: str, tur: str) -> dict:
    if tur != "select":
        return {}
    if ad == "Oncelik":
        return {ONCELIK_AD[k]: RENK[k] for k in RENK}
    return dict(DURUM_RENK)


def _degerler(gorev: dict) -> dict:
    """Pano satirindaki tek bir gorevi Notion property sozlugune cevirir."""
    gid = gorev.get("task_id", "")
    acik = aciklama_getir(gid)
    onc = gorev.get("oncelik", "P3")
    durum = DURUM_AD.get(gorev.get("durum", "plan"), "YAPILACAK")
    ajan = AJAN_AD.get(gorev.get("sahip", ""), str(gorev.get("sahip", "-")))
    return {
        "Gorev": {"title": [{"text": {"content": acik["baslik"]}}]},
        "Ne yapti": _metin(acik["yapti"]),
        "Bunu ne etkiledi": _metin(acik["etki"]),
        "Kim yapiyor": _tek(ajan),
        "Oncelik": _tek(ONCELIK_AD.get(onc, ONCELIK_AD["P3"])),
        "Durum": _tek(durum),
        "Gorevi ne acar": _metin(acik["bagli"]),
        "Kanit (dosya)": _metin(acik["kanit"]),
    }


def kur() -> None:
    """Panoyu olusturur ve 19 gorevi ekler. Tek yonlu: panoya YAZMAZ."""
    gorevler = pano_gorevleri()
    sayfa = istek("/pages", {
        "parent": {"type": "workspace", "workspace": True},
        "properties": {"title": {"title": [{"text": {"content": "HUGINN - Gorev Panosu"}}]}},
    })
    sayfa_id = sayfa["id"]
    print("Sayfa olusturuldu: " + sayfa_id)

    istek(f"/blocks/{sayfa_id}/children", yontem="PATCH", govde={
        "children": [{"object": "block", "type": "paragraph",
                      "paragraph": {"rich_text": [{"text": {"content":
                          "Bu pano sadece okunur. Kaynak: "
                          "data/orchestrator/task_board.json"}}]}}]
    })

    db = istek("/databases", {
        "parent": {"type": "page_id", "page_id": sayfa_id},
        "title": [{"type": "text", "text": {"content": "Tum Gorevler"}}],
        "properties": sema(),
    })
    db_id = db["id"]
    print("Veritabani olusturuldu: " + db_id)

    for g in gorevler:
        istek("/pages", {"parent": {"database_id": db_id},
                         "properties": _degerler(g)})
        print("  eklendi: " + str(g.get("task_id")))

    print("")
    print("TAMAM: " + str(len(gorevler)) + " gorev eklendi.")
    print("Pano: https://www.notion.so/" + sayfa_id.replace("-", ""))


def _db_id(sayfa_id: str) -> str | None:
    cocuklar = istek(f"/blocks/{sayfa_id}/children?page_size=100").get("results", [])
    for b in cocuklar:
        if b.get("type") == "child_database":
            return b.get("id")
    return None
