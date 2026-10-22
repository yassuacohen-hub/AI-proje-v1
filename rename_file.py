import os
import shutil

src = r'c:\Huginn Data Projesi\Huginn Data Insights\src\company_master\api\routers\v1\v1_network.py'
dst = r'c:\Huginn Data Projesi\Huginn Data Insights\src\company_master\api\routers\v1\network_router.py'

shutil.move(src, dst)
print(f"Moved {src} to {dst}")