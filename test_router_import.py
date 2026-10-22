import sys
sys.path.insert(0, r'c:\Huginn Data Projesi\Huginn Data Insights\src')
try:
    from company_master.api.routers.v1 import odeme
    print("Router import OK")
except Exception as e:
    print(f"Router import error: {e}")