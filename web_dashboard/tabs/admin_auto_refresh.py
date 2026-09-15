# -*- coding: utf-8 -*-
"""P7-39 / UI-REFRESH-01: Dashboard otomatik veri yenileme (kompakt blok).

- Ayarlanabilir aralık (15/30/60/300/600 sn)
- Aç/kapat: normal boyutlu ikincil buton (primary + stretch YOK — responsive)
- Durum tek satır caption (büyük st.metric YOK)
- Periyodik yenileme `st.fragment(run_every=...)` ile (Streamlit >= 1.37);
  `st.auto_refresh` Streamlit 1.62'de mevcut değildir, kullanılmaz.
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

REFRESH_INTERVALS = [15, 30, 60, 300, 600]
ETIKET_AC = "▶️ Otomatik yenilemeyi aç"
ETIKET_KAPAT = "⏹ Otomatik yenilemeyi kapat"


def _aralik_metni(saniye: int) -> str:
    """15 -> '15 sn', 300 -> '5 dk'."""
    return f"{saniye // 60} dk" if saniye >= 60 else f"{saniye} sn"


def _periyodik_yenileme(interval: int) -> None:
    """Aralık dolunca cache'i temizleyip sayfayı yeniler (fragment tabanlı).

    `st.fragment` yoksa (eski sürüm) sessizce uyarı verir; çökmez.
    """
    fragment = getattr(st, "fragment", None)
    if fragment is None:
        st.warning("Bu Streamlit sürümünde periyodik yenileme yok; 🔄 Yenile butonunu kullan.")
        return

    @fragment(run_every=f"{interval}s")
    def _tik() -> None:
        gecen = (datetime.now() - st.session_state.last_auto_refresh).total_seconds()
        if gecen >= interval:
            st.session_state.last_auto_refresh = datetime.now()
            st.cache_data.clear()
            st.rerun()

    _tik()


def render_auto_refresh() -> None:
    """Otomatik yenileme kontrolleri — tek satır, kompakt."""
    st.markdown("#### 🔄 Otomatik yenileme")
    st.caption("Açıkken seçilen aralıkta cache temizlenir ve sayfa yenilenir; kapalıyken 🔄 Yenile ile elle tazelersin.")

    st.session_state.setdefault("auto_refresh_interval", 30)
    st.session_state.setdefault("auto_refresh_enabled", False)
    st.session_state.setdefault("last_auto_refresh", datetime.now())

    col_int, col_btn, col_durum = st.columns([2, 2, 3])

    with col_int:
        interval = st.selectbox(
            "Aralık",
            REFRESH_INTERVALS,
            index=REFRESH_INTERVALS.index(st.session_state.auto_refresh_interval),
            format_func=_aralik_metni,
            key="refresh_interval_select",
        )
        st.session_state.auto_refresh_interval = interval

    with col_btn:
        st.markdown("<div style='height:1.7rem'></div>", unsafe_allow_html=True)
        acik = bool(st.session_state.auto_refresh_enabled)
        etiket = ETIKET_KAPAT if acik else ETIKET_AC
        if st.button(etiket, key="auto_refresh_toggle", type="secondary"):
            st.session_state.auto_refresh_enabled = not acik
            st.session_state.last_auto_refresh = datetime.now()
            st.rerun()

    with col_durum:
        st.markdown("<div style='height:1.9rem'></div>", unsafe_allow_html=True)
        son = st.session_state.last_auto_refresh.strftime("%H:%M:%S")
        if st.session_state.auto_refresh_enabled:
            gecen = (datetime.now() - st.session_state.last_auto_refresh).total_seconds()
            kalan = max(0, int(st.session_state.auto_refresh_interval - gecen))
            st.caption(f"🟢 Açık · her {_aralik_metni(interval)} · son {son} · kalan {kalan} sn")
        else:
            st.caption(f"⚪ Kapalı · son yenileme {son}")

    if st.session_state.auto_refresh_enabled:
        _periyodik_yenileme(int(st.session_state.auto_refresh_interval))

    # --- Veri tazeliği + elle yenile (tek satır) ---
    from company_master.tazelik import tazelik_etiketi as _tazelik_etiketi

    simdi = datetime.now()
    tazelik = _tazelik_etiketi(st.session_state.last_auto_refresh, simdi)
    renk_map = {"green": "🟢", "yellow": "🟡", "red": "🔴", "gray": "⚪"}
    icon = renk_map.get(tazelik.get("renk", "gray"), "⚪")
    col_taz, col_yenile = st.columns([5, 2])
    with col_taz:
        st.caption(f"{icon} Veri tazeliği: {tazelik.get('etiketi', 'bilinmiyor')}")
    with col_yenile:
        if st.button("🔄 Yenile", key="tazelik-yenile"):
            st.session_state.last_auto_refresh = datetime.now()
            st.cache_data.clear()
            st.session_state["tazelik_yenildi"] = True
            st.rerun()
