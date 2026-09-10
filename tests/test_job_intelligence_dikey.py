# -*- coding: utf-8 -*-
"""P7-GATE: Job Intelligence dikey akis dogrulama testleri.

Kapsam:
- prepare_job_record: firma eslestirme oneciligi, karantina, deterministic external_id
- Migration saglik kontrolu (gecersiz SQL kalintisi yok)
- DB erisimi varsa: gercek job_postings upsert dedup dogrulama (skip edilir yoksa)
"""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from company_master.intelligence.job_intelligence.pipeline.normalizer import (
    MatchResult,
    extract_domain,
)
from scripts.ingest_job_postings import _insert_batch, prepare_job_record

REPO_ROOT = ROOT
MIGRATION = REPO_ROOT / "src" / "company_master" / "db" / "migrations" / "0007_job_intelligence.sql"


class FakeMatcher:
    """DB bagimliligi olmadan eslestirme senaryolari icin sahte matcher."""

    def __init__(self, result: MatchResult) -> None:
        self.result = result
        self.calls: list[dict] = []

    def match(self, raw_name=None, domain=None, tax_number=None, mersis=None):
        self.calls.append(
            {"raw_name": raw_name, "domain": domain, "tax_number": tax_number, "mersis": mersis}
        )
        return self.result


CID = str(uuid.uuid4())


def _ok_matcher() -> FakeMatcher:
    return FakeMatcher(MatchResult(company_id=CID, matched_name="Acme A.S.", match_type="fuzzy", confidence=0.9))


# ---------------------------------------------------------------------------
# prepare_job_record
# ---------------------------------------------------------------------------

def test_prepare_firma_adi_onecikli_title_degil():
    """DATA-01: firma adı varken title eşleştirmeye gönderilmemeli."""
    m = _ok_matcher()
    record = {
        "company_name": "Acme A.S.",
        "title": "Senior Python Developer ilanı başlığı",
        "source_url": "https://kariyer.net/acme/ilan/123",
    }
    prepared = prepare_job_record(record, m, "kariyer-net")
    assert prepared is not None
    assert m.calls[0]["raw_name"] == "Acme A.S."
    assert prepared["company_id"] == CID
    assert prepared["title"].startswith("Senior Python")


def test_prepare_title_geri_donus_olarak_kullanilir():
    """Firma adı hiç yoksa title denenir (geri dönüş); ama company_name öncelikli."""
    m = _ok_matcher()
    record = {"title": "Acme Yazilim", "source_url": "https://x.com/a"}
    prepared = prepare_job_record(record, m, "kariyer-net")
    assert prepared is not None
    assert m.calls[0]["raw_name"] == "Acme Yazilim"


def test_eslesme_yoksa_none_donuyor():
    m = FakeMatcher(MatchResult(company_id=None))
    record = {"company_name": "Bilinmeyen Ltd", "title": "X"}
    assert prepare_job_record(record, m, "iskur") is None


def test_auto_external_id_deterministik_ve_farklilasan():
    """Aynı içerik → aynı external_id; farklı başlık → farklı id (dedup çalışır)."""
    m = _ok_matcher()
    record = {
        "company_name": "Acme A.S.",
        "title": "Backend Engineer",
        "source_url": "https://acme.com/careers/j1",
        "description": "Python + FastAPI",
    }
    p1 = prepare_job_record(record, m, "company-career")
    p2 = prepare_job_record(dict(record), m, "company-career")
    assert p1["external_id"] == p2["external_id"]
    assert p1["external_id"].startswith("auto:")
    assert p1["content_hash"] == p2["content_hash"]

    p3 = prepare_job_record(dict(record, title="Frontend Developer"), m, "company-career")
    assert p3 is not None
    assert p1["external_id"] != p3["external_id"]


def test_dis_company_id_yalniz_kendi_kaynagimizda_kabul():
    """raw_data.company_id yalnızca company-career-pages kaynağında güvenilir."""
    raw_id = str(uuid.uuid4())
    m_no = FakeMatcher(MatchResult(company_id=None))
    rec = {"title": "Muhasebeci", "raw_data": {"company_id": raw_id}}

    # Başka kaynakta keyfi company_id kabul edilmez
    assert prepare_job_record(rec, m_no, "iskur") is None
    # Kendi kaynağımızda UUID ise kabul edilir
    prepared = prepare_job_record(rec, m_no, "company-career-pages")
    assert prepared is not None
    assert prepared["company_id"] == raw_id


def test_dis_company_id_gecersiz_format_karantina():
    m_no = FakeMatcher(MatchResult(company_id=None))
    rec = {"title": "X", "raw_data": {"company_id": "bu-bir-uuid-degil"}}
    assert prepare_job_record(rec, m_no, "company-career-pages") is None


def test_extract_domain_portal_url():
    assert extract_domain("https://www.kariyer.net/firma/acme") == "kariyer.net"
    assert extract_domain(None) is None


# ---------------------------------------------------------------------------
# Migration saglik
# ---------------------------------------------------------------------------

def test_migration_gecersiz_sql_kalintisi_yok():
    """P7-GATE: DROP TRIGGER IF NOT EXISTS gecersizdir; tekrar oluşmamalı."""
    sql = MIGRATION.read_text(encoding="utf-8-sig")
    assert "DROP TRIGGER IF NOT EXISTS" not in sql
    assert "CREATE TABLE IF NOT EXISTS job_postings" in sql
    assert "UNIQUE(source_name, external_id)" in sql


# ---------------------------------------------------------------------------
# DB erisimi varsa gercek dedup dogrulama (yoksa skip)
# ---------------------------------------------------------------------------

def _db_available() -> bool:
    if not os.getenv("DATABASE_URL") and not (REPO_ROOT / ".env").exists():
        return False
    try:
        from company_master.db.connection import get_engine

        with get_engine().connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _db_available(), reason="DATABASE_URL erisimi yok; dikey DB testi atlandi")
def test_insert_batch_dedup_gercek_db():
    from company_master.db.connection import get_engine
    from sqlalchemy import text as sa_text

    test_source = f"dikey-test-{uuid.uuid4().hex[:8]}"
    engine = get_engine()
    try:
        # Gecici sirket (FK icin)
        with engine.begin() as conn:
            cid = conn.execute(
                sa_text("INSERT INTO companies (legal_name) VALUES (:n) RETURNING company_id"),
                {"n": f"Dikey Test A.S. {test_source}"},
            ).scalar_one()

        record = {
            "company_id": str(cid),
            "source_name": test_source,
            "source_url": "https://example.com/job/1",
            "external_id": f"auto-dikey-{uuid.uuid4().hex[:8]}",
            "title": "Dikey Test Ilani",
            "description": None,
            "department": None,
            "seniority_level": None,
            "location_city": None,
            "location_country": "Türkiye",
            "employment_type": None,
            "remote_type": None,
            "technologies": "[]",
            "salary_min": None,
            "salary_max": None,
            "salary_currency": "TRY",
            "posted_at": None,
            "expired_at": None,
            "collected_at": None,
            "content_hash": "testhash",
            "raw_data": "{}",
        }
        with engine.begin() as conn:
            ins1, dup1 = _insert_batch(conn, [record])
            ins2, dup2 = _insert_batch(conn, [dict(record)])
        assert ins1 == 1 and dup1 == 0
        assert ins2 == 0 and dup2 == 1
    finally:
        with engine.begin() as conn:
            conn.execute(
                sa_text("DELETE FROM job_postings WHERE source_name = :s"),
                {"s": test_source},
            )
            conn.execute(
                sa_text("DELETE FROM companies WHERE legal_name LIKE :p"),
                {"p": f"Dikey Test A.S. {test_source}%"},
            )
