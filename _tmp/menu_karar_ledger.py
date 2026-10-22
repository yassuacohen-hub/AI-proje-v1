import subprocess, sys
r = subprocess.run(
    [sys.executable, "-X", "utf8", "scripts/bulgu_defteri.py", "ekle",
     "--task-id", "MUSTERI-PANEL-MENU-KARAR-01",
     "--rol", "ihsan",
     "--ozet", "PO menu karari A: 4 gercek sayfa, 3 yakinda hayaleti menuden cikacak (kod ertelendi, utku T0-T2). PO 'bakimda' onerisi degerlendirildi, reddedildi (bakimda=var olan bozuk anlami; yol: menu disi Yakinda karti). Canli menu olculemedi (401), kaynak HEAD: 7 oge/3 yakinda.",
     "--karar", "WIREFRAME_T0 s2.1 + ORTAK s9.3 not; kod degismedi; iskelet-sozlesmesi.test K3 RED kalir (D-224)"],
    cwd=r"c:/Huginn Data Projesi/Huginn Data Insights", capture_output=True, text=True, encoding="utf-8")
print(r.returncode, r.stdout, r.stderr)
