# -*- coding: utf-8 -*-
"""GOC-DEFTER-01 mandali: defter ile sema ortusuyor mu? (gecici betik)

Uc soru:
  1. Diskteki her goc dosyasi defterde kayitli mi?
  2. 0025'in acmasi gereken kolonlar gercekten var mi?
  3. `mersis_no` ikizi dogmus mu? (dogmamali)
"""
import sys
from pathlib import Path

from sqlalchemy import text

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "src"))
from company_master.db.connection import get_engine  # noqa: E402

GOC_DIZINI = KOK / "src" / "company_master" / "schema" / "migrations"
BEKLENEN = ["vergi_dairesi", "ticaret_sicil_no", "sicil_dairesi",
            "kimlik_tamligi", "puan_surumu", "mersis_number"]


def main() -> None:
    diskte = {p.name for p in GOC_DIZINI.glob("*.sql")}
    with get_engine().connect() as c:
        defterde = {r[0] for r in c.execute(text(
            "SELECT filename FROM schema_migrations"))}
        kolonlar = {r[0] for r in c.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='companies'"))}

    eksik_defter = diskte - defterde
    print(f"diskte {len(diskte)} goc / defterde {len(defterde)} kayit")
    assert not eksik_defter, f"DEFTER EKSIK: {sorted(eksik_defter)}"

    eksik_kolon = [k for k in BEKLENEN if k not in kolonlar]
    assert not eksik_kolon, f"KOLON YOK: {eksik_kolon}"
    print(f"0025 kolonlari tamam: {', '.join(BEKLENEN)}")

    # D-251/2: mersis_no ikizi dogmamali.
    assert "mersis_no" not in kolonlar, \
        "IKIZ DOGDU: companies.mersis_no var; mersis_number kullanilmaliydi."
    print("ikiz yok: mersis_no acilmamis, mersis_number tek kaynak")
    print("\nMANDAL YESIL")


if __name__ == "__main__":
    main()
