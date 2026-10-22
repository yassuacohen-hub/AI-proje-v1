lines = open(r'c:\Huginn Data Projesi\Huginn Data Insights\web_dashboard\tabs\paketler.py', encoding='utf-8').readlines()
with open(r'c:\Huginn Data Projesi\output2.txt', 'w', encoding='utf-8') as f:
    for i, l in enumerate(lines):
        if 358 <= i <= 380:
            f.write(f"{i}: {l}")