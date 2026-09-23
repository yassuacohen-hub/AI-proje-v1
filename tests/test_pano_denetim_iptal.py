# -*- coding: utf-8 -*-
"""iptal gorev kapalidir: ne stuck uyarisi, ne kuyruk celiskisi, ne acik gorev.

Eksikligi 5 sahte uyari uretiyordu (ADMIN-UX-PROFILMENU-01, ADMIN-UX-MENUTREE-01,
ALTYAPI-KILIT-TEMIZLIK-V10-01). Uyari gurultusunu 16 -> 11'e dusurur.
"""
import importlib.util
import sys
from datetime import datetime, timedelta
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location("pano_denetim", KOK / "scripts" / "pano_denetim.py")
pd = importlib.util.module_from_spec(spec)
sys.modules["pano_denetim"] = pd
spec.loader.exec_module(pd)

SIMDI = datetime(2026, 9, 23, 12, 0)
ESKI = (SIMDI - timedelta(days=5)).isoformat(timespec="seconds")


def _gorev(tid, durum):
    return {"task_id": tid, "durum": durum, "atandi_tarihi": ESKI}


def test_iptal_gorev_stuck_uyarisi_uretmez():
    bulgular = pd.tara([_gorev("X-01", "iptal")], [], SIMDI)
    assert bulgular == [], f"iptal gorev uyari uretmemeli: {bulgular}"


def test_plan_gorev_hala_stuck_uyarisi_uretir():
    # Ters kontrol: duzeltme gercek sinyali susturmamali.
    tipler = [b["tip"] for b in pd.tara([_gorev("X-02", "plan")], [], SIMDI)]
    assert "stuck" in tipler, "acik gorev stuck uyarisini kaybetti"


def test_iptal_gorev_kuyruk_celiskisi_uretmez():
    kuyruk = [{"task_id": "X-03", "durum": "onaylandi", "onay_tarihi": ESKI}]
    assert pd.tara([_gorev("X-03", "iptal")], kuyruk, SIMDI) == []
