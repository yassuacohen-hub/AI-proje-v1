"""Cakisma isaretlerini siler, iki tarafi da tutar (append-only dosyalar: chat jsonl + bulgu defteri)."""
import sys

MARK = ("<<<<<<< ", "=======", ">>>>>>> ")
for yol in sys.argv[1:]:
    with open(yol, "r", encoding="utf-8", newline="") as f:
        satirlar = f.read().splitlines(keepends=True)
    cikti = [s for s in satirlar if not s.rstrip("\r\n").startswith(MARK) or s.rstrip("\r\n") not in
             [m for m in ("=======",)] and not s.startswith(("<<<<<<< ", ">>>>>>> "))]
    cikti = [s for s in satirlar
             if not (s.startswith(("<<<<<<< ", ">>>>>>> ")) or s.rstrip("\r\n") == "=======")]
    with open(yol, "w", encoding="utf-8", newline="") as f:
        f.writelines(cikti)
    print(yol, len(satirlar) - len(cikti), "isaret silindi")
