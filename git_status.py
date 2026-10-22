import subprocess
import os

os.chdir(r'c:\Huginn Data Projesi')

result = subprocess.run(['git', 'status'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)