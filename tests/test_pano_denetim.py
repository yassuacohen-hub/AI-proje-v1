# -*- coding: utf-8 -*-
"""pano_denetim tarama mantığı — çerçevesiz özdenetim."""
from datetime import datetime, timedelta
from pathlib import Path

from scripts.pano_denetim import (
    IZINLI_DUZELTMELER,
    _kanonik_yol_kontrol,
    arsiv_kimlikleri,
    ithalat_kontrol,
    tara,
)

VAULT = Path(__file__).resolve().parents[1]

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


# --- D-231: arşiv panonun devamıdır, yokluğu değil ---------------------------

ORPHAN_UYARI_TAVANI = 4  # ölçüm 2026-09-27: 216 uyarının 196'sı arşivde, 4'ü sahi öksüz


def test_arsivlenmis_kuyruk_kaydi_orphan_saymaz():
    """D-231: kapanıp arşive taşınan iş öksüz değil; denetim arşive bakmalı."""
    kuyruk = [{"task_id": "ARSIVDE", "durum": "onaylandi", "onay_tarihi": ESKI}]
    assert ("orphan", "ARSIVDE") in _tipler(tara([], kuyruk, SIMDI))          # arşive kör
    assert tara([], kuyruk, SIMDI, frozenset({"ARSIVDE"})) == []              # arşiv bilinirse sessiz


def test_pano_kapali_ama_onay_kaydi_bekliyor_uyarir():
    """VERI-03 (d0d5d76): pano 'done' yapıldı, kuyruk kaydı 'bekliyor' kaldı.
    Onay akışı iki dosyada yürüdüğü için sessizce kopabiliyordu."""
    pano = [{"task_id": "K", "durum": "done", "baslangic": YENI}]
    kuyruk = [{"task_id": "K", "durum": "bekliyor"}]
    b = tara(pano, kuyruk, SIMDI)
    assert ("kuyruk", "K") in _tipler(b)
    assert [x["seviye"] for x in b] == ["uyari"]      # bilgi amaçlı, CI kırmaz
    # negatif: pano da açıksa çelişki yok
    assert tara([{"task_id": "K", "durum": "doing", "baslangic": YENI}], kuyruk, SIMDI) == []


def test_arsivlenmis_gorev_icin_bekleyen_onay_hata_kalir():
    """Negatif kontrol: arşivlenmiş işe bekleyen onay gerçek çelişkidir, susturulamaz."""
    kuyruk = [{"task_id": "ARSIVDE", "durum": "bekliyor"}]
    b = tara([], kuyruk, SIMDI, frozenset({"ARSIVDE"}))
    assert [x["seviye"] for x in b] == ["hata"]


def test_gercek_kuyrukta_orphan_uyarisi_tavani_asmaz():
    """D-220 tavanı: sahi öksüz sayısı yalnız küçülebilir."""
    import json

    from scripts.pano_denetim import KUYRUK_DOSYA, PANO_DOSYA

    pano = json.loads(PANO_DOSYA.read_text(encoding="utf-8-sig"))
    kuyruk = json.loads(KUYRUK_DOSYA.read_text(encoding="utf-8-sig"))
    orphan = [b for b in tara(pano, kuyruk, datetime.now(), arsiv_kimlikleri())
              if b["tip"] == "orphan"]
    assert len(orphan) <= ORPHAN_UYARI_TAVANI, (
        f"D-231 ihlali: sahi öksüz {len(orphan)} > tavan {ORPHAN_UYARI_TAVANI} "
        f"-> {[b['task_id'] for b in orphan]}"
    )


def test_d231_agents_mde_kayitli() -> None:
    metin = (VAULT / "AGENTS.md").read_text(encoding="utf-8")
    assert "(D-231 " in metin, "D-231 kararı AGENTS.md'de yok."


if __name__ == "__main__":
    test_tara_uyumsuzluklari_bulur()
    test_otomat_gorevi_done_yapamaz()
    test_onaydan_sonra_yeniden_acilan_gorev_uyumsuz_sayilmaz()
    test_temiz_pano_bulgu_uretmez()
    test_ithalat_kontrol_gecerli()
    test_pano_yolu_kanonik()
    test_arsivlenmis_kuyruk_kaydi_orphan_saymaz()
    test_arsivlenmis_gorev_icin_bekleyen_onay_hata_kalir()
    test_gercek_kuyrukta_orphan_uyarisi_tavani_asmaz()
    test_d231_agents_mde_kayitli()
    print("OK")
