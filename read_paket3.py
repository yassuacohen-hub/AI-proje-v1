lines = open(r'c:\Huginn Data Projesi\Huginn Data Insights\src\company_master\paketler.py', encoding='utf-8').readlines()
for i, l in enumerate(lines):
    if '_ORJINAL_OZELLIKLER' in l or 'features' in l.lower() and i < 150:
        print(f"{i}: {l}", end='')