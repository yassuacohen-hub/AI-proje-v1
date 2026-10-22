import shutil, os

src_dir = r'c:\Huginn Data Projesi\Huginn Data Insights'
dst_dir = r'c:\_ARSIV\sahte_teslim_yasu'

files = [
    'TESLIM_ANKARA-15-OSB-KOORDINAT-OLCUM-01.md',
    'TESLIM_DOK-STRATEJI-BAYAT-DUZELT-01.md',
    'TESLIM_MIMIR-RAPOR-DD-01.md',
    'TESLIM_RAPOR-STANDARTI-01.md',
    'TESLIM_SINYAL-3KAYNAK-TASARIM-01.md',
    'TESLIM_VERI-OSB-HARITA-01.md'
]

for f in files:
    src = os.path.join(src_dir, f)
    dst = os.path.join(dst_dir, f)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f'COPIED: {f}')
    else:
        print(f'NOT FOUND: {f}')

print('\\nDone. Files in destination:')
for f in os.listdir(dst_dir):
    print(f'  {f}')