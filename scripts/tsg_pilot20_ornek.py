# -*- coding: utf-8 -*-
"""TSG-PILOT-20 — ornek secimi (D-306).

Brif: plans/brief_yasu_TSG-PILOT-20.md
Kural: `ORDER BY random() LIMIT 20`. Tanidik/kolay firma SECILMEZ.
Secilen 20 `company_id` rapora AYnen yazilir (tekrar uretilebilirlik).
Bu bir SCRIPT'tir: hicbir sey yazmaz, sadece okur ve rapor uretir.
"""
from __future__ import annotations

import json
import pathlib
import sys

KOK = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

SQL = """
SELECT company_id::text, legal_name, trade_registry_number
FROM companies
WHERE trade_registry_number IS NOT NULL AND trade_registry_number <> ''
  AND status IS DISTINCT FROM 'pasif'
ORDER BY random() LIMIT 20;
"""


def main() -> None:
    import psycopg
    from dotenv import load_dotenv
    load_dotenv(KOK / ".env", override=True)
    import os
    dsn = os.environ["DATABASE_URL"]

    with psycopg.connect(dsn) as cx:
        with cx.cursor() as cur:
            cur.execute(SQL)
            satirlar = cur.fetchall()

    print(f"Secilen firma: {len(satirlar)}")
    ornek = []
    for i, (cid, ad, sicil) in enumerate(satirlar, 1):
        print(f"  {i:2d}. {cid[:8]}  {sicil:<12s} {(ad or '')[:46]}")
        ornek.append({"sira": i, "company_id": cid,
                      "legal_name": ad, "trade_registry_number": sicil})

    cikti = KOK / "data" / "pilots" / "TSG-PILOT-20"
    cikti.mkdir(parents=True, exist_ok=True)
    (cikti / "ornek.json").write_text(
        json.dumps(ornek, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\ncikti: {cikti / 'ornek.json'}")


if __name__ == "__main__":
    main()
