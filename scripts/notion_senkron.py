# -*- coding: utf-8 -*-
"""Pano senkronu: yerel panoyu Notion'a YAZAR.

Neden ayri dosya (D-86): gorev_kutusu.py 41KB ve kanit zinciriyle dolu.
Icine yazmak geri alinabilir bir sey degil; senkron ayri, cagrilabilir bir
adim olarak durur (D-260: olcum yoksa iddia yok).

TEK YONLU KURAL: pano -> Notion. Geri yazim YOK. Notion'da elle degisiklik
silinir; kaynak daima data/orchestrator/task_board.json.

Idempotent (D-086): ayni komut 10 kez calissa Notion'da 10 satir olmaz.
Satirlar task_id uzerinden eslestirilir; sadece degisen alanlar PATCH edilir.
"""
from __future__ import annotations

import json
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from notion_pano import PANO          # noqa: E402
from notion_pano import (            # noqa: E402
    AJAN_AD, DURUM_AD, ONCELIK_AD, aciklama_getir, istek, pano_gorevleri,
)

VERITABANI = "3ed279b7-9d9d-8170-a11d-c54243f63eec"
GOREV_ANAHTAR = "Gorev Id"


def _metin(v: str) -> dict:
    return {"rich_text": [{"text": {"content": str(v)[:1900]}}]}


def _tek(v: str) -> dict:
    return {"select": {"name": v}}


def _duzle(deger: dict) -> str:
    """Notion property'sini karsilastirilabilir duz metne cevirir.

    Gerekce 1: API GET'te 'type' anahtarli doner; hedefte (PATCH icin
    hazirladigimiz sozlukte) 'type' YOKTUR. Anahtardan cozumlemek sart.
    Gerekce 2: GET'te 'plain_text' dolu gelir, hedefte 'text.content' vardir.
    Ikisini de ayni metne indirgersek dogru karsilastirma olur; aksi halde
    her calistirmada tum satirlar 'farkli' gorunur (D-260: olcum yaniltmaz).
    """
    tur = deger.get("type")
    if tur is None:
        for ad in ("title", "rich_text", "select", "multi_select", "checkbox",
                   "number", "date", "url", "email", "phone_number"):
            if ad in deger:
                tur = ad
                break
    if tur == "title":
        return "".join(_metin_al(x) for x in deger.get("title", []))
    if tur == "rich_text":
        return "".join(_metin_al(x) for x in deger.get("rich_text", []))
    if tur == "select":
        return (deger.get("select") or {}).get("name", "")
    if tur == "multi_select":
        return ",".join(sorted(x.get("name", "") for x in deger.get("multi_select", [])))
    if tur in ("checkbox",):
        return str(deger.get("checkbox"))
    if tur in ("number",):
        return str(deger.get("number"))
    return str(deger.get(tur, "") if tur else deger)


def _metin_al(parca: dict) -> str:
    return parca.get("plain_text") or parca.get("text", {}).get("content", "")


def _degisen(eski: dict, yeni: dict) -> dict:
    sadece = {}
    for ad, hedef in yeni.items():
        if ad not in eski or _duzle(eski[ad]) != _duzle(hedef):
            sadece[ad] = hedef
    return sadece


def hedef_degerler(gorev: dict) -> dict:
    """Yerel gorev kaydi -> Notion property sozlugu."""
    gid = gorev.get("task_id") or gorev.get("id", "")
    a = aciklama_getir(gid)
    return {
        GOREV_ANAHTAR: _metin(gid),
        "Gorev": {"title": [{"text": {"content": a["baslik"]}}]},
        "Ne yapti": _metin(a["yapti"]),
        "Bunu ne etkiledi": _metin(a["etki"]),
        "Kim yapiyor": _tek(AJAN_AD.get(gorev.get("sahip", ""), str(gorev.get("sahip", "-")))),
        "Oncelik": _tek(ONCELIK_AD.get(gorev.get("oncelik", "P3"), ONCELIK_AD["P3"])),
        "Durum": _tek(DURUM_AD.get(gorev.get("durum", "plan"), "YAPILACAK")),
        "Gorevi ne acar": _metin(a["bagli"]),
        "Kanit (dosya)": _metin(a["kanit"]),
    }


def _mevcut() -> dict[str, dict]:
    """Notion'daki satirlari task_id -> sayfa eslemesi olarak dondurur."""
    r = istek(f"/databases/{VERITABANI}/query", yontem="POST", govde={"page_size": 100})
    harita: dict[str, dict] = {}
    for s in r["results"]:
        pr = s["properties"]
        kimlik = ""
        if GOREV_ANAHTAR in pr:
            kimlik = "".join(x.get("plain_text", "") for x in pr[GOREV_ANAHTAR]["rich_text"])
        if not kimlik:
            bas = pr.get("Gorev", {}).get("title", [])
            kimlik = "".join(x.get("plain_text", "") for x in bas)
        harita[kimlik] = s
    return harita


def _ayni(eski: dict, yeni: dict) -> bool:
    """Iki property sozlugu ayni mi? Farkli olan alanlari PATCH icin secer."""
    for ad, deger in yeni.items():
        if ad not in eski:
            return False
        if eski[ad] != deger:
            return False
    return True


PANO_SAYFA = "3ed279b7-9d9d-8127-82d7-f78a2177eae3"
OZET_ISARETI = "\u2934gorev-ozeti\u2935"   # ozet blogunu bulmak icin isaret


def ozet_metni() -> str:
    """Pano sonundaki durum ozetini TEK metin olarak uretir.

    Neden tek blok: cok bloga bolmek her senkronda arsivlenen blok
    biriktiriyordu (olcum: 64 blok, 3 kopya ozet). Tek blok PATCH ile
    guncellenir, birikmez (D-086 idempotans).
    """
    b = json.loads(PANO.read_text(encoding="utf-8"))
    ts = b if isinstance(b, list) else b.get("tasks", [])
    aktif = [t for t in ts if t.get("durum") in ("plan", "aktif", "review")]
    say = lambda d: len([t for t in ts if t.get("durum") == d])          # noqa: E731
    on = lambda p: len([t for t in aktif if t.get("oncelik") == p])     # noqa: E731
    aj = lambda a, d: len([t for t in aktif                              # noqa: E731
                           if t.get("sahip") == a and t.get("durum") == d])
    sat = ["Simdi ne durumdayiz?  (" + OZET_ISARETI + ")",
           f"Su an {len(aktif)} iş açık. Biten işler arşivde durur, silinmez.",
           "\U0001F7E2 Çalışıyor: " + str(say("aktif"))
           + "   \U0001F7E1 Onay bekliyor: " + str(say("review"))
           + "   \U0001F7E3 Yapılacak: " + str(say("plan"))
           + "   ✅ Bitti (toplam): " + str(say("done")),
           "\U0001F534 " + str(on("P0")) + "  \U0001F7E0 " + str(on("P1"))
           + "  \U0001F7E1 " + str(on("P2")) + "  ⚪ " + str(on("P3"))
           + "   (kırmızı → gri, soldan sağa öncelik düşür)",
           "Kim ne yapıyor:"]
    for a in ("yasu", "utku", "ihsan", "salih"):
        n = aj(a, "plan") + aj(a, "aktif") + aj(a, "review")
        sat.append(f"  {a} — {n} iş "
                   f"(çalışıyor {aj(a,'aktif')}, "
                   f"onay {aj(a,'review')}, plan {aj(a,'plan')})")
    return "\n".join(sat)


def ozet_yenile() -> str:
    """Durum ozetini yeniden yazar: eskiyi sil, tek blogu PATCH et."""
    cocuklar = istek(f"/blocks/{PANO_SAYFA}/children?page_size=100")["results"]
    isaretli = []
    onceki = None
    for b in cocuklar:
        t = b.get("type", "")
        rt = b.get(t, {}).get("rich_text", []) if t != "divider" else []
        metin = "".join(x.get("plain_text", "") for x in rt)
        if OZET_ISARETI in metin:
            isaretli.append(b)
            onceki = b
    silinen = 0
    for b in isaretli:
        istek(f"/blocks/{b['id']}", {"archived": True}, yontem="PATCH")
        silinen += 1
    metin = ozet_metni()
    yeni = {"object": "block", "type": "callout",
            "callout": {"icon": {"type": "emoji", "emoji": "\U0001F4CA"},
                        "rich_text": [{"text": {"content": metin[:1950]}}]}}
    istek(f"/blocks/{PANO_SAYFA}/children", {"children": [yeni]}, yontem="PATCH")
    return f"ozet: 1 blok (silinen kopya {silinen})"


def _matris_yenile() -> str:
    """Ilerleme Matrisi tablolarini da gunceller.

    Neden ayri dosya: matris kendi olcumlerini yapar (notion_matris.py),
    senkron yalnizca gorunumu tazeler.
    """
    try:
        import notion_matris_kur
        notion_matris_kur.kur()
        return "matris: guncellendi"
    except ImportError:
        return "matris: kurulu degil (atlandi)"
    except SystemExit as exc:
        return f"matris: atlandi ({str(exc)[:60]})"


def kapatilanlari_temizle(mevcut: dict, aktif_kimlikler: set) -> int:
    """Panoda olup YERELDE olmayan gorevi arsivler.

    Neden gerekli (olcum): ajanlar calisirken pano 19 -> 12 dustu; panoda
    7 BITMIS is kalmisti. Gosteren bir yuzeyde yalan bilgi olmaz (D-260).
    Arsiv Notion Trash'ina gider, silinmez.

    DIKKAT: yalnizca `aktif_kimlikler` icinde OLMAYANLAR silinir. Tum
    sozlugu taramak (onceki yazim hatasi) aktif gorevleri de siliyordu ve
    pano bosaldi.
    """
    silinen = 0
    for gid, sayfa in list(mevcut.items()):
        if gid and gid not in aktif_kimlikler:
            istek(f"/pages/{sayfa['id']}", {"archived": True}, yontem="PATCH")
            silinen += 1
    return silinen


def senkron(bilesik_test: bool = False) -> None:
    gorevler = pano_gorevleri()
    mevcut = _mevcut()
    eklendi = guncellendi = ayni = 0
    for g in gorevler:
        gid = g.get("task_id") or g.get("id", "")
        hedef = hedef_degerler(g)
        if gid in mevcut:
            eski = mevcut[gid]["properties"]
            if bilesik_test:
                degisen = _degisen(eski, hedef)
                if degisen:
                    guncellendi += 1
                    istek(f"/pages/{mevcut[gid]['id']}", {"properties": degisen}, yontem="PATCH")
                else:
                    ayni += 1
            else:
                ayni += 1
        else:
            istek("/pages", {"parent": {"database_id": VERITABANI},
                             "properties": hedef})
            eklendi += 1
    aktif_kimlikler = {g.get("task_id") or g.get("id", "") for g in gorevler}
    kapali = kapatilanlari_temizle(mevcut, aktif_kimlikler)
    print(f"eklendi={eklendi} guncellendi={guncellendi} degismedi={ayni}"
          f" arsivlendi={kapali}")
    print(f"yerel gorev={len(gorevler)} notion satiri={len(mevcut)}")
    print(ozet_yenile())
    _matris_yenile()


if __name__ == "__main__":
    senkron(bilesik_test="--bilesik" in sys.argv)