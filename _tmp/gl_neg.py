import subprocess
from pathlib import Path

kok = Path("Huginn Data Insights")
gl = r"C:\Users\yasin\AppData\Local\Microsoft\WinGet\Packages\Gitleaks.Gitleaks_Microsoft.Winget.Source_8wekyb3d8bbwe\gitleaks.exe"
f = kok / "tests" / "gl_negatif_ornek.txt"
ad = "tests/gl_negatif_ornek.txt"
f.write_text("token = ghp_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8" + "\n", encoding="utf-8")
try:
    subprocess.run(["git", "add", ad], cwd=kok, check=True)
    rc = subprocess.run([gl, "git", "--staged", "--redact", "--no-banner", "."], cwd=kok,
                        capture_output=True, text=True).returncode
finally:
    subprocess.run(["git", "rm", "--cached", "-q", ad], cwd=kok)
    f.unlink()
assert rc == 1, f"kapi sahte token'i KACIRDI (rc={rc})"
print("NEGATIF TEST OK: sahte ghp_ token yakalandi, rc=1")
