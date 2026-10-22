with open('Huginn Data Insights/docs/MUSTERI_PANEL_WIREFRAME_V11B_TURUNCU.html', 'rb') as f:
    raw = f.read()

# ponytail: chardet yerine utf-8-sig/utf-8 denemesi; dosya BOM'lu veya duz UTF-8.
# Baska kodlama cikarsa chardet kurulur.
content = raw.decode('utf-8-sig', errors='replace')
lines = content.split('\n')

# Search for "Radardaki Şirket" or similar
print("=== Searching for 'Radardaki' ===")
for i, line in enumerate(lines):
    if 'radar' in line.lower() and ('şirket' in line.lower() or 'sirket' in line.lower() or 'company' in line.lower()):
        start = max(0, i-2)
        end = min(len(lines), i+3)
        print(f"\n--- Around line {i} (Radardaki Şirket?) ---")
        for j in range(start, end):
            marker = ">> " if j == i else "   "
            print(f"{marker}Line {j}: {lines[j][:200]}")

# Also look for "KPI" related to radar
print("\n=== Searching for KPI + radar combination ===")
for i, line in enumerate(lines):
    if 'kpi' in line.lower() and ('radar' in lines[i-1].lower() or 'radar' in lines[i+1].lower() or i > 0 and 'radar' in lines[i-1].lower()):
        start = max(0, i-2)
        end = min(len(lines), i+3)
        print(f"\n--- Around line {i} (KPI+radar) ---")
        for j in range(start, end):
            marker = ">> " if j == i else "   "
            print(f"{marker}Line {j}: {lines[j][:200]}")