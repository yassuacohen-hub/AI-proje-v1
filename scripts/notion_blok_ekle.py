# -*- coding: utf-8 -*-
"""Pano sayfasina aciklama bloklarini ekler. TEK YONLU (panoya yazmaz, sadece sayfaya blok ekler)."""
from __future__ import annotations

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from notion_pano import istek          # noqa: E402
from notion_bloklar import BLOKLAR     # noqa: E402

PANO = "3ed279b7-9d9d-8127-82d7-f78a2177eae3"   # HUGINN - Gorev Panosu


def yb(tur: str, icerik: str, kalemler: list) -> list[dict]:
    """BLOKLAR girdisini Notion API blok sozlugune cevirir.

    D-86 notu: Notion liste blogunun adi 'bulleted_list_item' dir, 'bulleted' degil.
    Yanlis ad gonderilirse API 400 verir ve sessizce yarim sayfa birakir.
    """
    if tur == "p":
        return [{"object": "block", "type": "paragraph",
                 "paragraph": {"rich_text": [{"text": {"content": icerik}}]}}]
    if tur == "h2":
        return [{"object": "block", "type": "heading_2",
                 "heading_2": {"rich_text": [{"text": {"content": icerik}}]}}]
    if tur == "h3":
        return [{"object": "block", "type": "heading_3",
                 "heading_3": {"rich_text": [{"text": {"content": icerik}}]}}]
    if tur == "quote":
        return [{"object": "block", "type": "quote",
                 "quote": {"rich_text": [{"text": {"content": icerik}}]}}]
    if tur == "callout":
        return [{"object": "block", "type": "callout",
                 "callout": {"icon": {"type": "emoji", "emoji": "\u26a0\ufe0f"},
                             "rich_text": [{"text": {"content": icerik}}]}}]
    if tur == "divider":
        return [{"object": "block", "type": "divider", "divider": {}}]
    if tur in ("bulleted_list_item", "numbered_list_item"):
        return [{"object": "block", "type": tur,
                 tur: {"rich_text": [{"text": {"content": f"{a} \u2014 {b}"}}]}}
                for a, b in kalemler]
    return []


def ekle() -> None:
    bloklar: list[dict] = []
    for tur, icerik, kalemler in BLOKLAR:
        bloklar.extend(yb(tur, icerik, kalemler))
    print("Gonderilecek blok:", len(bloklar))
    basarili = 0
    for i, b in enumerate(bloklar):
        try:
            istek(f"/blocks/{PANO}/children", {"children": [b]}, yontem="PATCH")
            basarili += 1
        except SystemExit as exc:
            print(f"  HATA #{i} {b['type']}: {str(exc)[:90]}")
    print("Basariyla eklendi:", basarili)


if __name__ == "__main__":
    ekle()