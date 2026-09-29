"""KAPALI göç yolunun mandalı (D-266, D-271).

Bu dosya eskiden `src/company_master/db/migrate.py`'nin `MIGRATIONS_DIR` ve
`_split_statements` API'sini test ediyordu. O yol bu turda **düşürüldü**
(çağıranı yoktu, ikinci defter doğuruyordu, şemayı nitelendirmiyordu).

Test de bir beyandır (D-258/7): düşen kodun testi silinmez, kapalılığı
bekçileyen mandala çevrilir. Aksi halde takım toplama anında ölür —
bu dosya tam olarak bunu yaptı: `AttributeError: MIGRATIONS_DIR`.

Göç dosyalarının kendi doğrulaması kanonik dizinde yapılır:
`tests/test_goc_defteri.py`.

Tek başına da koşar: python tests/company_master/test_migrate.py
"""

import sys
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KOK))

from src.company_master.db import migrate  # noqa: E402

# Kanonik göç dizini — `scripts/goc_defteri.py::GOC_DIZINI` ile aynı yol.
KANONIK = KOK / "src/company_master/schema/migrations"


def test_kapali_yol_yazmaya_kalkmaz() -> None:
    """D-266: düşürülen yol sessizce çalışmaz, yüksek sesle reddeder."""
    with pytest.raises(RuntimeError, match="KAPALI"):
        migrate.apply_migrations()
    assert migrate.main() == 2, "kapalı yol sıfır dönerse CI onu başarı sanar"


def test_kapali_yol_api_geri_gelmiyor() -> None:
    """D-271 mandalı: bu adlar geri gelirse ikinci defter de geri gelir.

    `MIGRATIONS_DIR` kendi dizinini, `_split_statements` kendi uygulayıcısını
    ima eder; ikisi birlikte `goc_defteri.py`'nin yanında ikinci bir kapı
    kurar (D-265: üç defter tutan sistem hiçbirine güvenemez).
    """
    for ad in ("MIGRATIONS_DIR", "_split_statements", "_ensure_table"):
        assert not hasattr(migrate, ad), (
            f"migrate.{ad} geri gelmiş — kapalı yol yeniden açılıyor.\n"
            "Göç tek kapıdan geçer: python scripts/goc_defteri.py --uygula <x.sql>"
        )


def test_tek_goc_dizini_var() -> None:
    """D-211/D-230: göç dosyaları tek dizinde durur, kopyası olmaz.

    Ölçüm (2026-09-28): `db/migrations/0007_job_intelligence.sql` ve
    `db/schema/migrations/0013_job_intelligence.sql` yetim kopyalardı —
    kanonik dosyadan byte olarak FARKLI (11252 / 11256 / 11518) ve hiçbir
    kod onlara bakmıyordu. Tabloları canlıda var, ama defterdeki kayıt
    kanonik `0013`e ait. Kopyalar silindi; bu mandal geri gelmelerini durdurur.
    """
    assert KANONIK.is_dir(), f"kanonik göç dizini yok: {KANONIK}"
    yetim = [
        p
        for p in (KOK / "src/company_master/db").rglob("*.sql")
        if "migrations" in p.parts
    ]
    assert not yetim, (
        "`db/` altında göç dosyası var — kanonik dizin "
        "`src/company_master/schema/migrations`:\n"
        + "\n".join(str(p.relative_to(KOK)) for p in yetim)
    )


def test_kanonik_dizin_numarali_ve_dolu() -> None:
    """Eski `test_migration_dosyalari_sirali_ve_numarali` — doğru dizinde."""
    import re

    dosyalar = sorted(KANONIK.glob("*.sql"))
    assert len(dosyalar) >= 4, f"en az 4 göç bekleniyor, {len(dosyalar)} var"
    for f in dosyalar:
        assert re.match(r"^\d{4}_.+\.sql$", f.name), f"geçersiz ad: {f.name}"


def test_core_tablolari_tanimli() -> None:
    """0001 çekirdek tabloları içerir (eski testin kanonik dizindeki hâli)."""
    sql = (KANONIK / "0001_core.sql").read_text(encoding="utf-8")
    for tablo in ("companies", "osbs", "sources", "source_records", "quarantine_firms"):
        assert f"CREATE TABLE IF NOT EXISTS {tablo}" in sql, f"{tablo} eksik"


if __name__ == "__main__":
    print(f"kanonik göç dosyası: {len(list(KANONIK.glob('*.sql')))}")
    test_kapali_yol_yazmaya_kalkmaz()
    test_kapali_yol_api_geri_gelmiyor()
    test_tek_goc_dizini_var()
    test_kanonik_dizin_numarali_ve_dolu()
    test_core_tablolari_tanimli()
    print("hepsi geçti")
