import os

root = r"c:\Huginn Data Projesi\Huginn Data Insights"
for dirpath, dirnames, filenames in os.walk(root):
    for f in filenames:
        if 'odeme' in f.lower() or 'api' in f.lower():
            print(os.path.join(dirpath, f))
    if len(filenames) > 0:
        for f in filenames[:5]:
            pass