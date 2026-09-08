"""Veri Kalitesi Kuralları ve Doğrulama Tanımları (Data Quality Rules).

Great Expectations ve Pandera standartlarında bildirimsel kurallar içerir.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import re
from typing import Any, Callable, Dict, List, Optional, Sequence


@dataclass
class RuleResult:
    """Tek bir kural doğrulama testinin sonucu."""
    rule_name: str
    column_name: str
    passed: bool
    total_records: int
    passed_records: int
    failed_records: int
    failure_rate_pct: float
    sample_failures: List[Any]
    description: str


class BaseRule(ABC):
    """Tüm doğrulama kurallarının temel soyut sınıfı."""

    def __init__(self, column_name: str, name: str, description: str):
        self.column_name = column_name
        self.name = name
        self.description = description

    @abstractmethod
    def evaluate(self, values: Sequence[Any]) -> RuleResult:
        """Sütun değerleri üzerinde kuralı değerlendirir."""
        pass


class NotNullRule(BaseRule):
    """Boş Değer Kontrol Kuralı (Completeness Check)."""

    def __init__(self, column_name: str):
        super().__init__(
            column_name=column_name,
            name="NOT_NULL",
            description=f"'{column_name}' sütununda hiçbir değer boş (Null/None) olmamalıdır.",
        )

    def evaluate(self, values: Sequence[Any]) -> RuleResult:
        total = len(values)
        if total == 0:
            return RuleResult(self.name, self.column_name, True, 0, 0, 0, 0.0, [], self.description)

        failed_indices = [
            (i, v) for i, v in enumerate(values)
            if v is None or str(v).strip() == ""
        ]
        failed_count = len(failed_indices)
        passed_count = total - failed_count
        failure_rate = round((failed_count / total) * 100, 2)
        sample_fails = [f"Satır {i}: {v}" for i, v in failed_indices[:5]]

        return RuleResult(
            rule_name=self.name,
            column_name=self.column_name,
            passed=(failed_count == 0),
            total_records=total,
            passed_records=passed_count,
            failed_records=failed_count,
            failure_rate_pct=failure_rate,
            sample_failures=sample_fails,
            description=self.description,
        )


class RangeRule(BaseRule):
    """Sayısal Aralık Kontrol Kuralı (Numeric Range Validity)."""

    def __init__(self, column_name: str, min_val: Optional[float] = None, max_val: Optional[float] = None):
        self.min_val = min_val
        self.max_val = max_val
        desc = f"'{column_name}' değeri"
        if min_val is not None and max_val is not None:
            desc += f" {min_val} ile {max_val} arasında olmalıdır."
        elif min_val is not None:
            desc += f" >= {min_val} olmalıdır."
        elif max_val is not None:
            desc += f" <= {max_val} olmalıdır."

        super().__init__(column_name=column_name, name="VALUE_RANGE", description=desc)

    def evaluate(self, values: Sequence[Any]) -> RuleResult:
        total = len(values)
        if total == 0:
            return RuleResult(self.name, self.column_name, True, 0, 0, 0, 0.0, [], self.description)

        failed_indices = []
        for i, v in enumerate(values):
            if v is None:
                continue
            try:
                num_v = float(v)
                if self.min_val is not None and num_v < self.min_val:
                    failed_indices.append((i, num_v))
                elif self.max_val is not None and num_v > self.max_val:
                    failed_indices.append((i, num_v))
            except (ValueError, TypeError):
                failed_indices.append((i, f"Geçersiz Sayı: {v}"))

        failed_count = len(failed_indices)
        passed_count = total - failed_count
        failure_rate = round((failed_count / total) * 100, 2)
        sample_fails = [f"Satır {i}: {v}" for i, v in failed_indices[:5]]

        return RuleResult(
            rule_name=self.name,
            column_name=self.column_name,
            passed=(failed_count == 0),
            total_records=total,
            passed_records=passed_count,
            failed_records=failed_count,
            failure_rate_pct=failure_rate,
            sample_failures=sample_fails,
            description=self.description,
        )


class UniqueRule(BaseRule):
    """Benzersizlik Kontrol Kuralı (Uniqueness Check)."""

    def __init__(self, column_name: str):
        super().__init__(
            column_name=column_name,
            name="UNIQUE",
            description=f"'{column_name}' sütunundaki tüm değerler benzersiz (unique) olmalıdır.",
        )

    def evaluate(self, values: Sequence[Any]) -> RuleResult:
        total = len(values)
        if total == 0:
            return RuleResult(self.name, self.column_name, True, 0, 0, 0, 0.0, [], self.description)

        seen = set()
        duplicates = []
        for i, v in enumerate(values):
            if v in seen:
                duplicates.append((i, v))
            seen.add(v)

        failed_count = len(duplicates)
        passed_count = total - failed_count
        failure_rate = round((failed_count / total) * 100, 2)
        sample_fails = [f"Mükerrer Kayıt (Satır {i}): {v}" for i, v in duplicates[:5]]

        return RuleResult(
            rule_name=self.name,
            column_name=self.column_name,
            passed=(failed_count == 0),
            total_records=total,
            passed_records=passed_count,
            failed_records=failed_count,
            failure_rate_pct=failure_rate,
            sample_failures=sample_fails,
            description=self.description,
        )


class RegexRule(BaseRule):
    """Biçim & Desen Kontrol Kuralı (Regex Pattern Matching)."""

    def __init__(self, column_name: str, pattern: str, description: str):
        self.pattern = re.compile(pattern)
        super().__init__(
            column_name=column_name,
            name="REGEX_MATCH",
            description=description,
        )

    def evaluate(self, values: Sequence[Any]) -> RuleResult:
        total = len(values)
        if total == 0:
            return RuleResult(self.name, self.column_name, True, 0, 0, 0, 0.0, [], self.description)

        failed_indices = []
        for i, v in enumerate(values):
            if v is None or not self.pattern.match(str(v).strip()):
                failed_indices.append((i, v))

        failed_count = len(failed_indices)
        passed_count = total - failed_count
        failure_rate = round((failed_count / total) * 100, 2)
        sample_fails = [f"Geçersiz Format (Satır {i}): {v}" for i, v in failed_indices[:5]]

        return RuleResult(
            rule_name=self.name,
            column_name=self.column_name,
            passed=(failed_count == 0),
            total_records=total,
            passed_records=passed_count,
            failed_records=failed_count,
            failure_rate_pct=failure_rate,
            sample_failures=sample_fails,
            description=self.description,
        )


class CustomRule(BaseRule):
    """Özel Fonksiyon Doğrulama Kuralı (Custom Python Validator)."""

    def __init__(self, column_name: str, name: str, validator_func: Callable[[Any], bool], description: str):
        self.validator_func = validator_func
        super().__init__(column_name=column_name, name=name, description=description)

    def evaluate(self, values: Sequence[Any]) -> RuleResult:
        total = len(values)
        if total == 0:
            return RuleResult(self.name, self.column_name, True, 0, 0, 0, 0.0, [], self.description)

        failed_indices = []
        for i, v in enumerate(values):
            try:
                if not self.validator_func(v):
                    failed_indices.append((i, v))
            except Exception as e:
                failed_indices.append((i, f"{v} (Hata: {e})"))

        failed_count = len(failed_indices)
        passed_count = total - failed_count
        failure_rate = round((failed_count / total) * 100, 2)
        sample_fails = [f"Kural İhlali (Satır {i}): {v}" for i, v in failed_indices[:5]]

        return RuleResult(
            rule_name=self.name,
            column_name=self.column_name,
            passed=(failed_count == 0),
            total_records=total,
            passed_records=passed_count,
            failed_records=failed_count,
            failure_rate_pct=failure_rate,
            sample_failures=sample_fails,
            description=self.description,
        )
