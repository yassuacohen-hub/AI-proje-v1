"""Hassas Veri (PII) ve DLP Tarayıcı Modülü.

Bu modül, veri setlerindeki sütunları tarayarak T.C. Kimlik No, Kredi Kartı (Luhn Algoritması),
IBAN, E-posta ve Telefon gibi hassas verileri algoritmik olarak tespit eder ve
güvenlik sınıflandırması (Restricted, Confidential, Internal, Public) yapar.
"""

from dataclasses import dataclass
from enum import Enum
import re
from typing import Any, Dict, List, Optional, Sequence


class SensitivityLevel(str, Enum):
    """Veri Güvenlik Seviyesi Sınıflandırması."""
    RESTRICTED = "RESTRICTED (Çok Gizli)"    # Kredi kartı, şifre vb.
    CONFIDENTIAL = "CONFIDENTIAL (Gizli)"    # TCKN, IBAN, Sağlık verisi vb.
    INTERNAL = "INTERNAL (Kurum İçi)"        # İsim, E-posta, Telefon vb.
    PUBLIC = "PUBLIC (Genel)"                # Ürün adı, genel kategoriler


@dataclass
class ColumnClassification:
    """Tek bir sütunun sınıflandırma raporu."""
    column_name: str
    detected_type: str
    sensitivity_level: SensitivityLevel
    confidence: float
    matched_samples_count: int
    total_samples_scanned: int
    recommendation: str


class PIIScanner:
    """Hassas Veri Tespit ve DLP Tarayıcısı."""

    # E-posta Regex (RFC 5322 uyumlu, Türkçe & Avrupa karakterleri destekler)
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9ÄäÖöÜüßÃãÕõÎîÌìÉéÈèÊêËëÝýÀàÁáÂâçÇğĞıIİöÖşŞüÜ_.\+\-]+@[a-zA-Z0-9ÄäÖöÜüßÃãÕõÎîÌìÉéÈèÊêËëÝýÀàÁáÂâçÇğĞıIİöÖşŞüÜ\-]+\.[a-zA-Z0-9ÄäÖöÜüßÃãÕõÎîÌìÉéÈèÊêËëÝýÀàÁáÂâçÇğĞıIİöÖşŞüÜ.\-]+$", re.UNICODE)
    
    # Telefon Regex (Türkiye: +90 veya 0 ile başlayan 5XX XXXXXX pattern, Diğer ülkeler)
    PHONE_PATTERN = re.compile(r"^(\+90|0)[5][0-9]{2}[0-9]{6}$|^(?!\+90)\+[1-9]\d{1,14}$", re.UNICODE)
    
    # IBAN Regex (TR IBAN - 26 karakter)
    IBAN_PATTERN = re.compile(r"^TR[0-9]{2}[0-9]{4}0[0-9]{16}$", re.IGNORECASE)

    @staticmethod
    def validate_tckn(tckn_str: str) -> bool:
        """T.C. Kimlik Numarası matematiksel doğrulama algoritması.
        
        Kurallar:
        1. 11 hanelidir ve sadece rakamlardan oluşur.
        2. İlk hane 0 olamaz.
        3. 1, 3, 5, 7 ve 9. hanelerin toplamının 7 katından, 2, 4, 6 ve 8. hanelerin toplamı
           çıkarıldığında elde edilen sonucun 10'a bölümünden kalan 10. haneyi verir.
        4. İlk 10 hanenin toplamının 10'a bölümünden kalan 11. haneyi verir.
        """
        clean_tckn = str(tckn_str).strip()
        if not clean_tckn.isdigit() or len(clean_tckn) != 11:
            return False
        
        if clean_tckn[0] == "0":
            return False

        digits = [int(d) for d in clean_tckn]
        odd_sum = digits[0] + digits[2] + digits[4] + digits[6] + digits[8]
        even_sum = digits[1] + digits[3] + digits[5] + digits[7]

        tenth_digit = ((odd_sum * 7) - even_sum) % 10
        if tenth_digit != digits[9]:
            return False

        eleventh_digit = sum(digits[:10]) % 10
        if eleventh_digit != digits[10]:
            return False

        return True

    @staticmethod
    def validate_luhn_credit_card(card_number_str: str) -> bool:
        """Luhn Algoritması (Mod 10) ile Kredi Kartı numarası doğrulama."""
        clean_card = re.sub(r"[\s-]", "", str(card_number_str))
        if not clean_card.isdigit() or not (13 <= len(clean_card) <= 19):
            return False

        digits = [int(d) for d in clean_card]
        total = 0

        for index, digit in enumerate(reversed(digits)):
            if index % 2 == 1:
                doubled = digit * 2
                total += (doubled - 9) if doubled > 9 else doubled
            else:
                total += digit

        return total % 10 == 0

    def classify_value(self, value: Any) -> Optional[str]:
        """Tek bir değerin hassas veri tipini belirler."""
        if value is None:
            return None
        
        val_str = str(value).strip()
        if not val_str:
            return None

        # 1. Kredi Kartı Kontrolü (Luhn)
        if self.validate_luhn_credit_card(val_str):
            return "CREDIT_CARD"

        # 2. TCKN Kontrolü
        if self.validate_tckn(val_str):
            return "TCKN"

        # 3. IBAN Kontrolü
        clean_iban = re.sub(r"[\s]", "", val_str)
        if self.IBAN_PATTERN.match(clean_iban):
            return "IBAN"

        # 4. E-posta Kontrolü
        if self.EMAIL_PATTERN.match(val_str):
            return "EMAIL"

        # 5. Telefon Kontrolü
        clean_phone = re.sub(r"[\s\(\)-]", "", val_str)
        if self.PHONE_PATTERN.match(clean_phone):
            return "PHONE"

        return None

    def scan_column(self, column_name: str, values: Sequence[Any]) -> ColumnClassification:
        """Bir sütundaki değerleri tarayarak PII ve güvenlik seviyesini raporlar."""
        total_samples = len(values)
        
        # Boş veya None-only sütun kontrolü
        non_null_values = [v for v in values if v is not None and str(v).strip()]
        if len(non_null_values) == 0:
            return ColumnClassification(
                column_name=column_name,
                detected_type="EMPTY",
                sensitivity_level=SensitivityLevel.PUBLIC,
                confidence=1.0,
                matched_samples_count=0,
                total_samples_scanned=total_samples,
                recommendation="Sütun boş veya tüm değerleri None. İşlem gerekmiyor.",
            )

        type_counts: Dict[str, int] = {}
        for val in values:
            detected = self.classify_value(val)
            if detected:
                type_counts[detected] = type_counts.get(detected, 0) + 1

        # Sütun isminden ipucu arama (name heuristic)
        col_lower = column_name.lower()
        if "tc" in col_lower or "kimlik" in col_lower or "national_id" in col_lower:
            type_counts["TCKN"] = type_counts.get("TCKN", 0) + 2
        elif "kart" in col_lower or "card" in col_lower or "pan" in col_lower:
            type_counts["CREDIT_CARD"] = type_counts.get("CREDIT_CARD", 0) + 2
        elif "iban" in col_lower or "hesap_no" in col_lower:
            type_counts["IBAN"] = type_counts.get("IBAN", 0) + 2
        elif "mail" in col_lower:
            type_counts["EMAIL"] = type_counts.get("EMAIL", 0) + 2
        elif "tel" in col_lower or "phone" in col_lower:
            type_counts["PHONE"] = type_counts.get("PHONE", 0) + 2
        elif "maas" in col_lower or "salary" in col_lower or "bakiye" in col_lower or "balance" in col_lower:
            type_counts["FINANCIAL"] = type_counts.get("FINANCIAL", 0) + 2

        if not type_counts:
            return ColumnClassification(
                column_name=column_name,
                detected_type="GENERIC_DATA",
                sensitivity_level=SensitivityLevel.PUBLIC,
                confidence=0.95,
                matched_samples_count=0,
                total_samples_scanned=total_samples,
                recommendation="Genel kurumsal veri. Ek bir maskeleme gerekmiyor.",
            )

        top_type, match_count = max(type_counts.items(), key=lambda x: x[1])
        confidence = min(round(match_count / max(len(non_null_values), 1), 2) + 0.3, 1.0)

        # Seviye ve Öneri Eşleştirmesi
        if top_type == "CREDIT_CARD":
            level = SensitivityLevel.RESTRICTED
            rec = "ACİL: Kredi kartı verisi şifrelenmeli (Tokenization) ve test ortamlarında maskelenmeli."
        elif top_type in ("TCKN", "IBAN", "FINANCIAL"):
            level = SensitivityLevel.CONFIDENTIAL
            rec = "KVKK Uyarısı: Doğrudan kimlik/finans verisi. Maskeleme ve sentetik veri ikamesi zorunlu."
        elif top_type in ("EMAIL", "PHONE"):
            level = SensitivityLevel.INTERNAL
            rec = "İletişim verisi: Kurum içi erişimle sınırlandırılmalı, testler için sahte veri kullanılmalı."
        else:
            level = SensitivityLevel.PUBLIC
            rec = "Açık veri."

        return ColumnClassification(
            column_name=column_name,
            detected_type=top_type,
            sensitivity_level=level,
            confidence=confidence,
            matched_samples_count=match_count,
            total_samples_scanned=total_samples,
            recommendation=rec,
        )
