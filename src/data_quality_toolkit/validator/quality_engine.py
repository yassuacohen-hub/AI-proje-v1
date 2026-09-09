"""Veri Kalitesi Test ve Puanlama Motoru (Data Quality Engine).

Büyük veri setleri üzerinde tanımlanan kuralları paralel/seri olarak koşturur,
0-100 arası Veri Kalite Skoru (Data Quality Score) hesaplar ve eyleme geçirilebilir
hata raporları sunar.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .rules import BaseRule, RuleResult


@dataclass
class QualityReport:
    """Kapsamlı Veri Kalitesi ve Doğrulama Raporu."""
    total_rules_evaluated: int
    passed_rules_count: int
    failed_rules_count: int
    data_quality_score: float  # 0.0 - 100.0
    results: List[RuleResult] = field(default_factory=list)
    critical_issues: List[str] = field(default_factory=list)
    actionable_recommendations: List[str] = field(default_factory=list)


class DataQualityEngine:
    """Veri Kalitesi ve Sözleşme Denetim Motoru."""

    def __init__(self):
        self.rules: List[BaseRule] = []

    def add_rule(self, rule: BaseRule) -> "DataQualityEngine":
        """Motora yeni bir doğrulama kuralı ekler."""
        self.rules.append(rule)
        return self

    def add_rules(self, rules: List[BaseRule]) -> "DataQualityEngine":
        """Toplu kural ekler."""
        self.rules.extend(rules)
        return self

    def validate(self, dataset: Dict[str, List[Any]]) -> QualityReport:
        """Veri setini tanımlı tüm kurallara göre test eder."""
        results: List[RuleResult] = []
        passed_count = 0
        failed_count = 0
        critical_issues = []
        recommendations = []

        total_records_sum = 0
        total_failed_records_sum = 0

        for rule in self.rules:
            col_name = rule.column_name
            values = dataset.get(col_name, [])
            res = rule.evaluate(values)
            results.append(res)

            total_records_sum += res.total_records
            total_failed_records_sum += res.failed_records

            if res.passed:
                passed_count += 1
            else:
                failed_count += 1
                issue = f"[{rule.name}] '{col_name}' sütununda %{res.failure_rate_pct} oranında kural ihlali ({res.failed_records} kayıt)."
                critical_issues.append(issue)
                recommendations.append(
                    f"'{col_name}' alanı için ETL boru hattına filtre veya düzeltme aşaması ekleyin: {rule.description}"
                )

        # Kalite Puanı Hesaplama:
        # Formül: 100 * (1 - (Toplam Hatalı Hücre / Toplam İncelenen Hücre)) * (Başarılı Kural Oranı)
        if total_records_sum > 0 and len(self.rules) > 0:
            record_pass_rate = 1.0 - (total_failed_records_sum / total_records_sum)
            rule_pass_rate = passed_count / len(self.rules)
            # Ağırlıklı skor (%60 kayıt doğruluğu, %40 kural başarısı)
            quality_score = round((record_pass_rate * 60.0) + (rule_pass_rate * 40.0), 2)
            quality_score = max(0.0, min(100.0, quality_score))
        else:
            quality_score = 100.0

        return QualityReport(
            total_rules_evaluated=len(self.rules),
            passed_rules_count=passed_count,
            failed_rules_count=failed_count,
            data_quality_score=quality_score,
            results=results,
            critical_issues=critical_issues,
            actionable_recommendations=recommendations,
        )
