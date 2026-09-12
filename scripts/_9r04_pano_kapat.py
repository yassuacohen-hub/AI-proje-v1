# -*- coding: utf-8 -*-
"""9R-04: Görev panosunu kapatır (durum=done) ve AGENT_SYNC.md'yi yeniler."""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOK = Path(__file__).resolve().parents[1]
if str(KOK) not in sys.path:
    sys.path.insert(0, str(KOK))

from src.company_master.orchestrator.task_board import gorev_getir, gorev_guncelle  # noqa: E402


def main() -> int:
    t = gorev_getir("9R-04")
    if t is None:
        print("HATA: 9R-04 görevi bulunamadı.")
        return 1
    print("ÖNCE:", t["durum"], "|", t.get("not", ""))
    r = gorev_guncelle(
        "9R-04",
        durum="done",
        bitis=datetime.now().isoformat(timespec="seconds"),
        not_="firecrawl+tavily provider baglandi; web_fetch/web_search lokal ve tunelde canli dogrulandi (4 web model: ollama/fetch, tavily/search, tavily/fetch, firecrawl/fetch); unit testler 14 yesil; katalog v1.0.2",
    )
    if r:
        print("SONRA:", r["durum"], "| bitis:", r.get("bitis"))
        print("not:", r.get("not_", "")[:120], "...")
        return 0
    print("HATA: gorev_guncelle kayıt döndürmedi.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())