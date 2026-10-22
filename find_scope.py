import sys
sys.path.insert(0, r'c:\Huginn Data Projesi\Huginn Data Insights\src')

import importlib
try:
    mod = importlib.import_module('company_master.core.scope')
    print(f"Found: {mod.__file__}")
except ModuleNotFoundError as e:
    print(f"Not found: {e}")
    
# Also try to find scope module
import os
base = r'c:\Huginn Data Projesi\Huginn Data Insights\src\company_master'
for root, dirs, files in os.walk(base):
    for f in files:
        if 'scope' in f.lower():
            print(f"Found file: {os.path.join(root, f)}")