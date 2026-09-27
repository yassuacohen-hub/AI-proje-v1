"""D-225 mandali: D-57 kalibi panonun KALICI halinde de gecerli.

Hastalik (2026-09-27): D-57 dogrulamasi yalnizca `gorev_at.py` giris kapisinda
calisiyordu. task_board.json'a dogrudan yazilan bir gorev denetimden kaciyordu.
Boylece "SEMA-01 / [SEMA] ..." kimligi panoya girdi; SEMA kanonik ALAN degil.
`pano_denetim.py` hata=0 dedi, `test_naming_audit.py` 9 yesil verdi, kimse
yakalamadi -> yesil test yanlis guven verdi.

Kural: aktif (plan/wip/review gibi henuz kapanmamis) her pano kaydi, giris
kapisiyla AYNI dogrulayiciyi gecmek zorunda. Gecmis done/archive kayitlari
geriye donuk kirmizilastirilmaz; onlar tarihsel kayittir.
"""

import importlib.util
import json
import pathlib

import pytest

VAULT = pathlib.Path(__file__).resolve().parents[1]
PANO = VAULT / "data/orchestrator/task_board.json"

# Kapanmis kayitlar tarihsel; kural yalnizca yasayan gorevleri baglar.
KAPALI = {"done", "archive", "iptal"}


def _gorev_at():
    """scripts/gorev_at.py'yi paket olmadan yukle (tek dogrulayici kaynagi)."""
    yol = VAULT / "scripts" / "gorev_at.py"
    spec = importlib.util.spec_from_file_location("_gorev_at_test", yol)
    assert spec and spec.loader, f"yuklenemedi: {yol}"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _aktif_kayitlar():
    return [
        k
        for k in json.loads(PANO.read_text(encoding="utf-8"))
        if k.get("durum") not in KAPALI
    ]


def test_aktif_gorevler_d57_gecer():
    """Panodaki her aktif kayit giris kapisi dogrulamasini gecmeli."""
    ga = _gorev_at()
    ihlaller = []
    for k in _aktif_kayitlar():
        # Pano kaydinda ajan alani "sahip" adiyla tutulur (D-57 sahip zorunlu).
        hata = ga._d57_dogrula(k.get("task_id", ""), k.get("baslik", ""), k.get("sahip", ""))
        if hata:
            ihlaller.append(f"{k.get('task_id')}: {hata}")
    assert not ihlaller, "aktif panoda D-57 ihlali:\n  " + "\n  ".join(ihlaller)


def test_alan_oneki_kanonik():
    """task_id on eki gorev_at.ALANLAR icinde olmali (SEMA-01 hatasinin mandali)."""
    ga = _gorev_at()
    yabanci = [
        k.get("task_id")
        for k in _aktif_kayitlar()
        if str(k.get("task_id", "")).split("-")[0] not in ga.ALANLAR
    ]
    assert not yabanci, (
        f"kanonik olmayan ALAN oneki: {yabanci}; izinli: {', '.join(ga.ALANLAR)}"
    )


@pytest.mark.parametrize(
    "task_id,baslik",
    [
        ("SEMA-01", "[SEMA] Migration down dosyalarini tek ad standardina tasi → x (3s)"),
        ("VERI-04", "[UI] Migration down dosyalarini tasi → x (3s)"),  # on ek uyusmuyor
        ("VERI-04", "down dosyalarini tasi"),  # kalip yok
    ],
)
def test_negatif_kontrol_ihlal_yakalanir(task_id, baslik):
    """Mandal gercekten isliyor mu: bilinen ihlaller hata dondurmeli."""
    ga = _gorev_at()
    assert ga._d57_dogrula(task_id, baslik, "ihsan") is not None, (
        "ihlal tespit edilmedi; mandal sahte guven veriyor"
    )
