"""V10 Obsidian vault wiki-index olusturucu.

V10 altindaki tum .md dosyalarini tarar ve ajanlarin hizli erisimi icin
data/orchestrator/wiki_index.json uretir. llm-wiki modeline uyarlama (DOC-02).

Kullanim:
    python scripts/build_wiki_index.py

Cikti semasi (her sayfa): path, title, summary, size, updated, type,
tags, links_out, links_in. Ek: hubs, orphans, _broken_links.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def frontmatter_oku(text: str) -> dict:
    """YAML frontmatter'i basit sekilde ayristirir (sadece type/tags)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    meta: dict = {}
    tags: list[str] = []
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip().lower()
        val = val.strip().strip("\"'")
        if key == "tags":
            tags = [t.strip() for t in val.strip("[]").split(",") if t.strip()]
        elif key == "type":
            meta["type"] = val
    meta["tags"] = tags
    return meta




def ilk_baslik(text: str) -> str:
    for line in text.splitlines():
        if line.strip().startswith("#"):
            return line.lstrip("#").strip()
    return ""


def ozet(text: str, limit: int = 200) -> str:
    """Ilk baslik ve frontmatter haric ilk paragraftan ozet uretir."""
    body = FRONTMATTER_RE.sub("", text, count=1)
    lines: list[str] = []
    for line in body.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or s.startswith(">") or s.startswith("Bağlantılar"):
            continue
        lines.append(s)
        if len(" ".join(lines)) >= limit:
            break
    oz = " ".join(lines)
    return oz[:limit] + ("…" if len(oz) > limit else "")


def index_olustur(v10_root: Path) -> dict:
    pages: dict[str, dict] = {}
    for f in sorted(v10_root.rglob("*.md")):
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"UYARI: okunamadi {f}: {e}", file=sys.stderr)
            continue
        rel = f.relative_to(v10_root).as_posix()
        meta = frontmatter_oku(text)
        links_out = list(dict.fromkeys(m.strip() for m in WIKILINK_RE.findall(text)))
        pages[rel] = {
            "path": rel,
            "title": ilk_baslik(text) or f.stem,
            "summary": ozet(text),
            "size": f.stat().st_size,
            "updated": dt.datetime.fromtimestamp(
                f.stat().st_mtime, tz=dt.timezone.utc
            ).isoformat(),
            "type": meta.get("type", "unknown"),
            "tags": meta.get("tags", []),
            "links_out": links_out,
            "links_in": [],
        }
    return pages


def linkleri_coz(pages: dict[str, dict]) -> list[str]:
    """links_in hesaplar; cozulemeyen hedefleri broken olarak dondurur.

    Hedef cozumleme sirasi: tam yol -> yol+'.md' -> stem -> klasor-ekli yol.
    """
    by_key: dict[str, str] = {}
    for rel in pages:
        no_ext = rel[:-3] if rel.endswith(".md") else rel
        by_key.setdefault(rel, rel)
        by_key.setdefault(no_ext, rel)
        by_key.setdefault(Path(rel).stem, rel)

    broken: list[str] = []
    for rel, p in pages.items():
        for target in p["links_out"]:
            resolved = by_key.get(target)
            if resolved is None:
                resolved = next(
                    (r for r in pages if r.endswith("/" + target + ".md")),
                    None,
                )
            if resolved:
                pages[resolved]["links_in"].append(rel)
            else:
                broken.append(f"{rel} -> {target}")
    return broken


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v10", default="AI proje v1/V10", help="V10 kok dizini")
    parser.add_argument(
        "--out", default="data/orchestrator/wiki_index.json", help="Cikti JSON"
    )
    args = parser.parse_args()

    proje_kok = Path(__file__).resolve().parent.parent
    v10_root = proje_kok / args.v10
    out_path = proje_kok / args.out

    if not v10_root.is_dir():
        print(f"HATA: V10 dizini bulunamadi: {v10_root}", file=sys.stderr)
        return 1

    pages = index_olustur(v10_root)
    broken = linkleri_coz(pages)

    hubs = sorted(
        ((rel, len(p["links_in"])) for rel, p in pages.items()),
        key=lambda x: x[1],
        reverse=True,
    )[:10]
    orphans = [rel for rel, p in pages.items() if not p["links_in"]]

    index = {
        "generated": dt.datetime.now(tz=dt.timezone.utc).isoformat(),
        "v10_root": v10_root.as_posix(),
        "page_count": len(pages),
        "hubs": [{"path": h[0], "links_in": h[1]} for h in hubs],
        "orphans": orphans,
        "_broken_links": broken,
        "pages": pages,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        f"OK pages={len(pages)} hubs={len(hubs)} orphans={len(orphans)} "
        f"broken={len(broken)} out={out_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

def ilk_baslik(text: str) -> str:
    for line in text.splitlines():
        if line.strip().startswith("#"):
            return line.lstrip("#").strip()
    return ""
