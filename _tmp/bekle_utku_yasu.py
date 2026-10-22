"""utku/yasu hakem_v12 dosyası değişene kadar (max 14 dk) bekler. ponytail: polling 30sn; olay tabanlı izleme gerekmez."""
import os
import subprocess
import time

D = "data/orchestrator/hakem_v12/"
F = ["utku.md", "yasu.md"]
base = {x: os.path.getmtime(D + x) for x in F}
t0 = time.time()
r = ""
while time.time() - t0 < 840:
    time.sleep(30)
    subprocess.run("git fetch -q origin chore/monorepo-merge", shell=True)
    r = subprocess.run(
        "git log origin/chore/monorepo-merge --format=%h_%s -6 -- data/orchestrator/hakem_v12/",
        shell=True, capture_output=True, text=True,
    ).stdout
    ch = [x for x in F if os.path.getmtime(D + x) != base[x]]
    if len(ch) == 2 or ("utku" in r and "yasu" in r):
        break
print("degisen:", [(x, os.path.getsize(D + x)) for x in F if os.path.getmtime(D + x) != base[x]])
print("sure_sn:", int(time.time() - t0))
print(r)
