# -*- coding: utf-8 -*-
"""ADMIN-NAV-HAZIR-02: `admin_auth` kimlik ön-dolum ve sessiz except regresyonları.

Kapsam:
- `_env_kimlik()` her dalda ``(eposta, sifre)`` demeti döndürmeli (DEBUG=1 iken
  `None` dönüp `TypeError` üretiyordu).
- `_gorunur_bolum_sayisi()` / `_env_sifre_guncelle()` hataları yutarken log basmalı.
- Modülde çıplak `except Exception: pass|return` kalıbı kalmamalı.
"""
from __future__ import annotations

import ast
import logging
from pathlib import Path

import pytest

import web_dashboard.tabs.admin_auth as mod

KAYNAK = Path(mod.__file__)


# ---------------------------------------------------------------- _env_kimlik


@pytest.mark.parametrize("debug", ["1", "true", "TRUE", "0", "", "hayir"])
def test_env_kimlik_daima_ikili_demet(monkeypatch: pytest.MonkeyPatch, debug: str) -> None:
    """Her DEBUG değeri için iki elemanlı ``(str, str)`` demeti dönmeli."""
    monkeypatch.setenv("DEBUG", debug)
    monkeypatch.delenv("ADMIN_EMAIL", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    sonuc = mod._env_kimlik()

    assert isinstance(sonuc, tuple)
    assert len(sonuc) == 2
    eposta, sifre = sonuc  # unpack çökmemeli (asıl hata buydu)
    assert isinstance(eposta, str) and eposta
    assert isinstance(sifre, str)


def test_env_kimlik_debug_acikken_env_degerlerini_kullanir(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DEBUG=1 iken ADMIN_EMAIL/ADMIN_PASSWORD forma taşınır."""
    monkeypatch.setenv("DEBUG", "1")
    monkeypatch.setenv("ADMIN_EMAIL", "sahip@huginn.local")
    monkeypatch.setenv("ADMIN_PASSWORD", "gizli-sifre")

    assert mod._env_kimlik() == ("sahip@huginn.local", "gizli-sifre")


def test_env_kimlik_debug_kapaliyken_sifre_sizdirmaz(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Prodüksiyonda (DEBUG kapalı) şifre asla ön-doldurulmaz."""
    monkeypatch.setenv("DEBUG", "0")
    monkeypatch.setenv("ADMIN_PASSWORD", "gizli-sifre")

    eposta, sifre = mod._env_kimlik()

    assert sifre == ""
    assert eposta == mod.VARSAYILAN_EPOSTA


def test_env_kimlik_debug_acik_ama_env_bossa_varsayilan(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DEBUG=1 + boş env → varsayılan e-posta, boş şifre."""
    monkeypatch.setenv("DEBUG", "1")
    monkeypatch.setenv("ADMIN_EMAIL", "")
    monkeypatch.setenv("ADMIN_PASSWORD", "")

    assert mod._env_kimlik() == (mod.VARSAYILAN_EPOSTA, "")


# -------------------------------------------------- _gorunur_bolum_sayisi


def test_gorunur_bolum_sayisi_gercek_tanimlarla_pozitif() -> None:
    """Navigasyon SSOT okunabildiğinde admin sayısı anon'dan büyük olmalı."""
    admin_n, anon_n = mod._gorunur_bolum_sayisi()

    assert admin_n > 0
    assert admin_n >= anon_n


def test_gorunur_bolum_sayisi_hatada_sifir_ve_log(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """İçe aktarma patlarsa ``(0, 0)`` döner ama sessiz kalmaz (debug log)."""
    import builtins

    gercek_import = builtins.__import__

    def _patlat(ad, *args, **kwargs):
        if ad == "web_dashboard.tabs":
            raise ImportError("test: navigasyon modülü yok")
        return gercek_import(ad, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _patlat)

    with caplog.at_level(logging.DEBUG, logger=mod.__name__):
        assert mod._gorunur_bolum_sayisi() == (0, 0)

    assert any("Görünür bölüm" in k.message for k in caplog.records)


# ---------------------------------------------------- _env_sifre_guncelle


def test_env_sifre_guncelle_hatada_false_ve_uyari_log(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """`.env` yazımı patlarsa ``False`` döner ve WARNING seviyesinde loglanır."""
    import builtins

    gercek_import = builtins.__import__

    def _patlat(ad, *args, **kwargs):
        if ad == "scripts.admin_sifre_sifirla":
            raise ImportError("test: env_upsert yok")
        return gercek_import(ad, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _patlat)

    with caplog.at_level(logging.WARNING, logger=mod.__name__):
        assert mod._env_sifre_guncelle("yeni-sifre-123") is False

    assert any("ADMIN_PASSWORD" in k.message for k in caplog.records)


# ------------------------------------------------------- statik denetimler


def test_modul_sessiz_yutma_icermez() -> None:
    """`except Exception:` bloğu ya loglamalı ya da yeniden fırlatmalı."""
    agac = ast.parse(KAYNAK.read_text(encoding="utf-8"))

    for dugum in ast.walk(agac):
        if not isinstance(dugum, ast.ExceptHandler):
            continue
        # Hata nesnesi bir ada bağlanmalı ki loglanabilsin.
        assert dugum.name, (
            f"L{dugum.lineno}: except bloğu hatayı bir ada bağlamıyor "
            "(`except Exception as exc:` kullanılmalı)"
        )
        govde = ast.dump(ast.Module(body=dugum.body, type_ignores=[]))
        loglar = ("_LOG", "'error'", "'warning'", "'debug'", "'info'")
        assert any(k in govde for k in loglar), (
            f"L{dugum.lineno}: except bloğu hatayı sessizce yutuyor"
        )


def test_env_kimlik_tum_dallarda_return_var() -> None:
    """`_env_kimlik` gövdesinde örtük ``None`` dönüşü kalmamalı."""
    agac = ast.parse(KAYNAK.read_text(encoding="utf-8"))
    fn = next(
        d
        for d in agac.body
        if isinstance(d, ast.FunctionDef) and d.name == "_env_kimlik"
    )

    son = fn.body[-1]
    assert isinstance(son, ast.Return), (
        "_env_kimlik son ifadesi `return` değil → DEBUG dalında None döner (TypeError)"
    )
    assert son.value is not None


def test_kaynak_bom_icermez() -> None:
    """UTF-8 BOM yasak (AGENTS.md kodlama kuralı)."""
    assert not KAYNAK.read_bytes().startswith(b"\xef\xbb\xbf")
