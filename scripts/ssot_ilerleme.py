# -*- coding: utf-8 -*-
"""SSOT ilerleme ölçümü — vaat edilen her tablonun canlı satır sayısı (D-238).

Kalıcı araç: `docs/SSOT_ILERLEME_MATRISI.md`'nin sayım kolonunun TEK kaynağı.
Beyan yerine ölçüm; tablo yoksa "YOK" yazar, sıfır ile karıştırmaz (D-249).

Kullanım:
    python scripts/ssot_ilerleme.py            # tablo
    python scripts/ssot_ilerleme.py --json     # makine okunur
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text  # noqa: E402

from src.company_master.db.connection import get_engine  # noqa: E402

# faz -> (tablo, SSOT vaadi)
VAATLER: list[tuple[int, str, str]] = [
    (1, "companies", "firma kimligi"),
    (1, "entity_resolution", "kimlik eslestirme"),
    (1, "company_industries", "NACE / ne is yapar"),
    (1, "company_events", "yasal olaylar (TSG)"),
    (2, "company_intelligence_scores", "RISK MOTORU - 8 skor"),
    (2, "company_signals", "sinyal kaydi (risk+firsat)"),
    (2, "company_tech_profile", "siber guvenlik profili"),
    (2, "company_state", "guncel hal"),
    (2, "evidence", "kanit kaydi"),
    (2, "key_personnel", "sahiplik / yonetim"),
    (3, "company_locations", "ILISKI AGI - kumelenme yakiti"),
    (3, "momentum_snapshot", "ivme olcumu"),
    (4, "company_products", "ne uretiyor (firsat eslesmesi)"),
    (4, "company_capabilities", "atil kapasite"),
    (4, "job_postings", "ise alim sinyali"),
]


def say(conn, tablo: str) -> int | None:
    """Satır sayısı; tablo yoksa None (YOK ≠ 0 — D-249)."""
    var = conn.execute(
        text("SELECT to_regclass(:t) IS NOT NULL"), {"t": tablo}
    ).scalar()
    if not var:
        return None
    return conn.execute(text(f"SELECT count(*) FROM {tablo}")).scalar()


def olc() -> list[dict]:
    with get_engine().connect() as conn:
        return [
            {"faz": f, "tablo": t, "vaat": v, "sayim": say(conn, t)}
            for f, t, v in VAATLER
        ]


def _isaret(sayim: int | None) -> str:
    if sayim is None:
        return "TABLO YOK"
    if sayim == 0:
        return "BOS"
    return "DOLU"


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    satirlar = olc()

    if "--json" in argv:
        print(json.dumps(satirlar, ensure_ascii=False, indent=2))
        return 0

    print(f"{'Faz':<4}{'Tablo':<32}{'Sayim':>9}  Durum")
    print("-" * 62)
    for s in satirlar:
        sayi = "-" if s["sayim"] is None else f"{s['sayim']:,}".replace(",", ".")
        print(f"{s['faz']:<4}{s['tablo']:<32}{sayi:>9}  {_isaret(s['sayim'])}")

    bos = [s["tablo"] for s in satirlar if not s["sayim"]]
    print(f"\nBos/yok: {len(bos)} / {len(satirlar)}")
    if bos:
        print("  " + ", ".join(bos))
    return 0


# --- otonom watchdog: ölçüm aracının kendisi yalan söylemesin -----------------
def _kendi_kendini_dogrula() -> None:
    """Çağrısı olmayan kod yalan söyler (D-266): araç kendi kapısını test eder."""
    assert _isaret(None) == "TABLO YOK", "yokluk sifirla karistirildi (D-249)"
    assert _isaret(0) == "BOS"
    assert _isaret(5) == "DOLU"
    assert len({t for _, t, _ in VAATLER}) == len(VAATLER), "mukerrer tablo"
    with get_engine().connect() as conn:
        assert say(conn, "kesinlikle_olmayan_tablo_xyz") is None
        assert say(conn, "companies") is not None
    print("ssot_ilerleme ozdenetimi: GECTI")


if __name__ == "__main__":
    if "--ozdenetim" in sys.argv:
        _kendi_kendini_dogrula()
    else:
        raise SystemExit(main())
