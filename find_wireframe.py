import os
root = r'c:\Huginn Data Projesi\Huginn Data Insights'
matches = []
for dirpath, dirnames, filenames in os.walk(root):
    for f in filenames:
        if 'WIREFRAME' in f.upper() or 'MUSTERI_PANEL' in f.upper():
            matches.append(os.path.join(dirpath, f))
print("Matches:", matches)