import os
p = r"c:\Huginn Data Projesi\Huginn Data Insights\frontend\src\app"
for root, dirs, files in os.walk(p):
    for f in files:
        print(os.path.join(root, f))