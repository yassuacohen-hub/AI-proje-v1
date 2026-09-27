#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify database connection and basic data loading.
"""

import sys
import os
from pathlib import Path

# .env dosyasını yükle
from dotenv import load_dotenv
load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[3]
XLSX_PATH = PROJECT_ROOT / "data" / "nace" / "sektor_meslek_nace_2026-05_resmi.xlsx"
DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    raise ValueError("DATABASE_URL environment variable not set. Please check .env file.")

from sqlalchemy import create_engine, text

def get_engine():
    return create_engine(DB_URL)

def main():
    print("Testing database connection...")
    engine = create_engine(os.getenv("DATABASE_URL"))
    with create_engine(DB_URL).connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
        print(f"Database connection OK: {result}")

        # Check nace_codes table
        result = conn.execute(text("SELECT COUNT(*) FROM nace_codes")).scalar()
        print(f"Current nace_codes count: {result}")

if __name__ == "__main__":
    main()
