# -*- coding: utf-8 -*-
"""SCRAPE-004: LLM ile siniflandirma.

EN KRITIK KURAL (D-245): hicbir model calismazsa ya da cevap JSON degilse
**uydurma etiket yazilmaz**. "Bilmiyorum" ile "0" ayni degildir.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "src"))

spec = importlib.util.spec_from_file_location(
    "kazima_qwen", KOK / "scripts" / "kazima_qwen_classify.py")
kq = importlib.util.module_from_spec(spec)
sys.modules["kazima_qwen"] = kq
spec.loader.exec_module(kq)

#: Fixture bunu stub'lar; gercek davranisi test eden test geri koyar.
GERCEK_EVREN_DENE = kq._evren_bir_model_dene


def test_json_ayikla_duz():
    assert kq._json_ayikla('{"a": 1}') == {"a": 1}


def test_json_ayikla_kod_fences():
    """LLM bazen ```json ile sarar; bu normaldir."""
    v = kq._json_ayikla('```json\n{"etiket_bos": false, "nace_kodu": "62.01"}\n```')
    assert v["nace_kodu"] == "62.01"


def test_json_ayikla_geri_sari_metin():
    v = kq._json_ayikla('Tamam: {"etiket_bos": false} umarim ise yarar')
    assert v["etiket_bos"] is False


def test_json_ayikla_cozulemezse_none():
    """JSON olmayan cevap ETIKET DEGILDIR."""
    assert kq._json_ayikla("Bilmiyorum, elimde veri yok") is None
    assert kq._json_ayikla("") is None
    assert kq._json_ayikla("[1,2,3]") is None


@pytest.fixture(autouse=True)
def _evren_kapali(monkeypatch):
    """EVREN varsayilan olarak ONCE denenir. 9Router zincirini test eden
    testlerde EVREN cagrisini devre disi birakiriz.

    DIKKAT: sadece `_evren_bir_model_dene` stub'lanir; `_evren_anahtari`
    GERCEK kalir, yoksa anahtar okuma testleri calisamaz.
    """
    monkeypatch.setattr(kq, "_evren_bir_model_dene",
                        lambda h, m: ("", "HTTPError: 503 (test)"))


def test_hicbir_model_calismazsa_etiket_yok(monkeypatch):
    """503/401 ne olursa olsun ETIKET UYDURULMAZ."""
    monkeypatch.setattr(kq, "_bir_model_dene", lambda h, m: ("", "HTTPError: 503"))
    s = kq.qwen_siniflandir("<html>x</html>")
    assert s["etiket_bos"] is True
    assert s["nace_kodu"] is None and s["sektor_adi"] is None
    assert s["denenen"] == len(kq.EVREN_MODELLER) + len(kq.MODEL_ZINCIRI)


def test_zincir_calisan_modele_gecer(monkeypatch):
    """Ilk model 503, ikinci calisir: sonuc ikinciden gelir."""
    def _dene(html, model):
        if model == kq.MODEL_ZINCIRI[1]:
            return '{"etiket_bos": false, "nace_kodu": "62.01", ' \
                   '"sektor_adi": "Yazilim", "unvan": "AC"}', ""
        return "", "HTTPError: 503"

    monkeypatch.setattr(kq, "_bir_model_dene", _dene)
    s = kq.qwen_siniflandir("<html>x</html>")
    assert s["etiket_bos"] is False
    assert s["nace_kodu"] == "62.01"
    assert s["model"] == kq.MODEL_ZINCIRI[1]


def test_json_but_model_bozuk_olursa_siradaki(monkeypatch):
    """Cevap 200 ama JSON degilse o model atlanir."""
    def _dene(html, model):
        if model == kq.MODEL_ZINCIRI[1]:
            return '{"etiket_bos": false, "nace_kodu": "10.11"}', ""
        return "Tabii ki! Iste sonuc...", ""

    monkeypatch.setattr(kq, "_bir_model_dene", _dene)
    s = kq.qwen_siniflandir("<html>x</html>")
    assert s["nace_kodu"] == "10.11"


def test_etiket_bos_donerse_alanlar_bos():
    """LLM 'bilmiyorum' dediyse etiket BOS kalir (D-245)."""
    s = kq.qwen_siniflandir("<html>x</html>", "x/y")
    assert s["etiket_bos"] is True
    assert s.get("nace_kodu") is None


def test_llm_bilmiyorum_derse_bos(monkeypatch):
    monkeypatch.setattr(kq, "_bir_model_dene", lambda h, m: (
        '{"etiket_bos": true, "unvan": "X Sirketi"}', ""))
    s = kq.qwen_siniflandir("<html>x</html>")
    assert s["etiket_bos"] is True
    assert s["unvan"] == "X Sirketi"
    assert s.get("nace_kodu") is None


def test_metin_kirpilir():
    """LLM'e uzun ham HTML gonderilmez (maliyet + KVKK)."""
    html = "<html><script>var x=1</script><body>" + ("A" * 9000) + "</body></html>"
    m = kq.metni_kirp(html)
    assert len(m) <= kq.METIN_TAVAN
    assert "var x=1" not in m


def test_evren_anahtari_bulunur(monkeypatch, tmp_path):
    """`.env` icindeki `X-API-Key:evren_llm_...` satirindan anahtar okunur."""
    monkeypatch.setattr(kq, "ROOT", tmp_path)
    (tmp_path / ".env").write_text(
        "X-API-Key:evren_llm_GIZLI_123\nOTHER=1\n", encoding="utf-8")
    monkeypatch.delenv("EVREN_API_KEY", raising=False)
    assert kq._evren_anahtari() == "evren_llm_GIZLI_123"


def test_evren_env_dogrudan_ustun(monkeypatch):
    """Ortam degiskeni `.env` satirini gecersiz kilar."""
    monkeypatch.setenv("EVREN_API_KEY", "evren_llm_ENV")
    assert kq._evren_anahtari() == "evren_llm_ENV"


def test_evren_anahtari_yoksa_hata_doner(monkeypatch, tmp_path):
    monkeypatch.setattr(kq, "ROOT", tmp_path)
    (tmp_path / ".env").write_text("OTHER=1\n", encoding="utf-8")
    monkeypatch.delenv("EVREN_API_KEY", raising=False)
    assert kq._evren_anahtari() == ""
    # fixture stub'ladigi icin GERCEK fonksiyonu geri koyuyoruz
    monkeypatch.setattr(kq, "_evren_bir_model_dene", GERCEK_EVREN_DENE)
    assert kq._evren_bir_model_dene("<html>x</html>", "auto") == \
        ("", "EVREN_ANAHTAR_YOK")


def test_evren_once_deniyor(monkeypatch):
    """Saglayici sirasi: EVREN once, 9Router yedek."""
    cagri = []
    monkeypatch.setattr(kq, "_evren_anahtari", lambda: "evren_llm_X")
    monkeypatch.setattr(kq, "_evren_bir_model_dene",
                        lambda h, m: (cagri.append(("evren", m))
                                      or ('{"etiket_bos": false, '
                                          '"nace_kodu": "62.01"}', "")))
    monkeypatch.setattr(kq, "_bir_model_dene",
                        lambda h, m: cagri.append(("9router", m)) or ("", "x"))
    s = kq.qwen_siniflandir("<html>x</html>")
    assert cagri[0][0] == "evren"
    assert s["model"].startswith("evren/")
    assert s["nace_kodu"] == "62.01"


def test_evren_dusunca_9routera_gecer(monkeypatch):
    """EVREN cokse 9Router devreye girer; sistem durmaz."""
    cagri = []
    monkeypatch.setattr(kq, "_evren_anahtari", lambda: "evren_llm_X")
    monkeypatch.setattr(kq, "_evren_bir_model_dene",
                        lambda h, m: (cagri.append(("evren", m))
                                      or ("", "HTTPError: 503")))
    monkeypatch.setattr(kq, "_bir_model_dene",
                        lambda h, m: ('{"etiket_bos": false, '
                                      '"nace_kodu": "10.11"}', ""))
    s = kq.qwen_siniflandir("<html>x</html>")
    assert cagri[0][0] == "evren"
    assert s["nace_kodu"] == "10.11"
    assert not s["model"].startswith("evren/")


def test_etiketle_sema_her_yolda_ayni():
    """D-245: basarili ve bos yollar ayni anahtarlari dondurur."""
    dolu = kq._etiketle({"etiket_bos": False, "nace_kodu": "62.01"}, "m")
    bos = kq._etiketle({"etiket_bos": True, "unvan": "X"}, "m")
    assert set(dolu) == set(bos)


def test_anahtar_ciktida_yazilmaz():
    kaynak = (KOK / "scripts" / "kazima_qwen_classify.py").read_text(encoding="utf-8")
    assert 'print(anahtar' not in kaynak
    assert "Authorization" in kaynak  # baslik gonderilir, deger yazilmaz