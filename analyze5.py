import os, re

with open('Huginn Data Insights/docs/MUSTERI_PANEL_WIREFRAME_V11B_TURUNCU.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
lines = content.split('\n')

# Print lines 500-530 to see the Radardaki Şirket card
print("=== Radardaki Şirket KPI Card (lines 500-530) ===")
for i in range(500, min(530, len(lines))):
    marker = ">> " if i == 509 else "   "
    print(f"{marker}Line {i}: {lines[i][:250]}")