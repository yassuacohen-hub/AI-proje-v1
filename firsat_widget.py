with open('Huginn Data Insights/docs/MUSTERI_PANEL_WIREFRAME_V11B_TURUNCU.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
lines = content.split('\n')
# Print lines 456-510 to see the w-firsat widget
with open('firsat_widget.txt', 'w', encoding='utf-8') as out:
    for i in range(456, min(510, len(lines))):
        out.write(f"Line {i+1}: {lines[i][:350]}\n")
print("Written to firsat_widget.txt")