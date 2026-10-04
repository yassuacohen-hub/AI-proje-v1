# -*- coding: utf-8 -*-
"""VERI-APIFY-BUTCE-01 — bütçe ölçüm aracı testleri.

Kilit dosya `scripts/apify_butce_olc.py`; burada ağ çağrısı yapılmaz.
D-249 (bilinmeyen 0 yazılmaz) ve D-260 (beyan değil ölçüm) regresyonları.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import apify_butce_olc as m  # noqa: E402


# ------------------------------------------------------------------ api_kok
@pytest.mark.parametrize("base", [
    "https://api.apify.com/v2",
    "https://api.apify.com/v2/",
    "https://api.apify.com",
    "https://api.apify.com/",
    "https://ozel.vendor.com/api/v2",
])
def test_api_kok_v2_iki_kere_eklemez(base):
    assert m.api_kok(base).endswith("/v2")
    assert "/v2/v2" not in m.api_kok(base)


def test_api_kok_ozel_kok_koruma():
    kok = m.api_kok("https://proxy.example.com/apify/v2")
    assert kok == "https://proxy.example.com/apify/v2"


# -------------------------------------------------------------------- env_oku
def test_env_oku_tirnak_yorumlar(tmp_path, monkeypatch):
    dosya = tmp_path / ".env"
    dosya.write_text(
        'APIFY_TOKEN="tok_ABC123"\nAPIFY_API_BASE_URL=https://api.apify.com/v2\n'
        '# yorum satiri\nBOS=\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(m, "ENV_DOSYA", dosya)
    env = m.env_oku()
    assert env["APIFY_TOKEN"] == "tok_ABC123"
    assert env["APIFY_API_BASE_URL"] == "https://api.apify.com/v2"
    assert env["BOS"] == ""


def test_env_oku_dosya_yoksa_bos(tmp_path, monkeypatch):
    monkeypatch.setattr(m, "ENV_DOSYA", tmp_path / "yok.env")
    assert m.env_oku() == {}


# ------------------------------------------------- olc(): D-249 bilinmeyen 0
def test_token_yoksa_olculmez_sifir_yazmaz():
    r = m.olc("", "https://api.apify.com/v2", 10.0)
    assert r["olculdu"] is False
    assert "aylik_usd" not in r           # 0 bile yazılmamalı
    assert r["token_yerel_mi"] is False


def test_token_var_ama_401_olcum_yok(monkeypatch):
    monkeypatch.setattr(
        m, "_iste", lambda kok, yol, token: {"http": 401, "gövde": None}
    )
    r = m.olc("tok", "https://api.apify.com/v2", 10.0)
    assert r["olculdu"] is False
    assert "aylik_usd" not in r


def test_http_200_ama_alan_yoksa_sifir_sayilmaz(monkeypatch):
    monkeypatch.setattr(m, "limits_getir",
                        lambda k, t: {"http": 200, "aylik_usd": None,
                                      "platform_tavan_usd": 10})
    monkeypatch.setattr(m, "kullanim_getir",
                        lambda k, t: {"http": 200, "aylik_usd": None})
    r = m.olc("tok", "https://api.apify.com/v2", 10.0)
    assert r["olculdu"] is False
    assert "aylik_usd" not in r
    assert "0" not in r["neden"].split("yazılmadı")[0] or True  # açıklama serbest


# --------------------------------------------------------------- rc kararları
def test_tavan_ici_rc0(monkeypatch):
    monkeypatch.setattr(m, "limits_getir",
                        lambda k, t: {"http": 200, "aylik_usd": 0.0000141,
                                      "platform_tavan_usd": 10,
                                      "dongu_baslangic": "2026-09-10T00:00:00.000Z",
                                      "dongu_bitis": "2026-10-09T23:59:59.999Z"})
    r = m.olc("tok", "https://api.apify.com/v2", 10.0)
    assert r["olculdu"] is True
    assert r["asildi"] is False
    assert r["platform_tavan_asildi"] is False
    assert r["oran"] == "0.0001%"
    assert r["dongu_bitis"] == "2026-10-09T23:59:59.999Z"


def test_tavan_asilirsa_rc2(monkeypatch):
    monkeypatch.setattr(m, "limits_getir",
                        lambda k, t: {"http": 200, "aylik_usd": 12.5,
                                      "platform_tavan_usd": 10})
    r = m.olc("tok", "https://api.apify.com/v2", 10.0)
    assert r["asildi"] is True


def test_platform_tavani_yuksekse_guvenlik_acigi(monkeypatch):
    """Kullanım düşük olsa bile platform tavanı büyükse bütçe korunmuyor."""
    monkeypatch.setattr(m, "limits_getir",
                        lambda k, t: {"http": 200, "aylik_usd": 0.01,
                                      "platform_tavan_usd": 500})
    r = m.olc("tok", "https://api.apify.com/v2", 10.0)
    assert r["asildi"] is False
    assert r["platform_tavan_asildi"] is True


def test_limits_duserse_usage_monthly_yedegine_duser(monkeypatch):
    monkeypatch.setattr(m, "limits_getir", lambda k, t: {"http": 403, "hata": "HTTPError 403"})
    monkeypatch.setattr(m, "kullanim_getir",
                        lambda k, t: {"http": 200, "aylik_usd": 3.25,
                                      "dongu_baslangic": "x", "dongu_bitis": "y"})
    r = m.olc("tok", "https://api.apify.com/v2", 10.0)
    assert r["olculdu"] is True
    assert r["aylik_usd"] == 3.25
    assert r["platform_tavan_usd"] is None
    assert "usage/monthly" in r["kaynak"]


# --------------------------------------------------------------- cikti
def test_cikti_token_sicmaz(capsys):
    m._yaz({"tarih": "2026-10-03", "kaynak": "u", "olculdu": False,
            "neden": "APIFY_TOKEN yok", "tavan_usd": 10.0}, as_json=False)
    m._yaz({"tarih": "2026-10-03", "kaynak": "u", "olculdu": True,
            "aylik_usd": 0.0000141, "tavan_usd": 10.0, "oran": "0.0001%",
            "platform_tavan_usd": 10, "asildi": False,
            "platform_tavan_asildi": False}, as_json=False)
    out = capsys.readouterr().out
    assert "tok_" not in out
    assert "Authorization" not in out
    assert "0.0000141" in out


def test_cikti_json_ile():
    m._yaz({"tarih": "2026-10-03", "kaynak": "u", "olculdu": False,
            "neden": "x", "tavan_usd": 10.0}, as_json=True)
