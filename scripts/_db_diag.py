# -*- coding: utf-8 -*-
"""DB aktif sorgu + kilit diyagnostiği (geçici)."""
import sys

sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

e = get_engine()
c = e.connect()
rows = c.execute(text(
    "SELECT pid, state, wait_event_type, wait_event, left(query,70) q, "
    "now()-query_start sure FROM pg_stat_activity "
    "WHERE state <> 'idle' AND pid <> pg_backend_pid() ORDER BY query_start"
)).fetchall()
print("AKTIF SORGU SAYISI:", len(rows))
for x in rows:
    print(x[0], "|", x[1], "|", x[2], "|", x[3], "|",
          str(x[4]).replace("\n", " "), "|", x[5])
locks = c.execute(text(
    "SELECT locktype, mode, granted, count(*) FROM pg_locks "
    "GROUP BY 1,2,3 ORDER BY 3,1"
)).fetchall()
for x in locks:
    print("LOCK:", x[0], x[1], "granted=" + str(x[2]), "adet=" + str(x[3]))
c.rollback()
c.close()