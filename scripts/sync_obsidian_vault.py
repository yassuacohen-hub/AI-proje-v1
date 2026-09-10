"""Obsidian vault <-> orkestrator senkronizasyonu (DOC-02, llm-wiki uyarlama).

Yapilan isler:
1. task_board.json -> TODO.md "Acik Gorevler" tablosunu guncelle
   (yalnizca plan/aktif/blocked gorevler; done gorevler [[CHANGELOG]]'da).
2. wiki_index.json yenile (build_wiki_index.main cagrisi).
3. Yetim sayfa raporu yazdir.

Kullanim:
    python scripts/sync_obsidian_vault.py          # tam senkron
    python scripts/sync_obsidian_vault.py --check  # sadece rapor, yazma yok
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime as dt
from pathlib import Path

PROJE = Path(__file__).resolve().parent.parent
BOARD = PROJE / "data" / "orchestrator" / "task_board.json"
TODO = PROJE / "AI proje v1" / "V10" / "TODO.md"
ACIK_DURUM = {"plan", "aktif", "blocked", "review"}


def yazi_durumu(durum: str) -> str:
    return durum if durum in ACIK_DURUM else "plan"


def acik_gorevler() -> list[dict]:
    data = json.loads(BOARD.read_text(encoding="utf-8"))
    # task_board.json bir liste (array) — direkt kullan
    if isinstance(data, list):
        gorevler = data
    elif isinstance(data, dict):
        gorevler = data.get("tasks", data.get("gorevler", []))
    else:
        gorevler = []
    return [g for g in gorevler if isinstance(g, dict) and yazi_durumu(g.get("durum", "")) in ACIK_DURUM]


def tablo_satiri(g: dict) -> str:
    """Bir gorevi TODO tablo satirina cevirir."""
    gid = g.get("task_id", g.get("id", "?"))
    baslik = (g.get("baslik", g.get("title", "")) or "").split("-")[0].strip()
    sahip = g.get("sahip", g.get("owner", "?"))
    durum = g.get("durum", g.get("status", "plan"))
    not_alan = g.get("not", g.get("note", "")) or ""
    not_kisa = not_alan[:60] + ("…" if len(not_alan) > 60 else "")
    return f"| {gid} | {baslik} | {sahip} | {durum} | {not_kisa} |"


def todo_guncelle(gorevler: list[dict], yaz: bool) -> list[str]:
    """TODO.md'deki '## Açık Görevler' tablosunu gorevlerle yeniler."""
    text = TODO.read_text(encoding="utf-8")
    if "## Açık Görevler" not in text:
        return ["UYARI: TODO.md'de '## Açık Görevler' bölümü yok"]

    satirlar = ["| ID | Görev | Sahip | Durum | Not |",
                "|----|-------|-------|-------|-----|"]
    satirlar += [tablo_satiri(g) for g in gorevler]
    tablo = "\n".join(satirlar)

    yeni, n = yeniden_kur(text, tablo)
    if yaz and n:
        TODO.write_text(yeni, encoding="utf-8", newline="\n")
    return [f"TODO.md Acik Gorevler: {n} gorev yazildi" if yaz
            else f"TODO.md RAPOR: {n} gorev (yazma yok)"]


def yeniden_kur(text: str, tablo: str) -> tuple[str, int]:
    """Bolum basligi ile sonraki '## ' basligi arasini tabloyla degistirir."""
    bas = text.index("## Açık Görevler")
    sonraki = text.find("\n## ", bas + 5)
    sonraki = sonraki + 1 if sonraki != -1 else len(text)
    eski_bolum = text[bas:sonraki]
    gorev_sayisi = eski_bolum.count("\n| ") - 1
    bolum = "## Açık Görevler\n\n" + tablo + "\n\n"
    return text[:bas] + bolum + text[sonraki:], gorev_sayisi


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="yazma yok")
    args = parser.parse_args()

    mesajlar: list[str] = []
    try:
        gorevler = acik_gorevler()
        mesajlar += todo_guncelle(gorevler, not args.check)
    except (OSError, json.JSONDecodeError) as e:
        mesajlar.append(f"HATA task_board: {e}")

    # wiki_index yenile
    if not args.check:
        from build_wiki_index import main as index_main  # ayni dizin
        sys.argv = ["build_wiki_index.py"]
        try:
            index_main()
            mesajlar.append("wiki_index.json yenilendi")
        except SystemExit:
            pass

    for m in mesajlar:
        print(f"[{dt.now().strftime('%H:%M:%S')}] {m}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
