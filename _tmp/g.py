"""file_locks.json okunuyor mu? IZIN_KILIT_ESIK tanimli mi? (olcum, kalici degil)"""
import pathlib
import re

KOK = pathlib.Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
ATLA = {".venv", ".git", "node_modules", "__pycache__", "_ARSIV_tek_kullanimlik",
        "yedekler", "backups", "logs", "data"}
IZIN = "IZIN_KILIT_ESIK"
KILIT = "file_locks"

okuyan, esik, kilit_oku = [], [], []
for p in sorted(KOK.rglob("*.py")):
    if ATLA & set(p.parts):
        continue
    try:
        t = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        continue
    rel = p.relative_to(KOK).as_posix()
    if KILIT in t:
        kilit_oku.append(rel)
    if IZIN in t:
        esik.append(rel)
    if re.search(r"def\s+\w*kilit\w*", t, re.I) or "KILIT_DOSYA" in t:
        okuyan.append(rel)

print("KILIT_DOSYA/file_locks gecen dosyalar:")
print("  ", okuyan or "YOK")
print("IZIN_KILIT_ESIK gecen dosyalar:")
print("  ", esik or "YOK")
print("kilit fonksiyonu/constant'i olan dosyalar:")
print("  ", kilit_oku or "YOK")