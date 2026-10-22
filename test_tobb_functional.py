#!/usr/bin/env python3
"""TOBB-01 Functional Test: search_by_vkn + bakiye"""
import sys
sys.path.insert(0, 'c:/Huginn Data Projesi/Huginn Data Insights')

from src.company_master.etl.tobb_api import search_by_vkn_sync, get_balance_sync

print("=" * 60)
print("TOBB-01 Functional Test")
print("=" * 60)

# Test 1: search_by_vkn with real VKN
print("\n[1] Testing search_by_vkn('7350835826')...")
try:
    result = search_by_vkn_sync('7350835826')
    print(f"   Status: {result.get('status', 'unknown')}")
    if result.get('status') == 'success':
        data = result.get('data', {})
        print(f"   Company: {data.get('company_title', 'N/A')}")
        print(f"   VKN: {data.get('company_vkn', 'N/A')}")
        print(f"   MERSIS: {data.get('mersis_number', 'N/A')}")
        print(f"   Trade Registry: {data.get('trade_registry_no', 'N/A')}")
        print(f"   Tax Office: {data.get('tax_office', 'N/A')}")
        print(f"   NACE Code: {data.get('nace_code', 'N/A')}")
        print(f"   NACE Name: {data.get('tobb_nace_name', 'N/A')}")
        print(f"   Website: {data.get('website', 'N/A')}")
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")
except Exception as e:
    print(f"   Exception: {e}")

# Test 2: get_balance
print("\n[2] Testing get_balance()...")
try:
    result = get_balance_sync()
    print(f"   Status: {result.get('status', 'unknown')}")
    if result.get('status') == 'success':
        data = result.get('data', {})
        print(f"   Balance: {data.get('balance_tl', 'N/A')} TL")
        print(f"   Remaining Queries: {data.get('remaining_queries', 'N/A')}")
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")
except Exception as e:
    print(f"   Exception: {e}")

print("\n" + "=" * 60)
print("TOBB-01 Functional Test Complete")
print("=" * 60)