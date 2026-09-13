# -*- coding: utf-8 -*-
"""P7-34: Veri Kalitesi iyilestirme scripti.

QS<30 firmalar icin otomatik duzeltme gorevleri olusturur.

Kullanim:
    python scripts/quality_remediation.py
    python scripts/quality_remediation.py --min-score 30 --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from company_master.db.connection import get_engine
from sqlalchemy import text

REMEDIATION_RULES: dict[str, dict[str, Any]] = {
    "tax_number": {
        "field": "tax_number",
        "action": "VKN arama / dogrulama",
        "priority": "high",
        "description": "VKN (Vergi Kimlik No) eksik veya gecersiz. Mevcut verilerden dogrulama yapilmalidir.",
    },
    "adres": {
        "field": "adres",
        "action": "Adres dogrulama",
        "priority": "high",
        "description": "Adres bilgisi eksik. Adres dogrulama servisi ile kontrol edilmeli.",
    },
    "primary_phone": {
        "field": "primary_phone",
        "action": "Telefon dogrulama",
        "priority": "medium",
        "description": "Telefon bilgisi eksik. Telefon dogrulama ile petik olusturulmalidir.",
    },
    "primary_email": {
        "field": "primary_email",
        "action": "E-posta dogrulama",
        "priority": "medium",
        "description": "E-posta bilgisi eksik. E-posta dogrulama ile petik olusturulmalidir.",
    },
    "website_domain": {
        "field": "website_domain",
        "action": "Web sitesi dogrulama",
        "priority": "medium",
        "description": "Web sitesi bilgisi eksik. Web sitesi dogrulama ile petik olusturulmalidir.",
    },
    "nace_code": {
        "field": "nace_code",
        "action": "NACE kodu dogrulama",
        "priority": "medium",
        "description": "NACE kodu eksik. Sektore gore NACE kodu atanmali.",
    },
    "osb_parsel": {
        "field": "osb_parsel",
        "action": "OSB parsel dogrulama",
        "priority": "low",
        "description": "OSB parsel bilgisi eksik. OSB kayitlari ile dogrulanmalidir.",
    },
    "trade_name": {
        "field": "trade_name",
        "action": "Unvan dogrulama",
        "priority": "low",
        "description": "Trade name (unvan) eksik. Ticaret sicilinden dogrulanmalidir.",
    },
}


def get_low_quality_companies(engine, min_score: float = 30.0, limit: int = 500):
    """QS<min_score olan firmalari getir."""
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT company_id, legal_name, tax_number, address, primary_phone,
                   primary_email, website_domain, nace_code, osb_parsel, trade_name,
                   data_quality_score, entity_confidence
            FROM companies
            WHERE data_quality_score < :min_score
            ORDER BY data_quality_score ASC
            LIMIT :limit
        """), {"min_score": min_score, "limit": limit}).mappings().all()
        return [dict(r) for r in rows]


def determine_missing_fields(company: dict[str, Any]) -> list[str]:
    """Hangi alanlarin eksik oldugunu belirle."""
    missing = []
    for key in REMEDIATION_RULES:
        val = company.get(key)
        if not val or (isinstance(val, str) and not val.strip()):
            missing.append(key)
    return missing


def build_remediation_tasks(company: dict[str, Any]) -> list[dict[str, Any]]:
    """Bir firma icin duzeltme gorevleri olustur."""
    missing = determine_missing_fields(company)
    tasks = []
    for field in missing:
        rule = REMEDIATION_RULES[field]
        tasks.append({
            "task_id": f"RQ-{company.get('company_id', 'unknown')}-{field}",
            "company_id": company.get("company_id"),
            "company_name": company.get("legal_name", "Bilinmeyen"),
            "data_quality_score": company.get("data_quality_score"),
            "field": rule["field"],
            "action": rule["action"],
            "priority": rule["priority"],
            "description": rule["description"],
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "due_date": (datetime.now(timezone.utc).replace(day=1) + timedelta(days=30)).isoformat(),
        })
    return tasks


def generate_report(tasks: list[dict[str, Any]], min_score: float) -> str:
    """Rapor metni olustur."""
    lines = [
        f"# Veri Kalitesi Duzeltme Raporu",
        f" Tarih: {datetime.now(timezone.utc).isoformat()}",
        f" Min Kalite Skoru: {min_score}",
        f" Toplam Duzeltme Gorevi: {len(tasks)}",
        f"",
        f"## Gorev Ozeti",
        f"",
    ]
    by_priority: dict[str, int] = {}
    by_field: dict[str, int] = {}
    for t in tasks:
        by_priority[t["priority"]] = by_priority.get(t["priority"], 0) + 1
        by_field[t["field"]] = by_field.get(t["field"], 0) + 1

    lines.append("### Priorite Göre")
    for p in ["high", "medium", "low"]:
        if p in by_priority:
            lines.append(f"- {p}: {by_priority[p]}")
    lines.append("")
    lines.append("### Alan Göre")
    for field, count in sorted(by_field.items(), key=lambda x: -x[1]):
        lines.append(f"- {field}: {count}")
    lines.append("")
    lines.append("## Duzeltme Gorevlari")
    lines.append("")
    for t in tasks:
        lines.append(
            f"- **{t['task_id']}** [{t['priority']}]: {t['company_name']} "
            f"(QS:{t['data_quality_score']}) → {t['action']}"
        )
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Veri Kalitesi Duzeltme Scripti")
    parser.add_argument("--min-score", type=float, default=30.0, help="Min kalite skoru")
    parser.add_argument("--limit", type=int, default=500, help="Firma siniri")
    parser.add_argument("--dry-run", action="store_true", help="Raporlama yap, DB yazma")
    parser.add_argument("--output", type=str, default=None, help="Cikis dosyasi")
    args = parser.parse_args()

    engine = get_engine()
    companies = get_low_quality_companies(engine, min_score=args.min_score, limit=args.limit)

    if not companies:
        print(f"QS < {args.min_score} olan firma bulunamadi.")
        return

    all_tasks: list[dict[str, Any]] = []
    for comp in companies:
        tasks = build_remediation_tasks(comp)
        all_tasks.extend(tasks)

    report = generate_report(all_tasks, args.min_score)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Rapor kaydedildi: {args.output}")
    else:
        print(report)

    print(f"\nToplam: {len(companies)} firma, {len(all_tasks)} duzeltme gorevi olusturuldu.")


if __name__ == "__main__":
    main()
