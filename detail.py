import re
with open(r'Huginn Data Insights/docs/MUSTERI_PANEL_WIREFRAME_V11B_TURUNCU.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
lines = content.split('\n')
# Print lines 514-560 to see the w-sirket widget
with open('sirket_detail.txt', 'w', encoding='utf-8') as out:
    for i in range(514, min(560, len(lines))):
        out.write(f"Line {i+1}: {lines[i][:350]}\n")
print("Written to sirket_detail.txt")