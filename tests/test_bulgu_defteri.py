# -*- coding: utf-8 -*-
"""D-318 — Bulgu defteri kanonik doküman + teslim kapısı.

Mandal ilkesi (D-244): kapıyı kırmadan yeşil saymak anlamsızdır. Bu
dosyada kapının **reddettiği** ve **geçirdiği** iki yol da kanıtlanır.
"""

from __future__ import annotations

import importlib.util as ilu
import sys
from pathlib import Path

import pytest

_KOK = Path(__file__).resolve().parents[1]


def _mod(ad: str, yol: Path):
    spec = ilu.spec_from_file_location(ad, yol)
    m = ilu.module_from_spec(spec)
    sys.modules[ad] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def bd():
    return _mod("bulgu_defteri", _KOK / "scripts" / "bulgu_defteri.py")


@pytest.fixture(scope="module")
def gk():
    return _mod("gorev_kutusu_d318", _KOK / "scripts" / "gorev_kutusu.py")


@pytest.fixture
def defter(tmp_path: Path) -> Path:
    p = tmp_path / "bulgu_defteri.md"
    p.write_text(_mod("bd2", _KOK / "scripts" / "bulgu_defteri.py").BASLIK,
                 encoding="utf-8")
    return p


# --- format ------------------------------------------------------------------


def test_satir_birlestir_alti_alan(bd):
    s = bd.satir_birlestir("2026-10-02", "T-1", "utku", "oneri", "ozet", "kapandi:x")
    assert len(s.split("|")) == 6
    assert s.startswith("2026-10-02 | T-1 | utku |")


@pytest.mark.parametrize("renk", ["oneri", "dikkat", "acil", "tamam"])
def test_renk_ismi_emoji_donusur(bd, renk):
    s = bd.satir_birlestir("2026-10-02", "T-1", "utku", renk, "o", "k")
    assert s.split("|")[3].strip() == bd.RENKLER[renk]


def test_cok_satirli_ozet_satir_kirmaz(bd):
    s = bd.satir_birlestir("2026-10-02", "T-1", "utku", "oneri",
                           "ilk\nsatir\nikinci", "kapandi:x")
    assert s.count("\n") == 0
    assert len(s.split("|")) == 6


@pytest.mark.parametrize("rol", ["bilinmeyen", "uretim", "URETIM", ""])
def test_kanonik_olmayan_rol_reddedilir(bd, rol):
    with pytest.raises(ValueError, match="rol"):
        bd.satir_birlestir("2026-10-02", "T-1", rol, "oneri", "o", "k")


def test_gecersiz_renk_reddedilir(bd):
    with pytest.raises(ValueError, match="renk"):
        bd.satir_birlestir("2026-10-02", "T-1", "utku", "pembe", "o", "k")


@pytest.mark.parametrize("bos_alan", ["tarih", "task_id", "rol", "ozet", "karar"])
def test_bos_alan_reddedilir(bd, bos_alan):
    a = {"tarih": "2026-10-02", "task_id": "T-1", "rol": "utku",
         "renk": "oneri", "ozet": "o", "karar": "k"}
    a[bos_alan] = "   "
    with pytest.raises(ValueError, match=bos_alan):
        bd.satir_birlestir(a["tarih"], a["task_id"], a["rol"], a["renk"],
                           a["ozet"], a["karar"])


def test_karar_alani_bos_birakilamaz(bd):
    """D-67: islenmemis bulgu olmamali; alan bos gecerse ValueError."""
    with pytest.raises(ValueError, match="karar"):
        bd.satir_birlestir("2026-10-02", "T-1", "utku", "oneri", "ozet", "")


# --- ayirici (baslik veri sanilmamali) ---------------------------------------


def test_baslik_paragrafi_veri_sayilmaz(bd, defter):
    """Markdown tablosu ve kod blogu boruya benzer; sayimi bozuyordu."""
    assert len(bd._veri_satirlari(defter)) == 0
    bd.ekle("T-1", "utku", "o", "k", "oneri", dosya=defter)
    assert len(bd._veri_satirlari(defter)) == 1


def test_bolum_isaretleri_veri_sayilmaz(bd, tmp_path):
    p = tmp_path / "d.md"
    p.write_text(
        "# Baslik\n\n| alan | kural |\n|---|---|\n| tarih | ISO |\n\n"
        "```\n2026-10-02 | ORNEK | satis | | | \n```\n",
        encoding="utf-8",
    )
    assert bd._veri_satirlari(p) == []


# --- yazici ------------------------------------------------------------------


def test_ekle_idempotent(bd, defter):
    a = dict(task_id="T-1", rol="utku", ozet="o", karar="k", renk="oneri")
    bd.ekle(dosya=defter, **a)
    bd.ekle(dosya=defter, **a)
    assert defter.read_text(encoding="utf-8").count("T-1") == 1


def test_ekle_farkli_bulgu_ekler(bd, defter):
    bd.ekle("T-1", "utku", "birinci", "k1", "oneri", dosya=defter)
    bd.ekle("T-1", "utku", "ikinci", "k2", "acil", dosya=defter)
    assert len(bd._veri_satirlari(defter)) == 2


def test_ekle_bos_dosyaya_basar(bd, tmp_path):
    p = tmp_path / "yeni.md"
    bd.ekle("T-1", "utku", "o", "k", "oneri", dosya=p)
    assert p.exists() and "T-1" in p.read_text(encoding="utf-8")


# --- teslim kapisi -----------------------------------------------------------


def test_task_var_mi(bd, defter):
    assert bd.task_var_mi("YOK", defter) is False
    bd.ekle("VAR", "utku", "o", "k", "oneri", dosya=defter)
    assert bd.task_var_mi("VAR", defter) is True


def test_task_var_mi_tam_eslik(bd, defter):
    """'T-1' ile 'T-10' birbirine karismamali."""
    bd.ekle("T-10", "utku", "o", "k", "oneri", dosya=defter)
    assert bd.task_var_mi("T-1", defter) is False


def test_kapi_teslimi_reddeder(gk, monkeypatch, capsys, tmp_path, bd):
    """Register'da kayit yoksa cmd_teslim 1 donmeli ve trigger'a ulasmamali."""
    cagrildi = []
    monkeypatch.setattr(gk.bulgu, "DEFLER", tmp_path / "yok.md")
    monkeypatch.setattr(gk.bulgu, "task_var_mi", lambda *a, **k: False)
    monkeypatch.setattr(gk, "_hafiza_izi", lambda t: True)
    monkeypatch.setattr(gk.chat, "teslim_kontrol_et",
                        lambda t: {"engel": False, "nedenler": []})
    monkeypatch.setattr(gk.trigger, "teslim_et",
                        lambda *a, **k: cagrildi.append(1))

    class A:
        task_id = "D-318-TEST"
        ajan = "utku"
        ozet = "o"
        cikti = None
        zorla = False

    assert gk.cmd_teslim(A()) == 1
    assert cagrildi == []  # trigger cagrilmadi: teslim yazilmadi
    assert "D-318" in capsys.readouterr().err


def test_kapi_teslimi_gecirir(gk, monkeypatch, capsys, tmp_path, bd):
    """Kayit varsa teslim yazilir — kapı yalnizca reddetmiyor."""
    yazildi = []
    d = tmp_path / "d.md"
    d.write_text(bd.BASLIK + "\n2026-10-02 | D-318-TEST | utku | oneri | o | k\n",
                 encoding="utf-8")
    monkeypatch.setattr(gk.bulgu, "DEFLER", d)
    monkeypatch.setattr(gk, "_hafiza_izi", lambda t: True)
    monkeypatch.setattr(gk.chat, "teslim_kontrol_et",
                        lambda t: {"engel": False, "nedenler": []})
    monkeypatch.setattr(gk.tb, "gorev_getir", lambda t: {"task_id": t})
    monkeypatch.setattr(gk.trigger, "teslim_et",
                        lambda *a, **k: yazildi.append(k) or
                        {"task_id": a[0], "ajan": a[1]})
    monkeypatch.setattr(gk.tb, "gorev_guncelle", lambda *a, **k: None)

    class A:
        task_id = "D-318-TEST"
        ajan = "utku"
        ozet = "o"
        cikti = None
        zorla = False

    assert gk.cmd_teslim(A()) == 0
    assert len(yazildi) == 1


def test_d321_board_kapisi_reddeder(gk, monkeypatch, capsys, tmp_path, bd):
    """D-321: hub'daki task_id board'da birebir yoksa (SKOR/SCOR gibi yazim
    sapmasi) teslim reddedilir — trigger.teslim_et'e hic ulasilmaz (kirma testi)."""
    cagrildi = []
    d = tmp_path / "d.md"
    d.write_text(bd.BASLIK + "\n2026-10-02 | D-321-TEST | utku | oneri | o | k\n",
                 encoding="utf-8")
    monkeypatch.setattr(gk.bulgu, "DEFLER", d)
    monkeypatch.setattr(gk, "_hafiza_izi", lambda t: True)
    monkeypatch.setattr(gk.chat, "teslim_kontrol_et",
                        lambda t: {"engel": False, "nedenler": []})
    monkeypatch.setattr(gk.tb, "gorev_getir", lambda t: None)  # board'da yok
    monkeypatch.setattr(gk.trigger, "teslim_et",
                        lambda *a, **k: cagrildi.append(1))

    class A:
        task_id = "D-321-TEST"
        ajan = "utku"
        ozet = "o"
        cikti = None
        zorla = False

    assert gk.cmd_teslim(A()) == 1
    assert cagrildi == []
    assert "D-321" in capsys.readouterr().err


# --- denetim -----------------------------------------------------------------


def test_islenmemis_yakalar(bd, tmp_path):
    p = tmp_path / "d.md"
    p.write_text(bd.BASLIK + "\n2026-10-02 | G1 | utku | oneri | o |  \n",
                 encoding="utf-8")
    assert len(bd.islenmemis(p)) == 1


def test_islenmemis_alan_sayisi_eksik(bd, tmp_path):
    p = tmp_path / "d.md"
    p.write_text(bd.BASLIK + "\n2026-10-02 | G1 | utku\n", encoding="utf-8")
    assert "ALAN SAYISI EKSİK" in bd.islenmemis(p)[0]


def test_istatistik(bd, defter):
    bd.ekle("T-1", "utku", "o", "k", "oneri", dosya=defter)
    bd.ekle("T-2", "utku", "o", "k", "acil", dosya=defter)
    st = bd.istatistik(defter)
    assert st["satir"] == 2 and st["gorev"] == 2 and st["islenmemis"] == 0
    assert st["renk"] == {"🔵": 1, "🔴": 1}


def test_tum_roller_gecerli(bd):
    """D-33/D-60: dort kanonik ajan."""
    for rol in bd.ROLLER:
        assert bd.satir_birlestir("2026-10-02", "T", rol, "oneri", "o", "k")


# --- gercek defter sagligi ----------------------------------------------------


def test_gercek_defter_kurallara_uyuyor(bd):
    """Diskteki kanonik defterde bozuk satir olmamali."""
    if not bd.DEFLER.exists():
        pytest.skip("defter henuz yok")
    veri = bd._veri_satirlari(bd.DEFLER)
    assert veri, "defter bos"
    for s in veri:
        a = [x.strip() for x in s.split("|")]
        assert len(a) == 6, f"6 alan beklenir: {s[:70]}"
        assert a[2] in bd.ROLLER, f"kanonik olmayan rol: {a[2]!r}"
        assert a[3] in bd.RENKLER.values()
        assert a[5].strip(), f"karar alani bos: {s[:70]}"
    assert bd.islenmemis(bd.DEFLER) == []


# --- eszamanli yazma (kilit) -----------------------------------------------


def test_eszamanli_ekle_kayip_olmaz(bd, tmp_path):
    """Dört eşzamanlı yazıcıda **hiçbir satır kaybolmamalı**.

    Kilit olmadan oku-değiştir-yaz kalıbı kayıp güncelleme üretir; kilit
    kalkınca bu test kırmızıya döner. Kanıt: kilitsiz koşuda 4 iş parçacığı
    1 satır üretir.
    """
    import threading

    d = tmp_path / "d.md"
    roller = ("utku", "yasu", "salih", "ihsan")
    hata: list[Exception] = []

    def yaz(i: int) -> None:
        try:
            bd.ekle(f"ESZ-{i}", roller[i], "ozet", "kapandi:x", "oneri",
                    "2026-10-02", d)
        except Exception as exc:  # noqa: BLE001 — hatayı teste taşı
            hata.append(exc)

    is_parcaciklari = [threading.Thread(target=yaz, args=(i,)) for i in range(4)]
    for t in is_parcaciklari:
        t.start()
    for t in is_parcaciklari:
        t.join()

    assert not hata, f"kilit hata verdi: {hata}"
    assert len(bd._veri_satirlari(d)) == 4


def test_kilit_dosyasi_geride_kalmaz(bd, tmp_path):
    d = tmp_path / "d.md"
    bd.ekle("X", "utku", "o", "k", "oneri", "2026-10-02", d)
    assert not d.with_suffix(d.suffix + ".kilit").exists()


def test_kilit_hata_durumunda_temizlenir(bd, tmp_path):
    """Yazma patlasa bile kilit dosyası kalmamalı."""
    d = tmp_path / "d.md"
    d.write_text(bd.BASLIK, encoding="utf-8")
    with pytest.raises(RuntimeError):
        with bd._kilit_ac(d):
            raise RuntimeError("yazma patladi")
    assert not d.with_suffix(d.suffix + ".kilit").exists()
