# -*- coding: utf-8 -*-
"""scripts/admin_sifre_sifirla.py — hash uyumu, .env upsert, DB yolu (DB'siz)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _modul():
    spec = importlib.util.spec_from_file_location("admin_sifre_sifirla", ROOT / "scripts" / "admin_sifre_sifirla.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)  # type: ignore[union-attr]
    return m


def test_hash_web_app_formatiyla_uyumlu():
    m = _modul()
    h = m.hash_password("GizliSifre123")
    parcalar = h.split("$")
    assert parcalar[0] == "pbkdf2" and parcalar[1] == "120000"
    assert len(bytes.fromhex(parcalar[2])) == 16
    assert m.verify_password("GizliSifre123", h)
    assert not m.verify_password("yanlis", h)


def test_web_app_verify_ile_dogrulanir():
    """Gerçek doğrulayıcı: web_app._verify_password aynı hash'i kabul etmeli."""
    m = _modul()
    from web_app import _verify_password

    assert _verify_password("Deneme-1234", m.hash_password("Deneme-1234"))


def test_env_upsert_gunceller_ve_ekler(tmp_path):
    m = _modul()
    env = tmp_path / ".env"
    env.write_text("DASH_API_URL=http://x\nADMIN_EMAIL=eski@x\n# yorum çğü\n", encoding="utf-8")
    m.env_upsert(env, {"ADMIN_EMAIL": "yeni@x", "ADMIN_PASSWORD": "p"})
    icerik = env.read_bytes()
    assert not icerik.startswith(b"\xef\xbb\xbf")
    metin = icerik.decode("utf-8")
    assert "DASH_API_URL=http://x" in metin
    assert "ADMIN_EMAIL=yeni@x" in metin and "eski@x" not in metin
    assert "ADMIN_PASSWORD=p" in metin and "# yorum çğü" in metin


def test_env_upsert_tekrarlari_siler(tmp_path):
    """D-24: `.env` içinde ADMIN_* 3x tekrar → upsert sonrası tek satır (dotenv son değeri alır, bug kaynağı)."""
    m = _modul()
    env = tmp_path / ".env"
    env.write_text(
        "A=1\nADMIN_EMAIL=a@x\nADMIN_PASSWORD=p1\nB=2\n"
        "ADMIN_EMAIL=b@x\nADMIN_PASSWORD=p2\nADMIN_EMAIL=c@x\nADMIN_PASSWORD=p3\n",
        encoding="utf-8",
    )
    m.env_upsert(env, {"ADMIN_EMAIL": "son@x", "ADMIN_PASSWORD": "pz"})
    satirlar = env.read_text(encoding="utf-8").splitlines()
    assert satirlar.count("ADMIN_EMAIL=son@x") == 1
    assert satirlar.count("ADMIN_PASSWORD=pz") == 1
    assert sum(s.startswith("ADMIN_EMAIL=") for s in satirlar) == 1
    assert sum(s.startswith("ADMIN_PASSWORD=") for s in satirlar) == 1
    assert satirlar[:2] == ["A=1", "ADMIN_EMAIL=son@x"] and "B=2" in satirlar


def test_kisa_sifre_reddedilir(capsys):
    m = _modul()
    assert m.main(["--email", "a@b", "--sifre", "kisa"]) == 2


def test_admin_bulunamazsa_hata(monkeypatch):
    m = _modul()
    monkeypatch.setattr(m, "db_sifre_guncelle", lambda e, h: 0)
    assert m.main(["--email", "yok@x", "--sifre", "UzunSifre123"]) == 1


def test_basari_env_yazar(monkeypatch, tmp_path):
    m = _modul()
    monkeypatch.setattr(m, "db_sifre_guncelle", lambda e, h: 1)
    monkeypatch.setattr(m, "ROOT", tmp_path)
    assert m.main(["--email", "a@x", "--sifre", "UzunSifre123", "--env-yaz"]) == 0
    assert "ADMIN_PASSWORD=UzunSifre123" in (tmp_path / ".env").read_text(encoding="utf-8")
