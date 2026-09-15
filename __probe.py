import io

path = r"C:\Huginn Data Projesi\Huginn Data Insights\tabs\admin_auto_refresh.py"
import os
if not os.path.exists(path):
    path = r"C:\Huginn Data Projesi\Huginn Data Insights\tabs\admin_auto_refresh.py"
    # try web_dashboard/tabs
    alt = r"C:\Huginn Data Projesi\Huginn Data Insights\tabs\admin_auto_refresh.py"
    alt2 = r"C:\Huginn Data Projesi\Huginn Data Insights\tabs\admin_auto_refresh.py"
    print("trying", alt)
    print("exists:", os.path.exists(alt))
    print("exists2:", os.path.exists(alt2))
