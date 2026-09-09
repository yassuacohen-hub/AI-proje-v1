"""Sentetik Veri Şema Tasarımcısı (Data Designer Schema Builder).

NVIDIA NeMo Data Designer ve modern sentetik veri motorları mantığında,
bildirimsel (declarative) şemalar ve iş senaryoları tanımlar.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class FieldType(str, Enum):
    """Sentetik alan türleri."""
    NUMERIC = "NUMERIC"
    CATEGORICAL = "CATEGORICAL"
    NAME = "NAME"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    TCKN_MOCK = "TCKN_MOCK"
    CREDIT_CARD_MOCK = "CREDIT_CARD_MOCK"
    IBAN_MOCK = "IBAN_MOCK"
    DATETIME = "DATETIME"
    UUID = "UUID"


@dataclass
class FieldDefinition:
    """Tek bir sentetik sütunun tanımı ve kısıtları."""
    name: str
    field_type: FieldType
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mean: Optional[float] = None
    std_dev: Optional[float] = None
    choices: Optional[List[str]] = None
    weights: Optional[List[float]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    null_probability: float = 0.0


@dataclass
class ScenarioConfig:
    """İş senaryoları ve anomali enjeksiyon parametreleri."""
    name: str
    description: str
    anomaly_rate: float = 0.05       # %5 anomali/fraud oranı
    high_value_spike_rate: float = 0.02  # %2 olağandışı yüksek tutar


@dataclass
class SyntheticSchema:
    """Sentetik Veri Setinin Ana Şeması."""
    schema_name: str
    fields: List[FieldDefinition] = field(default_factory=list)
    scenario: ScenarioConfig = field(
        default_factory=lambda: ScenarioConfig(name="Default", description="Standart kurumsal dağılım")
    )

    def add_field(self, field_def: FieldDefinition) -> "SyntheticSchema":
        """Şemaya yeni bir alan ekler."""
        self.fields.append(field_def)
        return self
