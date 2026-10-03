# -*- coding: utf-8 -*-
"""Paketler servisi — Paket CRUD + Firma-Paket ilişkisi.

Tablolar (Supabase/PostgreSQL):
  - packages: paket tanımları (isim, fiyat, özellikler)
  - company_packages: firma-paket atama (firma_id, paket_id, atama_tarihi, durum)

Kullanim:
    from src.company_master.paketler import (
        paket_olustur, paket_getir, paket_guncelle, paket_liste,
        firma_paket_ata, firma_paket_cikar, firma_paketleri_getir,
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
# Package CRUD
# ---------------------------------------------------------------------------

def paket_olustur(
    name: str,
    description: str = "",
    price: Optional[float] = None,
    features: Optional[List[str]] = None,
    icon: str = "",
) -> Dict[str, Any]:
    """Yeni bir paket olusturur."""
    engine = get_engine()
    features_json = json.dumps(features or []) if features else "[]"
    sql = text("""
        INSERT INTO packages (name, description, price, features, icon)
        VALUES (:name, :description, :price, :features, :icon)
        RETURNING package_id, name, description, price, features, icon, created_at
    """)
    with engine.connect() as conn:
        res = conn.execute(sql, {
            "name": name,
            "description": description,
            "price": price,
            "features": features_json,
            "icon": icon,
        })
        row = res.mappings().first()
        conn.commit()
        if row:
            return _paket_row(row)
    return {}


def paket_getir(package_id: str) -> Optional[Dict[str, Any]]:
    """Paket ID ile getirir."""
    engine = get_engine()
    sql = text("SELECT * FROM packages WHERE package_id = :id")
    with engine.connect() as conn:
        res = conn.execute(sql, {"id": package_id})
        row = res.mappings().first()
        if row:
            return _paket_row(row)
    return None


def paket_guncelle(
    package_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    price: Optional[float] = None,
    features: Optional[List[str]] = None,
    icon: Optional[str] = None,
) -> bool:
    """Paket guncelleri."""
    engine = get_engine()
    updates = []
    params: Dict[str, Any] = {"id": package_id}
    if name is not None:
        updates.append("name = :name")
        params["name"] = name
    if description is not None:
        updates.append("description = :description")
        params["description"] = description
    if price is not None:
        updates.append("price = :price")
        params["price"] = price
    if features is not None:
        updates.append("features = :features")
        params["features"] = json.dumps(features)
    if icon is not None:
        updates.append("icon = :icon")
        params["icon"] = icon
    if not updates:
        return False
    params["updated_at"] = datetime.now().isoformat(timespec="seconds")
    updates.append("updated_at = :updated_at")
    sql = text(f"UPDATE packages SET {', '.join(updates)} WHERE package_id = :id RETURNING package_id")
    with engine.connect() as conn:
        res = conn.execute(sql, params)
        conn.commit()
        return res.rowcount > 0


def paket_sil(package_id: str) -> bool:
    """Paket siler (firma atamalari ile birlikte)."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM company_packages WHERE package_id = :id"), {"id": package_id})
        res = conn.execute(text("DELETE FROM packages WHERE package_id = :id"), {"id": package_id})
        return res.rowcount > 0


def paket_liste(aktif_only: bool = True) -> List[Dict[str, Any]]:
    """Tum paketleri listeler."""
    engine = get_engine()
    if aktif_only:
        sql = text("SELECT * FROM packages WHERE is_active = TRUE ORDER BY name")
    else:
        sql = text("SELECT * FROM packages ORDER BY name")
    with engine.connect() as conn:
        res = conn.execute(sql)
        return [_paket_row(r) for r in res.mappings()]


# ---------------------------------------------------------------------------
# Firma-Paket
# ---------------------------------------------------------------------------

def firma_paket_ata(company_id: str, package_id: str) -> Dict[str, Any]:
    """Firma'ya paket atar."""
    engine = get_engine()
    sql = text("""
        INSERT INTO company_packages (company_id, package_id, assigned_at, status)
        VALUES (:company_id, :package_id, :assigned_at, 'active')
        ON CONFLICT (company_id, package_id) DO UPDATE SET status = 'active'
        RETURNING id, company_id, package_id, assigned_at, status
    """)
    with engine.connect() as conn:
        res = conn.execute(sql, {
            "company_id": company_id,
            "package_id": package_id,
            "assigned_at": datetime.now().isoformat(timespec="seconds"),
        })
        conn.commit()
        row = res.mappings().first()
        if row:
            return _firma_paket_row(row)
    return {}


def firma_paket_cikar(company_id: str, package_id: str) -> bool:
    """Firma'dan paketi cikarir."""
    engine = get_engine()
    sql = text("DELETE FROM company_packages WHERE company_id = :cid AND package_id = :pid")
    with engine.connect() as conn:
        res = conn.execute(sql, {"cid": company_id, "pid": package_id})
        conn.commit()
        return res.rowcount > 0


def firma_paketleri_getir(company_id: str) -> List[Dict[str, Any]]:
    """Firma'nın tum paketlerini getirir."""
    engine = get_engine()
    sql = text("""
        SELECT cp.id, cp.company_id, p.package_id, p.name, p.price, p.icon,
               cp.assigned_at, cp.status
        FROM company_packages cp
        JOIN packages p ON cp.package_id = p.package_id
        WHERE cp.company_id = :company_id AND cp.status = 'active'
        ORDER BY p.name
    """)
    with engine.connect() as conn:
        res = conn.execute(sql, {"company_id": company_id})
        return [_firma_paket_row(r) for r in res.mappings()]


def kampanya_paketleri_getir(campaign_id: str) -> List[Dict[str, Any]]:
    """Kampanyaya atanmis paketleri getirir."""
    engine = get_engine()
    sql = text("""
        SELECT p.package_id, p.name, p.price, p.icon
        FROM packages p
        JOIN campaign_packages cp ON p.package_id = cp.package_id
        WHERE cp.campaign_id = :campaign_id
        ORDER BY p.name
    """)
    with engine.connect() as conn:
        res = conn.execute(sql, {"campaign_id": campaign_id})
        return [_paket_row(r) for r in res.mappings()]


# ---------------------------------------------------------------------------
# Tek Fiyat Kaynağı — Müşteri Paneli & Kampanya Hedefleme (PO-BACK-04)
# ---------------------------------------------------------------------------

# PO-BACK-04: Orjinal fiyatlar (SSOT) — demo çakışması giderildi
_ORJINAL_FIYATLAR: dict[str, float] = {
    "Temel": 499.0,
    "Standart": 2999.0,
    "Profesyonel": 7999.0,
    "Kurumsal": 19999.0,
}

_ORJINAL_OZELLIKLER: dict[str, list[str]] = {
    "Temel": ["3 kullanıcı", "5GB depolama", "API 500 işlem/gün"],
    "Standart": ["25 kullanıcı", "100GB depolama", "API 50.000 işlem/gün", "Raporlama"],
    "Profesyonel": ["100 kullanıcı", "1TB depolama", "API 500.000 işlem/gün", "Raporlama", "API analitiği", "Özel destek"],
    "Kurumsal": ["Sınırsız kullanıcı", "Sınırsız depolama", "Sınırsız API", "SLA 99.9", "Özel güncelleme", "Öncelikli destek"],
}

_ORJINAL_SIRALAMA = ["Temel", "Standart", "Profesyonel", "Kurumsal"]

# Paket → Mimir-DIŞ haber kaynakları (PAKET_KOTA_TASARIMI §4). Üst paket alttakini kapsar.
# ponytail: sabit sözlük; packages.features JSON'a taşınır ilk müşteri paket değiştirince.
VARSAYILAN_KAYNAKLAR: tuple[str, ...] = ("dmo", "rg")
PAKET_KAYNAKLARI: dict[str, tuple[str, ...]] = {
    "Temel": VARSAYILAN_KAYNAKLAR,
    "Standart": VARSAYILAN_KAYNAKLAR + ("google_news", "linkedin", "patent"),
    "Profesyonel": VARSAYILAN_KAYNAKLAR + ("google_news", "linkedin", "patent", "instagram", "facebook", "is_ilani"),
    "Kurumsal": VARSAYILAN_KAYNAKLAR + ("google_news", "linkedin", "patent", "instagram", "facebook", "is_ilani"),
}


def paket_kaynaklari(paket_adlari: list[str] | tuple[str, ...]) -> frozenset[str]:
    """Paket adlarının izin verdiği kaynakların birleşimi; paket yoksa VARSAYILAN_KAYNAKLAR.

    Bilinmeyen paket adı sessizce yok sayılır (kapı kapalı kalır, açılmaz).
    """
    izinli: set[str] = set()
    for ad in paket_adlari:
        izinli.update(PAKET_KAYNAKLARI.get(ad, ()))
    return frozenset(izinli or VARSAYILAN_KAYNAKLAR)


def firma_haber_kaynaklari(company_id: str) -> frozenset[str]:
    """BORC-PLAN-ALANI-01 kapısı: firmanın aktif paketlerinden kaynak kümesi (DB okur)."""
    return paket_kaynaklari([p["name"] for p in firma_paketleri_getir(company_id)])


def fiyat_katalogu() -> list[dict[str, Any]]:
    """
    Müşteri paneli, kampanya hedefleme ve fatura pipeline'i için
    **tek güvenilir fiyat kaynağı** (SSOT).

    Dönüş: isim sırasına göre (Temel→Kurumsal) sabit 4 tier listesi.
    DB'deki `packages` tablosundaki price/features alanları bu fonksiyon
    ile **eşzamanlı** güncellenmelidir (bakım betiği: `scripts/sync_paket_fiyatlari.py`).
    """
    katalog = []
    for isim in _ORJINAL_SIRALAMA:
        katalog.append({
            "name": isim,
            "price": _ORJINAL_FIYATLAR[isim],
            "features": _ORJINAL_OZELLIKLER[isim],
            "icon": {"Temel": "fa-tag", "Standart": "fa-box", "Profesyonel": "fa-shield", "Kurumsal": "fa-building"}[isim],
            "description": {
                "Temel": "Küçük firmalar için giriş paketi",
                "Standart": "Orta ölçekli firmalar için standart paket",
                "Profesyonel": "Büyük firmalar için profesyonel paket",
                "Kurumsal": "Kurumlar için özelleştirilmiş paket",
            }[isim],
        })
    return katalog


def _paket_row(row: Any) -> Dict[str, Any]:
    return {
        "package_id": str(row["package_id"]) if row.get("package_id") else None,
        "name": row.get("name", ""),
        "description": row.get("description", ""),
        "price": float(row["price"]) if row.get("price") is not None else None,
        "features": row.get("features", "[]"),
        "icon": row.get("icon", ""),
        "created_at": row.get("created_at"),
    }


def _firma_paket_row(row: Any) -> Dict[str, Any]:
    return {
        "id": str(row["id"]) if row.get("id") else None,
        "company_id": str(row["company_id"]) if row.get("company_id") else None,
        "package_id": str(row["package_id"]) if row.get("package_id") else None,
        "name": row.get("name", ""),
        "price": float(row["price"]) if row.get("price") is not None else None,
        "icon": row.get("icon", ""),
        "assigned_at": row.get("assigned_at"),
        "status": row.get("status", "active"),
    }
