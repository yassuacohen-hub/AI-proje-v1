# -*- coding: utf-8 -*-
import subprocess
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ozet = (
    "Faz A (0062 odeme+musteri_ayar tablo/RLS + down) ve Faz B "
    "(musteri_odeme.py render_odemeler/render_ayarlar, musteri_kredi.py render_krediler) tamam. "
    "Bu oturum: test_sayfa_iskeleti MUAF muafiyeti (musteri_odeme/musteri_kredi alt sekme govdesi, PageHeader yok) "
    "+ 3 kilitli dosyada dosya_sonu yeni-satir duzeltmesi. "
    "Test: musteri_odeme+dashboard_nav+admin_sekme_mandali 134/134 PASSED, "
    "py_compile OK, kodlama_denetim kapsamda kilitli dosyalar temiz. "
    "Kapsam disi bulgu: admin_denetim 2 hata (baska gorevin kilidi). "
    "Rapor: data/orchestrator/VERI-MUSTERI-ODEME-AYAR-01_rapor_2026-10-12_yasu.md"
)
cikti = (
    "web_dashboard/tabs/musteri_odeme.py,"
    "web_dashboard/tabs/musteri_kredi.py,"
    "tests/test_musteri_odeme.py,"
    "src/company_master/schema/migrations/0062_odeme_musteri_ayar.sql,"
    "data/orchestrator/VERI-MUSTERI-ODEME-AYAR-01_rapor_2026-10-12_yasu.md"
)
cmd = [
    sys.executable, "scripts/gorev_kutusu.py", "teslim",
    "--ajan", "yasu",
    "--task-id", "VERI-MUSTERI-ODEME-AYAR-01",
    "--ozet", ozet,
    "--cikti", cikti,
]
r = subprocess.run(cmd, cwd=r"c:\HUGINN~1\HUGINN~1")
sys.exit(r.returncode)
