# -*- coding: utf-8 -*-
import sys, subprocess, pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
R = pathlib.Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
PY = sys.executable

ozet = (
    "GET /companies/{vkn}/network (derinlik 1-2, Query ge=1 le=2, scope network:read) + "
    "GET /companies/{vkn}/full-report (scope report:read) canli. "
    "Temizlik: v1_network.py 487->330 satir (get_full_report return-sonrasi 129 satir olu kod + "
    "_fetch_company_by_vkn/_get_company_vkn cift tanimlari silindi). "
    "web_app.py wrapper'larina Query(1,ge=1,le=2) eklendi -> derinlik=3 422. "
    "FazA olcum (chat kayit 0): entity_graph yok, company_edges=0 bos -> network bos graf (kenarlar=[], kesildi) "
    "doner; kimlik_tamligi tam; companies 10123. "
    "Test: tests/test_api_v1_network.py 5/5 PASSED (402 credit_exhausted x2, 422 derinlik=3, "
    "402 gecerli sinir 1-2, OpenAPI sema v1_network etiketi). "
    "Regresyon 8/8 PASSED; kodlama_denetim kilitli dosyalarda 0 ihlal; B-14 hub izi eklendi; "
    "bulgu defteri + chat 4/4 kapali."
)
p = subprocess.run(
    [PY, "scripts/gorev_kutusu.py", "teslim",
     "--ajan", "yasu",
     "--task-id", "API-V1-NETWORK-REPORT-01",
     "--ozet", ozet],
    cwd=str(R), capture_output=True, text=True, encoding="utf-8", errors="replace")
print(p.stdout)
print(p.stderr)
print("rc =", p.returncode)
