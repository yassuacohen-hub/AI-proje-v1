"""stash@{0} icindeki D-318 ve TSG islerini geri yukler.

Ne oluyor:
  Kirisi, ortak calisma agacinda (stash ekledikten sonra) calistigi icin
  dosyalarini calisma agacinda birakmis olabilir. `git stash apply` TUM
  dosyalari geri alir ve 40 dosyada elmasiz; kismi uygulama bu isi
  bitiremez.

  Bu script SADECE kaybolmus **uretim kodu** dosyalarini geri yukler:
    skills/services/ticaret_sicili_kanit.py   (olay_esle, ILAN_TURU_ESLEME, _TR_ASCII)
    scripts/gorev_kutusu.py                  (D-318 teslim kapisi + import)

  Veri dosyalari (onay_kuyrugu.json, tetikler, pano) **dokunulmaz** —
  onlar orkestrator alani (D-77) ve baska ajanlarin commit'leriyle degismis
  olabilir; eski haline dondurmek kayip yaratir.

Once yedek alir, sonra yazar, sonra test ile dogrular.
Idempotent: ikinci kosusta ayni sonucu verir.
"""

import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
STASH = "stash@{0}"
YEDEK = ROOT / "yedekler" / "geri_yukleme_oncesi_yedek"

# Sadece uretim kodu. Veri/orchestrator dosyalari kasten disarida.
HEDEFLER = [
    "skills/services/ticaret_sicili_kanit.py",
    "scripts/gorev_kutusu.py",
]

ZORUNLU_ISARETLER = {
    "skills/services/ticaret_sicili_kanit.py": ["def olay_esle", "ILAN_TURU_ESLEME"],
    "scripts/gorev_kutusu.py": ["D-318 BULGU KAPISI", "bulgu_defteri"],
}


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout


print("=== 1) ONCE KEDERI AL ===")
YEDEK.mkdir(parents=True, exist_ok=True)
for rel in HEDEFLER:
    kaynak = ROOT / rel
    if not kaynak.exists():
        print(f"  [ATLA] {rel} diskte yok")
        continue
    hedef = YEDEK / rel.replace("/", "__")
    if hedef.exists():
        print(f"  [VAR]  {rel} yedegi zaten var -> degistirilmedi")
        continue
    hedef.write_bytes(kaynak.read_bytes())
    print(f"  [AL]   {rel} -> yedekler/geri_yukleme_oncesi_yedek/{hedef.name}")

print("\n=== 2) STASH'TAN GERI YUKLE ===")
for rel in HEDEFLER:
    icerik = git("show", f"{STASH}:{rel}")
    if not icerik:
        print(f"  [HATA] {rel} stash'ta bulunamadi")
        continue

    eksik = [i for i in ZORUNLU_ISARETLER[rel] if i not in icerik]
    if eksik:
        print(f"  [RED]  {rel} stash surumu isaretleri tasimiyor: {eksik}")
        continue

    hedef = ROOT / rel
    canli = hedef.read_text(encoding="utf-8", errors="replace") if hedef.exists() else ""
    if canli == icerik:
        print(f"  [AYNI] {rel} zaten stash surumuyle ayni (idempotent)")
        continue

    # satir sonu turlari: git show her zaman \n verir
    hedef.write_text(icerik, encoding="utf-8", newline="\n")
    print(f"  [YAZ]  {rel} ({len(icerik.splitlines())} satir)")

print("\n=== 3) DOGRULAMA ===")
for rel in HEDEFLER:
    icerik = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
    durum = []
    for isaret in ZORUNLU_ISARETLER[rel]:
        durum.append(f"{isaret}={'VAR' if isaret in icerik else 'YOK'}")
    print(f"  {rel}: {', '.join(durum)}")

print("\n=== 4) SOZDIZIMI ===")
for rel in HEDEFLER:
    r = subprocess.run([sys.executable, "-m", "py_compile", str(ROOT / rel)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(f"  {rel}: {'OK' if r.returncode == 0 else 'HATA ' + r.stderr.strip()[-200:]}")

print("\n=== 5) IMPORT KONTROLU ===")
r = subprocess.run(
    [sys.executable, "-X", "utf8", "-c",
     "import sys; sys.path.insert(0, '.');"
     "from skills.services.ticaret_sicili_kanit import olay_esle, ILAN_TURU_ESLEME, _asciiye;"
     "print('IMPORT OK | anahtar:', len(ILAN_TURU_ESLEME),"
     "| asciiye(Artirimi):', _asciiye('Artırımı'),"
     "| olay_esle(SUBE ACILIS):', olay_esle('SUBE ACILIS'))"],
    capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(ROOT),
)
print("  " + (r.stdout.strip() or r.stderr.strip()[-300:]))
