# -*- coding: utf-8 -*-

"""OSINT Scraper Motoru — Kalite Kapisi (Quality Gate).

Bu modul scraper ciktilarini (JSONL) alir, veri kalitesi kurallarini
uygular ve _score() formulu ile birlesik kalite skoru hesaplar.
Dusuk kaliteli kayitlari filtreleyip raporlayip pipeline'a geçirir.

Kullanim:
    python -m company_master.engine.quality_gate data/ostim/firmalar_detayli.jsonl output.jsonl --min-score 30
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]

import yaml
from pathlib import Path as _Path


def load_quality_config() -> dict:
    """config/quality_gate.yaml'dan ayarları yükler."""
    cfg_path = _Path(__file__).resolve().parents[3] / "config" / "quality_gate.yaml"
    if cfg_path.exists():
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            pass
    return {}


sys.path.insert(0, str(ROOT / "src"))

# Data Quality Toolkit entegrasyonu
try:
    from data_quality_toolkit.validator.quality_engine import DataQualityEngine, QualityReport
    from data_quality_toolkit.validator.rules import (
        NotNullRule,
        RegexRule,
        RangeRule,
        CustomRule,
    )
    from data_quality_toolkit.classifier.pii_scanner import PIIScanner
    DQT_AVAILABLE = True
except ImportError:
    DQT_AVAILABLE = False
    DataQualityEngine = None
    QualityReport = None

# DB-level kalite skoru formulu (quality_recalc.py'den)
def _calculate_db_quality_score(row: dict) -> float:
    """Kalite skoru formulu (0-100) - DB schema'yla uyumludur."""
    score = 0.0
    vkn = row.get("tax_number") or row.get("vergi_no") or row.get("vkn") or ""
    if vkn and str(vkn).strip():
        score += 15
    adres = row.get("adres") or row.get("address") or ""
    if adres and str(adres).strip():
        score += 15
    phone = row.get("primary_phone") or row.get("telefon") or row.get("phone") or ""
    if phone and str(phone).strip():
        score += 15
    email = row.get("primary_email") or row.get("email") or row.get("eposta") or ""
    if email and str(email).strip():
        score += 15
    web = row.get("website_domain") or row.get("web_sitesi") or row.get("website") or ""
    if web and str(web).strip():
        score += 10
    nace = row.get("nace_code") or row.get("nace") or row.get("sektor_kodu") or ""
    if nace and str(nace).strip():
        score += 15
    parsel = row.get("osb_parcel") or row.get("osb_parsel") or row.get("parsel") or ""
    if parsel and str(parsel).strip():
        score += 10
    trade = row.get("trade_name") or row.get("unvan") or row.get("title") or ""
    if trade and str(trade).strip():
        score += 5
    return round(min(score, 100.0), 1)


@dataclass
class QualityGateReport:
    """Quality Gate calistirma raporu."""
    source_id: str = ""
    total_input: int = 0
    passed: int = 0
    rejected: int = 0
    dqt_report: Any = None
    avg_db_score: float = 0.0
    score_distribution: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            "",
            "=== Quality Gate Report: {} ===".format(self.source_id),
            "Total input:     {}".format(self.total_input),
            "Passed (>=min):  {}".format(self.passed),
            "Rejected (<min): {}".format(self.rejected),
            "Avg DB score:    {:.1f}".format(self.avg_db_score),
        ]
        if self.score_distribution:
            lines.append("Score distribution:")
            for bucket, cnt in sorted(self.score_distribution.items(), reverse=True):
                lines.append("  {}: {}".format(bucket, cnt))
        if self.errors:
            lines.append("Errors:")
            for e in self.errors:
                lines.append("  - {}".format(e))
        return "\n".join(lines)


class QualityGate:
    """Scraper ciktisi icin kalite kontrol kapisi."""

    DEFAULT_RULES = [
        ("legal_name", NotNullRule, {}),
        ("unvan", NotNullRule, {}),
        ("email", RegexRule, {"pattern": r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", "description": "Geçerli e-posta formatı"}),
        ("primary_email", RegexRule, {"pattern": r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", "description": "Geçerli e-posta formatı"}),
        ("eposta", RegexRule, {"pattern": r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", "description": "Geçerli e-posta formatı"}),
        ("website", RegexRule, {"pattern": r"^https?://", "description": "HTTP/HTTPS ile başlamalı"}),
        ("web_sitesi", RegexRule, {"pattern": r"^https?://", "description": "HTTP/HTTPS ile başlamalı"}),
        ("website_domain", RegexRule, {"pattern": r"^https?://", "description": "HTTP/HTTPS ile başlamalı"}),
        ("vergi_no", CustomRule, {"name": "VKN_FORMAT", "validator_func": lambda v: _validate_vkn(v), "description": "10-11 haneli VKN, 0 ile başlamamalı"}),
        ("tax_number", CustomRule, {"name": "VKN_FORMAT", "validator_func": lambda v: _validate_vkn(v), "description": "10-11 haneli VKN, 0 ile başlamamalı"}),
        ("vkn", CustomRule, {"name": "VKN_FORMAT", "validator_func": lambda v: _validate_vkn(v), "description": "10-11 haneli VKN, 0 ile başlamamalı"}),
        ("phone", RegexRule, {"pattern": r"^\+?\d[\d\s\-]{8,}$", "description": "Geçerli telefon formatı"}),
        ("telefon", RegexRule, {"pattern": r"^\+?\d[\d\s\-]{8,}$", "description": "Geçerli telefon formatı"}),
        ("primary_phone", RegexRule, {"pattern": r"^\+?\d[\d\s\-]{8,}$", "description": "Geçerli telefon formatı"}),
        ("adres", CustomRule, {"name": "MIN_LENGTH", "validator_func": lambda v: len(str(v).strip()) >= 5 if v else False, "description": "Adres en az 5 karakter"}),
        ("address", CustomRule, {"name": "MIN_LENGTH", "validator_func": lambda v: len(str(v).strip()) >= 5 if v else False, "description": "Adres en az 5 karakter"}),
        ("nace_code", RegexRule, {"pattern": r"^\d{4,6}$", "description": "4-6 haneli NACE kodu"}),
        ("nace", RegexRule, {"pattern": r"^\d{4,6}$", "description": "4-6 haneli NACE kodu"}),
        ("sektor_kodu", RegexRule, {"pattern": r"^\d{4,6}$", "description": "4-6 haneli NACE kodu"}),
    ]

    def __init__(self, min_score: float = 30.0, rules: list = None, use_dqt: bool = True, pii_scan: bool = False):
        """Quality Gate'i baslatir. Config'den min_score alir."""
        config = load_quality_config()
        quality_cfg = config.get("quality_gate", {}) if config else {}
        if min_score == 30.0 and "min_score" in quality_cfg:
            min_score = quality_cfg["min_score"]
        # DB weights from config
        db_weights = quality_cfg.get("db_fields", {}) if quality_cfg else {}
        self.db_weights = db_weights if db_weights else {
            "tax_number": 15, "address": 15, "primary_phone": 15,
            "primary_email": 15, "website_domain": 10, "nace_code": 15,
            "osb_parcel": 10, "trade_name": 5
        }
        self.min_score = min_score
        self.custom_rules = rules or self.DEFAULT_RULES
        self.use_dqt = use_dqt and DQT_AVAILABLE
        self.pii_scan = pii_scan and DQT_AVAILABLE
        self.engine = None
        self._pii_scanner = None
        if self.use_dqt:
            self.engine = DataQualityEngine()
            for col_name, rule_cls, kwargs in self.custom_rules:
                try:
                    rule = rule_cls(column_name=col_name, **kwargs)
                    self.engine.add_rule(rule)
                except Exception as e:
                    print("[UYARI] Kural olusturulamadi {}: {}".format(col_name, e), file=sys.stderr)
        if self.pii_scan:
            self._pii_scanner = PIIScanner()

    def run(self, input_path: str, output_path: str) -> QualityGateReport:
        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.exists():
            return QualityGateReport(source_id=input_path.stem, errors=["Girdi dosyası bulunamadı: {}".format(input_path)])

        output_path.parent.mkdir(parents=True, exist_ok=True)

        records = []
        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

        report = QualityGateReport(source_id=input_path.stem)
        report.total_input = len(records)

        if not records:
            return report

        # Data Quality Toolkit validasyonu
        dqt_report = None
        if self.use_dqt and self.engine and self.engine.rules:
            try:
                dataset = self._records_to_dataset(records)
                dqt_report = self.engine.validate(dataset)
                report.dqt_report = dqt_report
            except Exception as e:
                report.errors.append("DQT validation hatası: {}".format(e))

        # PII taraması
        pii_findings = {}
        if self.pii_scan and self._pii_scanner:
            try:
                dataset = self._records_to_dataset(records)
                for col_name, col_values in dataset.items():
                    classification = self._pii_scanner.scan_column(col_name, col_values)
                    if classification.detected_type != "NONE":
                        pii_findings[col_name] = {
                            "type": classification.detected_type,
                            "level": classification.sensitivity_level.value,
                            "confidence": classification.confidence,
                        }
            except Exception as e:
                report.errors.append("PII scan hatası: {}".format(e))

        # Her kayıt için birleşik skor hesapla ve filtrele
        passed_records = []
        scores = []

        for rec in records:
            db_score = _calculate_db_quality_score(rec)
            dqt_pass_rate = 100.0
            if dqt_report:
                total_failed = sum(r.failed_records for r in dqt_report.results)
                total_checked = sum(r.total_records for r in dqt_report.results)
                if total_checked > 0:
                    dqt_pass_rate = 100.0 * (1.0 - total_failed / total_checked)

            combined_score = round(0.7 * db_score + 0.3 * dqt_pass_rate, 1)
            scores.append(combined_score)

            if combined_score >= self.min_score:
                rec["_quality_score"] = combined_score
                rec["_db_quality_score"] = db_score
                rec["_dqt_pass_rate"] = dqt_pass_rate
                if pii_findings:
                    rec["_pii_findings"] = pii_findings
                passed_records.append(rec)
                report.passed += 1
            else:
                report.rejected += 1

        # Çıktıyı yaz
        with open(output_path, "w", encoding="utf-8") as f:
            for rec in passed_records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

        # Dağılım hesapla
        if scores:
            buckets = {"80-100": 0, "60-79": 0, "40-59": 0, "20-39": 0, "0-19": 0}
            for s in scores:
                if s >= 80:
                    buckets["80-100"] += 1
                elif s >= 60:
                    buckets["60-79"] += 1
                elif s >= 40:
                    buckets["40-59"] += 1
                elif s >= 20:
                    buckets["20-39"] += 1
                else:
                    buckets["0-19"] += 1
            report.score_distribution = {k: v for k, v in buckets.items() if v > 0}
            report.avg_db_score = round(sum(scores) / len(scores), 1)

        return report

    def _records_to_dataset(self, records: list) -> dict:
        if not records:
            return {}
        all_keys = set()
        for r in records:
            all_keys.update(r.keys())
        dataset = {k: [] for k in all_keys}
        for r in records:
            for k in all_keys:
                dataset[k].append(r.get(k))
        return dataset


def _validate_vkn(value) -> bool:
    if value is None:
        return False
    s = str(value).strip()
    if not s.isdigit():
        return False
    if len(s) not in (10, 11):
        return False
    if s[0] == "0":
        return False
    return True


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="OSINT Quality Gate CLI")
    parser.add_argument("input", help="Girdi JSONL dosyası")
    parser.add_argument("output", help="Çıktı JSONL dosyası")
    parser.add_argument("--min-score", type=float, default=30.0, help="Minimum kalite skoru (0-100)")
    parser.add_argument("--no-dqt", action="store_true", help="Data Quality Toolkit'i devre dışı bırak")
    parser.add_argument("--pii-scan", action="store_true", help="PII tarama yap")
    parser.add_argument("--report", help="Rapor JSON dosyası")
    args = parser.parse_args()

    gate = QualityGate(min_score=args.min_score, use_dqt=not args.no_dqt, pii_scan=args.pii_scan)
    report = gate.run(args.input, args.output)
    print(report.summary())

    if args.report:
        out = {
            "source_id": report.source_id,
            "total_input": report.total_input,
            "passed": report.passed,
            "rejected": report.rejected,
            "avg_db_score": report.avg_db_score,
            "score_distribution": report.score_distribution,
            "errors": report.errors,
        }
        if report.dqt_report:
            out["dqt"] = {
                "total_rules": report.dqt_report.total_rules_evaluated,
                "passed_rules": report.dqt_report.passed_rules_count,
                "failed_rules": report.dqt_report.failed_rules_count,
                "data_quality_score": report.dqt_report.data_quality_score,
            }
        Path(args.report).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print("Rapor kaydedildi: {}".format(args.report))

    return 0 if report.rejected < report.total_input else 1


if __name__ == "__main__":
    sys.exit(main())
