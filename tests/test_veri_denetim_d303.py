"""D-303 regresyon testleri — KAPSAMLI veri denetimi.

KAHIN (2026-09-29): "bu gibi hatalari onceden farkinda olalim, her satir
dogru veri varmi yok mu hatlari tekrar gozden gecir, ostim ve ivedik
dahil, her sey hazir olsun."

BU DOSYA NE KORUYOR:
  veri_denetim_tam.py yazilirken 3 YANLIŞ ALARM ve 1 VERİ BOZMA
  bulundu. Hepsi testle kilitlendi:
    1. Eski capraz kural, ayni slug'i iki kaynakta gordugu icin 8.296
       YANLIŞ ALARM uretiyordu (birlestirilmis kopya + temiz kopya
       normalde ayni firmayi icerir).
    2. EMAIL regex'i ASCII ile sinirliydi; Turkce karakterli GECERLI
       epostalari ("erenkocyigit26") hata ilan ediyordu.
    3. web_temizle'deki `(?<=/)\\s*\\d` deseni "http://3atest.com.tr"
       degerini "http:///" yapti — VERI KAYBI.
    4. URL_OK deseni `[^\\s]+` oldugu icin BOZUK "https://http//a.com"
       degerini gecerli sayiyor ve duzeltme hic calismiyordu.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import sys

import pytest

KOK = pathlib.Path(__file__).resolve().parents[1]
_MOD = KOK / "scripts" / "veri_denetim_tam.py"

if not _MOD.is_file():
    pytest.skip(f"modul yok: {_MOD}", allow_module_level=True)

_spec = importlib.util.spec_from_file_location("veri_denetim_tam", _MOD)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["veri_denetim_tam"] = _mod
_spec.loader.exec_module(_mod)

web_temizle = _mod.web_temizle


def re_alani(url: str) -> bool:
    """URL'de en az bir nokta + 2+ harfli alan adi var mi."""
    govde = url.split("://", 1)[-1].split("/")[0]
    return bool(re.search(r"\.[A-Za-z]{2,}$", govde))


# -------------------------------------------- YANLIŞ ALARM KORUMASI (1)

class TestCaprazKuraliYanlisAlarm:
    """Ayni slug iki kaynakta = NORMALDIR, hata degildir."""

    @pytest.fixture(scope="class")
    def temiz(self):
        yol = KOK / "data" / "ostim" / "OSTIM_TEMIZ.jsonl"
        if not yol.is_file():
            pytest.skip("OSTIM_TEMIZ.jsonl yok")
        return [json.loads(x) for x in
                yol.read_text(encoding="utf-8").splitlines() if x.strip()]

    def test_slug_tekillestirilmis(self, temiz):
        sluglar = [s.get("slug") for s in temiz if s.get("slug")]
        assert len(sluglar) == len(set(sluglar)), (
            f"{len(sluglar) - len(set(sluglar))} tekrar eden slug")

    def test_dosya_ici_capraz_kurali_temiz(self, temiz):
        r = _mod.Rapor("t")
        for i, s in enumerate(temiz, 1):
            _mod.denetle_kayit(s, r, i)
        assert r.sayi("capraz/dosya_ici_ayni_slug") == 0
        assert r.sayi("capraz/ayni_unvan_ayni_adres") <= 10, (
            "mukerrer grubu beklenenden fazla")


# ------------------------------------------- TURKCE EPOSTA (ALARM 2)

class TestEmailKurali:
    @pytest.mark.parametrize("e", [
        "erenkocyigit26@gmail.com",
        "yenidosusabdullah@gmail.com",
        "info@kaynaryol.com.tr",
        "C.Peker@age.com.tr",
    ])
    def test_turkce_karakterli_eposta_gecerli(self, e):
        assert _mod.EMAIL.match(e), f"gecerli eposta reddedildi: {e}"

    @pytest.mark.parametrize("e", ["bilgehan", "@firma.com", "info@", "a b@c.com"])
    def test_bozuk_eposta_reddedilir(self, e):
        assert not _mod.EMAIL.match(e), f"bozuk eposta kabul edildi: {e}"


# ------------------------------------------- VERI KAYBI KORUMASI (3)

class TestWebVeriKaybi:
    """Duzeltme ASLA alani bosaltmamali."""

    @pytest.mark.parametrize("ham", [
        "http://3atest.com.tr",
        "https://3d3teknoloji.com",
        "http://else.grimor.com/tr-TR/else-elektrik/208870",
    ])
    def test_alan_bosaltilmaz(self, ham):
        sonuc = web_temizle(ham)
        assert sonuc, f"deger YOK EDILDI: {ham}"
        govde = sonuc.split("://", 1)[-1]
        assert govde.strip("/"), f"alan BOSALTILDI: {ham} -> {sonuc}"
        assert re_alani(sonuc), f"alan adi kalmadi: {ham} -> {sonuc}"

    def test_sadece_rakam_web_alanina_yazilmaz(self):
        """"https://5050051468" bir TELEFON numarasidir, web adresi degil.
        Bu KOLON KARIŞMASI (K-2) — web alanina yazilmamalidir.
        Telefon zaten telefonlar listesinde durur; burada None doner."""
        assert web_temizle("https://5050051468") is None, (
            "sadece rakamdan olusan deger web sanildi")

    @pytest.mark.parametrize("eposta", [
        "https://erolnevpa@homail.com",
        "https://bsait@borusan.com",
        "https://kocaklarkaynak@hotmail.com",
        "https://nilkamakina@gmail.com",
        "https://muhasebe@prowin.com.tr",
    ])
    def test_eposta_web_alanina_yazilmaz(self, eposta):
        """'https://' ile baslayan E-POSTA degerleri K-2 kolon kirisidir.
        Ustelik bunlar GECERLI adresler; web_sitesi alaninda tutulmamali.
        web_temizle bunlari duzeltip web'e yazmaz."""
        sonuc = web_temizle(eposta)
        assert sonuc is None or "@" not in sonuc, (
            f"eposta web alanina yazildi: {eposta} -> {sonuc}")

    def test_gecerli_url_bozulmaz(self):
        for iyi in ("https://www.ekolyazilim.com",
                    "http://kal-met.com",
                    "https://www.merkezinsaat.com.tr"):
            assert web_temizle(iyi) == iyi, f"gecerli url degisti: {iyi}"


# ------------------------------------------- BOZUK URL YAKALAMA (4)

class TestBozukUrlYakalanir:
    @pytest.mark.parametrize("ham,duzeltilmis", [
        ("www bfblast.com", "bfblast.com"),
        ("https://http//www.ekolsistem.com.tr    http://www.esdor.com.tr",
         "esdor.com.tr"),
        ("https://http//www.forakim.com.tr     www.forakim.com",
         "forakim.com"),
        ("http://www.isikimalat.com/0 312 354 22 65", "isikimalat.com"),
    ])
    def test_duzeltme_urecege_girer(self, ham, duzeltilmis):
        sonuc = web_temizle(ham)
        assert sonuc, f"duzeltilemedi: {ham}"
        assert duzeltilmis in sonuc, f"beklenen alan adi yok: {ham} -> {sonuc}"

    @pytest.mark.parametrize("bozuk", [
        "https://http//a.com",
        "https://erolnevpa@homail.com",
        "https://5050051468",
    ])
    def test_bozuk_url_gecersiz_sayilir(self, bozuk):
        """Bozuk deger duzelttikten SONRA da gecersizse None doner."""
        sonuc = web_temizle(bozuk)
        assert sonuc is None or not _mod.URL_OK.match(sonuc), (
            f"bozuk kabul edildi: {bozuk} -> {sonuc}")


# ------------------------------------------- DIZI BUTUNLUGU (CANLI)

class TestCanliDizi:
    @pytest.fixture(scope="class")
    def temiz(self):
        yol = KOK / "data" / "ostim" / "OSTIM_TEMIZ.jsonl"
        if not yol.is_file():
            pytest.skip("OSTIM_TEMIZ.jsonl yok")
        return [json.loads(x) for x in
                yol.read_text(encoding="utf-8").splitlines() if x.strip()]

    def test_hicbir_url_bos_degil(self, temiz):
        kotu = [s.get("web_sitesi") for s in temiz
                if s.get("web_sitesi") and
                str(s["web_sitesi"]).strip() in ("", "http:///", "https:///", "/")]
        assert not kotu, f"bos/bozuk URL: {kotu[:3]}"

    def test_hicbir_eposta_bozuk_degil(self, temiz):
        kotu = [e for s in temiz for e in (s.get("emailler") or [])
                if not _mod.EMAIL.match(str(e).strip())]
        assert not kotu, f"{len(kotu)} bozuk eposta: {kotu[:3]}"

    def test_eposta_tekillestirilmis(self, temiz):
        for s in temiz:
            e = [str(x).strip().lower() for x in (s.get("emailler") or [])]
            assert len(e) == len(set(e)), f"tekrar eden eposta: {s.get('slug')}"

    def test_telefon_kahin_kuralina_uyuyor(self, temiz):
        """DIKKAT: desen test icine YAZILMAZ, modulun kendi sabitinden
        alinir. Teste ayri regex yazildiginde iki kural birbirinden
        ayrildi ve modul 0 hata verirken test 2 hata sayiyordu —
        denetleyen kod degil, TESTIN kendisi kaynakliydi."""
        kotu = [t for s in temiz for t in (s.get("telefonler") or [])
                if not (_mod.TEL_SABIT.match(str(t))
                        or _mod.TEL_CEP.match(str(t)))]
        assert not kotu, f"{len(kotu)} kural disi telefon: {kotu[:3]}"
