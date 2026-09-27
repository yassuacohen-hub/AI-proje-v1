# -*- coding: utf-8 -*-
"""VERI-03 mandali: ProxyRotator davranis testi.

Pano VERI-03 "src/scrapers/proxy_rotation.py yaz" diyordu; olcum kodun
src/company_master/utils/proxy_rotator.py'de HAZIR oldugunu, eksigin TEST
oldugunu gosterdi. Bu dosya o eksigi kapatir.
"""
from __future__ import annotations

import pytest

from src.company_master.utils.proxy_rotator import (
    DEFAULT_USER_AGENTS,
    ProxyRotator,
)


def test_proxysiz_rotator_none_dondurur():
    """Proxy listesi bos ise get_proxy None dondurur, patlamaz."""
    r = ProxyRotator(proxies=[])
    assert r.current_proxy is None
    assert r.get_proxy() is None
    assert r.status["proxy_count"] == 0


def test_get_proxy_requests_formatinda_ve_sirayla_doner():
    r = ProxyRotator(proxies=["http://a:1", "http://b:2"])
    assert r.get_proxy() == {"http": "http://a:1", "https": "http://a:1"}
    assert r.get_proxy() == {"http": "http://b:2", "https": "http://b:2"}
    # Tur: liste basa sarar, indeks buyumesi tasma yapmaz
    assert r.get_proxy() == {"http": "http://a:1", "https": "http://a:1"}


def test_user_agent_varsayilan_listeden_gelir_ve_dolasir():
    r = ProxyRotator(proxies=[])
    uas = {r.get_user_agent() for _ in range(len(DEFAULT_USER_AGENTS) * 2)}
    assert uas <= set(DEFAULT_USER_AGENTS)
    assert len(uas) == len(DEFAULT_USER_AGENTS), "tum UA'lar dolasilmali"


def test_add_remove_proxy_idempotent():
    r = ProxyRotator(proxies=[])
    r.add_proxy("http://x:1")
    r.add_proxy("http://x:1")  # ikinci kez eklenmemeli
    assert r.proxies == ["http://x:1"]
    r.remove_proxy("http://x:1")
    r.remove_proxy("http://x:1")  # yok olani silmek patlamamali
    assert r.proxies == []


def test_son_proxy_silinince_current_proxy_none():
    """Regresyon: silme sonrasi eski indeks tasma/IndexError vermemeli."""
    r = ProxyRotator(proxies=["http://a:1"])
    r.get_proxy()  # indeks 1'e cikti
    r.remove_proxy("http://a:1")
    assert r.current_proxy is None


def test_rotate_bos_listede_patlamaz():
    r = ProxyRotator(proxies=[])
    r.rotate()  # randint(0, -1) hatasi olmamali
    assert r.current_proxy is None


def test_dosyadan_yukleme_yorum_ve_bos_satiri_atlar(tmp_path):
    f = tmp_path / "proxies.txt"
    f.write_text(
        "# yorum\nhttp://a:1\n\n  http://b:2  \n#son\n",
        encoding="utf-8",
    )
    r = ProxyRotator(proxies=str(f))
    assert r.proxies == ["http://a:1", "http://b:2"]


def test_olmayan_dosya_bos_liste(tmp_path):
    r = ProxyRotator(proxies=str(tmp_path / "yok.txt"))
    assert r.proxies == []


def test_auto_detect_ortam_degiskeninden_okur(monkeypatch):
    # DIKKAT: Windows'ta os.environ anahtarlari BUYUK harfe normalize edilir;
    # bu yuzden delenv("http_proxy") HTTP_PROXY'yi de siler. Temizlik setenv'den
    # ONCE yapilmali, sonra degil.
    for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("HTTP_PROXY", "http://env:9")
    r = ProxyRotator()  # proxies=None -> auto detect
    assert r.proxies == ["http://env:9"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
