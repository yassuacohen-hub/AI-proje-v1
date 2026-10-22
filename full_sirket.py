import re
with open(r'Huginn Data Insights/docs/MUSTERI_PANEL_WIREFRAME_V11B_TURUNCU.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
lines = content.split('\n')
# Print lines 514-560 to see the w-sirket widget
for i in range(514, min(560, len(lines))):
    marker = ">> " if i == 514 else ("* " if i < len(lines) else "   ")
    print(f"Line {i+1}: {lines[i][:350]}")