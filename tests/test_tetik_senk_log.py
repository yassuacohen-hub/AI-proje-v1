# -*- coding: utf-8 -*-
"""ALTYAPI-TETIK-ZAMAN-01 — tetik_senk gunluk log + sessiz basari yasagi.

Kapsam:
1. `--gunluk` sonucu `tetik_senk_log.jsonl` satirina yazilir ve JSON okunabilir.
2. Duzeltilemeyen sapma (panoda olmayan ACIL tetik) bulunursa cikis kodu != 0.
3. Sifir satir etkilendiginde (log yazilamadi) sessizce 0 donmez.

Kural D-86: dogrulama Python/subprocess uzerinden; Windows cmd tuzaklari yok.
"""
import importlib.util
import json
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]


def _yukle(ad: str):
    """scripts/ paket degil; dosya yolundan modul yukler."""
    spec = importlib.util.spec_from_file_location(ad, KOK / "scripts" / f"{ad}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[ad] = mod
    spec.loader.exec_module(mod)
    return mod


def _izole(tmp_path, monkeypatch, pano: list | None = None, tetik_satirlari: list | None = None):
    """Pano + tetik kuyrugunu tmp_path'e yonlendir (gercek panoya dokunmaz)."""
    ts = _yukle("tetik_senk")
    monkeypatch.setattr(ts.tb, "STATE_DIR", tmp_path)
    monkeypatch.setattr(ts.tb, "TASK_BOARD", tmp_path / "pano.json")
    (tmp_path / "pano.json").write_text(
        json.dumps(pano or [], ensure_ascii=False), encoding="utf-8"
    )
    tetikler = tmp_path / "triggers"
    tetikler.mkdir(exist_ok=True)
    satirlar = "".join(
        json.dumps(s, ensure_ascii=False) + "\n" for s in (tetik_satirlari or [])
    )
    (tetikler / "yasu.jsonl").write_text(satirlar, encoding="utf-8")
    return ts


def test_gunluk_log_satiri_yazilir_ve_json_okunur(tmp_path, monkeypatch):
    """--gunluk: senk=0 olsa bile satir birakir ve satir JSON olarak okunur."""
    ts = _izole(tmp_path, monkeypatch)

    assert ts.main(["--gunluk"]) == 0, "temiz senkron -> exit 0"

    log = tmp_path / "tetik_senk_log.jsonl"
    assert log.exists(), "gunluk log dosyasi olusmali"

    satirlar = [s for s in log.read_text(encoding="utf-8").splitlines() if s.strip()]
    assert len(satirlar) == 1, "her kosu tam bir satir birakir"

    kayit = json.loads(satirlar[0])  # JSON olarak okunabilmeli
    assert set(kayit) == {"an", "senk", "sapma"}, f"beklenen sema degil: {kayit}"
    assert kayit["senk"] == 0 and kayit["sapma"] == 0
    assert kayit["an"], "ISO zaman damgasi bos olamaz"


def test_senk_artisi_loga_yansir(tmp_path, monkeypatch):
    """Panoda final olan gorevin ACIL tetigi kapatilir -> logda senk > 0."""
    ts = _izole(
        tmp_path,
        monkeypatch,
        pano=[{"task_id": "X-01", "durum": "done", "sahip": "yasu", "baslik": "x"}],
        tetik_satirlari=[
            {"task_id": "X-01", "ajan": "yasu", "durum": "bekliyor", "tarih": "t"}
        ],
    )

    assert ts.main(["--gunluk"]) == 0
    kayit = json.loads((tmp_path / "tetik_senk_log.jsonl").read_text(encoding="utf-8").splitlines()[-1])
    assert kayit["senk"] == 1, "kapatilan tetik senk sayacina yazilmali"
    assert kayit["sapma"] == 0

    kalan = json.loads((tmp_path / "triggers" / "yasu.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert kalan["durum"] == "kapandi"


def test_bildirim_tetigi_sapma_degil_kapanir(tmp_path, monkeypatch):
    """D-58 ORKESTRA-DEVRALMA panoda gorev degildir; sapma uretmez, okununca kapanir."""
    ts = _izole(
        tmp_path,
        monkeypatch,
        tetik_satirlari=[
            {"task_id": "ORKESTRA-DEVRALMA", "ajan": "yasu", "durum": "bekliyor", "tarih": "t"}
        ],
    )

    rapor = ts.tetik_senk()
    assert rapor["sapma"] == 0, "bildirim tetigi hayalet sayilmamali"
    assert rapor["basarili"] == 1, "bildirim tetigi kapandi olarak duzeltilmeli"
    kalan = json.loads((tmp_path / "triggers" / "yasu.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert kalan["durum"] == "kapandi"
    assert ts.main(["--gunluk"]) == 0


def test_duzeltilemeyen_sapmada_exit_sifir_degil(tmp_path, monkeypatch):
    """Panoda karsiligi olmayan ACIL tetik duzeltilemez -> exit != 0 (sapma)."""
    ts = _izole(
        tmp_path,
        monkeypatch,
        tetik_satirlari=[
            {"task_id": "HAYALET-01", "ajan": "yasu", "durum": "bekliyor", "tarih": "t"}
        ],
    )

    rapor = ts.tetik_senk()
    assert rapor["sapma"] == 1, "duzeltilemeyen sapma sayilmali"
    assert rapor["basarili"] == 0, "hayalet tetik duzeltilmemeli"

    kod = ts.main(["--gunluk"])
    assert kod != 0, "sapma varken sessizce 0 donulemez"
    assert kod == 2, "duzeltilemeyen sapma -> exit 2"


def test_log_yazilamazsa_sifir_donmez(tmp_path, monkeypatch):
    """Sifir satir etkilendi (log yazilamadi) ise sessizce 0 donulmez."""
    ts = _izole(tmp_path, monkeypatch)
    # Log yolunu dizin yap -> append edilemez (0 satir etkilendi).
    (tmp_path / "tetik_senk_log.jsonl").mkdir()

    kod = ts.main(["--gunluk"])
    assert kod == 4, "log yazilamadi -> exit 4"
