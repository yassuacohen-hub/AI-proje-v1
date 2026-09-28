# -*- coding: utf-8 -*-
"""TCKN gösterim düğmesi kontrolü (KVKK-TCKN-01).

Çalıştır: python scripts/_kontrol_tckn_dugme.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "src"))

from company_master.settings import (  # noqa: E402
    AYAR_SEMASI,
    ayar_kaydet,
    gruplar,
    tckn_sun,
    varsayilanlar,
)

TCKN = "12345678901"
ANAHTAR = "tckn_kullaniciya_gorunur"

with tempfile.TemporaryDirectory() as td:
    dizin = Path(td)
    kid = "test_kullanici"

    # 1) Şemada var ve panelde görünür (gruplar() panel sekmelerini üretir)
    assert ANAHTAR in varsayilanlar(), "ayar şemada yok"
    assert varsayilanlar()[ANAHTAR] is False, "varsayılan KAPALI olmalı"
    assert any(
        t.anahtar == ANAHTAR for t in gruplar()["Veri"]
    ), "ayar Veri grubunda görünmüyor"

    # 2) Varsayılan: kullanıcı maskeli görür
    assert tckn_sun(TCKN, kid, dizin=dizin) == "•" * 11, "varsayılan maskeli değil"

    # 3) Admin her zaman açık görür (ürün sahibi kararı)
    assert tckn_sun(TCKN, kid, admin=True, dizin=dizin) == TCKN, "admin maskelenmiş"

    # 4) Düğme açılınca kullanıcı da açık görür
    ayar_kaydet(kid, ANAHTAR, True, dizin)
    assert tckn_sun(TCKN, kid, dizin=dizin) == TCKN, "düğme açıkken maskeli kaldı"

    # 5) Düğme kapanınca geri maskelenir
    ayar_kaydet(kid, ANAHTAR, False, dizin)
    assert tckn_sun(TCKN, kid, dizin=dizin) == "•" * 11, "düğme kapanmadı"

    # 6) Boş değer maskeye dönüşmez (sahte veri üretmeyiz)
    assert tckn_sun(None, kid, dizin=dizin) is None
    assert tckn_sun("", kid, admin=True, dizin=dizin) is None

print(f"TAMAM - 6 mandal gecti ({len(AYAR_SEMASI)} ayar semada)")
