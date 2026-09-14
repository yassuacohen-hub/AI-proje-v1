"""Admin Panel - Karar Defteri ve Kullanici Ayarlari sekmeleri.

- `render_decision_tab`: Decision Log kayitlarini Streamlit dataframe olarak gosterir.
- `render_ayarlar_tab` (P7-46): Kullanici ayarlar paneli; sema odakli form uretimi,
  dogrulama ve kalici kayit `company_master.settings` uzerinden yapilir.

ADMIN-UI-10:
  Sayfa iskeleti Playground dokumantasyon mantigina tasindi:
  ``PageHeader`` -> ``SectionNav`` -> ``Section``. Renk, ikon ve tipografi
  secimleri **degismedi**; yalnizca hiyerarsi disipline edildi. Bu ekranin tek
  birincil butonu form icindeki "Kaydet" dugmesidir; bu yuzden baslik seridinde
  ikinci bir birincil buton yoktur.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from scripts.decision_log import read_decisions

_KOK = Path(__file__).resolve().parents[2]
if str(_KOK / "src") not in sys.path:
    sys.path.insert(0, str(_KOK / "src"))

from company_master.settings import (  # noqa: E402
    AyarHatasi,
    AyarTanimi,
    ayarlari_getir,
    ayarlari_sifirla,
    ayarlari_yaz,
    gruplar,
)
from company_master.ui import PageHeader, Section, SectionNav  # noqa: E402

#: ADMIN-UI-10 — Bolumler tek yerde tanimlanir (anchor tutarliligi).
BOLUMLER: tuple[Section, ...] = (
    Section("Ayar Grupları", "Gruplara ayrılmış tercihler; kaydetme tek işlemde doğrulanır.",
            ikon="🎛️", kimlik="ayar-gruplari"),
    Section("Sıfırlama", "Tüm tercihleri şema varsayılanlarına döndürür.",
            ikon="↩️", kimlik="ayar-sifirlama"),
)

GIRIS_METNI = (
    "Panel davranışını kendi kullanıcı kimliğinize göre ayarlayın. Değişiklikler "
    "sunucuda saklanır; tarayıcı değiştirseniz de korunur. Kaydetme hepsi-ya-hiç "
    "çalışır: bir alan geçersizse hiçbiri yazılmaz."
)


def _bolum(kimlik: str) -> Section:
    """Kimlige gore bolum tanimini getirir (anchor tutarliligi icin)."""
    for bolum in BOLUMLER:
        if bolum.kimlik == kimlik:
            return bolum
    raise KeyError(f"Tanımsız bölüm kimliği: {kimlik}")


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


# ---------------------------------------------------------------------------
# P7-46: Kullanici Ayarlar Paneli
# ---------------------------------------------------------------------------

#: Oturum acmamis kullanicilar icin ayarlarin yazildigi kimlik.
MISAFIR_KIMLIK = "misafir"


def aktif_kullanici(oturum: dict[str, Any] | None = None) -> str:
    """Oturumdan kullanici kimligini cozer; yoksa misafir kimligi doner.

    Streamlit `session_state` disinda da calisabilmesi icin sozluk alir
    (test edilebilirlik).
    """
    if oturum is None:
        try:
            oturum = dict(st.session_state)
        except Exception:
            oturum = {}
    for anahtar in ("admin_email", "user_email", "kullanici_id"):
        deger = oturum.get(anahtar)
        if isinstance(deger, str) and deger.strip():
            return deger.strip()
    return MISAFIR_KIMLIK


def _form_degeri(tanim: AyarTanimi, mevcut: Any) -> Any:
    """Tek bir ayar icin uygun Streamlit girdisini cizer ve degerini doner."""
    anahtar = f"ayar_{tanim.anahtar}"

    if tanim.tip == "bool":
        return st.checkbox(
            tanim.etiket,
            value=bool(mevcut),
            key=anahtar,
            help=tanim.aciklama or None,
        )

    if tanim.tip == "sayi":
        return int(
            st.number_input(
                tanim.etiket,
                min_value=tanim.alt_sinir,
                max_value=tanim.ust_sinir,
                value=int(mevcut),
                step=10,
                key=anahtar,
                help=tanim.aciklama or None,
            )
        )

    if tanim.tip == "secim":
        secenekler = list(tanim.secenekler)
        indeks = secenekler.index(mevcut) if mevcut in secenekler else 0
        return st.selectbox(
            tanim.etiket,
            secenekler,
            index=indeks,
            key=anahtar,
            help=tanim.aciklama or None,
        )

    return st.text_input(
        tanim.etiket,
        value=str(mevcut),
        key=anahtar,
        help=tanim.aciklama or None,
    )


def render_ayarlar_tab(kullanici_id: str | None = None) -> None:
    """Kullanici ayarlar panelini cizer (P7-46).

    Ayarlar `company_master.settings` semasindan uretilir; grup basina bir
    sekme acilir. Kaydet tek islemde dogrular (hepsi-ya-hic).
    """
    if kullanici_id is None:
        kullanici_id = aktif_kullanici()

    PageHeader("Kullanıcı Ayarları", giris=GIRIS_METNI,
               ust_etiket="Sistem · Ayarlar", ikon="⚙️").render()

    col_rehber, col_kimlik = st.columns([1, 3], vertical_alignment="center")
    with col_rehber:
        rehber = st.toggle("ℹ️ Sekme rehberi", key="ayarlar_rehber",
                           help="Bu ekranın amacını, veri kaynağını ve kısıtlarını gösterir.")
    with col_kimlik:
        st.caption(
            f"Ayarlar bu kullanıcıya özeldir (`{kullanici_id}`) ve tarayıcıdan bağımsız "
            "olarak sunucuda saklanır."
        )

    if rehber:
        st.info(
            "**Amaç:** Panel tercihlerini kullanıcı bazında kalıcı olarak saklamak.\n\n"
            "**Veri kaynağı:** `company_master.settings` şeması; alanlar şemadan "
            "otomatik üretilir.\n\n"
            "**Kısıt:** Kaydetme hepsi-ya-hiç doğrulanır; bir alan geçersizse "
            "hiçbir değer yazılmaz."
        )

    SectionNav(BOLUMLER, yatay=True).render()

    mevcut = ayarlari_getir(kullanici_id)
    grup_haritasi = gruplar()
    grup_adlari = list(grup_haritasi)

    _bolum("ayar-gruplari").render()
    yeni_degerler: dict[str, Any] = {}
    with st.form("kullanici_ayarlari_form"):
        sekmeler = st.tabs(grup_adlari)
        for sekme, grup_adi in zip(sekmeler, grup_adlari):
            with sekme:
                for tanim in grup_haritasi[grup_adi]:
                    yeni_degerler[tanim.anahtar] = _form_degeri(
                        tanim, mevcut.get(tanim.anahtar, tanim.varsayilan)
                    )

        kaydet = st.form_submit_button("💾 Kaydet", type="primary")

    if kaydet:
        try:
            ayarlari_yaz(kullanici_id, yeni_degerler)
        except AyarHatasi as hata:
            st.error(f"Ayar kaydedilemedi: {hata}")
        else:
            st.success("Ayarlar kaydedildi.")

    _bolum("ayar-sifirlama").render()
    if st.button("↩️ Varsayılanlara dön", key="ayar_sifirla"):
        ayarlari_sifirla(kullanici_id)
        st.success("Ayarlar varsayılanlara döndürüldü.")

    st.caption(
        "Not: Tema ayarı 'sistem' seçiliyken panel, işletim sistemi renk tercihini izler."
    )
