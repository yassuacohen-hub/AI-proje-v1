"""AGENTS.md sonuna karar kaydi ekler (D-227: numarayı yalniz AGENTS.md sahiplenir).

Tek kullanimlik yazim araci. Idempotent: ayni baslik varsa eklemez.
Satir sonlari LF, dosya BOM'suz UTF-8 kalir.
"""

import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENTS = os.path.join(KOK, "AGENTS.md")
BASLIK = "## D-317"
GOVDE_DOSYA = os.path.join(KOK, "data", "_tmp", "d317_govde.md")


def main() -> int:
    with open(AGENTS, encoding="utf-8") as f:
        icerik = f.read()

    if BASLIK in icerik:
        print(f"[ATLANDI] {BASLIK} zaten AGENTS.md icinde")
        return 0

    with open(GOVDE_DOSYA, encoding="utf-8") as f:
        govde = f.read().rstrip("\n")

    if not icerik.endswith("\n"):
        icerik += "\n"
    icerik += "\n" + govde + "\n"

    with io.open(AGENTS, "w", encoding="utf-8", newline="\n") as f:
        f.write(icerik)

    print(f"[OK] {BASLIK} eklendi ({AGENTS})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
