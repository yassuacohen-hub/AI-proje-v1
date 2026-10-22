import os, re

with open('Huginn Data Insights/docs/MUSTERI_PANEL_WIREFRAME_V11B_TURUNCU.html', 'r', encoding='utf-8') as f:
    content = f.read()
lines = content.split('\n')

# Print lines around "Radardaki" mentions
print("=== Looking for 'Radardaki' or 'radardaki' ===")
for i, line in enumerate(lines):
    if 'radardaki' in line.lower() or 'radar' in line.lower():
        # Print context: 3 lines before and after
        start = max(0, i-3)
        end = min(len(lines), i+4)
        print(f"\n--- Line {i} ---")
        for j in range(start, end):
            marker = ">> " if j == i else "   "
            print(f"{marker}Line {j}: {lines[j][:120]}")

# Also look for widget/card sections 
print("\n=== Looking for widget card structure ===")
for i, line in enumerate(lines):
    if 'kutu' in line.lower() and ('radar' in lines[i-1].lower() or 'widget' in lines[i-1].lower() or 'card' in lines[i-1].lower()):
        start = max(0, i-2)
        end = min(len(lines), i+3)
        print(f"\n--- Around line {i} ---")
        for j in range(start, end):
            marker = ">> " if j == i else "   "
            print(f"{marker}Line {j}: {lines[j][:150]}")