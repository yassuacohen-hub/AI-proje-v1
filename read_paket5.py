lines = open(r'c:\Huginn Data Projesi\Huginn Data Insights\web_dashboard\tabs\paketler.py', encoding='utf-8').readlines()
for i, l in enumerate(lines):
    if '_features' in l:
        print(f"{i}: {l}", end='')