# -*- coding: utf-8 -*-
import subprocess, sys, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
R = r"c:\Huginn Data Projesi\Huginn Data Insights"
ENV = dict(os.environ, HUGINN_AJAN="ihsan", PYTHONIOENCODING="utf-8")
M = ("ORKESTRATOR DENETIM (D-65 blokaj bypass): Pano 'blocked' ama not alanı boş; blokaj nedeni kayıtlı değil. "
     "utku: 24 saat içinde chat'e (1) neyi beklediğini (dosya/karar/ajan), (2) bypass yolunu (parçalı teslim, mock, alternatif) yaz. "
     "Yazılmazsa görev 'plan'a düşürülür ve aktif 2 UI görevin (DENETIM-ALTYAPI, DASHBOARD-YAYILIM) önce bitirilir. "
     "Onay kuyruğu boş (2026-10-10 08:07); yeni dağıtım yok, yükler: utku 2 aktif+2 blocked, yasu 1 in_progress+1 aktif+4 plan, salih 1 aktif (geri gönderildi).")
for t in ("UI-ADMIN-PANEL-TEMEL-REFERANS-01", "DOC-BRIEF-SABLON-KIRMIZI-01"):
    r = subprocess.run([sys.executable, "scripts/ajan_chat.py", "ac", "ihsan", t, M], cwd=R, env=ENV,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(t, r.returncode, (r.stdout + r.stderr).strip()[-200:])
