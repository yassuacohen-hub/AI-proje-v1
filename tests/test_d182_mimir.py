# -*- coding: utf-8 -*-
"""D-182 — MIMIR iki seviye + abrakadabra anahtar rotasyonu doğrulaması.

Çalıştırma: python tests/test_d182_mimir.py   (pytest de çalışır)

Karar: [[D-182]] — Orkestratör Asistanı İki Seviye (2026-09-21)
Implementasyon:
- [[src/company_master/ai_chat.py]] (GORUNEN_AD, chat mekanizması)
- [[src/company_master/orchestrator/trigger.py]] (AJAN_TAKMA_ADLAR, AJANLAR)
- [[scripts/gorev_at.py]] (cmd_abrakadabra komutu, key rotasyonu)
"""
from __future__ import annotations

import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

from scripts import gorev_at  # noqa: E402
from src.company_master.orchestrator import trigger  # noqa: E402


def test_mimir_kanonik_ajan() -> None:
    """MIMIR beşinci kanonik ajandır; takma adları mimir'e normalize olur."""
    assert "mimir" in trigger.AJANLAR
    for takma in ("mimir", "odin_ai", "odin-ai", "abrakadabra"):
        assert trigger.ajan_normalize(takma) == "mimir", takma


def test_varsayilan_orkestrator_canonical() -> None:
    """D-71: varsayılan orkestratör araç adı değil kanonik ad olmalı."""
    assert gorev_at._VARSAYILAN_ORKESTRATOR == "ihsan"


def test_anahtar_dondur_env_gunceller(tmp_path: Path, monkeypatch) -> None:
    """Rotasyon .env içindeki ABRAKADABRA_KEY satırını yerinde değiştirir, diğerlerine dokunmaz."""
    env = tmp_path / ".env"
    env.write_text("ONCE=1\nABRAKADABRA_KEY=eski\nSONRA=2\n", encoding="utf-8")
    monkeypatch.setattr(gorev_at, "KOK", tmp_path)

    gorev_at._anahtar_dondur("yeni_anahtar")

    satirlar = env.read_text(encoding="utf-8").splitlines()
    assert satirlar == ["ONCE=1", "ABRAKADABRA_KEY=yeni_anahtar", "SONRA=2"]
    assert not (tmp_path / ".env.tmp").exists(), "geçici dosya kalmamalı"


def test_anahtar_dondur_env_yoksa_key_dosyasi(tmp_path: Path, monkeypatch) -> None:
    """.env yoksa anahtar key dosyasına yazılır."""
    key_dosya = tmp_path / "data" / "orchestrator" / "abrakadabra.key"
    monkeypatch.setattr(gorev_at, "KOK", tmp_path)
    monkeypatch.setattr(gorev_at, "_ANAHTAR_DOSYA", key_dosya)

    gorev_at._anahtar_dondur("dosya_anahtari")

    assert key_dosya.read_text(encoding="utf-8") == "dosya_anahtari"


def _mini_monkeypatch():
    """pytest yokken kullanılan asgari monkeypatch ikamesi."""
    class _MP:
        def __init__(self) -> None:
            self._geri: list = []

        def setattr(self, hedef, ad, deger):
            eski = getattr(hedef, ad)
            self._geri.append((hedef, ad, eski))
            setattr(hedef, ad, deger)

        def undo(self) -> None:
            for hedef, ad, eski in reversed(self._geri):
                setattr(hedef, ad, eski)
            self._geri.clear()

    return _MP()


if __name__ == "__main__":
    import tempfile

    test_mimir_kanonik_ajan()
    test_varsayilan_orkestrator_canonical()
    for fn in (test_anahtar_dondur_env_gunceller, test_anahtar_dondur_env_yoksa_key_dosyasi):
        mp = _mini_monkeypatch()
        with tempfile.TemporaryDirectory() as td:
            try:
                fn(Path(td), mp)
            finally:
                mp.undo()
    print("D-182 dogrulamasi: TUM KONTROLLER GECTI")
