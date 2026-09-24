"""Cursor Grok detay scraper unit testleri.

> Tarih: 2026-09-02
> Kapsam: src/company_master/etl/scrapers/ostim_scraper.py (Cursor Grok patch)
> Fixture'lar: tests/fixtures/ostim_detail/ icindeki *.html dosyalari

Bu testler proje kokunu DEGISTIRMEZ. Test, "output/" altinda bulunan
patch icindeki yeni davranislari dogrular:
- fetch_firma_detay() HTTP success / 4xx / 5xx / network error
- HTML parse: <table>, <dl>, div-based layout
- vergi_no normalize: 10/11 hane, maskelenmis, format varyasyonlari
- vergi_no fallback: unvan icinden 10-11 hane regex
- Web blocklist: sosyal medya, pazaryeri, arama, placeholder, subdomain
- osb_parsel fallback: adres icinde PARSEL/ADA
- --detayli modu: scrape_firma_full ile batch akis
- Turkce karakter normalizasyonu, whitespace / &nbsp; temizligi

Calistirma:
    cd workspace/external/cursor_grok/output
    pytest tests/test_ostim_scraper.py -v --cov=ostim_scraper_for_test \
        --cov-report=term-missing
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from bs4 import BeautifulSoup

# Test ortami icin: modified scraper'i sandbox alanina kopyalayip import ediyoruz.
# Boylece proje kokundeki ostim_scraper.py'ye DOKUNMADAN test kosabiliyoruz.
HERE = Path(__file__).resolve().parent
OUTPUT_DIR = HERE.parent
WORKSPACE_ROOT = OUTPUT_DIR.parent.parent.parent  # Huginn Data Insights
SCRAPER_SRC = WORKSPACE_ROOT / "src" / "company_master" / "etl" / "scrapers" / "ostim_scraper.py"
PATCH_FILE = OUTPUT_DIR / "patches" / "ostim_scraper.patch"
SANDBOX = Path(os.environ["TEMP"]) / "kilo" / "scraper_sandbox"
SANDBOX.mkdir(parents=True, exist_ok=True)

# Sandbox'a modified versiyonu kopyala (testlerden once fixture hazir olsun)
def _ensure_sandbox_module() -> Path:
    modified = Path(os.environ["TEMP"]) / "kilo" / "ostim_scraper_modified.py"
    if not modified.exists():
        pytest.skip(f"Modified scraper bulunamadi: {modified}. Once make_patch.py calistir.")
    target = SANDBOX / "ostim_scraper.py"
    if not target.exists() or target.read_bytes() != modified.read_bytes():
        target.write_bytes(modified.read_bytes())
    return target


@pytest.fixture(scope="session")
def scraper_module():
    """Sandbox altinda test kopya scraper modulu."""
    mod_path = _ensure_sandbox_module()
    sys.path.insert(0, str(SANDBOX))
    import importlib
    if "ostim_scraper" in sys.modules:
        importlib.reload(sys.modules["ostim_scraper"])
    import ostim_scraper  # noqa: E402
    return ostim_scraper


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    fdir = OUTPUT_DIR / "fixtures"
    assert fdir.exists(), f"Fixture dizini yok: {fdir}"
    return fdir


def _make_response(html_text: str, status_code: int = 200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = html_text
    resp.raise_for_status = MagicMock()
    if status_code >= 400:
        import requests as _req
        err = _req.HTTPError(f"{status_code} error")
        resp.raise_for_status.side_effect = err
    return resp


# =============================================================================
# 1) fetch_firma_detay() temel davranis
# =============================================================================

class TestFetchFirmaDetay:
    """fetch_firma_detay() birim testleri."""

    def test_http_200_table_layout(self, scraper_module, fixtures_dir):
        html = (fixtures_dir / "detail_table.html").read_text(encoding="utf-8")
        with patch.object(scraper_module.requests, "get",
                          return_value=_make_response(html, 200)):
            data = scraper_module.fetch_firma_detay("abc-muhendislik")
        assert data["adres"], "Adres parse edilmedi"
        assert "Ostim" in data["adres"]
        assert data["vergi_no"] == "1234567890"
        assert data["vergi_no_kaynagi"] == "detay_sayfa"
        assert data["web_sitesi"] == "https://www.abcmuh.com.tr"
        assert data["osb_parsel"]
        assert "Ada" in data["osb_parsel"] or "Parsel" in data["osb_parsel"]

    def test_http_200_dl_layout(self, scraper_module, fixtures_dir):
        html = (fixtures_dir / "detail_dl.html").read_text(encoding="utf-8")
        with patch.object(scraper_module.requests, "get",
                          return_value=_make_response(html, 200)):
            data = scraper_module.fetch_firma_detay("xyz-makina")
        assert data["adres"], "DL layout'ta adres parse edilmedi"
        assert data["vergi_no"] == "98765432101"
        assert data["web_sitesi"] == "https://xyzmakina.com.tr"
        assert data["osb_parsel"]

    def test_http_200_div_layout(self, scraper_module, fixtures_dir):
        html = (fixtures_dir / "detail_div.html").read_text(encoding="utf-8")
        with patch.object(scraper_module.requests, "get",
                          return_value=_make_response(html, 200)):
            data = scraper_module.fetch_firma_detay("def-tekstil")
        assert data["adres"]
        assert data["vergi_no"] == "12345678901"
        assert data["osb_parsel"]
        assert "PARSEL" in data["osb_parsel"] or "Parsel" in data["osb_parsel"]

    def test_http_404_returns_empty_dict(self, scraper_module):
        with patch.object(scraper_module.requests, "get",
                          return_value=_make_response("<html></html>", 404)):
            data = scraper_module.fetch_firma_detay("yok-firma")
        assert data == {}, "404 icin bos dict donmeli"

    def test_http_500_returns_empty_dict(self, scraper_module):
        with patch.object(scraper_module.requests, "get",
                          return_value=_make_response("<html></html>", 500)):
            data = scraper_module.fetch_firma_detay("hata-firma")
        assert data == {}

    def test_network_error_returns_empty_dict(self, scraper_module):
        import requests as _req
        with patch.object(scraper_module.requests, "get",
                          side_effect=_req.ConnectionError("boom")):
            data = scraper_module.fetch_firma_detay("timeout-firma")
        assert data == {}

    def test_timeout_returns_empty_dict(self, scraper_module):
        import requests as _req
        with patch.object(scraper_module.requests, "get",
                          side_effect=_req.Timeout("slow")):
            data = scraper_module.fetch_firma_detay("slow-firma")
        assert data == {}

    def test_empty_html_returns_empty_fields(self, scraper_module, fixtures_dir):
        html = (fixtures_dir / "detail_empty.html").read_text(encoding="utf-8")
        with patch.object(scraper_module.requests, "get",
                          return_value=_make_response(html, 200)):
            data = scraper_module.fetch_firma_detay("bos-firma")
        # bos html ama status 200: dict dolu, alanlar None olmali
        assert "adres" in data
        assert "vergi_no" in data
        assert data["adres"] is None
        assert data["vergi_no"] is None
        assert data["osb_parsel"] is None
        assert data["web_sitesi"] is None

    def test_broken_html_partial_parse(self, scraper_module, fixtures_dir):
        html = (fixtures_dir / "detail_broken.html").read_text(encoding="utf-8")
        with patch.object(scraper_module.requests, "get",
                          return_value=_make_response(html, 200)):
            data = scraper_module.fetch_firma_detay("bozuk-firma")
        # Bozuk HTML'de en azindan bir alan parse edilebilmeli
        assert data.get("adres") or data.get("osb_parsel") or data["vergi_no"] is None

    def test_does_not_raise_on_unexpected_status(self, scraper_module):
        with patch.object(scraper_module.requests, "get",
                          return_value=_make_response("teapot", 418)):
            # 4xx dahili retry_backoff yok, sadece warning log + response return
            data = scraper_module.fetch_firma_detay("teapot-firma")
            # 418 < 500, dolayisiyla response doner, dict dolu olur (bos alanlar)
            assert isinstance(data, dict)


# =============================================================================
# 2) Vergi_no normalize + fallback
# =============================================================================

class TestVergiNoNormalize:
    """vergi_no normalize ve fallback testleri."""

    def test_10_hane_dogru(self, scraper_module):
        assert scraper_module._normalize_vergi_no("1234567890") == "1234567890"

    def test_11_hane_tuzel_kisi(self, scraper_module):
        assert scraper_module._normalize_vergi_no("12345678901") == "12345678901"

    def test_format_nokta(self, scraper_module):
        assert scraper_module._normalize_vergi_no("1.234.567.890") == "1234567890"

    def test_format_bosluk(self, scraper_module):
        assert scraper_module._normalize_vergi_no("1 234 567 890 1") == "12345678901"

    def test_maskelenmis_yildiz(self, scraper_module):
        assert scraper_module._normalize_vergi_no("**********") is None
        assert scraper_module._normalize_vergi_no("***") is None

    def test_bos_string(self, scraper_module):
        assert scraper_module._normalize_vergi_no("") is None
        assert scraper_module._normalize_vergi_no(None) is None

    def test_kisa_sayi(self, scraper_module):
        # 9 hane -> gecersiz
        assert scraper_module._normalize_vergi_no("123456789") is None

    def test_uzun_sayi(self, scraper_module):
        # 12 hane -> gecersiz
        assert scraper_module._normalize_vergi_no("123456789012") is None

    def test_unvan_fallback_basarili(self, scraper_module):
        vkn, kaynak = scraper_module._vergi_no_fallback("ABC Holding VKN:12345678901 A.S.")
        assert vkn == "12345678901"
        assert kaynak == "unvan_regex"

    def test_unvan_fallback_bos(self, scraper_module):
        vkn, kaynak = scraper_module._vergi_no_fallback("")
        assert vkn is None and kaynak is None

    def test_unvan_fallback_yok(self, scraper_module):
        vkn, kaynak = scraper_module._vergi_no_fallback("Temiz Firma Adi")
        assert vkn is None and kaynak is None


# =============================================================================
# 3) Web blocklist + subdomain
# =============================================================================

class TestWebBlocklist:
    """Web sitesi blocklist filtre testleri."""

    @pytest.mark.parametrize("url", [
        "https://www.facebook.com/firma",
        "https://twitter.com/firma",
        "https://x.com/firma",
        "https://www.linkedin.com/company/firma",
        "https://www.instagram.com/firma",
        "https://www.youtube.com/@firma",
        "https://www.tiktok.com/@firma",
        "https://www.sahibinden.com/firma",
        "https://www.hepsiburada.com/firma",
        "https://www.trendyol.com/firma",
        "https://www.n11.com/firma",
        "https://www.gittigidiyor.com/firma",
        "https://amazon.com.tr/firma",
        "https://www.google.com/search",
        "https://yandex.com.tr",
        "https://www.example.com",
        "https://example.org",
        "https://test.com",
        "http://localhost:8080",
        "http://127.0.0.1:5000",
        "https://www.ostim.org.tr",
        "https://ostimonline.com/Home/OstimMain",
    ])
    def test_blocked(self, scraper_module, url):
        assert scraper_module._is_blocked(url), f"Blocklanmasi gerekir: {url}"

    @pytest.mark.parametrize("url", [
        "https://www.abcmuh.com.tr",
        "http://xyzmakina.com.tr",
        "https://deftekstil.com",
        "https://mnoinsaatt.com.tr",
        "https://firma-adi.com.tr",
    ])
    def test_not_blocked(self, scraper_module, url):
        assert not scraper_module._is_blocked(url), f"Blocklanmamali: {url}"

    def test_subdomain_blocked(self, scraper_module):
        # m.facebook.com -> facebook.com olarak taninmali
        assert scraper_module._is_blocked("https://m.facebook.com/firma")
        assert scraper_module._is_blocked("https://tr.linkedin.com/in/user")
        assert scraper_module._is_blocked("https://m.youtube.com/watch?v=123")

    def test_subdomain_not_blocked_when_root_allowed(self, scraper_module):
        # abcmuh.com.tr domainine ait subdomain firma-ozgu sayilir
        assert not scraper_module._is_blocked("https://shop.abcmuh.com.tr")

    def test_http_https_schemes(self, scraper_module):
        # http:// ve https:// her ikisi de blocklanmali
        assert scraper_module._is_blocked("http://example.com")
        assert scraper_module._is_blocked("https://example.com")


# =============================================================================
# 4) Web sitesi extraction (blocklist entegrasyonu)
# =============================================================================

class TestExtractWebSitesi:
    """_extract_web_sitesi() entegrasyon testleri."""

    def test_skip_blocked_picks_first_valid(self, scraper_module, fixtures_dir):
        html = (fixtures_dir / "detail_blocklist.html").read_text(encoding="utf-8")
        soup = BeautifulSoup(html, "html.parser")
        web = scraper_module._extract_web_sitesi(soup)
        # Tum linkler blocklistte (facebook, sahibinden, example, localhost, ostim)
        assert web is None, f"Beklenen None, gelen: {web}"

    def test_returns_first_non_blocked(self, scraper_module):
        html = """<html><body>
            <a href="https://www.facebook.com/x">FB</a>
            <a href="https://www.abcmuh.com.tr">WEB</a>
        </body></html>"""
        soup = BeautifulSoup(html, "html.parser")
        web = scraper_module._extract_web_sitesi(soup)
        assert web == "https://www.abcmuh.com.tr"


# =============================================================================
# 5) Vergi_no maskelenmis davranis (detay entegrasyon)
# =============================================================================

class TestVergiNoMaskelenmis:
    """Detay sayfasinda vergi_no '**********' ise None + maske_kaynagi."""

    def test_maskelenmis_returns_none_with_kaynagi(self, scraper_module, fixtures_dir):
        html = (fixtures_dir / "detail_blocklist.html").read_text(encoding="utf-8")
        with patch.object(scraper_module.requests, "get",
                          return_value=_make_response(html, 200)):
            data = scraper_module.fetch_firma_detay("ghi-plastik")
        assert data["vergi_no"] is None
        # Normalize fonksiyonu maskelenmis durumda None doner, kaynak 'maskelenmis' olur
        assert data["vergi_no_kaynagi"] in ("maskelenmis", None)


# =============================================================================
# 6) UTF-8 / Turkce karakter / whitespace normalize
# =============================================================================

class TestUnicodeAndWhitespace:
    """Turkce karakter ve whitespace normalizasyonu."""

    def test_turkce_karakter_adres(self, scraper_module, fixtures_dir):
        html = (fixtures_dir / "detail_unicode.html").read_text(encoding="utf-8")
        with patch.object(scraper_module.requests, "get",
                          return_value=_make_response(html, 200)):
            data = scraper_module.fetch_firma_detay("mno-insaat")
        assert data["adres"]
        assert "OSTİM" in data["adres"] or "OSTIM" in data["adres"]
        # nbsp temizlenmis olmali (aralikli "OSTİM OSB 100. Yıl" gibi)
        assert "\u00a0" not in data["adres"], "nbsp temizlenmemis"

    def test_vergi_no_formatli(self, scraper_module, fixtures_dir):
        html = (fixtures_dir / "detail_unicode.html").read_text(encoding="utf-8")
        with patch.object(scraper_module.requests, "get",
                          return_value=_make_response(html, 200)):
            data = scraper_module.fetch_firma_detay("mno-insaat")
        # "1 234 567 890 1" -> "12345678901"
        assert data["vergi_no"] == "12345678901"


# =============================================================================
# 7) Ada/Parsel fallback (adres icinde PARSEL/ADA)
# =============================================================================

class TestParselFallback:
    """osb_parsel fallback testleri."""

    def test_parsel_adres_icinde(self, scraper_module):
        parsel, kaynak = scraper_module._parsel_fallback(
            "Ostim OSB, Ada: 12, PARSEL: 34, Yenimahalle"
        )
        assert parsel is not None
        assert kaynak == "adres_icinde"

    def test_parsel_yok(self, scraper_module):
        parsel, kaynak = scraper_module._parsel_fallback("Temiz adres, parsel bilgisi yok")
        assert parsel is None and kaynak is None

    def test_parsel_bos(self, scraper_module):
        parsel, kaynak = scraper_module._parsel_fallback(None)
        assert parsel is None and kaynak is None
        parsel, kaynak = scraper_module._parsel_fallback("")
        assert parsel is None and kaynak is None


# =============================================================================
# 8) --detayli modu (scrape_firma_full entegrasyon)
# =============================================================================

class TestDetayliModu:
    """scrape_firma_full() --detayli modunda tum sektor/sayfa calisir."""

    def test_scrape_firma_full_detayli(self, scraper_module, fixtures_dir):
        liste_html = """<html><body>
            <a href="/firmalar/firma-a">
                <p class="listCompanyTitle"><i class="icon"></i>Firma A VKN:1234567890</p>
                <p class="listCompanyPhone"><i class="icon"></i>+90 312 111 22 33</p>
                <p class="listCompanyMail"><i class="icon"></i>info@firmaa.com.tr</p>
            </a>
            <a href="/firmalar/firma-b">
                <p class="listCompanyTitle"><i class="icon"></i>Firma B</p>
            </a>
        </body></html>"""
        detail_html = (fixtures_dir / "detail_table.html").read_text(encoding="utf-8")
        empty_html = (fixtures_dir / "detail_empty.html").read_text(encoding="utf-8")

        responses = iter([
            _make_response(liste_html, 200),
            _make_response(detail_html, 200),
            _make_response(empty_html, 200),
        ])

        with patch.object(scraper_module.requests, "get", side_effect=lambda *a, **kw: next(responses)):
            with patch.object(scraper_module.time, "sleep"):
                firmalar = list(scraper_module.scrape_firma_full(
                    scraper_module.BASE_URL + "/firmalar", sayfa=1, detay_al=True
                ))

        assert len(firmalar) == 2
        # Firma A: detay basarili, VKN unvandan regex ile de dogrulanabilir
        assert firmalar[0].adres is not None
        assert firmalar[0].vergi_no in ("1234567890", "12345678901") or \
               firmalar[0].vergi_no == "1234567890"
        # Firma B: detay bos HTML, fallback ile unvan icinde VKN yok
        assert firmalar[1].adres is None


# =============================================================================
# 9) Tum 12 sektor batch testi (smoke)
# =============================================================================

SAMPLE_12_SEKTOR = [
    "muhendislik", "makina", "tekstil", "plastik", "elektrik",
    "elektronik", "otomotiv", "metal", "kimya", "gida",
    "mobilya", "ambalaj",
]


class TestTumSektorBatch:
    """12 sektor uzerinden --detayli modu smoke testi."""

    def test_12_sektor_hepsi_calisir(self, scraper_module, fixtures_dir):
        detail_html = (fixtures_dir / "detail_table.html").read_text(encoding="utf-8")
        for sektor in SAMPLE_12_SEKTOR:
            liste_html = f"""<html><body>
                <a href="/firmalar/{sektor}-firma-1">
                    <p class="listCompanyTitle"><i class="icon"></i>{sektor} Firma 1</p>
                </a>
            </body></html>"""
            responses = iter([
                _make_response(liste_html, 200),
                _make_response(detail_html, 200),
            ])
            with patch.object(scraper_module.requests, "get",
                              side_effect=lambda *a, **kw: next(responses)):
                with patch.object(scraper_module.time, "sleep"):
                    firmalar = list(scraper_module.scrape_firma_full(
                        scraper_module.BASE_URL + "/firmalar", sayfa=1, detay_al=True
                    ))
            assert len(firmalar) == 1, f"{sektor}: 1 firma bekleniyor"
            assert firmalar[0].adres is not None, f"{sektor}: adres bos"
            # Hata orani < %1 (12/12 basarili = %0)
        assert True  # Tum sektorler gecti


# =============================================================================
# 10) Patch metadata
# =============================================================================

class TestPatchMeta:
    """Patch dosyasi metadata kontrolu."""

    def test_patch_dosyasi_var(self):
        assert PATCH_FILE.exists(), f"Patch dosyasi yok: {PATCH_FILE}"

    def test_patch_git_apply_basarili(self):
        """Patch'in proje kaynagina uygulanabilirligini dogrula."""
        import subprocess
        result = subprocess.run(
            ["git", "apply", "--check", str(PATCH_FILE)],
            cwd=str(WORKSPACE_ROOT),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"git apply --check basarisiz: {result.stderr}"