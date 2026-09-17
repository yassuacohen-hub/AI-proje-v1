# -*- coding: utf-8 -*-
"""TEST-CI-01: CI test işi sertleştirme — pano guard + workflow sözleşmesi."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
import yaml

KOK = Path(__file__).resolve().parents[1]
CI_YML = KOK / ".github" / "workflows" / "ci.yml"


def _guard_modulu():
    spec = importlib.util.spec_from_file_location("pano_guard", KOK / "scripts" / "pano_guard.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def guard():
    return _guard_modulu()


# ---------------------------------------------------------------- pano_guard


def test_anlik_goruntu_yalniz_json_dosyalarini_alir(tmp_path, guard):
    (tmp_path / "a.json").write_text("{}", encoding="utf-8")
    (tmp_path / "b.md").write_text("x", encoding="utf-8")
    (tmp_path / "alt").mkdir()
    (tmp_path / "alt" / "c.json").write_text("{}", encoding="utf-8")
    goruntu = guard.anlik_goruntu(tmp_path)
    assert set(goruntu) == {"a.json"}


def test_anlik_goruntu_dizin_yoksa_bos(tmp_path, guard):
    assert guard.anlik_goruntu(tmp_path / "yok") == {}


def test_farklar_yeni_silindi_degisti(guard):
    once = {"a.json": "1", "b.json": "2", "c.json": "3"}
    sonra = {"a.json": "1", "b.json": "X", "d.json": "4"}
    fark = guard.farklar(once, sonra)
    assert fark == ["DEGISTI  b.json", "SILINDI  c.json", "YENI     d.json"]


def test_cli_snapshot_check_degisiklik_yoksa_0(tmp_path, guard, capsys):
    dizin = tmp_path / "orch"
    dizin.mkdir()
    (dizin / "task_board.json").write_text("[]", encoding="utf-8")
    cikti = tmp_path / "snap.json"
    assert guard.main(["--dizin", str(dizin), "snapshot", "--out", str(cikti)]) == 0
    assert json.loads(cikti.read_text(encoding="utf-8")).keys() == {"task_board.json"}
    assert guard.main(["--dizin", str(dizin), "check", "--in", str(cikti)]) == 0
    assert "OK" in capsys.readouterr().out


def test_cli_check_degisiklik_varsa_1_ve_error_annotasyonu(tmp_path, guard, capsys):
    dizin = tmp_path / "orch"
    dizin.mkdir()
    pano = dizin / "task_board.json"
    pano.write_text("[]", encoding="utf-8")
    cikti = tmp_path / "snap.json"
    guard.main(["--dizin", str(dizin), "snapshot", "--out", str(cikti)])
    pano.write_text('[{"task_id": "SIZINTI"}]', encoding="utf-8")
    (dizin / "handoffs.json").write_text("{}", encoding="utf-8")
    assert guard.main(["--dizin", str(dizin), "check", "--in", str(cikti)]) == 1
    out = capsys.readouterr().out
    assert "::error::" in out
    assert "DEGISTI  task_board.json" in out
    assert "YENI     handoffs.json" in out


# ---------------------------------------------------------------- ci.yml sözleşmesi


@pytest.fixture(scope="module")
def ci():
    return yaml.safe_load(CI_YML.read_text(encoding="utf-8"))


def _test_adimlari(ci) -> list[dict]:
    return ci["jobs"]["test"]["steps"]


def _adim(ci, ad_parcasi: str) -> dict:
    for s in _test_adimlari(ci):
        if ad_parcasi in str(s.get("name", "")):
            return s
    raise AssertionError(f"adim bulunamadi: {ad_parcasi}")


def test_ci_yml_gecerli_ve_test_isi_var(ci):
    assert "test" in ci["jobs"]
    assert ci["jobs"]["test"]["needs"] == "lint"


def test_kapsam_esigi_85_altina_dusmez(ci):
    assert int(ci["env"]["COVERAGE_THRESHOLD"]) >= 85


def test_pytest_komutu_sertlestirilmis(ci):
    run = _adim(ci, "Run tests with coverage")["run"]
    assert "-p no:cacheprovider" in run
    assert "--timeout=${{ env.PYTEST_TIMEOUT_SN }}" in run
    assert "--cov-fail-under=${{ env.COVERAGE_THRESHOLD }}" in run
    assert int(ci["env"]["PYTEST_TIMEOUT_SN"]) == 300


def test_pytest_timeout_kuruluyor(ci):
    run = _adim(ci, "Install dependencies")["run"]
    assert "pytest-timeout" in run


def test_pano_guard_snapshot_testten_once_check_sonra(ci):
    adlar = [str(s.get("name", "")) for s in _test_adimlari(ci)]
    i_snap = next(i for i, a in enumerate(adlar) if "anlik goruntusu" in a)
    i_test = next(i for i, a in enumerate(adlar) if "Run tests with coverage" in a)
    i_check = next(i for i, a in enumerate(adlar) if "izolasyon kontrolu" in a)
    assert i_snap < i_test < i_check
    check = _test_adimlari(ci)[i_check]
    assert check.get("if") == "always()", "testler kirmizi olsa da sizinti raporlanmali"
    assert "pano_guard.py check" in check["run"]


def test_requirements_dev_pytest_timeout_icerir():
    metin = (KOK / "requirements-dev.txt").read_text(encoding="utf-8")
    assert "pytest-timeout" in metin
