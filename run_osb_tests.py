import subprocess
import sys
import os

os.chdir(r'c:\Huginn Data Projesi\Huginn Data Insights')
result = subprocess.run(
    [sys.executable, '-m', 'pytest', 'tests/test_osb_master.py', '-v'],
    capture_output=True,
    text=True
)
print("STDOUT:")
print(result.stdout)
if result.stderr:
    print("STDERR:")
    print(result.stderr)
print(f"\nReturn code: {result.returncode}")