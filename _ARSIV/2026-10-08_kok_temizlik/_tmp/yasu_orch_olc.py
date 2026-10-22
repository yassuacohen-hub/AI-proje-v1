# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
KOK = r"c:\HUGINN~1\HUGINN~1"
sys.path.insert(0, KOK)
sys.path.insert(0, KOK + r"\scripts")

import importlib.util
spec = importlib.util.spec_from_file_location("kd", KOK + r"\scripts\kodlama_denetim.py")
kd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kd)

# ORCH-KODLAMA-TEMIZLIK-01 kapsami (brief Adimlar Faz A-E)
# kilitli 5 dosya baska gorevce -> HARIC
KILITLI_BASKA = {
    "web_dashboard/tabs/admin_sistem_saglik.py",
    "web_dashboard/tabs/admin_denetim.py",
    "tests/test_admin_denetim.py",
    "src/company_master/engine/rapidapi_osint.py",
    "tests/test_rapidapi_osint.py",
}

sonuc = kd.tara(kd.KAPSAM_DIZINLERI)

# kapsamimdaki kabul kategorileri (dosya_sonu haric: brief Faz E ile kapsanir ama
# baska gorevlerin dosyalari da var; biz SADECE brief'teki dosyalari raporlariz)
print("=== ORCH-KODLAMA-TEMIZLIK-01 kapsamindaki GUNCEL ihlaller ===")
print("(kilitli-5 haric; sadece bu gorevin duzeltebilecegi dosyalar)\n")

for kod in ("utf8_bom", "mojibake", "crlf_karisik", "sondaki_bosluk", "dosya_sonu"):
    liste = sonuc.get(kod, [])
    # dosya_sonu/sondaki_bosluk "path:line" formatinda; normalize et
    temiz = []
    for d in liste:
        path = d.split(":")[0]
        if path not in KILITLI_BASKA:
            temiz.append(d)
    print(f"[{kod}] {len(temiz)} ihlal (kilitli-5 haric, tum repo):")
    for d in temiz:
        print(f"   {d}")
