#!/usr/bin/env python3
"""
Obsidian Vault Bakım Scripti (D-185/D-186 takibi)
- Orphan node oranı, hub<->hub yoğunluk, kırık link sayısı ölçer
- Idempotent, salt okunur (hiçbir .md dosyasını değiştirmez)
- Log: data/orchestrator/.vault_bakim_log.txt

Not (2026-09-22 düzeltme): Ignore listesi artık .obsidian/app.json'dan
okunuyor (elle kopya tutmuyoruz), link çözümü Obsidian'ın gerçek davranışını
izliyor: önce tam yol+.md, yoksa benzersiz stem eşleşmesi.
"""
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HUBS = ROOT / "Huginn Data Insights" / "hubs"
LOG_FILE = ROOT / "data" / "orchestrator" / ".vault_bakim_log.txt"
WIKILINK = re.compile(r"\[\[([^\]|#]+)")

IGNORE = json.loads((ROOT / ".obsidian" / "app.json").read_text(encoding="utf-8"))["userIgnoreFilters"]


def kapsamda(p: Path) -> bool:
    s = p.relative_to(ROOT).as_posix()
    return not any(ig.rstrip("/") in s for ig in IGNORE)


def _index():
    """Kapsamdaki dosyalar + yol-index + stem-index (Obsidian çözümleme için)."""
    files = [p for p in ROOT.rglob("*.md") if kapsamda(p)]
    yol_index = {p.relative_to(ROOT).as_posix()[:-3] for p in files}
    stem_index = defaultdict(list)
    for p in files:
        stem_index[p.stem].append(p.relative_to(ROOT).as_posix()[:-3])
    return files, yol_index, stem_index


def _cozulur_mu(hedef: str, yol_index: set, stem_index: dict) -> str | None:
    """Obsidian gibi çözer: tam yol var mı, yoksa benzersiz stem. Çözülen yolu döndürür."""
    h = hedef.strip().removesuffix(".md")
    if h in yol_index:
        return h
    adaylar = stem_index.get(h.split("/")[-1], [])
    if len(adaylar) == 1:
        return adaylar[0]
    return None


def orphan_orani():
    files, yol_index, stem_index = _index()
    gelen = Counter()
    for p in files:
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for m in WIKILINK.finditer(txt):
            cozulen = _cozulur_mu(m.group(1), yol_index, stem_index)
            if cozulen:
                gelen[cozulen] += 1
    orphan = [y for y in yol_index if gelen[y] == 0]
    return len(orphan), len(yol_index), sorted(orphan)


def hub_yogunluk():
    files = sorted(HUBS.glob("*.md"))
    names = {f.stem for f in files}
    edges = set()
    for f in files:
        txt = f.read_text(encoding="utf-8", errors="ignore")
        hits = {m.group(1).strip().split("/")[-1] for m in WIKILINK.finditer(txt)}
        for p in (hits & names) - {f.stem}:
            edges.add(tuple(sorted((f.stem, p))))
    n = len(files)
    maks = n * (n - 1) // 2
    return len(edges), maks, n


def kirik_link():
    _, yol_index, stem_index = _index()
    kirik = []
    for hub in sorted(HUBS.glob("*.md")):
        for hedef in WIKILINK.findall(hub.read_text(encoding="utf-8")):
            if not _cozulur_mu(hedef, yol_index, stem_index):
                kirik.append(f"{hub.name} -> {hedef.strip()}")
    return kirik


def main():
    n_orphan, n_total, orphans = orphan_orani()
    n_edges, n_maks, n_hub = hub_yogunluk()
    kirik = kirik_link()

    oran = n_orphan / n_total if n_total else 0
    yogunluk = n_edges / n_maks if n_maks else 0

    lines = [
        f"[{datetime.now().isoformat(timespec='seconds')}] VAULT BAKIM RAPORU",
        f"ORPHAN {n_orphan}/{n_total} ({oran:.2%})",
        f"HUB_YOGUNLUK {n_edges}/{n_maks} ({yogunluk:.2%}) — {n_hub} hub",
        f"KIRIK_LINK {len(kirik)}",
    ]
    if kirik:
        lines += [f"  KIRIK {k}" for k in kirik]
    if oran > 0.10:
        lines.append(f"UYARI: orphan orani %10 esigini asti ({oran:.2%})")
    if kirik:
        lines.append("UYARI: kirik link tespit edildi, hub dosyalari kontrol edilmeli")

    rapor = "\n".join(lines) + "\n"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(rapor + "\n")
    print(rapor)


if __name__ == "__main__":
    main()
