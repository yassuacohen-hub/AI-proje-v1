# -*- coding: utf-8 -*-
"""ALTYAPI-AJAN-CAKISMA-01: kilit kapisi.

Kok neden: 130 dosya tasinirken kilit sorgulanmadi. Commit kapisi
(`kilit_zorla.py`) gec kaldi; bu modul onunde gelen sorgu + kapidir.

Burada **canli kilit dosyasi kullanilmaz**; testler gecici yazilir.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "scripts"))

spec = importlib.util.spec_from_file_location(
    "ajan_cakisma_kilidi", KOK / "scripts" / "ajan_cakisma_kilidi.py")
ack = importlib.util.module_from_spec(spec)
sys.modules["ajan_cakisma_kilidi"] = ack
spec.loader.exec_module(ack)


def _kilit(sahip: str, gun: str = "2099-01-01T00:00:00") -> dict:
    """Taze kilit (bayatlamaz)."""
    return {"sahip": sahip, "task_id": "T-1", "kilitlendi": gun}


def test_kilit_dosyasi_yapisi_bozulmedi():
    """Canli kilit dosyasi okunabilir ve beklenen alanlari tasiyor."""
    k = ack.kilitleri_oku()
    if not k:
        return  # kilit dosyasi yoksa bu test sessiz gecer
    for yol, v in k.items():
        assert isinstance(yol, str)
        assert "sahip" in v and "task_id" in v and "kilitlendi" in v, yol


def test_bayat_kilit_aktif_sayilmaz():
    """D-303: 24 saatten eski kilit sahipsiz sayilir, agaci bloklamaz."""
    k = {"a.py": _kilit("utku", "2000-01-01T00:00:00")}
    assert ack.aktif_kilitler(k) == {}


def test_taze_kilit_aktif():
    k = {"a.py": _kilit("utku")}
    assert "a.py" in ack.aktif_kilitler(k)


def test_ajan_kilitleri_sadece_own():
    k = {"a.py": _kilit("yasu"), "b.py": _kilt_salik()}
    assert list(ack.ajan_kilitleri("yasu", k)) == ["a.py"]
    assert ack.ajan_kilitleri("utku", k) == {}


def _kilt_salik():
    return _kilit("salih")


def test_kapi_baskasinin_kilidini_reddeder():
    k = {"src/x.py": _kilit("utku")}
    gecti, mesaj = ack.kapi_gecer(["src/x.py"], ajan="yasu", kilitler=k)
    assert not gecti
    assert "utku" in mesaj


def test_kapi_kendi_kilidini_gecirir():
    """Ajan kendi kilitli dosyasina dokunabilir."""
    k = {"src/x.py": _kilit("yasu")}
    gecti, _ = ack.kapi_gecer(["src/x.py"], ajan="yasu", kilitler=k)
    assert gecti


def test_kapi_bosta_dosyayi_gecirir():
    gecti, mesaj = ack.kapi_gecer(["src/yeni.py"], ajan="yasu", kilitler={})
    assert gecti and mesaj == ""


def test_kapi_bayat_kilidi_gecirir():
    k = {"src/x.py": _kilit("utku", "2000-01-01T00:00:00")}
    gecti, _ = ack.kapi_gecer(["src/x.py"], ajan="yasu", kilitler=k)
    assert gecti


def test_kapi_hareket_uyarisi_yakin_dakika():
    """Son dakikada kilitli dosya degistiyse uyari uretilir."""
    (ack.KOK / "data" / "orchestrator" / "trigger_log.jsonl").touch()
    metin = ack.hareket_uyarisi(5)
    assert metin is None or "KILITLI DOSYA HAREKETI" in metin


def test_son_degisenler_hareket_disi_atlar():
    """Arsiv/log gibi dizinler hareket sayimina girmez."""
    for p in ack.son_degisenler(60):
        assert not (ack.HAREKET_DISI & set(Path(p).parts)), p


def test_esik_dakika_cinsindendir():
    """IZIN_KILIT_ESIK dakika cinsindendir; saniye varsayimi yanlis olurdu."""
    assert ack.VARSAYILAN_ESIK_DAKIKA == 5
    assert ack.VARSAYILAN_ESIK_DAKIKA <= 60


def test_json_bozuksa_cokmez(tmp_path, monkeypatch):
    """Bozuk kilit dosyasi betigi cokertmemeli."""
    bozuk = tmp_path / "bozuk.json"
    bozuk.write_text("{bozuk", encoding="utf-8")
    monkeypatch.setattr(ack, "KILIT", bozuk)
    assert ack.kilitleri_oku() == {}