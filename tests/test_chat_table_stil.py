# -*- coding: utf-8 -*-
"""D-192 Faz 2: Ajan/Önem Derecesi kolon+renk self-check."""
import pandas as pd

from web_dashboard.tabs.admin_panel import _sohbet_tablo_stil, _AJAN_RENKLERI, _ONEM_RENKLERI


def test_sohbet_tablo_stil_ajan_ve_onem_renklendirir():
    # SEMA-DENETIM-01: kolon adlari "Ajan"/"Hangi Ajana?" -> "Gonderen"/"Alici"
    # olarak degismisti; test eski semada kaldigi icin stil hic uygulanmiyordu.
    df = pd.DataFrame([{
        "Tarih": "x", "Gönderen": "IHSAN", "Alıcı": "UTKU",
        "Görev": "D-1", "Sorun": "s", "Durum": "acik",
        "Önem Derecesi": "Kritik",
        "_ajan_gonderici": "ihsan", "_ajan_alici": "utku", "_onem_ham": "kritik",
    }])
    html = df.style.apply(_sohbet_tablo_stil, axis=1).to_html()
    assert _AJAN_RENKLERI["ihsan"] in html
    assert _AJAN_RENKLERI["utku"] in html
    assert _ONEM_RENKLERI["kritik"] in html


def test_chat_ac_onem_alani_varsayilan_orta():
    import sys
    from pathlib import Path
    _kok = Path(__file__).resolve().parent.parent
    if str(_kok / "src") not in sys.path:
        sys.path.insert(0, str(_kok / "src"))
    from company_master.chat import ac

    satir = ac("yasu", "TEST-ONEM-01", "test sorun", data_dir=Path(__file__).parent / "_tmp_onem_test")
    assert satir["onem"] == "orta"
    assert satir["kimden"] == "orkestrator"
