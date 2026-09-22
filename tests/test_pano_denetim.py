# -*- coding: utf-8 -*-
"""pano_denetim tarama mantığı — çerçevesiz özdenetim."""
from datetime import datetime, timedelta

from scripts.pano_denetim import IZINLI_DUZELTMELER, ithalat_kontrol, tara, _kanonik_yol_kontrol

SIMDI = datetime(2026, 9, 22, 12, 0, 0)
COK_ESKI = (SIMDI - timedelta(days=5)).isoformat()
ESKI = (SIMDI - timedelta(days=3)).isoformat()
YENI = (SIMDI - timedelta(hours=1)).isoformat()


def _tipler(bulgular):
    return {(b["tip"], b["task_id"]) for b in bulgular}


def test_tara_uyumsuzluklari_bulur():
    pano = [
        {"task_id": "A", "durum": "blocked", "blokaj": ["YOK"], "baslangic": YENI},
        {"task_id": "B", "durum": "doing", "bitis": ESKI, "baslangic": YENI},
        {"task_id": "C", "durum": "blocked", "blokaj": ["D"], "baslangic": YENI},
        {"task_id": "D", "durum": "done", "bitis": ESKI},
        {"task_id": "E", "durum": "plan", "baslangic": ESKI},
        {"task_id": "F", "durum": "review", "baslangic": COK_ESKI},
    ]
    kuyruk = [
        {"task_id": "F", "durum": "onaylandi", "onay_tarihi": ESKI},
        {"task_id": "HAYALET", "durum": "bekliyor"},
    ]
    b = tara(pano, kuyruk, SIMDI)
    t = _tipler(b)
    assert ("orphan", "A") in t          # blokaj panoda yok
    assert ("alan", "B") in t            # bitis dolu, durum doing
    assert ("normalize", "C") in t       # blokaj kapandı, hâlâ blocked
    assert ("stuck", "E") in t           # 24h+ hareketsiz
    assert ("kuyruk", "F") in t          # onaylandi ama pano review
    assert ("orphan", "HAYALET") in t    # kuyrukta var, panoda yok
    assert not [x for x in t if x[1] == "D"]  # temiz görev bulgu üretmez
    # stuck ve kuyruk yalnız uyarı (kapatma kararı kanıt ister), geri kalanlar hata
    assert {x["seviye"] for x in b if x["tip"] in ("stuck", "kuyruk")} == {"uyari"}
    assert {x["seviye"] for x in b if x["tip"] in ("alan", "normalize")} == {"hata"}


def test_otomat_gorevi_done_yapamaz():
    """D-66/D-77: kanıt gerektiren 'done' kararı otomatın yetkisinde değil."""
    assert "done_yap" not in IZINLI_DUZELTMELER
    pano = [{"task_id": "F", "durum": "review", "baslangic": COK_ESKI}]
    kuyruk = [{"task_id": "F", "durum": "onaylandi", "onay_tarihi": ESKI}]
    for bulgu in tara(pano, kuyruk, SIMDI):
        assert bulgu.get("duzeltme") not in ("done_yap",)
        assert bulgu.get("duzeltme") in (None, *IZINLI_DUZELTMELER)


def test_onaydan_sonra_yeniden_acilan_gorev_uyumsuz_sayilmaz():
    """Kuyruk bir ekleme-günlüğü: eski onay + yeni atama = tarihsel kayıt."""
    pano = [{"task_id": "G", "durum": "plan", "atandi_tarihi": YENI}]
    kuyruk = [{"task_id": "G", "durum": "onaylandi", "onay_tarihi": ESKI}]
    assert [x for x in tara(pano, kuyruk, SIMDI) if x["tip"] == "kuyruk"] == []


def test_temiz_pano_bulgu_uretmez():
    pano = [{"task_id": "X", "durum": "doing", "baslangic": YENI}]
    assert tara(pano, [], SIMDI) == []


def test_ithalat_kontrol_gecerli():
    assert ithalat_kontrol() is None, "trigger.py göreli ithalatı bozulmuş"


def test_pano_yolu_kanonik():
    """D-186: denetim her zaman merkez panosunu okur; worktree kopyası split üretir."""
    assert _kanonik_yol_kontrol() is None, "PANO_DOSYA kanonik değil veya worktree'de split kopya var"


if __name__ == "__main__":
    test_tara_uyumsuzluklari_bulur()
    test_otomat_gorevi_done_yapamaz()
    test_onaydan_sonra_yeniden_acilan_gorev_uyumsuz_sayilmaz()
    test_temiz_pano_bulgu_uretmez()
    test_ithalat_kontrol_gecerli()
    test_pano_yolu_kanonik()
    print("OK")
