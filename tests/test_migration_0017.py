# -*- coding: utf-8 -*-
"""Migration 0017: user_activity_log tablosu testleri (VERI-ADMIN-AKTIVITE-LOG-13).

Kapsam:
- 0017_user_activity_log.sql dosyasi mevcut ve uygun sema iceriyor
- Tablo ve indeksler olusturuluyor
- PK, FK, CHECK constraint'leri var
- ip_adresi ve ulke_kodu kolonlari NULL gecebiliyor
- Regresyon kapisi: kokte 0017*.down.sql yok (migrate.py glob("*.sql") recursive degil)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ------------------------------------------------------------------- migration file

def test_migration_0017_exists():
    """0017_user_activity_log.sql dosyasi mevcut."""
    assert (
        Path("src/company_master/schema/migrations/0017_user_activity_log.sql").exists()
    ), "0017_user_activity_log.sql bulunamadi"


def test_migration_0017_has_table():
    """Migration user_activity_log tablosunu olusturuyor."""
    sql = Path("src/company_master/schema/migrations/0017_user_activity_log.sql").read_text(
        encoding="utf-8"
    )
    assert "CREATE TABLE IF NOT EXISTS user_activity_log" in sql


def test_migration_0017_has_columns():
    """Migration gerekli tum kolonlari iceriyor."""
    sql = Path("src/company_master/schema/migrations/0017_user_activity_log.sql").read_text(
        encoding="utf-8"
    )
    # PK + FK + ana alanlar
    assert "id" in sql and "BIGSERIAL" in sql  # PK numarası artan
    assert "user_id" in sql and "UUID" in sql
    assert "REFERENCES users(user_id)" in sql
    assert "ON DELETE CASCADE" in sql
    # Olay bilgileri
    assert "olay_tipi" in sql
    assert "olay_zamani" in sql
    assert "TIMESTAMPTZ" in sql
    assert "DEFAULT NOW()" in sql
    # KVKK alanları
    assert "detay" in sql and "JSONB" in sql
    assert "basarili" in sql and "BOOLEAN" in sql
    assert "ip_adresi" in sql and "INET" in sql
    assert "ulke_kodu" in sql and "CHAR(2)" in sql


def test_migration_0017_has_check_constraint():
    """Migration olay_tipi icin CHECK constraint iceriyor."""
    sql = Path("src/company_master/schema/migrations/0017_user_activity_log.sql").read_text(
        encoding="utf-8"
    )
    assert "CHECK" in sql
    assert "olay_tipi" in sql
    assert "giris" in sql
    assert "arama" in sql
    assert "ai_kullanim" in sql


def test_migration_0017_has_indexes():
    """Migration iki indeks olusturuyor: user_zaman ve tip_zaman."""
    sql = Path("src/company_master/schema/migrations/0017_user_activity_log.sql").read_text(
        encoding="utf-8"
    )
    assert "idx_activity_user_zaman" in sql
    assert "user_id, olay_zamani DESC" in sql
    assert "idx_activity_tip_zaman" in sql
    assert "olay_tipi, olay_zamani DESC" in sql


def test_migration_0017_kvkk_nullable():
    """KVKK alanları (ip_adresi, ulke_kodu) NULL gecebiliyor."""
    sql = Path("src/company_master/schema/migrations/0017_user_activity_log.sql").read_text(
        encoding="utf-8"
    )
    lines = sql.split('\n')
    # ip_adresi satiri NULL'i icermeli
    ip_line = [l for l in lines if 'ip_adresi' in l and 'INET' in l]
    assert ip_line, "ip_adresi satiri bulunamadi"
    assert 'NULL' in ip_line[0], "ip_adresi NULL gecemeli"
    # ulke_kodu satiri NULL'i icermeli
    code_line = [l for l in lines if 'ulke_kodu' in l and 'CHAR' in l]
    assert code_line, "ulke_kodu satiri bulunamadi"
    assert 'NULL' in code_line[0], "ulke_kodu NULL gecemeli"


# ------------------------------------------------------------------- down file

# VERI-04 kanonik down yolu: `migrations/down/NNNN_ad.down.sql`.
# Bu dosya once `down/0017_user_activity_log.sql` (`.down` eki olmadan) ariyordu;
# o bicimde tek bir dosya bile yoktu.
DOWN_0017 = Path("src/company_master/schema/migrations/down/0017_user_activity_log.down.sql")


def test_migration_0017_down_exists():
    """0017_user_activity_log.down.sql dosyasi down/ alt dizininde mevcut."""
    assert DOWN_0017.exists(), f"{DOWN_0017} bulunamadi"


def test_migration_0017_down_drops_table():
    """Down dosyasi DROP TABLE iceriyor."""
    sql = DOWN_0017.read_text(encoding="utf-8")
    assert "DROP TABLE IF EXISTS user_activity_log" in sql


def test_migration_0017_down_drops_indexes():
    """Down dosyasi indeksleri dusuruyor."""
    sql = DOWN_0017.read_text(encoding="utf-8")
    assert "idx_activity_tip_zaman" in sql
    assert "idx_activity_user_zaman" in sql
    assert "DROP INDEX IF EXISTS" in sql


def test_migration_0017_surum_defteri_json():
    """Surum defteri `schema_versions.json`'dir, `schema_migrations` tablosu DEGIL.

    Eski hali down dosyasinda `DELETE FROM schema_migrations` ariyordu; boyle bir
    tablo projede hicbir yerde (SQL veya Python) tanimli degil. Gercek sozlesme:
    versiyon defteri JSON dosyasi ve 0017 girdisini iceriyor.
    """
    import json

    defter = Path("src/company_master/schema/migrations/schema_versions.json")
    veri = json.loads(defter.read_text(encoding="utf-8"))
    assert any(m["version"] == 17 for m in veri["migrations"]), "defterde 0017 girdisi yok"


# ------------------------------------------------------------------- regresyon kapisi

def test_migration_0017_no_root_down_file():
    """REGRESYON: Kokte 0017*.down.sql dosyasi YOKTUR.

    Down dosyalari up klasorunde durursa `migrations/*.sql` globlari onlari ileri
    migration sanar. Yeni migration'da down dosyasi MUTLAKA down/ altinda olmali.
    """
    migrations_dir = Path("src/company_master/schema/migrations")
    # Kok dizinde 0017 ile baslayan down dosyasi araştır
    root_down_files = list(migrations_dir.glob("0017*.down.sql"))
    assert (
        not root_down_files
    ), f"REGRESYON: Kokte 0017*.down.sql dosyasi bulundu, up globuna sikisacak: {root_down_files}"
    # Down dosyasi SADECE down/ alt dizininde olmali
    assert DOWN_0017.exists(), f"{DOWN_0017} yok, kok dizinde mi arandi?"


def test_schema_versions_json_updated():
    """schema_versions.json version 17 girisi iceriyor."""
    import json
    versions = json.loads(
        Path("src/company_master/schema/migrations/schema_versions.json").read_text(
            encoding="utf-8"
        )
    )
    assert versions["current_version"] >= 17, f"current_version 17 olmali, {versions['current_version']}"
    assert any(
        m["version"] == 17 and "0017_user_activity_log.sql" in m.get("file", "")
        for m in versions["migrations"]
    ), "schema_versions.json'da version 17 entry yok"
