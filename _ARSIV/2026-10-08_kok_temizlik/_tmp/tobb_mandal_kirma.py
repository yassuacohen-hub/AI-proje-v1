"""Mandal kirma (D-256/4): ALANLAR'da Alan(2)/Alan(3) yer degistir -> pytest kirmizi -> geri al -> yesil."""
import subprocess, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
P = Path("src/company_master/etl/tobb_alan_haritasi.py")
A, B = "    Alan(2, 'Merkez', 'Unvani'),\n    Alan(3, 'Merkez', 'IsletmeAdi'),\n", "    Alan(2, 'Merkez', 'IsletmeAdi'),\n    Alan(3, 'Merkez', 'Unvani'),\n"
orj = P.read_text(encoding="utf-8")
assert A in orj

def kos(etiket):
    r = subprocess.run([sys.executable, "-m", "pytest", "tests/test_tobb_alan_haritasi.py", "-q", "--no-header", "-p", "no:cacheprovider"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    son = [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l]
    print(f"{etiket}: exit={r.returncode} {son[-1] if son else r.stdout[-300:]}")
    return r.returncode

try:
    y1 = kos("1) ONCE")
    P.write_text(orj.replace(A, B), encoding="utf-8")
    k = kos("2) SWAP Alan2<->Alan3")
finally:
    P.write_text(orj, encoding="utf-8")
y2 = kos("3) GERI ALINDI")
ok = y1 == 0 and k != 0 and y2 == 0
print("MANDAL", "KIRILDI+ONARILDI OK" if ok else "BASARISIZ")
sys.exit(0 if ok else 1)
