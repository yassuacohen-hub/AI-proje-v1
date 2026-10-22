import os, re

with open('Huginn Data Insights/docs/MUSTERI_PANEL_WIREFRAME_V11B_TURUNCU.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
lines = content.split('\n')

# Print lines 510-530 to see more of the card structure
print("=== More context (lines 510-540) ===")
for i in range(510, min(540, len(lines))):
    marker = ">> " if i == 509 else "   "
    print(f"{marker}Line {i}: {lines[i][:300]}")