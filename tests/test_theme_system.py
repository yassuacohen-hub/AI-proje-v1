# -*- coding: utf-8 -*-
"""UX-03: Design Token ve Theme Management System testleri.

Kapsam:
  * theme.css sozdizimi, legacy -> semantik kopru butunlugu
  * admin_tokens.css light/dark token esligi
  * theme.js sozlesmesi (localStorage, prefers-color-scheme, API yuzeyi)
  * index.html entegrasyonu (data-theme, yukleme sirasi, FOUC engeli, buton a11y)
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_WEB_DIR = Path(__file__).resolve().parents[1] / "web_dashboard"
CSS_DIR = _WEB_DIR / "css"
THEME_CSS = CSS_DIR / "theme.css"
TOKENS_CSS = CSS_DIR / "admin_tokens.css"
STYLE_CSS = CSS_DIR / "style.css"
THEME_JS = _WEB_DIR / "js" / "theme.js"
INDEX_HTML = _WEB_DIR / "index.html"


def _oku(yol: Path) -> str:
    return yol.read_text(encoding="utf-8")


def _blok(css: str, secici_rx: str) -> str:
    """Verilen seciciye ait ilk kural blogunun govdesini dondurur."""
    m = re.search(secici_rx + r"\s*\{(.*?)\}", css, flags=re.DOTALL)
    assert m, f"secici bulunamadi: {secici_rx}"
    return m.group(1)


def _degiskenler(govde: str) -> set[str]:
    return set(re.findall(r"(--[a-z0-9-]+)\s*:", govde))


# ---------------------------------------------------------------------------
# Dosya butunlugu
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("yol", [THEME_CSS, THEME_JS])
def test_dosyalar_var_ve_utf8(yol: Path) -> None:
    assert yol.exists(), f"eksik dosya: {yol.name}"
    assert _oku(yol).strip(), f"bos dosya: {yol.name}"


def test_theme_css_suslu_parantez_dengeli() -> None:
    css = _oku(THEME_CSS)
    assert css.count("{") == css.count("}")


def test_theme_css_bos_blok_yok() -> None:
    css = re.sub(r"/\*.*?\*/", "", _oku(THEME_CSS), flags=re.DOTALL)
    assert not re.search(r"\{\s*\}", css), "icerigi bos kural blogu var"


# ---------------------------------------------------------------------------
# Legacy -> semantik kopru
# ---------------------------------------------------------------------------

_LEGACY_DEGISKENLER = (
    "--bg",
    "--sidebar-bg",
    "--panel-bg",
    "--panel-hover",
    "--border",
    "--border-light",
    "--text",
    "--text-dim",
    "--text-muted",
    "--accent",
    "--accent-glow",
    "--green",
    "--yellow",
    "--red",
    "--purple",
    "--cyan",
    "--orange",
)


def test_style_css_legacy_degisken_listesi_guncel() -> None:
    """style.css yeni legacy degisken eklerse kopru testi bunu yakalar."""
    kok = _degiskenler(_blok(_oku(STYLE_CSS), r":root"))
    assert kok == set(_LEGACY_DEGISKENLER), (
        "style.css :root degisken kumesi degisti; theme.css koprusu guncellenmeli"
    )


@pytest.mark.parametrize("tema", ["dark", "light"])
def test_kopru_tum_legacy_degiskenleri_kapsar(tema: str) -> None:
    govde = _blok(_oku(THEME_CSS), r':root\[data-theme="' + tema + r'"\]')
    tanimli = _degiskenler(govde)
    eksik = set(_LEGACY_DEGISKENLER) - tanimli
    assert not eksik, f"{tema} temasinda koprulenmemis legacy degisken: {sorted(eksik)}"


@pytest.mark.parametrize("tema", ["dark", "light"])
def test_kopru_hardcoded_renk_kullanmaz(tema: str) -> None:
    """Kopru yalniz semantik token'a isaret etmeli; sabit renk tek kaynak ilkesini bozar."""
    govde = _blok(_oku(THEME_CSS), r':root\[data-theme="' + tema + r'"\]')
    assert "#" not in govde, f"{tema} koprusunde hardcoded hex renk var"
    assert "rgb" not in govde, f"{tema} koprusunde hardcoded rgb renk var"
    assert govde.count("var(--color-") >= len(_LEGACY_DEGISKENLER)


# ---------------------------------------------------------------------------
# Token esligi (light <-> dark)
# ---------------------------------------------------------------------------

_TEMAYA_BAGLI_TOKENLAR = (
    "--color-bg",
    "--color-surface",
    "--color-surface-2",
    "--color-border",
    "--color-border-strong",
    "--color-text",
    "--color-text-muted",
    "--color-text-subtle",
    "--color-text-inverse",
    "--color-accent",
    "--color-success",
    "--color-warning",
    "--color-danger",
    "--color-info",
    "--color-purple",
    "--color-orange",
    "--color-sidebar-bg",
    "--color-topbar-bg",
    "--color-drawer-bg",
)


@pytest.mark.parametrize("token", _TEMAYA_BAGLI_TOKENLAR)
def test_token_hem_light_hem_dark_tanimli(token: str) -> None:
    css = _oku(TOKENS_CSS)
    light = _degiskenler(_blok(css, r":root"))
    dark = _degiskenler(_blok(css, r'\[data-theme="dark"\]'))
    assert token in light, f"{token} light (:root) temada yok"
    assert token in dark, f"{token} dark temada yok (light degeri miras alinir)"


def test_dark_ve_light_degerleri_farkli() -> None:
    """Dark blok light degerini birebir tekrar ederse override anlamsizdir."""
    css = _oku(TOKENS_CSS)
    light_govde = _blok(css, r":root")
    dark_govde = _blok(css, r'\[data-theme="dark"\]')

    def _cifter(govde: str) -> dict[str, str]:
        return {
            k: v.strip()
            for k, v in re.findall(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", govde)
        }

    light = _cifter(light_govde)
    dark = _cifter(dark_govde)
    ayni = [k for k, v in dark.items() if light.get(k) == v]
    # --color-success gibi bilincli ortak degerler olabilir; yuzeyi sinirli tut.
    assert len(ayni) <= 2, f"dark blokta gereksiz tekrar eden token'lar: {ayni}"


# ---------------------------------------------------------------------------
# theme.js sozlesmesi
# ---------------------------------------------------------------------------


def test_js_localstorage_anahtari_sabit() -> None:
    js = _oku(THEME_JS)
    assert 'DEPO_ANAHTARI = "huginn-theme"' in js


def test_js_sistem_tercihini_izler() -> None:
    js = _oku(THEME_JS)
    assert "prefers-color-scheme" in js
    assert "matchMedia" in js


def test_js_localstorage_erisimi_korumali() -> None:
    """Private mode / quota hatasi tema sistemini cokertmemeli."""
    js = _oku(THEME_JS)
    assert js.count("try {") >= 4, "localStorage/matchMedia erisimleri try ile sarilmali"


def test_js_data_theme_niteligini_yazar() -> None:
    js = _oku(THEME_JS)
    assert 'setAttribute("data-theme"' in js
    assert "documentElement" in js


@pytest.mark.parametrize(
    "uye",
    ["aktifTema", "temaUygula", "temaDegistir", "sistemeDon", "sistemTemasi"],
)
def test_js_genel_api_yuzeyi(uye: str) -> None:
    js = _oku(THEME_JS)
    assert re.search(r"HuginnTheme\s*=\s*\{(.*?)\};", js, flags=re.DOTALL), (
        "HuginnTheme global sozlesmesi yok"
    )
    assert uye + ":" in js, f"HuginnTheme.{uye} disa acilmamis"


def test_js_tema_degisimi_olay_yayar() -> None:
    """Chart.js gibi tuketiciler renkleri yeniden okuyabilmeli."""
    js = _oku(THEME_JS)
    assert "huginn:themechange" in js
    assert "dispatchEvent" in js


def test_js_buton_erisilebilirligi_gunceller() -> None:
    js = _oku(THEME_JS)
    assert "aria-pressed" in js
    assert "aria-label" in js


# ---------------------------------------------------------------------------
# index.html entegrasyonu
# ---------------------------------------------------------------------------


def test_html_kokte_varsayilan_tema_var() -> None:
    html = _oku(INDEX_HTML)
    assert re.search(r'<html[^>]*data-theme="(dark|light)"', html), (
        "<html> uzerinde varsayilan data-theme yok (FOUC riski)"
    )


def test_html_css_yukleme_sirasi() -> None:
    """tokens -> style -> responsive -> theme; theme en sonda olmali."""
    html = _oku(INDEX_HTML)
    sira = [html.index(ad) for ad in ("admin_tokens.css", "style.css",
                                      "responsive.css", "theme.css")]
    assert sira == sorted(sira), f"CSS yukleme sirasi bozuk: {sira}"


def test_html_theme_js_headde_ve_app_js_den_once() -> None:
    html = _oku(INDEX_HTML)
    i_theme = html.index("js/theme.js")
    i_head_kapanis = html.index("</head>")
    i_app = html.index("js/app.js")
    assert i_theme < i_head_kapanis, "theme.js <head> icinde olmali (FOUC engeli)"
    assert i_theme < i_app


def test_html_theme_js_defer_veya_async_degil() -> None:
    """FOUC engeli icin senkron calismali; defer/async ilk boyamayi kacirir."""
    html = _oku(INDEX_HTML)
    m = re.search(r"<script[^>]*js/theme\.js[^>]*>", html)
    assert m, "theme.js script etiketi yok"
    assert "defer" not in m.group(0)
    assert "async" not in m.group(0)


def test_html_tema_butonu_erisilebilir() -> None:
    html = _oku(INDEX_HTML)
    m = re.search(r'<button[^>]*id="theme-toggle"[^>]*>', html)
    assert m, "theme-toggle butonu yok"
    etiket = m.group(0)
    assert 'type="button"' in etiket
    assert "aria-pressed" in etiket
    assert "aria-label" in etiket


def test_theme_css_buton_dokunmatik_hedef() -> None:
    """WCAG 2.5.5: dokunmatik hedef en az 40px."""
    govde = _blok(_oku(THEME_CSS), r"\.theme-toggle")
    assert "min-height: 40px" in govde
    assert "min-width: 40px" in govde


def test_theme_css_focus_visible_tanimli() -> None:
    assert ".theme-toggle:focus-visible" in _oku(THEME_CSS)


def test_theme_css_reduced_motion_destegi() -> None:
    css = _oku(THEME_CSS)
    assert "prefers-reduced-motion" in css
    assert "transition: none" in css


def test_html_kacis_karakteri_sizmasi_yok() -> None:
    """Gecmis bir duzenlemede onclick icine `\\(` sizmisti; nukse karsi bekci."""
    html = _oku(INDEX_HTML)
    assert "showView\\(" not in html
    assert 'class="fas\\ ' not in html
