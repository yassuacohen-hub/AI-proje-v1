import subprocess
import os
import sys

p = r"c:\Huginn Data Projesi\Huginn Data Insights\frontend"
next_dir = os.path.join(p, ".next")
if os.path.exists(next_dir):
    import shutil
    shutil.rmtree(next_dir)
    print("eski .next silindi")

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
print(f"\n=== BITTI (KOD: {proc.returncode}) ===")