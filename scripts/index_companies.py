#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""9R-02: Firma verisini vektorleyip ChromaDB'ye indexler + dublikasyon raporu.

Kullanim:
    python scripts/index_companies.py --jsonl data/ostim/firmalar_detayli.jsonl
    python scripts/index_companies.py --all          # data/ostim/*.jsonl tarar
    python scripts/index_companies.py --vkn-rap  10  # VKN dublikasyon raporu

Ciktilari:
  - ChromaDB koleksiyonu 'companies' (persist: data/vector_chroma)
  - Ayni VKN'li firmalarin semantik skor raporu (varsa)
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("index_companies")


def _jsonl_okumalar(path: Path) -> list[dict]:
    """JSONL dosyasini satirlari sozluk olarak okur (jsonlines paketi olmadan)."""
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                logger.warning("JSON kodlama hatasi atlandi: %s", line[:80])
                continue
            if isinstance(data, dict):
                rows.append(data)
            elif isinstance(data, list):
                rows.extend(x for x in data if isinstance(x, dict))
    return rows


def _tarama_yap(paths: list[Path]) -> list[dict]:
    rows: list[dict] = []
    for p in paths:
        if not p.exists():
            logger.warning("Dosya yok: %s", p)
            continue
        logger.info("Okunuyor: %s", p.name)
        rows.extend(_jsonl_okumalar(p))
    return rows


def _vkn_raporu(rows: list[dict], vkn_key: str = "vkn", id_key: str = "company_id") -> None:
    from src.company_master.vector import VectorService

    svc = VectorService()
    gruplar = svc.deduplicate_by_vkn(rows, id_key=id_key, vkn_key=vkn_key)
    print(f"\n=== Ayni VKN paylasan gruplar: {len(gruplar)} ===")
    for g in gruplar:
        ortalama = sum(g.scores) / len(g.scores) if g.scores else 0.0
        print(f"VKN {g.vkn}: {len(g.ids)} kayit | ortalama benzerlik {ortalama:.3f} | "
              f"ids={g.ids[:5]}" + ("..." if len(g.ids) > 5 else ""))


def main() -> int:
    parser = argparse.ArgumentParser(description="9R-02 firma indexleme")
    parser.add_argument("--jsonl", nargs="*", help="JSONL dosya yollari (birden fazla olur)")
    parser.add_argument("--all", action="store_true", help="data/ostim/*.jsonl tarar")
    parser.add_argument("--vkn-rap", type=int, nargs="?", const=10, metavar="N",
                        help="VKN dublikasyon raporu (ilk N grup)")
    parser.add_argument("--vkn-key", default="vkn")
    parser.add_argument("--id-key", default="company_id")
    parser.add_argument("--persist", default=str(ROOT / "data/vector_chroma"))
    args = parser.parse_args()

    if args.all:
        paths = sorted((ROOT / "data/ostim").glob("*.jsonl"))
    elif args.jsonl:
        paths = [ROOT / p for p in args.jsonl]
    else:
        parser.error("--jsonl veya --all gerekli")

    rows = _tarama_yap(paths)
    if not rows:
        logger.error("Hic veri okunamadi — islem iptal.")
        return 1
    logger.info("Toplam %d satir okundu", len(rows))

    from src.company_master.vector import VectorService, EmbeddedVectorStore

    store = EmbeddedVectorStore(persist_dir=args.persist)
    svc = VectorService(store=store)
    n = svc.index_firmalar(rows, id_key=args.id_key)
    print(f"Indexlenen firma sayisi: {n}")
    print(f"ChromaDB koleksiyon sayisi: {store.count()}")

    if args.vkn_rap is not None:
        _vkn_raporu(rows, vkn_key=args.vkn_key, id_key=args.id_key)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())