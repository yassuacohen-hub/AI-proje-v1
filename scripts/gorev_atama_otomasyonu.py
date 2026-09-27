#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Görev atama otomasyonu: brif var → tetik gönder → pano güncelle (hepsi bir komut).

Kullanım:
  python scripts/gorev_atama_otomasyonu.py --task-id DASH-UX-02a --ajan utku

Kontrol:
  1. Brif dosyası var mı? (plans/brief_{ajan}_{task_id}.md)
  2. Panodan görev oku (task_board.json)
  3. Tetik gönder (trigger.tetik_ekle)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Yol düzelt
script_dir = Path(__file__).resolve().parent
huginn_dir = script_dir.parent  # "Huginn Data Insights"
_root = huginn_dir.parent  # "c:/Huginn Data Projesi"
# Module-level root attribute for test monkeypatching
root = _root
sys.path.insert(0, str(huginn_dir))

from src.company_master.orchestrator import trigger


def _get_root():
    """Get the root directory, checking for monkeypatched module.root first."""
    import sys
    possible_module_names = ["gorev_atama_otomasyonu", "gorev_atama_otomasyonu_test"]
    for module_name in possible_module_names:
        if module_name in sys.modules:
            module = sys.modules[module_name]
            if hasattr(module, 'root'):
                return module.root
    return _root


def brif_bul(task_id: str, ajan: str, gorev: dict | None = None) -> Path | None:
    """Brif dosyasını bul.

    Sıra: 1) panodaki `brief` alanı (zincir brifleri buraya düşer),
          2) uzlaşma yolu plans/brief_{ajan}_{task_id}.md
    """
    root = _get_root()
    if gorev and gorev.get("brief"):
        pano_brif = root / str(gorev["brief"])
        if pano_brif.exists():
            return pano_brif

    brif = root / "plans" / f"brief_{ajan}_{task_id}.md"
    return brif if brif.exists() else None


def gorev_oku(task_id: str, root_dir=None) -> dict | None:
    """task_board.json'dan görev oku (büyük/küçük harf duyarsız eşleşme)."""
    # Use root_dir if provided, otherwise use _get_root()
    if root_dir is not None:
        board_file = root_dir / "data" / "orchestrator" / "task_board.json"
    else:
        root = _get_root()
        board_file = root / "Huginn Data Insights" / "data" / "orchestrator" / "task_board.json"

    if not board_file.exists():
        return None

    board = json.loads(board_file.read_text(encoding="utf-8"))
    hedef = task_id.lower()
    for t in board:
        if str(t.get("task_id", "")).lower() == hedef or str(t.get("id", "")).lower() == hedef:
            return t
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--task-id", required=True, help="Görev ID'si (örn. DASH-UX-02a)")
    parser.add_argument("--ajan", required=True, help="Ajan adı (örn. utku)")
    parser.add_argument("--talimat", default="", help="Özel talimat (brif varsa yok sayılır)")

    args = parser.parse_args()
    ajan = args.ajan.lower()

    # 1. Görev var mı? (büyük/küçük harf duyarsız ara, panodaki gerçek yazımı kullan)
    root_dir = _get_root()
    gorev = gorev_oku(args.task_id, root_dir)

    if not gorev:
        print(f"[ERROR] Gorev bulunamadi: {args.task_id}")
        return 1
    task_id = gorev.get("task_id") or gorev.get("id")

    # 2. Brif var mı?
    brif = brif_bul(task_id, ajan, gorev)

    if not brif:
        print("[ERROR] Brif bulunamadi")
        print(f"        Beklenen: plans/brief_{ajan}_{task_id}.md")
        print(f"        veya panoda 'brief' alanı (şu an: {gorev.get('brief') or '-'})")
        return 1

    # 3. Talimat belirle
    talimat = args.talimat.strip()
    if not talimat:
        # Brif'ten ilk satırı al (başlık)
        brif_text = brif.read_text(encoding="utf-8")
        ilk_satir = brif_text.split("\n")[0]
        talimat = ilk_satir.replace("#", "").strip()
        if not talimat:
            talimat = f"Brif: {brif.relative_to(root_dir)}"

    # 4. Tetik gönder
    try:
        sonuc = trigger.tetik_ekle(task_id, ajan, talimat)
        print(f"[OK] Tetik gönderildi: {task_id} -> {ajan}")
        print(f"    Talimat: {talimat[:60]}...")
        print(f"    Brif: {brif.relative_to(root_dir)}")
        return 0
    except Exception as e:
        print(f"[ERROR] Tetik gönderilemedi: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
