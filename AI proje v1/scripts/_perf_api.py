# -*- coding: utf-8 -*-
"""P4-4: web_app'in gercek sorgularini olcer (source join + kalite dagilimi dahil)."""
import sys, time
sys.path.insert(0, "src"); sys.path.insert(0, ".")
import web_app
from fastapi.testclient import TestClient

c = TestClient(web_app.app)
web_app._QUERY_TIMES.clear()
r = c.get("/api/companies", params={"limit": 20})
print("companies status:", r.status_code, "total:", r.json().get("total"), "donen:", len(r.json().get("items", [])))
for q in web_app._QUERY_TIMES:
    print(f"  SQL {q['name']}: {q['ms']} ms")
t0 = time.perf_counter(); c.get("/api/companies", params={"limit": 20, "search": "dogan"}); print(f"arama dogan: {(time.perf_counter()-t0)*1000:.0f} ms")
t0 = time.perf_counter(); c.get("/api/quality-distribution"); print(f"quality-distribution: {(time.perf_counter()-t0)*1000:.0f} ms")
t0 = time.perf_counter(); c.get("/api/sources"); print(f"sources: {(time.perf_counter()-t0)*1000:.0f} ms")
