import os, re

with open('Huginn Data Insights/docs/MUSTERI_PANEL_WIREFRAME_V11B_TURUNCU.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
lines = content.split('\n')

# Print lines 513-560 to see the w-sirket widget
print("=== w-sirket widget (lines 513-560) ===")
for i in range(513, min(560, len(lines))):
    marker = ">> " if i == 513 else "   "
    print(f"{marker}Line {i}: {lines[i][:350]}")