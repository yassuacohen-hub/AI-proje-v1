with open('Huginn Data Insights/docs/MUSTERI_PANEL_WIREFRAME_V11B_TURUNCU.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
lines = content.split('\n')
# Print lines 340-380 to see the Fırsatlar widget
with open('firsat_detail.txt', 'w', encoding='utf-8') as out:
    for i in range(340, min(380, len(lines))):
        out.write(f"Line {i+1}: {lines[i][:350]}\n")
print("Written to firsat_detail.txt")