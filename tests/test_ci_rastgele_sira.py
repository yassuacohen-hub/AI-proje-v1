# -*- coding: utf-8 -*-
"""MANDAL-SIRA-01 (D-301): CI rastgele sirada kosmali, yoksa yesil beyandir.

Olculen olay: D-299 sira bagimli bir testi (`test_ui_search_gap`,
`st.cache_data` onceki testin sonucunu donduruyor) **yalnizca rastgele sirada
kostugu icin** yakaladi. CI sabit sirada kosuyorsa ayni kirik yesil gorunur ve
"4592 passed" bir kanit degil, bir beyan olur (D-288).

Olculen durum (D-301, tahmin degil): `pytest-randomly>=3.15.0` zaten
`requirements-dev.txt`'te **beyan edilmisti**, ama CI'in `test` job'i o dosyayi
hic kurmuyordu -- `pip install -r requirements-dev.txt` yalnizca `lint` job'inda
geciyor. Test job'i elle `pytest pytest-cov pytest-timeout` kuruyordu. Yani
beyan vardi, kurulum yoktu. Bu, bu projenin tekrar eden kusuru: yazili olan ile
kosan ayni sey degil.

Neden `-p randomly` bayragi da eklendi: olculdu -- eklenti kurulu degilken
pytest `-p <eklenti>` ile RC=1 verip ImportError atiyor. Yani bayrak, kurulumun
sessizce kaybolmasini imkansiz kilar; eklenti dusarse CI kirmizi olur, sabit
siraya **sessizce** dusmez.

Bu mandal CI'i kosturamaz (GitHub Actions burada yok), bu yuzden konfigurasyonu
okur. Kapsami budur: yazilanin dogrulugunu mandallar, kosanin degil.

Kendi hatam (D-260), **ayni hatayi bu turda ikinci kez yaptim**: ilk surum
`run:` blogunu yorumlariyla birlikte tariyordu ve hatayi *anlatan yorumu*
kurulum sandi -- kirarak dogrularken mandal yesil kaldi. Ayni tuzaga
`test_admin_kpi.py`'de de dusmustum. Ders: **kod tarayan mandal, aciklamayi
koddan ayirmadan yazilmaz.** `_adimlar()` artik `#` ile baslayan satirlari atar.
"""
from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml", reason="PyYAML yok; CI konfig mandali atlandi")

_KOK = Path(__file__).resolve().parents[1]
_CI = _KOK / ".github" / "workflows" / "ci.yml"


def _test_job() -> dict:
    veri = yaml.safe_load(_CI.read_text(encoding="utf-8"))
    return veri["jobs"]["test"]


def _adimlar() -> str:
    """Yalniz kosan kabuk satirlari. Yorumlar atilir (D-260: bkz. modul notu)."""
    ham = "\n".join(str(a.get("run", "")) for a in _test_job()["steps"])
    return "\n".join(s for s in ham.splitlines() if not s.lstrip().startswith("#"))


def test_ci_konfigu_okunabilir():
    assert _CI.exists(), f"CI konfigu bulunamadi: {_CI}"
    assert "test" in yaml.safe_load(_CI.read_text(encoding="utf-8"))["jobs"]


def test_pytest_randomly_ci_test_jobunda_kuruluyor():
    """Beyan yetmez: paket bu job'da gercekten kurulmali (D-260)."""
    metin = _adimlar()
    kuruluyor = "pytest-randomly" in metin or "requirements-dev.txt" in metin
    assert kuruluyor, (
        "CI test job'i pytest-randomly kurmuyor; testler sabit sirada kosar ve "
        "sira bagimli kiriklar gorunmez kalir (D-288). requirements-dev.txt'te "
        "yazili olmasi yetmez -- bu job onu kurmuyor."
    )


def test_randomly_eklentisi_acikca_zorunlu_kilinmis():
    """`-p randomly`: eklenti dusarse CI patlar, sessizce sabit siraya dusmez."""
    assert "-p randomly" in _adimlar(), (
        "pytest cagrisinda `-p randomly` yok. Eklenti kurulumdan duserse pytest "
        "sessizce sabit sirada kosar ve kimse fark etmez."
    )


def test_rastgele_sira_kapatilmamis():
    """Kimse `-p no:randomly` veya `--randomly-dont-shuffle` ile susturmasin."""
    metin = _adimlar()
    for susturma in ("no:randomly", "randomly-dont-shuffle", "-p no:randomly"):
        assert susturma not in metin, (
            f"CI rastgele sirayi `{susturma}` ile kapatmis; mandal islevsiz kalir"
        )


def test_yerel_konfig_rastgele_sirayi_kapatmiyor():
    """pytest.ini'deki bir `addopts` CI bayragini sessizce ezebilir."""
    ini = _KOK / "pytest.ini"
    if not ini.exists():
        pytest.skip("pytest.ini yok")
    icerik = ini.read_text(encoding="utf-8")
    assert "no:randomly" not in icerik, (
        "pytest.ini rastgele sirayi kapatiyor; CI bayragi bir sey ifade etmez"
    )
