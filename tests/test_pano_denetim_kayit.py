# -*- coding: utf-8 -*-
"""D-237: kapanan görev sahibinin context dosyasında kayıtlı mı?

Kural her görev sonu hafıza güncellemesini zorunlu kılar. Ölçüm gerekçesi:
59 kapanmış görevin yalnız 1'i (%1.7) sahibinin dosyasında geçiyordu.
"""
from datetime import datetime

from scripts.pano_denetim import KAYIT_YURURLUK, tara

SIMDI = datetime(2026, 9, 29, 12, 0)


def _gorev(tid="X-01", sahip="utku", bitis="2026-09-28T10:00:00"):
    return {"task_id": tid, "durum": "done", "sahip": sahip, "bitis": bitis}


def _bulgu(bulgular, tip="kayit"):
    return [b for b in bulgular if b["tip"] == tip]


def test_kayit_yoksa_uyari():
    b = tara([_gorev()], [], SIMDI, contextler={"utku": "bos metin"})
    assert len(_bulgu(b)) == 1
    assert _bulgu(b)[0]["seviye"] == "uyari"
    assert "utku" in _bulgu(b)[0]["mesaj"]


def test_kayit_varsa_sessiz():
    b = tara([_gorev()], [], SIMDI, contextler={"utku": "X-01 tamamlandi"})
    assert _bulgu(b) == []


def test_yururluk_oncesi_gorev_denetlenmez():
    """Geriye dönük 58 görev için uyarı üretmez — yoksa denetim gürültüye boğulur."""
    b = tara([_gorev(bitis="2026-09-20T10:00:00")], [], SIMDI, contextler={"utku": ""})
    assert _bulgu(b) == []
    assert KAYIT_YURURLUK == "2026-09-28"


def test_context_dosyasi_olmayan_ajan_denetlenmez():
    """kahin/orkestrator gibi dosyasız sahipler uyarı üretmemeli."""
    b = tara([_gorev(sahip="kahin")], [], SIMDI, contextler={"utku": ""})
    assert _bulgu(b) == []


def test_contextler_verilmezse_geri_uyumlu():
    assert _bulgu(tara([_gorev()], [], SIMDI)) == []


def test_acik_gorev_kayit_beklemez():
    acik = dict(_gorev(), durum="aktif", bitis=None)
    assert _bulgu(tara([acik], [], SIMDI, contextler={"utku": ""})) == []


if __name__ == "__main__":
    for ad, fn in sorted(globals().items()):
        if ad.startswith("test_"):
            fn()
            print("OK", ad)
