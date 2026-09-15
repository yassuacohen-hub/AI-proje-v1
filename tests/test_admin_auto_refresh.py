# -*- coding: utf-8 -*-
"""UI-REFRESH-01: Otomatik yenileme bloğu kompakt/responsive + Streamlit 1.62 uyumu."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from web_dashboard.tabs import admin_auto_refresh as mod

DOSYA = Path(__file__).resolve().parent.parent / "web_dashboard" / "tabs" / "admin_auto_refresh.py"


class _Kolon:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class _Oturum(dict):
    """st.session_state taklidi: hem sözlük hem öznitelik erişimi."""

    def __getattr__(self, ad):
        try:
            return self[ad]
        except KeyError as e:  # pragma: no cover
            raise AttributeError(ad) from e

    def __setattr__(self, ad, deger):
        self[ad] = deger


def _sahte_st(monkeypatch, *, acik: bool, tiklanan: str | None = None, fragment_var: bool = True):
    """render_auto_refresh için streamlit taklidi; çağrıları kaydeder."""
    st = MagicMock()
    st.session_state = _Oturum(
        auto_refresh_interval=30,
        auto_refresh_enabled=acik,
        last_auto_refresh=datetime.now() - timedelta(seconds=5),
    )
    st.columns = lambda spec: [_Kolon() for _ in spec]
    st.selectbox = lambda *a, **k: 30
    st.button = lambda etiket, **k: st.button_calls.append((etiket, k)) or (etiket == tiklanan)
    st.button_calls = []
    st.rerun = MagicMock(side_effect=RuntimeError("rerun"))
    if fragment_var:
        def fragment(run_every=None):
            st.fragment_calls.append(run_every)

            def dekor(fn):
                return fn  # anında çalıştırılabilir bırak
            return dekor
        st.fragment = fragment
    else:
        del st.fragment
    st.fragment_calls = []
    monkeypatch.setattr(mod, "st", st)
    return st


def test_st_auto_refresh_kullanilmiyor():
    """Streamlit 1.62'de st.auto_refresh yok; kaynakta çağrı olmamalı."""
    kaynak = DOSYA.read_text(encoding="utf-8")
    assert "st.auto_refresh(" not in kaynak
    assert not kaynak.startswith("\ufeff"), "UTF-8 BOM olmamalı"


def test_buton_kompakt_primary_ve_stretch_yok(monkeypatch):
    st = _sahte_st(monkeypatch, acik=False)
    mod.render_auto_refresh()
    for etiket, k in st.button_calls:
        assert k.get("type") != "primary", etiket
        assert k.get("width") != "stretch", etiket
        assert k.get("use_container_width") is not True, etiket
    # büyük metric kullanılmıyor
    assert not st.metric.called


def test_etiket_mantigi_dogru(monkeypatch):
    st = _sahte_st(monkeypatch, acik=False)
    mod.render_auto_refresh()
    etiketler = [e for e, _ in st.button_calls]
    assert mod.ETIKET_AC in etiketler and mod.ETIKET_KAPAT not in etiketler

    st = _sahte_st(monkeypatch, acik=True)
    mod.render_auto_refresh()
    etiketler = [e for e, _ in st.button_calls]
    assert mod.ETIKET_KAPAT in etiketler and mod.ETIKET_AC not in etiketler


def test_toggle_durumu_cevirir_ve_rerun(monkeypatch):
    st = _sahte_st(monkeypatch, acik=False, tiklanan=mod.ETIKET_AC)
    with pytest.raises(RuntimeError, match="rerun"):
        mod.render_auto_refresh()
    assert st.session_state.auto_refresh_enabled is True


def test_acikken_fragment_ile_periyodik_yenileme(monkeypatch):
    st = _sahte_st(monkeypatch, acik=True)
    mod.render_auto_refresh()
    assert st.fragment_calls == ["30s"]
    # 5 sn geçti < 30 → rerun tetiklenmedi
    assert not st.rerun.called


def test_kapaliyken_fragment_yok(monkeypatch):
    st = _sahte_st(monkeypatch, acik=False)
    mod.render_auto_refresh()
    assert st.fragment_calls == []


def test_fragment_yoksa_cokmez(monkeypatch):
    st = _sahte_st(monkeypatch, acik=True, fragment_var=False)
    mod.render_auto_refresh()
    assert st.warning.called


def test_aralik_metni():
    assert mod._aralik_metni(15) == "15 sn"
    assert mod._aralik_metni(300) == "5 dk"
