import sys
import os

base = "c:/Huginn Data Projesi/Huginn Data Insights"
sys.path.insert(0, base)  # Add the base to sys.path
sys.path.insert(0, os.path.join(base, "src"))  # Add src to sys.path

print("sys.path:", sys.path[:3])

try:
    import company_master.etl.gece_besleme
    print("IMPORT SUCCESS: module loaded")
    print("Module has besleme_listesi:", hasattr(company_master.etl.gece_besleme, 'besleme_listesi'))
    print("Module has besleme_butcesi:", hasattr(company_master.etl.gece_besleme, 'besleme_butcesi'))
    print("Module has MAKS_BESLEME:", hasattr(company_master.etl.gece_besleme, 'MAKS_BESLEME'))
    
    # Test the functions
    result = company_master.etl.gece_besleme.besleme_listesi(limit=5)
    print("besleme_listesi result:", result)
    
    butce = company_master.etl.gece_besleme.besleme_butcesi(250)
    print("besleme_butcesi(250):", butce)
    
except Exception as e:
    print("IMPORT ERROR:", e)
    import traceback
    traceback.print_exc()