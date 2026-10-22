import os
import shutil
p = r"c:\Huginn Data Projesi\Huginn Data Insights\frontend"
for d in ['.next', 'node_modules/.cache', 'node_modules/.cache/typescript']:
    dpath = os.path.join(p, d)
    if os.path.exists(dpath):
        shutil.rmtree(dpath)
        print(f"silindi: {d}")
print("temizlendi")