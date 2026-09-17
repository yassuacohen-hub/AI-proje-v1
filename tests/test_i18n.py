# -*- coding: utf-8 -*-
"""MRK-02g — Dil paketinin sozlesmesini kalici olarak koruyan test dosyasi."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from company_master.i18n import (
    I18nHatasi,
    ParametreHatasi,
    anahtarlar,
    onbellek_temizle,
    ses,
    sozluk,
    t,
)

KOK = Path(__file__).resolve().parents[1] / "src" / "company_master" / "i18n"
SES_DOSYA = KOK / "ses.json"
UI_DOSYA = KOK / "ui.json"

TONLAR = {"info", "success", "warning", "danger", "neutral"}
KATMANLAR = {"veri", "cerceve"}

HATALI_YAZIM = re.compile(r"Muginn|Hugin\b|Munin\b|Hugginn|Munnin|Odinn|Huggin\b", re.IGNORECASE)
ODIN_MISSPELLING = re.compile(r"Odın")  # exact: Turkish dotless ı (U+0131)


def _ham(dosya: Path) -> dict:
    veri = json.loads(dosya.read_text(encoding="utf-8"))
    return {k: v for k, v in veri.items() if not k.startswith("_")}


SES_KAYITLAR = _ham(SES_DOSYA)
UI_KAYITLAR = _ham(UI_DOSYA)
TUM_KAYITLAR = {**SES_KAYITLAR, **UI_KAYITLAR}


@pytest.mark.parametrize("anahtar", sorted(TUM_KAYITLAR))
def test_bekci_01_tr_ve_en_kumeleri_esit(anahtar: str) -> None:
    assert "tr" in TUM_KAYITLAR[anahtar] and "en" in TUM_KAYITLAR[anahtar]


@pytest.mark.parametrize("anahtar", sorted(TUM_KAYITLAR))
def test_bekci_02_deger_bos_degil(anahtar: str) -> None:
    v = TUM_KAYITLAR[anahtar]
    assert v.get("tr") and v.get("en")


# Bekci 03: Sadece gerçek olmayan bir anahtar için
def test_bekci_03_bilinmeyen_anahtar_cokmez() -> None:
    """`t("gercekten_olmayan_bir_anahtar")` istisna atmaz ve anahtarin kendisini dondurur; `ses(...).bulundu is False`."""
    anahtar = "gercekten_olmayan_bir_anahtar"
    m = t(anahtar)
    assert m == anahtar, f"t() {m!r} yerine {anahtar!r} dondurmeli"
    ses_sonuc = ses(anahtar)
    assert ses_sonuc.bulundu is False, f"ses().bulundu {ses_sonuc.bulundu}, False olmalı"
    assert ses_sonuc.metin == anahtar


@pytest.mark.parametrize("anahtar", sorted(SES_KAYITLAR))
def test_bekci_04_ses_json_marka_oneki(anahtar: str) -> None:
    assert anahtar.startswith(("huginn_", "muninn_", "odin_"))


@pytest.mark.parametrize("anahtar", sorted(SES_KAYITLAR))
def test_bekci_05_ses_json_en_az_uc_parca(anahtar: str) -> None:
    assert anahtar.count("_") >= 2


@pytest.mark.parametrize("anahtar", sorted(TUM_KAYITLAR))
def test_bekci_06_ton_gecerli(anahtar: str) -> None:
    v = TUM_KAYITLAR[anahtar]
    assert v.get("ton") in TONLAR


@pytest.mark.parametrize("anahtar", sorted(TUM_KAYITLAR))
def test_bekci_08_katman_zorunlu(anahtar: str) -> None:
    v = TUM_KAYITLAR[anahtar]
    assert v.get("katman") in KATMANLAR


@pytest.mark.parametrize("anahtar", {k: v for k, v in TUM_KAYITLAR.items() if v.get("katman") == "veri"})
def test_bekci_09_veri_katmani_duz_string(anahtar: str) -> None:
    v = TUM_KAYITLAR[anahtar]
    assert isinstance(v.get("tr"), str)
    assert isinstance(v.get("en"), str)


@pytest.mark.parametrize("anahtar", {k: v for k, v in TUM_KAYITLAR.items() if isinstance(v.get("tr"), dict)})
def test_bekci_11_cerceve_objede_cirak_zorunlu(anahtar: str) -> None:
    v = TUM_KAYITLAR[anahtar]
    assert "cirak" in v.get("tr", {})


@pytest.mark.parametrize("anahtar", sorted(TUM_KAYITLAR))
def test_bekci_12_en_asla_obje_degil(anahtar: str) -> None:
    v = TUM_KAYITLAR[anahtar]
    assert not isinstance(v.get("en"), dict)


@pytest.mark.parametrize("anahtar", sorted(TUM_KAYITLAR))
def test_bekci_13_marka_yazim_hatasi_yok(anahtar: str) -> None:
    v = TUM_KAYITLAR[anahtar]
    for s in (v.get("tr", ""), v.get("en", "")):
        if isinstance(s, dict):
            s = " ".join(s.values())
        assert not HATALI_YAZIM.search(str(s))
        assert not ODIN_MISSPELLING.search(str(s))


def test_onbellek_temizleme_calisir() -> None:
    onbellek_temizle()
    assert t("menu_kpi") == "KPI Özeti"


def test_anahtar_sayisi_beklenen_aralikta() -> None:
    sayi = len(anahtarlar())
    assert sayi == len(TUM_KAYITLAR) >= 170


def test_ses_ve_ui_anahtar_cakismasi_yok() -> None:
    assert not (set(SES_KAYITLAR) & set(UI_KAYITLAR))


def test_seviye_fallback_calisir() -> None:
    cirak = t("huginn_liste_bos", seviye="cirak")
    usta = t("huginn_liste_bos", seviye="usta")
    assert cirak and usta and cirak != usta
