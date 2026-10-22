import subprocess
import sys
import time

print("npm run build baslatiliyor...")
start = time.time()
proc = subprocess.Popen(
    "npm run build",
    cwd=r"c:\Huginn Data Projesi\Huginn Data Insights\frontend",
    shell=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
)

for line in proc.stdout:
    print(line.rstrip())

proc.wait()
elapsed = time.time() - start
print(f"\n=== BITTI (KOD: {proc.returncode}, sure: {elapsed:.1f}s) ===")