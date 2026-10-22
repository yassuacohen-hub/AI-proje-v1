# -*- coding: utf-8 -*-
import sys, subprocess, pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
R = pathlib.Path(r"c:\HUGINN~1\Huginn Data Insights")
PY = sys.executable
TID = "API-V1-NETWORK-REPORT-01"

def cal(*args):
    p = subprocess.run([PY, *args], cwd=str(R), capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    print("$", " ".join(str(a) for a in args)[:120])
    print((p.stdout or "") + (p.stderr or ""))
    print("rc =", p.returncode, "\n")
    return p.returncode

# 1) bulgu defteri
cal("scripts/bulgu_defteri.py", "ekle",
    "--task-id", TID, "--rol", "yasu",
    "--ozet",
    "v1_network.py 487->330 satir temizlik (return-sonrasi olu kod 129 satir + "
    "2 cift helper tanimi silindi); web_app.py wrapper'larina Query(ge=1,le=2) "
    "eklendi (derinlik=3 icin 422); test_api_v1_network.py 5/5 PASSED "
    "(402 credit_exhausted, 422, OpenAPI sema v1_network etiketi)",
    "--karar",
    "D-318 | kapandi: pytest tests/test_api_v1_network.py 5/5 PASSED + "
    "regresyon 8/8 PASSED + kodlama_denetim kilitli dosyalarda 0 ihlal + "
    "B-14 hub izi eklendi",
    "--renk", "tamam")

# 2) chat kayitlarini kapat (index 1, 2, 3)
kapatma_gerekce = {
    1: "ayni bulgu kayit 0'da olculup cozuldu (FazA: entity_graph yok -> "
       "bos graf kenarlar=[], kimlik_tamligi tam); FazC testleri 5/5",
    2: "ayni bulgu kayit 0'da olculup cozuldu (FazA: entity_graph yok -> "
       "bos graf kenarlar=[], kimlik_tamligi tam); FazC testleri 5/5",
    3: "FazC tamam: tests/test_api_v1_network.py 5/5 PASSED "
       "(402 credit_exhausted network+full-report, 422 derinlik=3 "
       "Query ge=1 le=2, OpenAPI sema v1_network etiketi)",
}
for idx, karar in kapatma_gerekce.items():
    cal("scripts/ajan_chat.py", "kapat", TID, str(idx), "--karar", karar)
