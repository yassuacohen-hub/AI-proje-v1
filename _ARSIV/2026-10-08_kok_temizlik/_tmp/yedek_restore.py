# -*- coding: utf-8 -*-
"""Geri yukleme testi: gecici PostgreSQL 17 kumesi (initdb, port 54329) -> psql ile yedek yukle -> satir say -> kume kaldir.
Diske yalniz %TEMP% altina yazar, canli DB'ye dokunmaz (D-243)."""
import gzip, os, shutil, subprocess, sys, tempfile, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BIN = r"C:\Program Files\PostgreSQL\17\bin"
PORT = "54329"
yedek = sys.argv[1]
kume = tempfile.mkdtemp(prefix="huginn_restore_")
env = {**os.environ, "PGPASSWORD": "x"}
def run(*a, **k):
    r = subprocess.run(a, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, **k)
    if r.returncode and not k.get("input"):
        print("HATA", a[0], r.stderr[-800:]); sys.exit(1)
    return r
try:
    run(os.path.join(BIN, "initdb.exe"), "-D", kume, "-U", "postgres", "-A", "trust", "-E", "UTF8", "--locale=C")
    run(os.path.join(BIN, "pg_ctl.exe"), "-D", kume, "-o", f"-p {PORT} -c listen_addresses=127.0.0.1", "-l", os.path.join(kume, "log.txt"), "start", "-w")
    psql = [os.path.join(BIN, "psql.exe"), "-h", "127.0.0.1", "-p", PORT, "-U", "postgres", "-v", "ON_ERROR_STOP=0", "-q"]
    run(*psql, "-d", "postgres", "-c", "CREATE DATABASE restore_test;")
    # Supabase rolleri yerelde yok; dump --no-owner/--no-privileges ama extension/schema sahipligi hata verebilir -> say, durma
    with gzip.open(yedek, "rt", encoding="utf-8", errors="replace") as f:
        sql = f.read()
    t0 = time.time()
    r = subprocess.run(psql + ["-d", "restore_test"], input=sql, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    hata = [l for l in r.stderr.splitlines() if "ERROR" in l]
    print(f"psql yukleme {time.time()-t0:.0f}s, hata satiri={len(hata)}")
    for l in hata[:15]: print("  ", l[:160])
    q = ("SELECT 'companies',count(*) FROM public.companies UNION ALL "
         "SELECT 'field_dictionary',count(*) FROM public.field_dictionary UNION ALL "
         "SELECT 'schema_migrations',count(*) FROM public.schema_migrations UNION ALL "
         "SELECT 'tablo_sayisi',count(*) FROM information_schema.tables WHERE table_schema='public';")
    print(run(*psql, "-d", "restore_test", "-At", "-c", q).stdout)
finally:
    subprocess.run([os.path.join(BIN, "pg_ctl.exe"), "-D", kume, "stop", "-m", "fast"], capture_output=True, env=env)
    shutil.rmtree(kume, ignore_errors=True)
    print("gecici kume silindi:", kume, "kaldi" if os.path.exists(kume) else "OK")
