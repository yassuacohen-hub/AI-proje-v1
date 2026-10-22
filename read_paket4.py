lines = open(r'c:\Huginn Data Projesi\Huginn Data Insights\src\company_master\paketler.py', encoding='utf-8').readlines()
for i, l in enumerate(lines):
    if 220 <= i <= 270:
        print(f"{i}: {l}", end='')