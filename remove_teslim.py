import os, glob
for f in glob.glob(r'c:\Huginn Data Projesi\Huginn Data Insights\TESLIM_*.md'):
    os.remove(f)
    print(f'REMOVED: {f}')
print('\\nDone. Remaining files in Huginn Data Insights:')
for f in os.listdir(r'c:\Huginn Data Projesi\Huginn Data Insights'):
    print(f'  {f}')