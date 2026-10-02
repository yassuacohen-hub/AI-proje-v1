# -*- coding: utf-8 -*-
"""SSOT Ilerleme Matrisi - projenin nereye kadar geldigini gosteren tablo.

KAYNAK (SSOT): her sayi dosyadan olculur, elle yazilmaz (D-260).
  - karar sayisi      : AGENTS.md
  - migration         : src/company_master/schema/migrations/*.sql
  - gorev             : data/orchestrator/task_board.json
  - ajan              : docs/ajanlar/*.md
  - modul             : src/company_master/

Kural: pano ve bu matris YALNIZCA gorunur. Kaynak dosyalardir.
"""
from __future__ import annotations

import collections
import json
import pathlib
import re

KOK = pathlib.Path(__file__).resolve().parents[1]

# --- SSOT okuyucular -------------------------------------------------------


def kararlar() -> list[int]:
    t = (KOK / "AGENTS.md").read_text(encoding="utf-8", errors="replace")
    return sorted({int(x) for x in re.findall(r"D-(\d{3})", t)})


def migrationlar() -> list[str]:
    d = KOK / "src" / "company_master" / "schema" / "migrations"
    return sorted(p.name for p in d.glob("*.sql") if not p.name.endswith(".down.sql"))


def gorevler() -> list[dict]:
    b = json.loads((KOK / "data" / "orchestrator" / "task_board.json").read_text(encoding="utf-8"))
    ts = b if isinstance(b, list) else b.get("tasks", [])
    return [t for t in ts if t.get("durum") in ("plan", "aktif", "review")]


def ajanlar() -> list[str]:
    return sorted(p.stem for p in (KOK / "docs" / "ajanlar").glob("*.md"))


def modul_olcugu() -> dict:
    """Ana moduller ve olculur dosya sayilari."""
    kok = KOK / "src" / "company_master"
    out = {}
    for p in sorted(kok.iterdir()):
        if not p.is_dir() or p.name.startswith(("__", ".")):
            continue
        n = len([f for f in p.rglob("*.py")])
        if n:
            out[p.name] = n
    return out


def satirlar() -> tuple[int, int]:
    """(python satiri, markdown dosyasi) - proje buyuklugu."""
    kok = KOK / "src" / "company_master"
    py = sum(len(f.read_text(encoding="utf-8", errors="replace").splitlines())
             for f in kok.rglob("*.py"))
    md = len([f for f in KOK.rglob("*.md")
              if not any(g in str(f) for g in (".git", ".venv", ".kilo", ".agents", "backups"))])
    return py, md


# --- matris satirlari ------------------------------------------------------

DURUM_AD = {"done": "Bitti", "aktif": "Calisiyor",
            "review": "Onay bekliyor", "plan": "Yapilacak",
            "iptal": "Iptal", "archive": "Arsiv"}

ONCELIK_AD = {"P0": "Kirmizi - en onemli", "P1": "Turuncu - onemli",
              "P2": "Sari - orta", "P3": "Gri - sonra"}


def ilerleme_satirlari() -> list[dict]:
    """Projenin her alani icin olculmus ilerleme satirlari."""
    ts = gorevler()                      # yalnizca AKTIF isler
    b = json.loads((KOK / "data" / "orchestrator" / "task_board.json").read_text(encoding="utf-8"))
    tum = b if isinstance(b, list) else b.get("tasks", [])
    # say TUM kayitlardan kurulur: 'done' aktif listede YOKTUR (D-260).
    # Aktif listeden saymak 'bitti' sayisini sifir cikarir, yuzde 0 olur.
    say = collections.Counter(t.get("durum") for t in tum)
    on = collections.Counter(t.get("oncelik") for t in ts)
    py, md = satirlar()
    migs = migrationlar()
    ks = kararlar()
    aj = ajanlar()
    mod = modul_olcugu()

    t = lambda k: say.get(k, 0)                                          # noqa: E731
    o = lambda k: on.get(k, 0)                                           # noqa: E731
    y = lambda n, d: (n / d * 100 if d else 0)                           # noqa: E731

    toplam = len(tum)
    biten = t("done") + t("iptal") + t("archive")

    return [
        {"alan": "Gorevler", "olcu": f"{t('aktif')} calisiyor / {len(ts)} acik",
         "ilerleme": f"{y(t('done'), toplam):.0f}% bitti", "toplam": toplam,
         "not": "data/orchestrator/task_board.json - tek dogruluk kaynagi"},
        {"alan": "Oncelik dagilimi",
         "olcu": f"{o('P0')} kirmizi / {o('P1')} turuncu / {o('P2')} sari / {o('P3')} gri",
         "ilerleme": f"{o('P0')} kritik is", "toplam": len(ts),
         "not": "Kirmizi isler once; gri isler en sona birakilir"},
        {"alan": "Onay kapisi", "olcu": f"{t('review')} teslim onay bekliyor",
         "ilerleme": "Bitti ama teslim edilmedi" if t("review") else "Temiz",
         "toplam": t("review"), "not": "Onaylanmadan 'bitti' sayilmaz"},
        {"alan": "Karar kaydi", "olcu": f"{len(ks)} karar (D-{min(ks)}..D-{max(ks)})",
         "ilerleme": "Surekli buyuyor", "toplam": len(ks),
         "not": "AGENTS.md - her karar bir kural"},
        {"alan": "Veritabani", "olcu": f"{len(migs)} goc uygulandi",
         "ilerleme": "Sema dosyada = uygulanmis", "toplam": len(migs),
         "not": "src/company_master/schema/migrations/"},
        {"alan": "Ajanlar", "olcu": f"{len(aj)} ajan: {', '.join(aj)}",
         "ilerleme": "Hepsi aktif", "toplam": len(aj),
         "not": "docs/ajanlar/ - her birinin rol dosyasi"},
        {"alan": "Kod", "olcu": f"{py:,} satir python ({len(mod)} modul)",
         "ilerleme": f"En buyuk: {max(mod, key=mod.get) if mod else '-'}", "toplam": py,
         "not": "src/company_master/"},
        {"alan": "Dokumantasyon", "olcu": f"{md:,} markdown dosyasi",
         "ilerleme": "Obsidian grafina bagli", "toplam": md,
         "not": "Tek kok, tek vault (D-223)"},
    ]


def ajan_satirlari() -> list[dict]:
    """Ajan bazli ilerleme."""
    ts = gorevler()
    out = []
    for a in ajanlar():
        s = [t for t in ts if t.get("sahip") == a]
        c = collections.Counter(t.get("durum") for t in s)
        out.append({"ajan": a, "toplam": len(s),
                    "calisiyor": c.get("aktif", 0),
                    "onay": c.get("review", 0),
                    "plan": c.get("plan", 0)})
    return out