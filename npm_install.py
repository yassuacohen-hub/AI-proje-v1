import subprocess
import sys
result = subprocess.run("npm install", cwd=r"c:\Huginn Data Projesi\Huginn Data Insights\frontend", shell=True, capture_output=True, text=True, timeout=600)
print(result.stdout[-2000:])
print(result.stderr[-1000:])
print("KOD:", result.returncode)