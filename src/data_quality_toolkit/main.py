"""Kurumsal Büyük Veri Sınıflandırma, Sentetik Tasarım ve Kalite Test Platformu - Ana Çalıştırıcı.

Bu modül, tüm sistemi entegre ederek uçtan uca şu 3 aşamayı icra eder:
1. Kurumsal veri setlerini tarayıp hassas verileri (PII/DLP) sınıflandırma.
2. NVIDIA NeMo Data Designer vizyonunda KVKK uyumlu sentetik test verisi üretme.
3. Great Expectations mantığında veri kalitesi ve doğrulama testleri koşturup kalite puanı üretme.
"""

import sys
from typing import Any, Dict, List

from data_quality_toolkit.classifier.pii_scanner import PIIScanner
from data_quality_toolkit.classifier.schema_profiler import SchemaProfiler
from data_quality_toolkit.designer.schema_builder import FieldDefinition, FieldType, ScenarioConfig, SyntheticSchema
from data_quality_toolkit.designer.synthetic_generator import SyntheticDataGenerator
from data_quality_toolkit.sample_data import create_sample_banking_dataset
from data_quality_toolkit.validator.quality_engine import DataQualityEngine
from data_quality_toolkit.validator.rules import CustomRule, NotNullRule, RangeRule, RegexRule, UniqueRule


def print_banner(title: str) -> None:
    """Görsel başlık yazdırır."""
    print("\n" + "=" * 80)
    print(f" 🚀 {title.upper()}")
    print("=" * 80)


def run_classification_demo(dataset: Dict[str, List[Any]]) -> None:
    """Aşama 1: Veri Sınıflandırma ve DLP Taraması."""
    print_banner("1. AŞAMA: KURUMSAL VERİ SINIFLANDIRMA VE DLP TARAMASI")
    
    scanner = PIIScanner()
    profiler = SchemaProfiler()
    
    profile = profiler.profile_dataset(dataset)
    print(f"📊 Veri Boyutu: {profile.total_rows} Satır, {profile.total_columns} Sütun")
    print(f"📈 Veri Eksiksizlik Skoru (Completeness): %{profile.missing_data_score}\n")

    print(f"{'SÜTUN ADI':<18} | {'TİP':<10} | {'TESPİT EDİLEN PII':<18} | {'GÜVENLİK SEVİYESİ':<26} | {'GÜVEN'}")
    print("-" * 85)

    for col_name, col_values in dataset.items():
        col_prof = profile.column_profiles[col_name]
        classification = scanner.scan_column(col_name, col_values)
        print(
            f"{col_name:<18} | {col_prof.inferred_type:<10} | {classification.detected_type:<18} | "
            f"{classification.sensitivity_level.value:<26} | %{int(classification.confidence * 100)}"
        )


def run_synthetic_designer_demo() -> Dict[str, List[Any]]:
    """Aşama 2: NVIDIA NeMo Data Designer vizyonunda Sentetik Veri Tasarımı."""
    print_banner("2. AŞAMA: NVIDIA NeMo DATA DESIGNER İLE SENTETİK VERİ ÜRETİMİ")

    # Bildirimsel Şema Tasarımı
    schema = SyntheticSchema(
        schema_name="EnterpriseBankingSynthetic_v1",
        scenario=ScenarioConfig(
            name="BankacilikGuvenliTestSenaryosu",
            description="KVKK Uyumlu Müşteri ve İşlem Verisi",
            anomaly_rate=0.04,  # %4 anomali simülasyonu
        )
    )

    schema.add_field(FieldDefinition("customer_id", FieldType.UUID))
    schema.add_field(FieldDefinition("full_name", FieldType.NAME))
    schema.add_field(FieldDefinition("tckn_mock", FieldType.TCKN_MOCK))
    schema.add_field(FieldDefinition("credit_card_mock", FieldType.CREDIT_CARD_MOCK))
    schema.add_field(FieldDefinition("email", FieldType.EMAIL))
    schema.add_field(FieldDefinition("phone", FieldType.PHONE))
    schema.add_field(
        FieldDefinition(
            "city",
            FieldType.CATEGORICAL,
            choices=["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya"],
            weights=[0.40, 0.25, 0.15, 0.10, 0.10],
        )
    )
    schema.add_field(
        FieldDefinition(
            "account_balance_tl",
            FieldType.NUMERIC,
            min_value=0.0,
            max_value=250000.0,
            mean=45000.0,
            std_dev=20000.0,
        )
    )
    schema.add_field(FieldDefinition("created_at", FieldType.DATETIME))

    print(f"📋 Şema: '{schema.schema_name}' ({len(schema.fields)} Alan Tanımlandı)")
    print(f"🎯 Senaryo: {schema.scenario.description} (Anomali Oranı: %{schema.scenario.anomaly_rate * 100})\n")

    generator = SyntheticDataGenerator()
    row_count = 250
    synthetic_data = generator.generate(schema, row_count=row_count)

    print(f"✅ {row_count} Satır %100 KVKK Uyumlu Sentetik Veri Üretildi!")
    print("\nÖrnek İlk 3 Sentetik Kayıt:")
    for i in range(3):
        print(f"  • Müşteri {i+1}: {synthetic_data['full_name'][i]} | TCKN: {synthetic_data['tckn_mock'][i]} | Bakiye: {synthetic_data['account_balance_tl'][i]:,.2f} TL | Şehir: {synthetic_data['city'][i]}")

    return synthetic_data


def run_data_quality_testing_demo(dataset: Dict[str, List[Any]]) -> None:
    """Aşama 3: Veri Kalitesi ve Doğrulama Testleri."""
    print_banner("3. AŞAMA: GREAT EXPECTATIONS MODELİNDE VERİ KALİTE TESTLERİ")

    engine = DataQualityEngine()

    # Kalite ve Bütünlük Kurallarının Eklenmesi
    engine.add_rule(NotNullRule("transaction_id"))
    engine.add_rule(UniqueRule("transaction_id"))
    engine.add_rule(NotNullRule("customer_tckn"))
    engine.add_rule(
        CustomRule(
            column_name="customer_tckn",
            name="TCKN_ALGORITHM_VALIDITY",
            validator_func=lambda val: val is not None and PIIScanner.validate_tckn(str(val)),
            description="TCKN değerleri resmi matematiksel doğrulama algoritmasına uymalıdır.",
        )
    )
    engine.add_rule(
        RangeRule("amount_tl", min_val=0.0, max_val=500_000.0)
    )
    engine.add_rule(
        RegexRule(
            column_name="customer_email",
            pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
            description="E-posta adresleri geçerli RFC standardında olmalıdır.",
        )
    )

    print(f"🧪 {len(engine.rules)} Adet Veri Kalite Kuralı Çalıştırılıyor...\n")

    report = engine.validate(dataset)

    print(f"{'KURAL ADI':<26} | {'SÜTUN':<16} | {'DURUM':<8} | {'BAŞARILI':<10} | {'HATALI':<8} | {'HATA %'}")
    print("-" * 85)

    for r in report.results:
        status_str = "✅ GEÇTİ" if r.passed else "❌ KALDI"
        print(
            f"{r.rule_name:<26} | {r.column_name:<16} | {status_str:<8} | "
            f"{r.passed_records:<10} | {r.failed_records:<8} | %{r.failure_rate_pct}"
        )

    print("\n" + "=" * 85)
    print(f" 🏆 TOPLAM VERİ KALİTE SKORU (DATA QUALITY SCORE): {report.data_quality_score} / 100")
    print("=" * 85)

    if report.critical_issues:
        print("\n⚠️ TESPİT EDİLEN KRİTİK VERİ SORUNLARI:")
        for issue in report.critical_issues:
            print(f"  • {issue}")

    if report.actionable_recommendations:
        print("\n💡 DÜZELTME VE ETIL AKSİYON ÖNERİLERİ:")
        for rec in set(report.actionable_recommendations):
            print(f"  📌 {rec}")


def main() -> None:
    """Platform Ana Giriş Noktası."""
    print("\n" + "★" * 85)
    print(" KURUMSAL BÜYÜK VERİ SINIFLANDIRMA, SENTETİK TASARIM VE KALİTE TEST PLATFORMU ")
    print("★" * 85)

    # 1. Örnek Bankacılık Veri Seti Oluştur
    raw_dataset = create_sample_banking_dataset(row_count=100)

    # 2. Aşama 1: Sınıflandırma ve DLP
    run_classification_demo(raw_dataset)

    # 3. Aşama 2: Sentetik Tasarım
    run_synthetic_designer_demo()

    # 4. Aşama 3: Kalite Testleri
    run_data_quality_testing_demo(raw_dataset)

    print("\n" + "★" * 85)
    print(" TÜM AŞAMALAR BAŞARIYLA TAMAMLANDI! ")
    print("★" * 85 + "\n")


if __name__ == "__main__":
    main()
