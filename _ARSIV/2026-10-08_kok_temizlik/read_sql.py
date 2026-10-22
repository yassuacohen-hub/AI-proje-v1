import os
base = r'c:\Huginn Data Projesi\Huginn Data Insights'
p = os.path.join(base, 'src', 'company_master', 'schema', 'companies.sql')
with open(p, encoding='utf-8') as f:
    lines = f.readlines()
for i in range(107, 125):
    if i < len(lines):
        print(f'{i+1}: {lines[i].rstrip()}')