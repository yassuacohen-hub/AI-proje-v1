# -*- coding: utf-8 -*-
"""Pazarlama servisi — Kampanya + Segment + Öneri.

Tablolar (Supabase/PostgreSQL):
  - campaigns: kampanya tanımları
  - segments: segment tanımları + kriterler
  - campaign_segments: kampanya-segment ilişkisi
  - segment_companies: segment-firma ilişkisi

Kullanim:
    from src.company_master.pazarlama import (
        kampanya_olustur, kampanya_getir, kampanya_liste,
        segment_olustur, segment_getir, segment_liste,
        kampanya_segment_ekle, segment_firma_ekle,
        ozet_rapor,
    )
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import text

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from company_master.db.connection import get_engine


# ---------------------------------------------------------------------------
# Kampanya CRUD
# ---------------------------------------------------------------------------

def kampanya_olustur(
    name: str,
    description: str = "",
    status: str = "draft",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    budget: Optional[float] = None,
) -> Dict[str, Any]:
    """Yeni bir kampanya olusturur."""
    engine = get_engine()
    sql = text("""
        INSERT INTO campaigns (name, description, status, start_date, end_date, budget)
        VALUES (:name, :description, :status, :start_date, :end_date, :budget)
        RETURNING campaign_id, name, description, status, start_date, end_date, budget, created_at
    """)
    with engine.connect() as conn:
        res = conn.execute(sql, {
            "name": name,
            "description": description,
            "status": status,
            "start_date": start_date,
            "end_date": end_date,
            "budget": budget,
        })
        row = res.mappings().first()
        conn.commit()
        if row:
            return _kampanya_row(row)
    return {}


def kampanya_getir(campaign_id: str) -> Optional[Dict[str, Any]]:
    """Kampanya ID ile getirir."""
    engine = get_engine()
    sql = text("SELECT * FROM campaigns WHERE campaign_id = :id")
    with engine.connect() as conn:
        res = conn.execute(sql, {"id": campaign_id})
        row = res.mappings().first()
        if row:
            return _kampanya_row(row)
    return None


def kampanya_guncelle(
    campaign_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    budget: Optional[float] = None,
) -> bool:
    """Kampanya guncelleri."""
    engine = get_engine()
    updates = []
    params: Dict[str, Any] = {"id": campaign_id}
    if name is not None:
        updates.append("name = :name"); params["name"] = name
    if description is not None:
        updates.append("description = :description"); params["description"] = description
    if status is not None:
        updates.append("status = :status"); params["status"] = status
    if start_date is not None:
        updates.append("start_date = :start_date"); params["start_date"] = start_date
    if end_date is not None:
        updates.append("end_date = :end_date"); params["end_date"] = end_date
    if budget is not None:
        updates.append("budget = :budget"); params["budget"] = budget
    if not updates:
        return False
    updates.append("updated_at = :updated_at")
    params["updated_at"] = datetime.now().isoformat(timespec="seconds")
    sql = text(f"UPDATE campaigns SET {', '.join(updates)} WHERE campaign_id = :id RETURNING campaign_id")
    with engine.connect() as conn:
        res = conn.execute(sql, params)
        conn.commit()
        return res.rowcount > 0


def kampanya_sil(campaign_id: str) -> bool:
    """Kampanya siler (segment ilişkileri ile birlikte)."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM campaign_segments WHERE campaign_id = :id"), {"id": campaign_id})
        res = conn.execute(text("DELETE FROM campaigns WHERE campaign_id = :id"), {"id": campaign_id})
        return res.rowcount > 0


def kampanya_liste(aktif_only: bool = False) -> List[Dict[str, Any]]:
    """Tum kampanyalari listeler."""
    engine = get_engine()
    if aktif_only:
        sql = text("SELECT * FROM campaigns WHERE status = 'active' ORDER BY name")
    else:
        sql = text("SELECT * FROM campaigns ORDER BY name")
    with engine.connect() as conn:
        res = conn.execute(sql)
        return [_kampanya_row(r) for r in res.mappings()]


# ---------------------------------------------------------------------------
# Segment CRUD
# ---------------------------------------------------------------------------

def segment_olustur(
    name: str,
    description: str = "",
    criteria: Optional[Dict[str, Any]] = None,
    is_active: bool = True,
) -> Dict[str, Any]:
    """Yeni bir segment olusturur."""
    engine = get_engine()
    criteria_json = json.dumps(criteria or {})
    sql = text("""
        INSERT INTO segments (name, description, criteria, is_active)
        VALUES (:name, :description, :criteria, :is_active)
        RETURNING segment_id, name, description, criteria, is_active, created_at, updated_at
    """)
    with engine.connect() as conn:
        res = conn.execute(sql, {
            "name": name,
            "description": description,
            "criteria": criteria_json,
            "is_active": is_active,
        })
        row = res.mappings().first()
        conn.commit()
        if row:
            return _segment_row(row)
    return {}


def segment_getir(segment_id: str) -> Optional[Dict[str, Any]]:
    """Segment ID ile getirir."""
    engine = get_engine()
    sql = text("SELECT * FROM segments WHERE segment_id = :id")
    with engine.connect() as conn:
        res = conn.execute(sql, {"id": segment_id})
        row = res.mappings().first()
        if row:
            return _segment_row(row)
    return None


def segment_guncelle(
    segment_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    criteria: Optional[Dict[str, Any]] = None,
    is_active: Optional[bool] = None,
) -> bool:
    """Segment guncelleri."""
    engine = get_engine()
    updates = []
    params: Dict[str, Any] = {"id": segment_id}
    if name is not None:
        updates.append("name = :name"); params["name"] = name
    if description is not None:
        updates.append("description = :description"); params["description"] = description
    if criteria is not None:
        updates.append("criteria = :criteria"); params["criteria"] = json.dumps(criteria)
    if is_active is not None:
        updates.append("is_active = :is_active"); params["is_active"] = is_active
    if not updates:
        return False
    updates.append("updated_at = :updated_at")
    params["updated_at"] = datetime.now().isoformat(timespec="seconds")
    sql = text(f"UPDATE segments SET {', '.join(updates)} WHERE segment_id = :id RETURNING segment_id")
    with engine.connect() as conn:
        res = conn.execute(sql, params)
        conn.commit()
        return res.rowcount > 0


def segment_liste(aktif_only: bool = True) -> List[Dict[str, Any]]:
    """Tum segmentleri listeler."""
    engine = get_engine()
    if aktif_only:
        sql = text("SELECT * FROM segments WHERE is_active = TRUE ORDER BY name")
    else:
        sql = text("SELECT * FROM segments ORDER BY name")
    with engine.connect() as conn:
        res = conn.execute(sql)
        return [_segment_row(r) for r in res.mappings()]


# ---------------------------------------------------------------------------
# İlişkiler
# ---------------------------------------------------------------------------

def kampanya_segment_ekle(campaign_id: str, segment_id: str) -> bool:
    """Kampanyaya segment ekler."""
    engine = get_engine()
    sql = text("""
        INSERT INTO campaign_segments (campaign_id, segment_id)
        VALUES (:campaign_id, :segment_id)
        ON CONFLICT DO NOTHING
    """)
    with engine.connect() as conn:
        res = conn.execute(sql, {"campaign_id": campaign_id, "segment_id": segment_id})
        conn.commit()
        return res.rowcount > 0


def kampanya_segmentleri_liste(campaign_id: str) -> List[Dict[str, Any]]:
    """Kampanyasin segmentlerini getirir."""
    engine = get_engine()
    sql = text("""
        SELECT s.segment_id, s.name, s.description, s.criteria
        FROM segments s
        JOIN campaign_segments cs ON s.segment_id = cs.segment_id
        WHERE cs.campaign_id = :campaign_id
    """)
    with engine.connect() as conn:
        res = conn.execute(sql, {"campaign_id": campaign_id})
        return [_segment_row(r) for r in res.mappings()]


def segment_firma_ekle(segment_id: str, company_id: str) -> bool:
    """Segmente firma ekler."""
    engine = get_engine()
    sql = text("""
        INSERT INTO segment_companies (segment_id, company_id, added_at)
        VALUES (:segment_id, :company_id, :added_at)
        ON CONFLICT DO NOTHING
    """)
    with engine.connect() as conn:
        res = conn.execute(sql, {
            "segment_id": segment_id,
            "company_id": company_id,
            "added_at": datetime.now().isoformat(timespec="seconds"),
        })
        conn.commit()
        return res.rowcount > 0


def segment_firmaları_liste(segment_id: str) -> List[Dict[str, Any]]:
    """Segment firmanlarini getirir."""
    engine = get_engine()
    sql = text("""
        SELECT c.company_id, c.legal_name, c.tax_number, sc.added_at
        FROM companies c
        JOIN segment_companies sc ON c.company_id = sc.company_id
        WHERE sc.segment_id = :segment_id
        ORDER BY c.legal_name
    """)
    with engine.connect() as conn:
        res = conn.execute(sql, {"segment_id": segment_id})
        return [
            {
                "company_id": str(r["company_id"]) if r.get("company_id") else None,
                "legal_name": r.get("legal_name", ""),
                "tax_number": r.get("tax_number", ""),
                "added_at": r.get("added_at"),
            }
            for r in res.mappings()
        ]


# ---------------------------------------------------------------------------
# Öneri / Rapor
# ---------------------------------------------------------------------------

def ozet_rapor() -> Dict[str, Any]:
    """Kampanya + segment ozet raporu."""
    engine = get_engine()
    kampanyalar = kampanya_liste(aktif_only=False)
    segmentler = segment_liste(aktif_only=False)
    return {
        "kampanya_sayisi": len(kampanyalar),
        "segment_sayisi": len(segmentler),
        "aktif_kampanyalar": len([k for k in kampanyalar if k.get("status") == "active"]),
        "aktif_segmentler": len([s for s in segmentler if s.get("is_active")]),
    }


# ---------------------------------------------------------------------------
# Yardimci
# ---------------------------------------------------------------------------

def _kampanya_row(row: Any) -> Dict[str, Any]:
    return {
        "campaign_id": str(row["campaign_id"]) if row.get("campaign_id") else None,
        "name": row.get("name", ""),
        "description": row.get("description", ""),
        "status": row.get("status", "draft"),
        "start_date": row.get("start_date"),
        "end_date": row.get("end_date"),
        "budget": float(row["budget"]) if row.get("budget") is not None else None,
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
    }


def _segment_row(row: Any) -> Dict[str, Any]:
    return {
        "segment_id": str(row["segment_id"]) if row.get("segment_id") else None,
        "name": row.get("name", ""),
        "description": row.get("description", ""),
        "criteria": row.get("criteria", "{}"),
        "is_active": bool(row.get("is_active", True)),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
    }
