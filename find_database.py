import os
for root, dirs, files in os.walk(r'c:\Huginn Data Projesi'):
    for f in files:
        if 'database' in f.lower():
            print(os.path.join(root, f))