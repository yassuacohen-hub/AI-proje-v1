# -*- coding: utf-8 -*-
"""UX-02: responsive.css + admin_tokens.css sozlesme testleri.

Kapsam:
- Kucuk sozdizimi garantileri (suslu parantez dengesi, bos dosya degil).
- Kirilim noktalari sozlesmesi: 1440 / 1024 / 640 (admin_tokens.css ile hizali).
- 12 kolon grid yardimcilari (.grid, .col-span-1..12).
- admin_tokens.css: light + dark temada zorunlu semantik tokenlar
  (ROO-UX-ADMIN-01 test acigini kapatir).
- index.html CSS katman sirasi: admin_tokens -> style -> responsive.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

_CSS_DIR = Path(__file__).resolve().parents[1] / "web_dashboard" / "css"
RESPONSIVE = _CSS_DIR / "responsive.css"
TOKENS = _CSS_DIR / "admin_tokens.css"
INDEX_HTML = _CSS_DIR.parent / "index.html"

_KIRILIMLAR = ("1440px", "1024px", "640px")

_ZORUNLU_TOKENLAR = (
    "--color-bg",
    "--color-surface",
    "--color-border",
    "--color-text",
    "--color-accent",
    "--color-success",
    "--color-warning",
    "--color-danger",
)


def _oku(yol: Path) -> str:
    return yol.read_text(encoding="utf-8")


# ── Sozdizimi ──────────────────────────────────────────────────────


@pytest.mark.parametrize("yol", [RESPONSIVE, TOKENS], ids=["responsive", "tokens"])
def test_css_dosyasi_var_ve_dengeli(yol: Path):
    assert yol.exists(), f"{yol.name} bulunamadi"
    css = _oku(yol)
    assert css.strip(), f"{yol.name} bos"
    assert css.count("{") == css.count("}"), f"{yol.name}: suslu parantez dengesi bozuk"


def test_responsive_yorum_disinda_bos_blok_yok():
    css = re.sub(r"/\*.*?\*/", "", _oku(RESPONSIVE), flags=re.DOTALL)
    assert not re.search(r"\{\s*\}", css), "responsive.css icinde bos kural blogu var"


# ── Kirilim noktalari ─────────────────────────────────────────────


@pytest.mark.parametrize("kirilim", _KIRILIMLAR)
def test_responsive_kirilim_noktasi(kirilim: str):
    css = _oku(RESPONSIVE)
    assert f"(max-width:{kirilim})" in css.replace(" ", ""), (
        f"responsive.css icinde {kirilim} kirilimi yok"
    )


@pytest.mark.parametrize("kirilim", _KIRILIMLAR)
def test_tokens_kirilim_noktasi(kirilim: str):
    css = _oku(TOKENS).replace(" ", "")
    assert f"(max-width:{kirilim})" in css, (
        f"admin_tokens.css icinde {kirilim} kirilimi yok"
    )


def test_reduced_motion_destegi():
    for yol in (RESPONSIVE, TOKENS):
        assert "prefers-reduced-motion" in _oku(yol), (
            f"{yol.name}: prefers-reduced-motion destegi yok"
        )


# ── Grid sistemi ──────────────────────────────────────────────────


def test_grid_yardimcilari_tam():
    css = _oku(RESPONSIVE)
    assert ".grid{" in css.replace(" ", "")
    assert "var(--grid-cols" in css, "grid, admin_tokens --grid-cols tokenini kullanmali"
    for n in range(1, 13):
        assert f".col-span-{n}{{" in css.replace(" ", ""), f".col-span-{n} eksik"
    assert ".col-full" in css


def test_tokens_grid_cols_tanimli():
    css = _oku(TOKENS).replace(" ", "")
    assert "--grid-cols:12" in css, "admin_tokens.css :root icinde --grid-cols:12 olmali"


# ── admin_tokens.css semantik sozlesme (ROO-UX-ADMIN-01 acigi) ────


def _blok(css: str, secici_rx: str) -> str:
    m = re.search(secici_rx + r"\s*\{(.*?)\}", css, flags=re.DOTALL)
    assert m, f"Secici bulunamadi: {secici_rx}"
    return m.group(1)


@pytest.mark.parametrize("token", _ZORUNLU_TOKENLAR)
def test_light_ve_dark_tema_tokeni(token: str):
    css = _oku(TOKENS)
    light = _blok(css, r":root")
    dark = _blok(css, r'\[data-theme="dark"\]')
    assert f"{token}:" in light.replace(" ", ""), f"light temada {token} eksik"
    assert f"{token}:" in dark.replace(" ", ""), f"dark temada {token} eksik"


def test_kritik_renk_degerleri():
    light = _blok(_oku(TOKENS), r":root").replace(" ", "").lower()
    assert "--color-accent:#6366f1" in light
    assert "--color-success:#22c55e" in light
    assert "--color-warning:#f59e0b" in light
    assert "--color-danger:#ef4444" in light


# ── index.html katman sirasi ──────────────────────────────────────


def test_index_html_css_katman_sirasi():
    html = _oku(INDEX_HTML)
    i_tokens = html.find("admin_tokens.css")
    i_style = html.find("css/style.css")
    i_resp = html.find("responsive.css")
    assert -1 not in (i_tokens, i_style, i_resp), "index.html'de CSS linklerinden biri eksik"
    assert i_tokens < i_style < i_resp, (
        "CSS katman sirasi yanlis: admin_tokens -> style -> responsive olmali"
    )
