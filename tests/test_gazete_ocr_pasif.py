"""D-278 pasif kapilarinin testi.

Bu testler OCR hattinin KAZARA calismadigini kanitlar:
  1. `OCR_ETKIN` varsayilan olarak kapali
  2. Kapaliyken `pdf_ocr()` HTTP istegi YAPMADAN hata firlatir
  3. `--aktif` ile acilabiliyor (yeniden lazim oldugunda)
  4. Saf yardimcilar (MERSIS duzeltme, JSON ayiklama) calismaya devam eder
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
from PIL import Image

KOK = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

_MOD_YOLU = KOK / "scripts" / "gazete_ocr.py"
_spec = importlib.util.spec_from_file_location("gazete_ocr", _MOD_YOLU)
gazete_ocr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gazete_ocr)


class TestPasifKapi:
    """D-278: OCR varsayilan olarak kapali olmali."""

    def test_modul_import_edilir(self):
        """Pasifleştirme silme degil — modul ayakta olmali."""
        assert hasattr(gazete_ocr, "pdf_ocr")
        assert hasattr(gazete_ocr, "OCR_ETKIN")

    def test_varsayilan_kapali(self):
        assert gazete_ocr.OCR_ETKIN is False

    def test_kapaliyken_http_atmaz(self, monkeypatch):
        """Kritik: kapaliyken istek ATILMAMALI, hata firlatilmali."""
        cagrildi = []
        monkeypatch.setattr(
            gazete_ocr, "_istek_9router",
            lambda *a, **k: cagrildi.append(1),
        )
        with pytest.raises(gazete_ocr.OcrPasifHatasi):
            gazete_ocr.pdf_ocr(KOK / "data" / "kanit" / "448217_a18a2282.pdf")
        assert cagrildi == [], "kapaliyken HTTP atildi — PASIF KAPI CALISMIYOR"

    def test_pasif_uyari_menserisi_icerir(self):
        assert "D-278" in gazete_ocr.PASIF_UYARI
        assert "XML" in gazete_ocr.PASIF_UYARI

    def test_ocr_ac_kapat(self):
        """Yeniden lazim oldugunda acilabilmeli (geri alinabilirlik)."""
        try:
            assert gazete_ocr.ocr_ac(True) is True
            assert gazete_ocr.OCR_ETKIN is True
        finally:
            gazete_ocr.ocr_ac(False)
        assert gazete_ocr.OCR_ETKIN is False

    def test_zorla_bayragi_akitir(self, monkeypatch, tmp_path):
        """`zorla=True` kapiyi acar → istek yapilir.

        NOT: `pdf_ocr` ic cagriyi `sayfa_ocr` uzerinden yapar; ag
        katmanini test etmek icin `sayfa_ocr` patch edilir.
        """
        cagrildi = []
        png = tmp_path / "ornek.png"
        Image.new("RGB", (40, 40), "white").save(png)

        def sahte_sayfa(gorsel, model=gazete_ocr.VARSAYILAN_MODEL, ipucu=""):
            cagrildi.append(1)
            return {
                "gorsel": str(gorsel),
                "model": model,
                "sure_saniye": 0.1,
                "veri": {"ilan_sira_no": "49136"},
                "ham_cevap": "{}",
                "kullanim": {"toplam_token": 10},
                "hata": None,
            }

        monkeypatch.setattr(gazete_ocr, "pdf_tek_sayfa_png", lambda *a, **k: png)
        monkeypatch.setattr(gazete_ocr, "sayfa_ocr", sahte_sayfa)

        sonuc = gazete_ocr.pdf_ocr(tmp_path / "x.pdf", dilim=False, zorla=True)

        assert cagrildi == [1], "zorla=True olmasina ragmen istek atilmadi"
        assert sonuc["kanonik_veri"]["ilan_sira_no"] == "49136"


class TestSafYardimcilar:
    """Pasif olsa da saf (ag'siz) yardimcilar saglam kalmali."""

    def test_rakamlastir_turkce_karisikligi(self):
        # "0O12032O741OOO24" -> O harfleri rakam olur -> 17 haneli MERSIS
        # (bastaki sifir korunur; 17->16 kanonikleme `dogrula()` yapar).
        assert gazete_ocr._rakamlastir("0O12032O741OOO24") == "0012032074100024"

    def test_rakamlastir_bos(self):
        assert gazete_ocr._rakamlastir(None) is None
        assert gazete_ocr._rakamlastir("") is None

    def test_rakamlastir_nokta_tire_temizler(self):
        assert gazete_ocr._rakamlastir("4.482-217") == "4482217"

    def test_json_ayikla_kod_bloklu(self):
        metin = '```json\n{"a": 1}\n```'
        assert gazete_ocr._json_ayikla(metin) == {"a": 1}

    def test_json_ayikla_bozuk_girdi(self):
        assert gazete_ocr._json_ayikla("json yok") == {}

    def test_cevap_ayikla_sse_kalintisi(self):
        """D-280 KÖK NEDEN: gecerli JSON'un sonuna `data: [DONE]` ekleniyor.

        `r.json()` bu yuzden `Extra data` hatasi veriyor; model cagrisi
        aslinda basarili. Ayristirici kalintiyi kesmeli.
        """
        class FakeYanit:
            text = (
                '{"choices":[{"message":{"content":"{\\"a\\":1}"}}],'
                '"usage":{"total_tokens":5}}\ndata: [DONE]\n\n'
            )

            def json(self):
                # Gercek davranisi taklit et: once dogrudan dener.
                import json as _j

                _j.loads(self.text)

        sonuc = gazete_ocr._cevap_ayikla(FakeYanit())
        assert sonuc["choices"][0]["message"]["content"] == '{"a":1}'
        assert sonuc["usage"]["total_tokens"] == 5

    def test_cevap_ayikla_temiz_json(self):
        class Temiz:
            text = '{"choices": [], "usage": {"total_tokens": 1}}'

            def json(self):
                return {"choices": [], "usage": {"total_tokens": 1}}

        assert gazete_ocr._cevap_ayikla(Temiz())["usage"]["total_tokens"] == 1

    def test_cevap_ayikla_ayristirilamaz_hata_verir(self):
        class Bozuk:
            text = "hiç json değil"

            def json(self):
                import json as _j

                _j.loads(self.text)

        with pytest.raises(RuntimeError, match="ayristirilamadi"):
            gazete_ocr._cevap_ayikla(Bozuk())

    def test_ocr_hatasi_kapidan_girmez(self):
        """D-280: OCR 15 haneli (bozuk) MERSIS uretti — kapı REDDEDMELİ.

        Canlı ölçüm: gpt-4o-mini `001203074100024` (15 hane) okudu;
        gerçek `0012032074100024` (17 hane). Bu test regresyon kilididir.
        """
        bozuk = gazete_ocr.dogrula({"mersis_no": "001203074100024"})
        assert bozuk["mersis_kanonik_16"] is None
        assert bozuk["vkn_dogrulama"] is None

        dogru = gazete_ocr.dogrula({"mersis_no": "0012032074100024"})
        assert dogru["mersis_kanonik_16"] == "0012032074100024"
