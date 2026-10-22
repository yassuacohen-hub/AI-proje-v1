# Yalniz anahtar ADI + dolu/bos; DEGER yazdirilmaz (D-380).
import re
import subprocess
from pathlib import Path

ROOT = Path(r"c:/Huginn Data Projesi")
DOSYALAR = [ROOT / ".env", ROOT / "Huginn Data Insights" / ".env"]
DESEN = re.compile(r"MAIL|SMTP|RESEND|SENDGRID|MAILGUN|POSTMARK|BREVO|SES_|EMAIL", re.I)

for d in DOSYALAR:
    print("==", d, "var" if d.exists() else "YOK")
    if not d.exists():
        continue
    for ln in d.read_text(encoding="utf-8", errors="replace").splitlines():
        if "=" not in ln or ln.lstrip().startswith("#"):
            continue
        ad, _, deger = ln.partition("=")
        if DESEN.search(ad):
            print("  ", ad.strip(), "DOLU" if deger.strip().strip("'\"") else "BOS")

for repo in (ROOT, ROOT / "Huginn Data Insights"):
    r = subprocess.run(["git", "ls-files", "--error-unmatch", ".env"], cwd=repo, capture_output=True, text=True)
    i = subprocess.run(["git", "check-ignore", "-q", ".env"], cwd=repo)
    print(repo.name, ".env izleniyor:", r.returncode == 0, "| ignore:", i.returncode == 0)
