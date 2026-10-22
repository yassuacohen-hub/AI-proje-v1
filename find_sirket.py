import re
with open(r'Huginn Data Insights/docs/MUSTERI_PANEL_WIREFRAME_V11B_TURUNCU.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
lines = content.split('\n')
# Find line numbers containing w-sirket
for i, line in enumerate(lines):
    if 'w-sirket' in line.lower():
        print(f'Line {i+1}: {line[:200]}')