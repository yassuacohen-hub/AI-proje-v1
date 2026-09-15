# -*- coding: utf-8 -*-
"""Destek Merkezi admin sekmesi (PO-BACK-06).

Streamlit admin paneli: ticket listesi + yeni ticket + durum degistir.
"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from company_master.ui import PageHeader, Section, SectionNav
from company_master.destek import (
    ticket_olustur,
    ticketlar_listele,
    durum_gecis_depo,
)

#: ADMIN-UI-10 — Bolumler tek yerde tanimlanir (anchor tutarliligi).
BOLUMLER: tuple[Section, ...] = (
    Section("Ticket Listesi", "Mevcut ticketleri listele.",
            ikon="📀", kimlik="destek-listesi"),
    Section("Yeni Ticket", "Yeni ticket olustur.",
            ikon="➕", kimlik="destek-yeni"),
    Section("Durum Degistir", "Ticket durumunu guncelle.",
            ikon="🔄", kimlik="destek-durum"),
)


def _bolum(kimlik: str) -> Section:
    """Kimlige gore bolum tanimini getirir (anchor tutarliligi icin)."""
    for bolum in BOLUMLER:
        if bolum.kimlik == kimlik:
            return bolum
    raise KeyError(f"Tanimiz bolum kimligi: {kimlik}")


def _render_baslik() -> None:
    """ADMIN-UI-10: Playground kalibi — ust etiket -> H1 -> giris -> nav."""
    PageHeader("Destek Merkezi",
               "Ticket listesi, olusturma ve durum degistirme.",
               ust_etiket="Is Operasyonlari", ikon="🎫").render()
    SectionNav(BOLUMLER, yatay=True).render()


def render_destek_tab() -> None:
    """Destek merkezi ekranini cizer."""
    _render_baslik()

    _bolum("destek-listesi").render()
    _listele()

    _bolum("destek-yeni").render()
    _yeni()

    _bolum("destek-durum").render()
    _durum()


def _listele() -> None:
    tickets = ticketlar_listele()
    if not tickets:
        st.info("Henuz ticket yok.")
        return
    for t in tickets:
        st.markdown(
            f"**{t.id}** — {t.baslik} | {t.durum} | {t.olusturma}"
        )


def _yeni() -> None:
    with st.form("yeni_ticket"):
        baslik = st.text_input("Baslik")
        aciklama = st.text_area("Aciklama")
        submitted = st.form_submit_button("Olustur")
        if submitted and baslik:
            t = ticket_olustur("kilo", baslik, aciklama)
            st.success(f"Ticket olusturuldu: {t.id}")


def _durum() -> None:
    ticket_id = st.text_input("Ticket ID")
    yeni_durum = st.selectbox(
        "Yeni Durum",
        ["inceleniyor", "cozuldu", "kapali"],
    )
    if st.button("Durumu Degistir"):
        try:
            updated = durum_gecis_depo(ticket_id, yeni_durum)
            if updated:
                st.success(f"Durum guncellendi: {updated.durum}")
            else:
                st.error("Ticket bulunamadi.")
        except ValueError as e:
            st.error(str(e))
