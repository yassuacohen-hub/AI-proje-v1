# -*- coding: utf-8 -*-
"""`.env` içindeki ADMIN_EMAIL/ADMIN_PASSWORD çiftlerinin DB hash'iyle eşleşip eşleşmediğini
satır satır raporlar. Şifre değerleri asla yazdırılmaz. Çıkış: 0 en az bir eşleşme, 1 yok."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.admin_sifre_sifirla import verify_password  # noqa: E402


def main() -> int:
    from sqlalchemy import text

    from company_master.db import get_engine

    satirlar = (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines()
    ciftler: list[tuple[int, str, int, str]] = []
    em: tuple[int, str] | None = None
    for i, l in enumerate(satirlar, 1):
        if l.startswith("ADMIN_EMAIL="):
            em = (i, l.split("=", 1)[1].strip())
        elif l.startswith("ADMIN_PASSWORD=") and em:
            ciftler.append((em[0], em[1], i, l.split("=", 1)[1].strip()))
    with get_engine().connect() as c:
        rows = {r[0]: r[1] or "" for r in c.execute(text("SELECT email,password_hash FROM users WHERE role='admin'"))}
    eslesen = 0
    for el, e, pl, p in ciftler:
        ok = verify_password(p, rows.get(e, ""))
        eslesen += int(ok)
        print(f"satir {el}/{pl} {e}: DB kaydi={e in rows} eslesme={ok}")
    print(f"toplam cift={len(ciftler)} eslesen={eslesen}")
    return 0 if eslesen else 1


if __name__ == "__main__":
    raise SystemExit(main())
