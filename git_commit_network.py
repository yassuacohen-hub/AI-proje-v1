import subprocess
import os

os.chdir(r'c:\Huginn Data Projesi')

# Add the specific files for API-V1-NETWORK-REPORT-01
# Note: Huginn Data Insights is a submodule, so we need to cd into it
files_to_add = [
    'Huginn Data Insights/src/company_master/api/routers/v1/network_router.py',
    'Huginn Data Insights/src/company_master/api/routers/v1/__init__.py',
    'Huginn Data Insights/src/company_master/api/routers/v1/fraud.py',
    'Huginn Data Insights/tests/test_api_v1_network.py',
    'Huginn Data Insights/web_app.py',
]

for file_path in files_to_add:
    if os.path.exists(file_path):
        subprocess.run(['git', 'add', file_path], check=True)
        print(f'Added: {file_path}')
    else:
        print(f'Warning: File not found: {file_path}')

# Commit
commit_msg = 'VERI-OSB-MASTER-LISTE-01: OSB master 9→15 migration + seed + source_registry + tests + backup + network_router integration'
result = subprocess.run(['git', 'commit', '-m', commit_msg], capture_output=True, text=True)
print('Commit output:')
print(result.stdout)
if result.stderr:
    print('Commit stderr:')
    print(result.stderr)

# Push
result = subprocess.run(['git', 'push', 'origin', 'HEAD'], capture_output=True, text=True)
print('Push output:')
print(result.stdout)
if result.stderr:
    print('Push stderr:')
    print(result.stderr)