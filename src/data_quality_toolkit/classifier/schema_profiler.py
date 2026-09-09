"""Veri Profili ve Şema Çıkarıcı Modülü.

Bu modül, kurumsal veri setlerinin veri tiplerini, eksik veri oranlarını,
benzersizlik yüzdelerini ve istatistiksel dağılımlarını analiz eder.
"""

from dataclasses import dataclass
from datetime import datetime
import math
from typing import Any, Dict, List, Optional, Sequence


@dataclass
class ColumnProfile:
    """Tek bir sütunun profilleme istatistikleri."""
    column_name: str
    inferred_type: str
    total_count: int
    null_count: int
    null_percentage: float
    unique_count: int
    unique_percentage: float
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    mean_value: Optional[float] = None
    top_values: Optional[List[Dict[str, Any]]] = None


@dataclass
class DatasetProfile:
    """Tüm veri setinin kapsamlı profili."""
    total_rows: int
    total_columns: int
    column_profiles: Dict[str, ColumnProfile]
    missing_data_score: float  # 0.0 - 100.0 (100 = hiç boş veri yok)


class SchemaProfiler:
    """Veri Seti Profilleme ve Şema Çıkarım Motoru."""

    @staticmethod
    def infer_type(values: Sequence[Any]) -> str:
        """Sütundaki değerlerin çoğunluğuna bakarak veri tipini belirler."""
        non_nulls = [v for v in values if v is not None and str(v).strip() != ""]
        if not non_nulls:
            return "EMPTY"

        type_votes = {"INTEGER": 0, "FLOAT": 0, "DATETIME": 0, "BOOLEAN": 0, "STRING": 0}

        for v in non_nulls[:100]:  # İlk 100 örnekle hızlı çıkarım
            val_str = str(v).strip()
            
            # Boolean kontrolü
            if val_str.lower() in ("true", "false", "1", "0", "evet", "hayir"):
                type_votes["BOOLEAN"] += 1
                continue

            # Integer kontrolü
            if val_str.isdigit() or (val_str.startswith("-") and val_str[1:].isdigit()):
                type_votes["INTEGER"] += 1
                continue

            # Float kontrolü
            try:
                float(val_str)
                type_votes["FLOAT"] += 1
                continue
            except ValueError:
                pass

            # Datetime kontrolü
            try:
                datetime.fromisoformat(val_str.replace("Z", "+00:00"))
                type_votes["DATETIME"] += 1
                continue
            except (ValueError, TypeError):
                pass

            type_votes["STRING"] += 1

        top_type = max(type_votes.items(), key=lambda x: x[1])[0]
        return top_type

    def profile_column(self, column_name: str, values: Sequence[Any]) -> ColumnProfile:
        """Tek bir sütun için detaylı istatistikleri hesaplar."""
        total_count = len(values)
        if total_count == 0:
            return ColumnProfile(
                column_name=column_name,
                inferred_type="EMPTY",
                total_count=0,
                null_count=0,
                null_percentage=0.0,
                unique_count=0,
                unique_percentage=0.0,
            )

        null_count = sum(1 for v in values if v is None or str(v).strip() == "")
        null_pct = round((null_count / total_count) * 100, 2)

        non_null_values = [v for v in values if v is not None and str(v).strip() != ""]
        unique_vals = set(non_null_values)
        unique_count = len(unique_vals)
        unique_pct = round((unique_count / max(len(non_null_values), 1)) * 100, 2)

        inferred = self.infer_type(values)

        min_val: Optional[Any] = None
        max_val: Optional[Any] = None
        mean_val: Optional[float] = None
        top_vals: Optional[List[Dict[str, Any]]] = None

        if inferred in ("INTEGER", "FLOAT") and non_null_values:
            numeric_vals = []
            for v in non_null_values:
                try:
                    numeric_vals.append(float(v))
                except (ValueError, TypeError):
                    pass
            if numeric_vals:
                min_val = min(numeric_vals)
                max_val = max(numeric_vals)
                mean_val = round(sum(numeric_vals) / len(numeric_vals), 2)
        elif non_null_values:
            # Kategorik sık tekrar eden değerler
            freq: Dict[str, int] = {}
            for v in non_null_values:
                k = str(v)
                freq[k] = freq.get(k, 0) + 1
            sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:3]
            top_vals = [{"value": k, "count": count} for k, count in sorted_freq]

        return ColumnProfile(
            column_name=column_name,
            inferred_type=inferred,
            total_count=total_count,
            null_count=null_count,
            null_percentage=null_pct,
            unique_count=unique_count,
            unique_percentage=unique_pct,
            min_value=min_val,
            max_value=max_val,
            mean_value=mean_val,
            top_values=top_vals,
        )

    def profile_dataset(self, data_dict: Dict[str, List[Any]]) -> DatasetProfile:
        """Tüm veri setini profiller."""
        column_profiles = {}
        total_rows = 0
        total_nulls = 0
        total_cells = 0

        for col_name, col_values in data_dict.items():
            profile = self.profile_column(col_name, col_values)
            column_profiles[col_name] = profile
            total_rows = max(total_rows, len(col_values))
            total_nulls += profile.null_count
            total_cells += profile.total_count

        completeness_score = round(100.0 - ((total_nulls / max(total_cells, 1)) * 100), 2)

        return DatasetProfile(
            total_rows=total_rows,
            total_columns=len(data_dict),
            column_profiles=column_profiles,
            missing_data_score=completeness_score,
        )
