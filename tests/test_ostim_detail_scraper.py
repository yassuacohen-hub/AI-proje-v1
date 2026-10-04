# -*- coding: utf-8 -*-
"""[[D-292]] OSTIM detay kaziyicisi web sitesi href filtresi (VERI-OSTIM-HREF-FILTRE-01).

Kirlama aninda olculmus gercek veri: `data/ostim/firmalar_detailed.jsonl`
icinde `web_sitesi` dolu 1555 kaydin **tamami** iki adrese bakiyordu
(1415 x nsosyal.com/ostim_osb, 140 x ostimonline.com/Home/OstimMain).
Yani gercek firma sitesi sayisi 0 idi. Testler bu kaziyi mandalla.
"""
import sys
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.etl.scrapers.ostim_detail_scraper import (  # noqa: E402
    WEB_BLOCKLIST,
    _etiketten_site,
    _is_company_website,
    extract_detail,
)

# Kirlama aninda olculmus iki adres. Ikisi de gercek firma sitesi DEGIL.
SIZINTI_ADRESLERI = (
    "https://nsosyal.com/ostim_osb",
    "https://www.ostimonline.com/Home/OstimMain",
)


class TestIsCompanyWebsite:
    """4 dogru + 4 yanlis href."""

    @pytest.mark.parametrize("href", [
        "https://arsmetal.com.tr",
        "http://www.dundarelektrik.com",
        "https://zmtpto.com/iletisim",
        "https://www.gidadanismanlik.com.tr/",
    ])
    def test_dogru_adres_kabul(self, href):
        assert _is_company_website(href) is True

    @pytest.mark.parametrize("href", [
        "https://nsosyal.com/ostim_osb",
        "https://www.ostimonline.com/Home/OstimMain",
        "mailto:info@arsmetal.com.tr",
        "javascript:void(0)",
    ])
    def test_yanlis_adres_red(self, href):
        assert _is_company_website(href) is False

    def test_sema_disiksema_red(self):
        assert _is_company_website("ftp://arsmetal.com.tr") is False
        assert _is_company_website("tel:+903121234567") is False
        assert _is_company_website("www.arsmetal.com.tr") is False

    def test_kancalama_yaln_yalin_sozlesme_sozleri(self):
        """'http' ile baslayan ama sema olmayan bir deger de reddedilmeli."""
        assert _is_company_website("httpfoo://arsmetal.com.tr") is False

    @pytest.mark.parametrize("adres", SIZINTI_ADRESLERI)
    def test_sizinti_adresleri_ret_listesinde(self, adres):
        assert any(b in adres for b in WEB_BLOCKLIST)

    def test_bos_girdi_ve_kok_adres(self):
        assert _is_company_website("") is False
        assert _is_company_website(None) is False
        assert _is_company_website("https://www.arsmetal.com.tr/") is True


class TestEtikettenSite:
    def _soup(self, html):
        return BeautifulSoup(html, "html.parser")

    def test_etiket_yakinindaki_link_alinir(self):
        soup = self._soup(
            '<div><a href="https://nsosyal.com/ostim_osb">OSB</a>'
            '<li>Web Sitesi: <a href="https://arsmetal.com.tr">ARS</a></li></div>'
        )
        assert _etiketten_site(soup) == "https://arsmetal.com.tr"

    def test_etiket_yoksa_bos_doner_tahmin_yok(self):
        soup = self._soup('<div><a href="https://arsmetal.com.tr">ARS</a></div>')
        assert _etiketten_site(soup) is None

    def test_etiket_kutusunda_yalniz_sizinti_varsa_bos(self):
        soup = self._soup(
            '<li>Web Sitesi: <a href="https://nsosyal.com/ostim_osb">OSB</a></li>'
        )
        assert _etiketten_site(soup) is None


class TestExtractDetail:
    def _html(self, site_html):
        return (
            '<html><body>'
            '<a href="https://nsosyal.com/ostim_osb">OSB sosyal</a>'
            f'{site_html}'
            '</body></html>'
        )

    def test_sayfa_sablonu_linki_web_sitesi_sayilmaz(self, monkeypatch):
        html = self._html('<li>Web Sitesi: <a href="https://arsmetal.com.tr">ARS</a></li>')

        class R:
            status_code = 200
            text = html

            def raise_for_status(self):
                return None

        monkeypatch.setattr(
            "company_master.etl.scrapers.ostim_detail_scraper.requests.get",
            lambda *a, **k: R(),
        )
        d = extract_detail("ornek-firma")
        assert d["web_sitesi"] == "https://arsmetal.com.tr"

    def test_etiket_yoksa_web_sitesi_bos_kalir(self, monkeypatch):
        html = self._html('<a href="https://arsmetal.com.tr">ARS</a>')

        class R:
            status_code = 200
            text = html

            def raise_for_status(self):
                return None

        monkeypatch.setattr(
            "company_master.etl.scrapers.ostim_detail_scraper.requests.get",
            lambda *a, **k: R(),
        )
        d = extract_detail("ornek-firma")
        assert d["web_sitesi"] is None


class TestOlcumTekKaynak:
    """[[D-211]] / [[D-266]] — olcum araci kendi kuralini TASIYAMAZ.

    Kirilma: `ostim_href_olc.py` kendi `KOTU_DESEN` regex'ini tasiyordu ve
    `nsosyal.com` listede yoktu. Olcum 1555 dolu kaydin 140'ini yanlis-pozitif
    saydi; gercek tablo 1555/1555. Aracin kendi hatasini gizlemesi D-309/1'in
    taze ornegi ("aracin yesil demesi kanit degil").
    """

    def test_olcum_betiği_uretici_kuralini_ithal_eder(self):
        kaynak = (ROOT / "scripts" / "ostim_href_olc.py").read_text(encoding="utf-8")
        assert "from company_master.etl.scrapers.ostim_detail_scraper import" in kaynak
        assert "_is_company_website" in kaynak
        # Kendi basina alan adi listesi/regesi TASIMAMALI (ikiz yapi yasagi).
        assert "KOTU_DESEN =" not in kaynak

    def test_olcum_ureticinin_ayni_karari_verir(self, tmp_path):
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "ostim_href_olc", ROOT / "scripts" / "ostim_href_olc.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        ornek = tmp_path / "o.jsonl"
        ornek.write_text(
            "\n".join(
                '{"web_sitesi": "%s"}' % a for a in SIZINTI_ADRESLERI
            ) + "\n",
            encoding="utf-8",
        )
        r = mod.olc(ornek)
        assert r["web_sitesi_dolu"] == 2
        assert r["yanlis_pozitif"] == 2
        assert r["filtreyi_gecen"] == 0
        assert r["bloklist_uzunluk"] == len(WEB_BLOCKLIST)


class TestPilotSecimi:
    """KAHIN 2026-10-03: pilot A.S. olsun. ASCII regex 606 firmayi elemişti."""

    def _mod(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "ostim_pilot_firma_sec", ROOT / "scripts" / "ostim_pilot_firma_sec.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_turkce_anonim_sirketi_eslesir(self):
        mod = self._mod()
        assert mod.uygun({"unvan": "3E ELEKTRO OPTİK SİSTEMLER SANAYİ VE TİCARET ANONİM ŞİRKETİ"})
        assert mod.uygun({"unvan": "4N BİLİŞİM TEKNOLOJİLERİ A.Ş."})

    def test_ltd_tasfiye_ve_sube_elenir(self):
        mod = self._mod()
        assert not mod.uygun({"unvan": "ARS METAL SAN. VE TİC. LTD. ŞTİ."})
        assert not mod.uygun({"unvan": "Dönmez Motorlu Araçlar San.Tic Anonim Şti-Ankara Şubesi"})
        assert not mod.uygun({"unvan": ""})

    def test_kirilma_denemesi_ascii_regex_turkce_yazimi_gormez(self):
        """KIRMA TESTI — olculmus mekanizma.

        Python `re.IGNORECASE`: U+0130 ("I") ASCII "I" ile ESLESIR, ama
        U+015E ("S") ASCII "S" ile ESLESMEZ. Yani eski regex
        `\\bA\\.\\s*S\\.|ANONIM|SIRKETI`:
          - "ANONIM" dali "ANONIM SIRKETI" yazimini yakaladi (296 kayit),
          - `A\\.\\s*S\\.` dali "A.S." ASCII yazimini yakaladi (88 kayit),
          - "A.S." (cedillali S) yazili 607 A.S. kaydi **hic gormedi**.
        Olcum: 385 eslesen / 991 gercek -> 606 A.S. firma elendi.
        """
        import re as _re

        mod = self._mod()
        turkce = "Epsilon Havacılık Uzay Ve Savunma San. Tic. A.Ş."
        assert _re.search(r"A\.\s*S\.", "A.S.", _re.IGNORECASE)
        assert _re.search(r"ANONIM", "ANONİM", _re.IGNORECASE)  # I eslesir
        assert not _re.search(r"A\.\s*S\.", turkce, _re.IGNORECASE)  # S eslesmez
        assert mod.uygun({"unvan": turkce}) is True

    def test_sektor_odakli_sayi(self):
        mod = self._mod()
        savunma = mod.sektor_puan({"unvan": "ASECRON SAVUNMA VE HAVACILIK A.Ş."})
        yazilim = mod.sektor_puan({"unvan": "4N BİLİŞİM TEKNOLOJİLERİ A.Ş."})
        assert savunma > 0
        assert yazilim == 0
