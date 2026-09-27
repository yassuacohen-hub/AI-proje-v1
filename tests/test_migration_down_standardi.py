#!/usr/bin/env python3
"""VERI-04 MANDALI: migration down dosya adi/yol standardi.

Kanonik bicim: `schema/migrations/down/NNNN_ad.down.sql`
Gerekce: down dosyalari up klasorunde durursa `migrations/*.sql` globlari onlari
ileri migration sanar; ayrica testlerin `DOWN_DIR` beklentisi budur.
"""

from pathlib import Path

MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / "src" / "company_master" / "schema" / "migrations"
DOWN_DIR = MIGRATIONS_DIR / "down"


def _up_files() -> list[Path]:
    return [f for f in MIGRATIONS_DIR.glob("*.sql") if not f.name.endswith(".down.sql")]


def test_kokte_down_dosyasi_yok():
    """Up klasorunde hicbir `.down.sql` bulunmayacak."""
    kacaklar = sorted(f.name for f in MIGRATIONS_DIR.glob("*.down.sql"))
    assert kacaklar == [], f"down dosyalari `down/` altina tasinmali: {kacaklar}"


def test_her_up_icin_tam_bir_down():
    """Her `NNNN_ad.sql` icin `down/NNNN_ad.down.sql` tam 1 kez var olacak."""
    eksik = [f.name for f in _up_files() if not (DOWN_DIR / f"{f.stem}.down.sql").exists()]
    assert eksik == [], f"down karsiligi olmayan up migration'lar: {eksik}"


def test_down_dosya_adlari_kanonik():
    """`down/` altindaki her sql `.down.sql` ile bitecek ve bir up'a karsilik gelecek."""
    up_stems = {f.stem for f in _up_files()}
    for d in sorted(DOWN_DIR.glob("*.sql")):
        assert d.name.endswith(".down.sql"), f"{d.name} `.down.sql` ile bitmiyor"
        stem = d.name[: -len(".down.sql")]
        assert stem in up_stems, f"{d.name} icin up migration yok (sahipsiz down)"


if __name__ == "__main__":
    test_kokte_down_dosyasi_yok()
    test_her_up_icin_tam_bir_down()
    test_down_dosya_adlari_kanonik()
    print("[MANDAL] migration down standardi: PASSED")
