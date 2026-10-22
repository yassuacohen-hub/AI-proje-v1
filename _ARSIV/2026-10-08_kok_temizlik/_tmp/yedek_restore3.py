# -*- coding: utf-8 -*-
"""Geri yukleme testi v3: stdout/stderr PIPE degil, dogrudan dosyaya (deadlock riski yok).
v2 dersi: capture_output=True (PIPE) + kesintiye ugrayan terminal -> psql yazma bloklandi (CPU 0, 17dk asili).
"""
import gzip, os, shutil, subprocess, sys, tempfile, time

BIN = r"C:\Program Files\PostgreSQL\17\bin"
PORT = "54331"
yedek = sys.argv[1]
is_dir = tempfile.mkdtemp(prefix="huginn_restore3_work_")
kume = os.path.join(is_dir, "data")  # initdb bu klasore yazar, BOS olmali
dump_sql = os.path.join(is_dir, "dump.sql")  # kume DISINDA, initdb'yi kirletmez
log_path = os.path.join(is_dir, "run.log")


def logf():
    return open(log_path, "a", encoding="utf-8")


def run(args, timeout=60):
    with logf() as lf:
        lf.write(f"\n$ {' '.join(args)}\n")
        lf.flush()
        r = subprocess.run(args, stdout=lf, stderr=subprocess.STDOUT, timeout=timeout)
    return r.returncode


with logf() as lf:
    lf.write("1) gzip -> dosya acma\n")
t0 = time.time()
with gzip.open(yedek, "rt", encoding="utf-8", errors="replace") as f, open(dump_sql, "w", encoding="utf-8") as out:
    shutil.copyfileobj(f, out)
with logf() as lf:
    lf.write(f"   {os.path.getsize(dump_sql)/1024:.0f} KB, {time.time()-t0:.1f}s\n")

try:
    with logf() as lf:
        lf.write("2) initdb\n")
    rc = run([os.path.join(BIN, "initdb.exe"), "-D", kume, "-U", "postgres", "-A", "trust", "-E", "UTF8", "--locale=C"], timeout=60)
    with logf() as lf:
        lf.write(f"   rc={rc}\n3) pg_ctl start\n")
    rc = run([os.path.join(BIN, "pg_ctl.exe"), "-D", kume, "-o", f"-p {PORT} -c listen_addresses=127.0.0.1", "-l", os.path.join(kume, "server.log"), "start", "-w"], timeout=30)
    with logf() as lf:
        lf.write(f"   rc={rc}\n")
    psql = [os.path.join(BIN, "psql.exe"), "-h", "127.0.0.1", "-p", PORT, "-U", "postgres", "-v", "ON_ERROR_STOP=0", "-q"]
    with logf() as lf:
        lf.write("4) createdb\n")
    rc = run(psql + ["-d", "postgres", "-c", "CREATE DATABASE restore_test;"], timeout=30)
    with logf() as lf:
        lf.write(f"   rc={rc}\n5) psql -f dump.sql\n")
    t0 = time.time()
    rc = run(psql + ["-d", "restore_test", "-f", dump_sql], timeout=240)
    with logf() as lf:
        lf.write(f"   bitti {time.time()-t0:.0f}s rc={rc}\n6) sorgu\n")
    q = ("SELECT 'companies',count(*)::text FROM public.companies UNION ALL "
         "SELECT 'field_dictionary',count(*)::text FROM public.field_dictionary UNION ALL "
         "SELECT 'schema_migrations',count(*)::text FROM public.schema_migrations UNION ALL "
         "SELECT 'tablo_sayisi',count(*)::text FROM information_schema.tables WHERE table_schema='public';")
    rc = run(psql + ["-d", "restore_test", "-At", "-c", q], timeout=30)
    with logf() as lf:
        lf.write(f"   rc={rc}\n")
finally:
    try:
        run([os.path.join(BIN, "pg_ctl.exe"), "-D", kume, "stop", "-m", "immediate"], timeout=30)
    except Exception as e:
        with logf() as lf:
            lf.write(f"durdurma hatasi: {e}\n")
    with logf() as lf:
        lf.write("BITTI\n")
    shutil.copy(log_path, sys.argv[2] if len(sys.argv) > 2 else "restore3_log_kopya.txt")
    shutil.rmtree(is_dir, ignore_errors=True)
