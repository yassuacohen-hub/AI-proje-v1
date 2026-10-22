import os, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
def ps(s):
    sys.stdout.write(str(s).encode("ascii","replace").decode()+"\n")

kok = "c:\\Huginn Data Projesi"
ins = "c:\\Huginn Data Projesi\\Huginn Data Insights"
dosyalar = [
    os.path.join(kok, f) for f in (
        "gate_check.py","check_ux02.py","find_msgs.py","read_bd.py","read_bd2.py",
        "read_bd3.py","read_range.bat","read_tr.py","read_tr2.py","verify_gates.py",
        "fix_msgs.py","teslim_run.py","onay_run.py","verify_done.py",
    )
] + [os.path.join(ins, "find_ux02.py")]
for d in dosyalar:
    if os.path.exists(d):
        os.remove(d)
        ps("silindi: " + d)
    else:
        ps("yok (atlandi): " + d)

# messages.jsonl duzeltmesini kanona isle (teslim kapisi icin isaretlenen mesajlar)
msg_rel = "Huginn Data Insights/data/orchestrator/chat/messages.jsonl"
r = subprocess.run(["git", "add", "--", msg_rel],
                   cwd=kok, capture_output=True, text=True, encoding="utf-8", errors="replace")
ps("git add rc=" + str(r.returncode))
if r.stderr: ps("add stderr: " + r.stderr.strip())
r = subprocess.run(["git", "commit", "-q", "-m",
                    "D-210: PANEL-MIMIR-UX-02 4 cevapsiz ihsan mesaji yasu tarafindan isaretlendi cozuldu",
                    "--", msg_rel],
                   cwd=kok, capture_output=True, text=True, encoding="utf-8", errors="replace")
ps("git commit rc=" + str(r.returncode))
if r.stdout: ps(r.stdout)
if r.stderr: ps("stderr: " + r.stderr)
ps("done")