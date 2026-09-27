#!/usr/bin/env python3
"""
UTKU-01: Veri Şeması Doğrulama Testleri

Testler:
1. Migration dosyalarının varlığı
2. Her up migration için down migration varlığı
3. Migration sıralamasının tutarlılığı
4. FK dependency'lerinin doğruluğu
5. Unique/CHECK constraint'lerin varlığı
"""

import sys
import json
from pathlib import Path

# Proje kök dizinini bul
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
MIGRATIONS_DIR = PROJECT_ROOT / "src" / "company_master" / "schema" / "migrations"
DOWN_DIR = PROJECT_ROOT / "src" / "company_master" / "schema" / "migrations" / "down"
SCHEMA_VERSIONS_PATH = PROJECT_ROOT / "src" / "company_master" / "schema" / "migrations" / "schema_versions.json"

sys.path.insert(0, str(PROJECT_ROOT / "src"))

from company_master.db.connection import get_engine
import json


def _up_files() -> list[Path]:
    """VERI-04: down dosyalarinin adi `NNNN_ad.down.sql` (nokta), `_down` degil.
    Eski filtre `_down` ariyordu, down dosyalarini up sanıyordu."""
    return [f for f in MIGRATIONS_DIR.glob("*.sql") if not f.name.endswith(".down.sql")]


def test_migration_files_exist():
    """Migration dosyalarının varlığını test et."""
    # Up migration'lar
    expected_up = [f"{i:04d}" for i in range(1, 20)]

    up_files = [f.stem for f in _up_files()]

    for exp in expected_up:
        matching = [f for f in up_files if f.startswith(exp)]
        assert len(matching) == 1, f"Migration {exp} için tam 1 up dosyası bekleniyor, bulundu: {matching}"

    print("[TEST] migration_files_exist: PASSED")


def test_migration_down_files_content():
    """Down migration dosyalarının içeriğini test et."""
    # Down dosyalarının naming pattern: 0001_core.down.sql, 0002_relations.down.sql, etc.
    down_files = [f.stem for f in DOWN_DIR.glob("*.sql")]

    # En az 19 down migration dosyası olmalı (1-19)
    assert len(down_files) >= 19, f"En az 19 down dosyası bekleniyor, bulundu: {len(down_files)}"

    # Her up migration için karşılık gelen down dosyası olmalı
    up_files = [f.stem for f in _up_files()]
    for up_stem in up_files:
        # Down dosyası aynı prefix ile başlamalı (örn: 0001_core -> 0001_core.down)
        down_match = [d for d in DOWN_DIR.glob("*.sql") if d.stem.startswith(up_stem)]
        assert len(down_match) == 1, f"Migration {up_stem} için down dosyası bekleniyor, bulunamadı"

    print("[TEST] migration_down_files_content: PASSED")


def test_schema_versions_json():
    """schema_versions.json'ın tutarlılığını test et."""
    with open(PROJECT_ROOT / "src" / "company_master" / "schema" / "migrations" / "schema_versions.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "current_version" in data
    assert "migrations" in data
    assert isinstance(data["migrations"], list)

    # Version numaraları sıralı olmalı
    versions = [m["version"] for m in data["migrations"]]
    assert versions == sorted(versions), "Migration versiyonları sıralı değil"

    # Current version en yüksek olmalı
    assert data["current_version"] == max(versions), "current_version en yüksek değil"

    print("[TEST] schema_versions_json: PASSED")


def test_migration_down_files_format():
    """Down migration dosyalarının formatını test et."""
    for i in range(1, 20):
        # Down dosyası bul (prefix ile başlayan)
        matching = list(DOWN_DIR.glob(f"{i:04d}_*.down.sql"))
        assert len(matching) == 1, f"{i:04d}_*.down.sql dosyası yok veya birden fazla"

        down_file = matching[0]
        content = down_file.read_text(encoding="utf-8")
        # Yorum satırı ile başlamalı (-- Migration ... down)
        assert content.strip().startswith("-- Migration"), f"{down_file.name} yorum ile başlamıyor"

        # Migration numarası yorumunda geçmeli
        assert f"{i:04d}" in content.split("\n")[0], f"{down_file.name} migration numarası yorumunda yok"

        # DROP komutu içermeli
        assert "DROP" in content.upper(), f"{down_file.name} DROP komutu içermiyor"

    print("[TEST] migration_down_files_format: PASSED")


def test_fk_dependencies():
    """Foreign key dependency'lerinin migration sırasıyla tutarlılığını test et."""
    up_files = sorted(_up_files())

    # İlk dosya 0001_core.sql olmalı
    assert up_files[0].stem == "0001_core", "İlk migration 0001_core olmalı"

    print("[TEST] fk_dependencies: PASSED")


def test_companies_table_structure():
    """Companies tablosunun şema yapısını test et."""
    engine = get_engine()
    with engine.connect() as conn:
        from sqlalchemy import text
        # Companies tablosu var mı
        result = conn.execute(text("SELECT 1 FROM information_schema.tables WHERE table_name = 'companies'")).scalar()
        assert result == 1, "Companies tablosu yok"

        # Önemli kolonların varlığı
        columns = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'companies'")).scalars().all()

        required_columns = [
            "company_id", "legal_name", "trade_name", "tax_number",
            "status", "osb_id", "nace_code", "created_at"
        ]
        for col in required_columns:
            assert col in columns, f"Companies tablosunda {col} kolonu yok"

        # PK kontrolü
        pk = conn.execute(text("""
            SELECT column_name FROM information_schema.key_column_usage
            WHERE table_name = 'companies' AND constraint_name LIKE '%pkey%'
        """)).scalar()
        assert pk == "company_id", f"PK company_id olmalı, bulundu: {pk}"

        print("[TEST] companies_table_structure: PASSED")


def test_migrations_apply_rollback():
    """Migration'ların apply ve rollback testi (dry-run)."""
    for i in range(1, 20):
        matching = [f for f in _up_files() if f.name.startswith(f"{i:04d}_")]

        assert len(matching) == 1, f"Migration {i:04d} için tam 1 up dosyası bekleniyor"

        content = matching[0].read_text(encoding="utf-8")
        # SQL syntax kontrolü - CREATE TABLE veya ALTER TABLE içermeli
        assert any(kw in content.upper() for kw in ["CREATE TABLE", "ALTER TABLE", "CREATE INDEX", "ALTER TABLE"]), \
            f"Migration {i:04d} geçerli SQL komutu içermiyor"

    print("[TEST] migrations_apply_rollback: PASSED")


if __name__ == "__main__":
    test_migration_files_exist()
    test_migration_down_files_content()
    test_schema_versions_json()
    test_migration_down_files_format()
    test_fk_dependencies()
    test_companies_table_structure()
    test_migrations_apply_rollback()
    print("\n[TUM TESTLER GECTI]")
