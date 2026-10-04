"""9Router anahtar betigi - gecici dosya uzerinde dogrulama (GERCEK .env'E DOKUNMAZ)."""
import importlib.util
import pathlib
import sys
import tempfile

BETIK = pathlib.Path(r"c:\Huginn Data Projesi\Huginn Data Insights\scripts"
                     r"\ninerouter_anahtar_guncelle.py")
spec = importlib.util.spec_from_file_location("nr9", BETIK)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

GIZLI = "ntn_TEST_GIZLI_1234567890"
with tempfile.TemporaryDirectory() as d:
    env = pathlib.Path(d) / ".env"
    env.write_text("A=1\nNINEROUTER_KEY=eski\nB=2\n", encoding="utf-8")

    yedek, adet, maske = m._guncelle(env, GIZLI)
    sonuc = env.read_text(encoding="utf-8")

    print("--- sonuc ---")
    print(sonuc.replace(GIZLI, "<GIZLI>"))
    print("adet   :", adet)
    print("maske  :", maske)
    print("yedek var:", yedek.exists())
    print("--- kontroller ---")
    print("anahtar yazildi :", GIZLI in sonuc)
    print("eski anahtar yok :", "eski" not in sonuc)
    print("satir sayisi 3   :", len(sonuc.strip().splitlines()) == 3)
    print("A ve B korundu   :", "A=1" in sonuc and "B=2" in sonuc)
    print("sifre maskede    :", GIZLI not in maske)
    print("sifre yedekte    :", GIZLI in yedek.read_text(encoding="utf-8"))
    print("bitis newline    :", sonuc.endswith("\n"))

    # idempotans: ayni anahtari 2 kez yaz
    y2, a2, _ = m._guncelle(env, GIZLI)
    s2 = env.read_text(encoding="utf-8")
    print("idempotans (1 satir):", len([x for x in s2.splitlines()
                                       if x.startswith("NINEROUTER_KEY=")]) == 1)

sys.exit(0)