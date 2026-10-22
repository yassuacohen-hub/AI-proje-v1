import sys
sys.path.insert(0, "c:/Huginn Data Projesi/Huginn Data Insights")
try:
    from company_master.etl.gece_besleme import besleme_listesi, besleme_butcesi, MAKS_BESLEME
    print("IMPORT SUCCESS")
    print("besleme_listesi:", besleme_listesi)
    print("besleme_butcesi:", besleme_butcesi)
    print("MAKS_BESLEME:", MAKS_BESLEME)
except Exception as e:
    print("IMPORT ERROR:", e)
    import traceback
    traceback.print_exc()