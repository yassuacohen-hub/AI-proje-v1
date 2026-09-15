# -*- coding: utf-8 -*-
"""Anthropic PR review script'inin saf (ağsız) yardımcı fonksiyon testleri."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_YOL = Path(__file__).resolve().parents[1] / "scripts" / "anthropic_pr_review.py"
_spec = importlib.util.spec_from_file_location("anthropic_pr_review", _YOL)
m = importlib.util.module_from_spec(_spec)
sys.modules["anthropic_pr_review"] = m
_spec.loader.exec_module(m)  # type: ignore[union-attr]


def test_dosya_utf8_bom_yok():
    ham = _YOL.read_bytes()
    assert not ham.startswith(b"\xef\xbb\xbf")
    assert b"\x00" not in ham


@pytest.mark.parametrize(
    "girdi,beklenen_yok",
    [
        ("API_KEY=abc123xyz", "abc123xyz"),
        ("password: 's3cret!'", "s3cret!"),
        ("x = 'sk-ant-abcdefghijklmnop'", "sk-ant-abcdefghijklmnop"),
        ("ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ", "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
    ],
)
def test_redact_secrets_maskeler(girdi, beklenen_yok):
    cikti = m.redact_secrets(girdi)
    assert beklenen_yok not in cikti
    assert "[REDACTED]" in cikti


def test_redact_secrets_normal_kodu_bozmaz():
    kod = "def token_say(x):\n    return x + 1\n"
    assert m.redact_secrets(kod) == kod


def _blok(yol: str) -> str:
    return f"diff --git a/{yol} b/{yol}\n--- a/{yol}\n+++ b/{yol}\n@@ -1 +1 @@\n-a\n+b\n"


def test_diff_filtrele_gurultuyu_atar():
    diff = _blok("src/app.py") + _blok("data/x.jsonl") + _blok("package-lock.json") + _blok("tests/t.py")
    cikti = m.diff_filtrele(diff)
    assert "src/app.py" in cikti and "tests/t.py" in cikti
    assert "data/x.jsonl" not in cikti and "package-lock.json" not in cikti


def test_kirp_sinir():
    metin, kirpildi = m.kirp("a" * 10, limit=5)
    assert kirpildi and metin.startswith("aaaaa") and "kırpıldı" in metin
    assert m.kirp("abc", limit=5) == ("abc", False)


def test_yorum_guncelle_marker_varsa_patch(monkeypatch):
    monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
    monkeypatch.setenv("GITHUB_TOKEN", "t")
    cagrilar: list[tuple[str, str]] = []

    def sahte(path, method="GET", data=None, raw=False):
        cagrilar.append((method, path))
        if method == "GET":
            return [{"id": 7, "body": f"{m.MARKER}\neski"}]
        return None

    monkeypatch.setattr(m, "_github", sahte)
    m.yorum_yaz_veya_guncelle("12", "yeni")
    assert cagrilar[-1] == ("PATCH", "/repos/o/r/issues/comments/7")


def test_yorum_yoksa_post(monkeypatch):
    monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
    monkeypatch.setenv("GITHUB_TOKEN", "t")
    cagrilar: list[str] = []
    monkeypatch.setattr(m, "_github", lambda path, method="GET", data=None, raw=False: (cagrilar.append(method), [])[1] if method == "GET" else cagrilar.append(method))
    m.yorum_yaz_veya_guncelle("12", "yeni")
    assert cagrilar == ["GET", "POST"]


def test_main_mod_secimi(monkeypatch):
    cagri: list[str] = []
    monkeypatch.setattr(m, "mod_pr", lambda: cagri.append("pr"))
    monkeypatch.setattr(m, "mod_ci_failure", lambda: cagri.append("ci"))
    assert m.main(["--mode", "ci-failure"]) == 0
    assert m.main([]) == 0
    assert cagri == ["ci", "pr"]
