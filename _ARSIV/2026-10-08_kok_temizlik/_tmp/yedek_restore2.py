# -*- coding: utf-8 -*-
"""Geri yukleme testi v2: decompress -> dosyaya yaz (TEMP) -> psql -f ile yukle (timeout'lu, pipe degil).
Onceki surum (stdin pipe, buyuk string) ~36 dk asilip kaldi; bu surum dosyadan okutur + sure siniri koyar."""
import gzip, os, shutil, subprocess, sys, tempfile, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BIN = r"C:\Program Files\PostgreSQL\17\bin"
PORT = "54330"
yedek = sys.argv[1]
kume = tempfile.mkdtemp(prefix="huginn_restore2_")
dump_sql = os.path.join(kume, "dump.sql")
env = {**os.environ}


def run(args, timeout=60, **k):
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace",
                        env=env, timeout=timeout, **k)
    return r


print("1) gzip -> dosya acma")
t0 = time.time()
with gzip.open(yedek, "rt", encoding="utf-8", errors="replace") as f, open(dump_sql, "w", encoding="utf-8") as out:
    shutil.copyfileobj(f, out)
print(f"   {os.path.getsize(dump_sql)/1024:.0f} KB, {time.time()-t0:.1f}s")

try:
    if os.path.exists(kume):
        shutil.rmtree(kume, ignore_errors=True)
    print("2) initdb")
    r = run([os.path.join(BIN, "initdb.exe"), "-D", kume, "-U", "postgres", "-A", "trust", "-E", "UTF8", "--locale=C"], timeout=60)
    print("   rc=", r.returncode, r.stderr[-300:] if r.returncode else "")
    print("3) pg_ctl start")
    r = run([os.path.join(BIN, "pg_ctl.exe"), "-D", kume, "-o", f"-p {PORT} -c listen_addresses=127.0.0.1", "-l", os.path.join(kume, "log.txt"), "start", "-w"], timeout=30)
    print("   rc=", r.returncode, r.stdout, r.stderr[-500:])
    if os.path.exists(os.path.join(kume, "log.txt")):
        print("   log.txt:", open(os.path.join(kume, "log.txt"), encoding="utf-8", errors="replace").read()[-800:])
    psql = [os.path.join(BIN, "psql.exe"), "-h", "127.0.0.1", "-p", PORT, "-U", "postgres", "-v", "ON_ERROR_STOP=0", "-q"]
    print("4) createdb")
    r = run(psql + ["-d", "postgres", "-c", "CREATE DATABASE restore_test;"], timeout=30)
    print("   rc=", r.returncode, r.stderr[-300:] if r.returncode else "")
    print("5) psql -f dump.sql (timeout=240s)")
    t0 = time.time()
    try:
        r = run(psql + ["-d", "restore_test", "-f", dump_sql], timeout=240)
        hata = [l for l in r.stderr.splitlines() if "ERROR" in l]
        print(f"   bitti {time.time()-t0:.0f}s, returncode={r.returncode}, hata satiri={len(hata)}")
        print("   stdout_son:", r.stdout[-300:])
        print("   stderr_son:", r.stderr[-1500:])
        for l in hata[:15]:
            print("   ", l[:160])
    except subprocess.TimeoutExpired:
        print(f"   ZAMAN ASIMI >{time.time()-t0:.0f}s (240s siniri) -- restore tamamlanmadi")
        raise SystemExit(2)
    q = ("SELECT 'companies',count(*) FROM public.companies UNION ALL "
         "SELECT 'field_dictionary',count(*) FROM public.field_dictionary UNION ALL "
         "SELECT 'schema_migrations',count(*) FROM public.schema_migrations UNION ALL "
         "SELECT 'tablo_sayisi',count(*)::text FROM information_schema.tables WHERE table_schema='public';")
    r = run(psql + ["-d", "restore_test", "-At", "-c", q], timeout=30)
    print("6) SONUC:\n" + r.stdout)
finally:
    try:
        run([os.path.join(BIN, "pg_ctl.exe"), "-D", kume, "stop", "-m", "immediate"], timeout=30)
    except Exception as e:
        print("durdurma hatasi:", e)
    shutil.rmtree(kume, ignore_errors=True)
    print("gecici kume silindi:", kume, "-- kaldi" if os.path.exists(kume) else "-- OK")
