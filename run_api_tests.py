import subprocess
import os
import sys

os.chdir(r'c:\Huginn Data Projesi\Huginn Data Insights')

result = subprocess.run(
    [sys.executable, '-m', 'pytest', 'tests/test_api_v1_network.py', '-v', '--tb=short'],
    capture_output=True,
    text=True
)

print("STDOUT:")
print(result.stdout)
if result.stderr:
    print("STDERR:")
    print(result.stderr)
print(f"\nReturn code: {result.returncode}")