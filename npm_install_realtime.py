import subprocess
import sys
import time

print("npm install baslatiliyor...")
start = time.time()
proc = subprocess.Popen(
    "npm install",
    cwd=r"c:\Huginn Data Projesi\Huginn Data Insights\frontend",
    shell=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
)

# Real-time output
for line in proc.stdout:
    print(line.rstrip())

proc.wait()
elapsed = time.time() - start
print(f"\n=== BITTI (KOD: {proc.returncode}, sure: {elapsed:.1f}s) ===")