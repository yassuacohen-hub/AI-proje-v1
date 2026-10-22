# -*- coding: utf-8 -*-
import sys, subprocess, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
# Dikkat: Windows'ta drive letter CASE'i vitest iki instance'a bozuyor
# (vitest #10692 / PR #10843): CLI kucuk harf 'c:\' ile yuklenirse
# Vite'in 'C:/' normalize'u ile ayni degil -> collector bos kalir.
# Bu yuzden BÜYÜK HARF drive ile calistiriyoruz.
R = r"C:\Huginn Data Projesi\Huginn Data Insights\frontend"
assert R[1] == ":", R
args = ["npx.cmd", "vitest", "run"] + (sys.argv[1:] or ["app/firma"])
p = subprocess.run(args, cwd=R, capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
print(p.stdout[-4000:] if p.stdout else "")
print("STDERR:", p.stderr[-2500:] if p.stderr else "")
print("rc =", p.returncode)


