# -*- coding: utf-8 -*-
"""messages.jsonl dedupe. Varsayilan: kuru calisma. --yaz: yedek al + yaz.
Anahtar: (tarih,kimden,kime,type,task_id,mesaj). Ilk gorulen kalir, sira korunur.
Bozuk/bos satir ve anahtarsiz satir: oldugu gibi korunur. BOM korunur.
ponytail: tek dosya, bellek ici; 100 MB ustunde akis (stream) gerekir.
"""
import json
import shutil
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent / "Huginn Data Insights"
HEDEF = KOK / "data" / "orchestrator" / "chat" / "messages.jsonl"
CIKTI = Path(__file__).resolve().parent / "msg_dedupe.txt"
ALANLAR = ("tarih", "kimden", "kime", "type", "task_id", "mesaj")


def main() -> int:
    yaz = "--yaz" in sys.argv
    ham = HEDEF.read_bytes()
    bom = ham.startswith(b"\xef\xbb\xbf")
    metin = ham.decode("utf-8-sig")
    satirlar = metin.splitlines()
    gorulen: set = set()
    cikis: list[str] = []
    bozuk = 0
    for s in satirlar:
        if not s.strip():
            continue
        try:
            o = json.loads(s)
            k = tuple(str(o.get(a)) for a in ALANLAR) if isinstance(o, dict) else None
        except ValueError:
            bozuk += 1
            k = None
        if k is None:
            cikis.append(s)
            continue
        if k in gorulen:
            continue
        gorulen.add(k)
        cikis.append(s)
    yeni = ("\ufeff" if bom else "") + "\n".join(cikis) + "\n"
    rapor = [
        f"dosya: {HEDEF}",
        f"once satir: {len(satirlar)}  boyut: {len(ham)} bayt",
        f"sonra satir: {len(cikis)}  boyut: {len(yeni.encode('utf-8'))} bayt",
        f"benzersiz: {len(gorulen)}  bozuk(korundu): {bozuk}  bom: {bom}",
        f"mod: {'YAZ' if yaz else 'KURU'}",
    ]
    if yaz:
        yedek = Path(__file__).resolve().parent / "messages.jsonl.bak_dedupe"
        shutil.copy2(HEDEF, yedek)
        HEDEF.write_bytes(yeni.encode("utf-8"))
        rapor.append(f"yedek: {yedek}")
    CIKTI.write_text("\n".join(rapor) + "\n", encoding="utf-8")
    print("\n".join(rapor))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
