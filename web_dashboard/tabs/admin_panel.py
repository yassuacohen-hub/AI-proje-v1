"""Admin Panel - Karar Defteri sekmesi.

Decision Log kayitlarini Streamlit dataframe olarak gosterir.
"""
from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from scripts.decision_log import read_decisions


def render_decision_tab(decisions: list[dict[str, Any]] | None = None) -> None:
    """Admin panelinde karar defteri kayitlarini gosterir.

    Args:
        decisions: Karar listesi. None ise decision_log.jsonl dosyasindan okur.
    """
    if decisions is None:
        decisions = read_decisions()

    if not decisions:
        st.info("Henüz karar kaydı yok")
        return

    # Son 50 kaydi goster
    recent = decisions[-50:]

    rows = []
    for d in recent:
        tags = d.get("tags", [])
        if not isinstance(tags, list):
            tags = [str(t) for t in tags]
        rows.append({
            "Tarih": d.get("ts", ""),
            "Baslik": d.get("title", ""),
            "Karar": d.get("decision", ""),
            "Karar Veren": d.get("decider", ""),
            "Aciklama": d.get("reason", ""),
            "Etiketler": ", ".join(str(t) for t in tags),
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption("Toplam " + str(len(decisions)) + " karar kaydi gosterniliyor (son 50).")
