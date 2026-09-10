"""Ankara OSB firmaları için sentetik veri üretici.

Gerçek veri toplanana kadar test/demo amaçlı 200 firma üretir:
- 150'si Ankara + OSB üyesi (MVP kapsam)
- 50'si farklı senaryolar (Ankara ama OSB dışı, İstanbul dışı, vb.) → karantina
"""

import random
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# data_quality_toolkit kullanımı
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from data_quality_toolkit.designer import SyntheticDataGenerator

# OSB master listesi (companies.sql ile aynı)
OSB_LIST = [
    ("OSTİM OSB", "Yenimahalle", "karma"),
    ("İvedik OSB", "Yenimahalle", "karma"),
    ("ASO 1. OSB", "Sincan", "karma"),
    ("ASO 2-3 OSB", "Sincan", "karma"),
    ("Başkent OSB", "Kazan", "karma"),
    ("HAB OSB (Havaalanı)", "Yenimahalle", "ihtisas"),
    ("Dökümcüler OSB", "Sincan", "ihtisas"),
    ("Anadolu OSB", "Sincan", "karma"),
    ("Polatlı OSB", "Polatlı", "karma"),
]

# NACE C (İmalat) kodları — kısaltılmış liste
NACE_C_SECTORS = [
    ("25", "Metal ürünleri imalatı"),
    ("26", "Bilgisayar, elektronik, optik"),
    ("27", "Elektrikli teçhizat imalatı"),
    ("28", "Başka yerde sınıflandırılmamış makine"),
    ("29", "Motorlu kara taşıtı"),
    ("31", "Mobilya imalatı"),
    ("32", "Diğer imalat"),
]

COMPANY_SUFFIXES = ["A.Ş.", "Ltd. Şti.", "San. ve Tic. Ltd. Şti.", "Makina A.Ş."]
COMPANY_TYPES = ["anonim", "limited"]


def generate_osb_master():
    """OSB master kayıtlarını döndürür."""
    rows = []
    for name, district, osb_type in OSB_LIST:
        rows.append({
            "osb_id": str(uuid.uuid4()),
            "name": name,
            "city": "Ankara",
            "district": district,
            "osb_type": osb_type,
        })
    return rows


def generate_osb_firm(osb_id: str, n: int) -> list:
    """Belirli bir OSB için n firma üretir."""
    rows = []
    for i in range(n):
        sector_code, sector_name = random.choice(NACE_C_SECTORS)
        legal_name = f"{SyntheticDataGenerator.generate_valid_mock_tckn()[:6]} {sector_name.split()[0]} {random.choice(COMPANY_SUFFIXES)}"
        # Üretilen legal_name çok saçma olabilir, daha gerçekçi yap:
        sector_short = sector_name.split()[0][:8]
        legal_name = f"Ankara {sector_short} {random.choice(['Makina', 'Sanayi', 'Endüstri', 'Metal', 'Plastik'])} {random.choice(COMPANY_SUFFIXES)}"
        tax_number = SyntheticDataGenerator.generate_valid_mock_tckn() if random.random() < 0.7 else None
        employee = random.choice([5, 10, 15, 20, 30, 50, 75, 100, 150, 200, 300])
        # Kalite skoru
        dq_score = round(60 + random.random() * 35, 2)
        ec_score = round(70 + random.random() * 25, 2)
        now = datetime.utcnow().isoformat()
        rows.append({
            "company_id": str(uuid.uuid4()),
            "legal_name": legal_name,
            "trade_name": None,
            "company_type": random.choice(COMPANY_TYPES),
            "tax_number": tax_number,
            "mersis_number": None,
            "establishment_date": (datetime.now() - timedelta(days=random.randint(365, 7300))).date().isoformat(),
            "status": random.choices(["active", "inactive", "unknown"], weights=[0.80, 0.10, 0.10])[0],
            "status_confidence": round(50 + random.random() * 50, 2),
            "employee_count": employee,
            "website_domain": f"www.{legal_name.split()[1].lower() if len(legal_name.split())>1 else 'firma'}.com.tr" if random.random() < 0.5 else None,
            "primary_phone": f"+90 312 {random.randint(200, 599)} {random.randint(10, 99)} {random.randint(10, 99)}",
            "primary_email": f"info@{legal_name.split()[1].lower() if len(legal_name.split())>1 else 'firma'}.com.tr" if random.random() < 0.4 else None,
            "description": f"{sector_name} (NACE {sector_code})",
            "data_quality_score": dq_score,
            "entity_confidence": ec_score,
            "is_ankara": True,
            "is_osb_member": True,
            "osb_id": osb_id,
            "nace_validity": random.choices(["verified", "inferred", "unknown"], weights=[0.5, 0.3, 0.2])[0],
            "quarantine_reason": None,
            "first_seen_at": now,
            "last_verified_at": now,
            "created_at": now,
            "updated_at": now,
            "nace_code": sector_code,
        })
    return rows


def generate_non_osb_or_outside_ankara(n: int) -> list:
    """Test amaçlı MVP dışı kayıtlar — karantinaya düşecek."""
    rows = []
    for i in range(n):
        is_ankara = random.random() < 0.4
        rows.append({
            "company_id": str(uuid.uuid4()),
            "legal_name": f"Test Firma {i} {random.choice(COMPANY_SUFFIXES)}",
            "is_ankara": is_ankara,
            "is_osb_member": False,
            "data_quality_score": round(40 + random.random() * 30, 2),
            "quarantine_reason": "not_ankara" if not is_ankara else "not_osb_member",
        })
    return rows


def main():
    osbs = generate_osb_master()
    print(f"OSB master: {len(osbs)} kayıt")
    
    all_firms = []
    for osb in osbs:
        # OSB başına 12-20 firma
        n = random.randint(12, 20)
        firms = generate_osb_firm(osb["osb_id"], n)
        all_firms.extend(firms)
        print(f"  {osb['name']}: {n} firma")
    
    # Karantina test kayıtları
    quarantine_test = generate_non_osb_or_outside_ankara(50)
    print(f"Karantina test: {len(quarantine_test)} kayıt")
    
    print(f"\nToplam MVP firma: {len(all_firms)}")
    print(f"Toplam karantina: {len(quarantine_test)}")
    return osbs, all_firms, quarantine_test


if __name__ == "__main__":
    main()