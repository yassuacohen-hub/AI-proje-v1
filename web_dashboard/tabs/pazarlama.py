# -*- coding: utf-8 -*-
"""DASH-UX-04: Pazarlama sekmesi (kampanya + segment).

Kaynak: DASH-UX-03 backend'i (``company_master.pazarlama``).
Veritabani yoksa ``data/demo/*.jsonl`` demo verisine duser ve DEMO rozeti gosterir.

Sentez kalibi:
  K1 - Ortak sekme basligi (ikon + baslik + son guncelleme + yenile + bilgi expander)
  K2 - Bos grafik yok; "Veri gelince ... burada gorunecek" yer tutucusu
  K3 - Her metrigin yaninda tek satir Turkce aciklama + operasyonel soru
  K7 - Demo veri DEMO rozetiyle isaretlenir

ADMIN-UI-10:
  Sayfa iskeleti Playground dokumantasyon mantigina tasindi:
  ``PageHeader`` -> ``SectionNav`` -> ``Section``. Renk, ikon ve tipografi
  secimleri **degismedi**; yalnizca hiyerarsi disipline edildi. Ekranin tek
  birincil butonu "Veriyi Yenile" dugmesidir.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from company_master.ui import PageHeader, Section, SectionNav  # noqa: E402

DEMO_KAMPANYA = ROOT / "data" / "demo" / "kampanya_demo.jsonl"
DEMO_SEGMENT = ROOT / "data" / "demo" / "segment_demo.jsonl"

#: ADMIN-UI-10 — Sayfa ici gezinmede gorunen ust duzey bolumler (H2).
BOLUMLER: tuple[Section, ...] = (
    Section(
        "Kampanya ve Segment Özeti",
        "Kampanya/segment adetleri ve aktiflik durumu.",
        ikon="🧮",
        kimlik="pazarlama-ozeti",
    ),
    Section(
        "Kampanya Performansı",
        "Bütçe, tıklama oranı, dönüşüm ve dönüşüm başı maliyet.",
        ikon="📈",
        kimlik="kampanya-performansi",
    ),
    Section(
        "Detay Listeleri",
        "Kampanyalar, segmentler ve segment–kampanya kapsaması.",
        ikon="📋",
        kimlik="detay-listeleri",
    ),
)

#: Detay sekmelerinin ic basliklari (H3; gezinmede gorunmez).
ALT_BOLUMLER: tuple[Section, ...] = (
    Section(
        "Kampanyalar",
        "Bütçe ve dönüşüm tablosu; altında bütçe dağılımı grafiği.",
        ikon="📣",
        kimlik="alt-kampanyalar",
        seviye=3,
    ),
    Section(
        "Segmentler",
        "Segment kriterleri ve segmentteki firmalar.",
        ikon="👥",
        kimlik="alt-segmentler",
        seviye=3,
    ),
    Section(
        "Segment–Kampanya Kapsaması",
        "Hangi segment kampanyasız kalmış?",
        ikon="🔗",
        kimlik="alt-kapsama",
        seviye=3,
    ),
)

GIRIS_METNI = (
    "Kampanyaları ve müşteri segmentlerini tek ekrandan izleyin; hangi segmentin "
    "hangi kampanyayla beslendiğini, hangisinin kampanyasız kaldığını görün. "
    "Bütçe tutarları ₺ cinsindendir."
)


def _bolum(kimlik: str) -> Section:
    """Kimlige gore bolum tanimini getirir (anchor tutarliligi icin)."""
    for bolum in BOLUMLER + ALT_BOLUMLER:
        if bolum.kimlik == kimlik:
            return bolum
    raise KeyError(f"Tanımsız bölüm kimliği: {kimlik}")

DURUM_ETIKET = {
    "active": "🟢 Aktif",
    "paused": "🟡 Duraklatildi",
    "draft": "⚪ Taslak",
    "completed": "🔵 Tamamlandi",
    "cancelled": "🔴 Iptal",
}


# ---------------------------------------------------------------- veri yukleme


def _jsonl_oku(dosya: Path) -> list[dict[str, Any]]:
    """JSONL dosyasini tolere ederek okur; bozuk satirlari atlar."""
    kayitlar: list[dict[str, Any]] = []
    if not dosya.exists():
        return kayitlar
    try:
        with open(dosya, encoding="utf-8") as f:
            for satir in f:
                satir = satir.strip()
                if not satir:
                    continue
                try:
                    kayit = json.loads(satir)
                except json.JSONDecodeError:
                    continue
                if isinstance(kayit, dict):
                    kayitlar.append(kayit)
    except OSError:
        return []
    return kayitlar


@st.cache_data(ttl=60)
def load_kampanyalar() -> tuple[list[dict[str, Any]], bool]:
    """Kampanyalari getirir. Donus: (kampanyalar, demo_mu)."""
    try:
        from company_master.pazarlama import kampanya_liste

        kayitlar = kampanya_liste(aktif_only=False)
        if kayitlar:
            return list(kayitlar), False
    except Exception:  # DB yok / tablo yok / baglanti hatasi
        pass
    return _jsonl_oku(DEMO_KAMPANYA), True


@st.cache_data(ttl=60)
def load_segmentler() -> tuple[list[dict[str, Any]], bool]:
    """Segmentleri getirir. Donus: (segmentler, demo_mu)."""
    try:
        from company_master.pazarlama import segment_liste

        kayitlar = segment_liste(aktif_only=False)
        if kayitlar:
            return list(kayitlar), False
    except Exception:
        pass
    return _jsonl_oku(DEMO_SEGMENT), True


@st.cache_data(ttl=60)
def load_segment_firmalari(segment_id: str) -> list[dict[str, Any]]:
    """Segmentteki firmalari getirir; hata halinde bos liste."""
    if not segment_id:
        return []
    try:
        from company_master.pazarlama import segment_firmaları_liste

        return list(segment_firmaları_liste(segment_id))
    except Exception:
        return []


def ozet_hesapla(
    kampanyalar: list[dict[str, Any]], segmentler: list[dict[str, Any]]
) -> dict[str, Any]:
    """Kampanya/segment ozet sayilarini hesaplar.

    Once backend ``ozet_rapor()`` denenir; basarisiz olursa eldeki
    (demo) listelerden hesaplanir.
    """
    try:
        from company_master.pazarlama import ozet_rapor

        rapor = ozet_rapor()
        if rapor and rapor.get("kampanya_sayisi"):
            return dict(rapor)
    except Exception:
        pass
    return {
        "kampanya_sayisi": len(kampanyalar),
        "segment_sayisi": len(segmentler),
        "aktif_kampanyalar": len(
            [k for k in kampanyalar if k.get("status") == "active"]
        ),
        "aktif_segmentler": len([s for s in segmentler if s.get("is_active")]),
    }


def performans_ozeti(kampanyalar: list[dict[str, Any]]) -> dict[str, float]:
    """Gosterim/tiklama/donusum toplamlari ve oranlari (veri varsa)."""
    gosterim = sum(float(k.get("impressions") or 0) for k in kampanyalar)
    tiklama = sum(float(k.get("clicks") or 0) for k in kampanyalar)
    donusum = sum(float(k.get("conversions") or 0) for k in kampanyalar)
    butce = sum(float(k.get("budget") or 0) for k in kampanyalar)
    return {
        "gosterim": gosterim,
        "tiklama": tiklama,
        "donusum": donusum,
        "butce": butce,
        "ctr": (tiklama / gosterim * 100) if gosterim else 0.0,
        "donusum_orani": (donusum / tiklama * 100) if tiklama else 0.0,
        "donusum_maliyeti": (butce / donusum) if donusum else 0.0,
    }


# ------------------------------------------------------------------- yardimci


def _durum_etiketi(durum: Any) -> str:
    return DURUM_ETIKET.get(str(durum or "").lower(), f"⚪ {durum or 'bilinmiyor'}")


def _kriter_metni(kriter: Any) -> str:
    """Segment kriterini okunur metne cevirir (dict veya JSON string)."""
    if isinstance(kriter, str):
        try:
            kriter = json.loads(kriter)
        except json.JSONDecodeError:
            return kriter
    if isinstance(kriter, dict):
        return " · ".join(f"{k}: {v}" for k, v in kriter.items())
    return str(kriter or "-")


# -------------------------------------------------------------------- render


def _render_baslik(demo_mu: bool) -> None:
    """ADMIN-UI-10: Playground kalibi — ust etiket -> H1 -> giris -> aksiyonlar."""
    PageHeader(
        "Pazarlama",
        giris=GIRIS_METNI,
        ust_etiket="İş · Pazarlama",
        ikon="📣",
    ).render()

    col_btn, col_rehber, col_zaman = st.columns([1, 1, 3], vertical_alignment="center")
    with col_btn:
        yenile = st.button(
            "🔄 Veriyi Yenile",
            key="pazarlama_yenile",
            type="primary",
            use_container_width=True,
            help="Önbelleği temizler ve kampanya/segment verisini yeniden yükler.",
        )
    with col_rehber:
        rehber = st.toggle(
            "ℹ️ Sekme rehberi",
            key="pazarlama_rehber",
            help="Bu ekranın amacını, veri kaynağını ve kısıtlarını gösterir.",
        )
    with col_zaman:
        if demo_mu:
            st.caption(
                "🧪 DEMO VERİ — veritabanı bağlantısı yok, örnek kayıtlar gösteriliyor. · "
                f"Son güncelleme: {datetime.now().strftime('%H:%M')}"
            )
        else:
            st.caption(
                "Canlı veritabanı verisi. · "
                f"Son güncelleme: {datetime.now().strftime('%H:%M')}"
            )

    if yenile:
        st.cache_data.clear()
        st.rerun()

    if rehber:
        st.info(
            "**Amaç:** Kampanya ve müşteri segmentlerini tek ekrandan izlemek, "
            "hangi segmentin hangi kampanyayla beslendiğini görmek.\n\n"
            "**Veri kaynağı:** `company_master.pazarlama` (kampanyalar / segmentler "
            "tabloları). Bağlantı yoksa `data/demo/` altındaki örnek veri.\n\n"
            "**Kısıt:** Demo modda kampanya oluşturma/düzenleme kapalıdır; "
            "gösterim/tıklama metrikleri yalnızca kaynakta varsa hesaplanır."
        )

    SectionNav(BOLUMLER, yatay=True).render()


def _render_ozet(ozet: dict[str, Any]) -> None:
    """K3: ozet metrikler + tek satir aciklama."""
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric(
            "Kampanya Sayısı",
            ozet.get("kampanya_sayisi", 0),
            help="Sistemdeki toplam kampanya kaydı (aktif + pasif).",
        )
        st.caption("📊 Kaç kampanya yönetiyoruz?")
    with k2:
        st.metric(
            "Aktif Kampanya",
            ozet.get("aktif_kampanyalar", 0),
            help="Durumu 'active' olan, şu an yayında olan kampanyalar.",
        )
        st.caption("📊 Şu an sahada kaç kampanya çalışıyor?")
    with k3:
        st.metric(
            "Segment Sayısı",
            ozet.get("segment_sayisi", 0),
            help="Tanımlı müşteri segmenti sayısı.",
        )
        st.caption("📊 Müşteriyi kaç farklı gruba ayırdık?")
    with k4:
        st.metric(
            "Aktif Segment",
            ozet.get("aktif_segmentler", 0),
            help="Kampanyalarda kullanılabilir durumdaki segmentler.",
        )
        st.caption("📊 Hedeflemeye hazır kaç segment var?")


def _render_performans(kampanyalar: list[dict[str, Any]]) -> None:
    """Gosterim/tiklama/donusum ozeti (veri varsa)."""
    perf = performans_ozeti(kampanyalar)
    if not perf["gosterim"] and not perf["butce"]:
        st.info("Veri gelince kampanya performans özeti burada görünecek.")
        return

    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.metric(
            "Toplam Bütçe",
            f"{perf['butce']:,.0f} ₺",
            help="Tüm kampanyaların bütçe toplamı.",
        )
        st.caption("📊 Pazarlamaya ne kadar ayırdık?")
    with p2:
        st.metric(
            "Tıklama Oranı (CTR)",
            f"%{perf['ctr']:.2f}",
            help="Tıklama / gösterim oranı. Reklamın ilgi çekiciliğini ölçer.",
        )
        st.caption("📊 Gösterimler tıklamaya dönüşüyor mu?")
    with p3:
        st.metric(
            "Dönüşüm Oranı",
            f"%{perf['donusum_orani']:.2f}",
            help="Dönüşüm / tıklama oranı. Tıklayanın müşteriye dönüşme yüzdesi.",
        )
        st.caption("📊 Tıklayanlar müşteriye dönüyor mu?")
    with p4:
        st.metric(
            "Dönüşüm Başı Maliyet",
            f"{perf['donusum_maliyeti']:,.0f} ₺" if perf["donusum"] else "-",
            help="Toplam bütçe / dönüşüm sayısı.",
        )
        st.caption("📊 Bir müşteri kazanmak kaça mal oluyor?")


def _render_kampanyalar(kampanyalar: list[dict[str, Any]], demo_mu: bool) -> None:
    """Kampanya listesi + butce grafigi (K2 yer tutucu)."""
    _bolum("alt-kampanyalar").render()
    if not kampanyalar:
        st.info("Veri gelince kampanya listesi burada görünecek.")
        return

    satirlar = []
    for k in kampanyalar:
        satirlar.append(
            {
                "Kampanya": k.get("name", "-"),
                "Durum": _durum_etiketi(k.get("status")),
                "Başlangıç": k.get("start_date") or "-",
                "Bitiş": k.get("end_date") or "-",
                "Bütçe (₺)": float(k.get("budget") or 0),
                "Dönüşüm": int(k.get("conversions") or 0),
            }
        )
    df = pd.DataFrame(satirlar)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption("📊 Hangi kampanya ne kadar bütçeyle ne kadar dönüşüm getirdi?")

    butce_df = df[df["Bütçe (₺)"] > 0]
    if butce_df.empty:
        st.info("Veri gelince bütçe dağılımı grafiği burada görünecek.")
    else:
        st.bar_chart(butce_df.set_index("Kampanya")["Bütçe (₺)"])

    if demo_mu:
        st.caption("🧪 Demo modda kampanya oluşturma/düzenleme kapalıdır.")


def _render_segmentler(segmentler: list[dict[str, Any]], demo_mu: bool) -> None:
    """Segment kartlari + firma detayina inme."""
    _bolum("alt-segmentler").render()
    if not segmentler:
        st.info("Veri gelince segment listesi burada görünecek.")
        return

    for seg in segmentler:
        ad = seg.get("name", "-")
        aktif = "🟢" if seg.get("is_active") else "⚪"
        rozet = " · 🧪 DEMO" if demo_mu or seg.get("DEMO") else ""
        with st.expander(f"{aktif} **{ad}**{rozet}"):
            if seg.get("description"):
                st.write(seg["description"])
            st.caption(f"Kriter: {_kriter_metni(seg.get('criteria'))}")

            segment_id = str(seg.get("segment_id") or "")
            firmalar = load_segment_firmalari(segment_id) if not demo_mu else []
            if firmalar:
                st.caption(f"Segmentte {len(firmalar)} firma var.")
                st.dataframe(
                    pd.DataFrame(firmalar),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("Veri gelince bu segmentteki firma listesi burada görünecek.")


def _render_segment_kampanya_eslesme(
    kampanyalar: list[dict[str, Any]], segmentler: list[dict[str, Any]]
) -> None:
    """Hangi segmentin kampanyayla beslendigini, hangisinin bos kaldigini gosterir."""
    _bolum("alt-kapsama").render()
    if not segmentler:
        st.info("Veri gelince segment kapsama analizi burada görünecek.")
        return

    kampanyali = {
        str(k.get("segment") or "").strip().lower()
        for k in kampanyalar
        if k.get("segment")
    }
    satirlar = []
    for seg in segmentler:
        ad = str(seg.get("name") or "-")
        kapsandi = ad.strip().lower() in kampanyali
        satirlar.append(
            {
                "Segment": ad,
                "Durum": "🟢 Kampanyası var" if kapsandi else "🟡 Kampanyasız",
                "Aktif": "Evet" if seg.get("is_active") else "Hayır",
            }
        )
    st.dataframe(pd.DataFrame(satirlar), use_container_width=True, hide_index=True)
    bos = [s for s in satirlar if s["Durum"].startswith("🟡")]
    if bos:
        st.warning(
            f"⚠️ {len(bos)} segment hiçbir kampanyaya bağlı değil: "
            + ", ".join(s["Segment"] for s in bos[:5])
        )
    st.caption("📊 Hangi müşteri grubunu kampanyasız bırakıyoruz?")


def render_pazarlama_tab() -> None:
    """Pazarlama sekmesi giris noktasi."""
    kampanyalar, k_demo = load_kampanyalar()
    segmentler, s_demo = load_segmentler()
    demo_mu = k_demo or s_demo

    _render_baslik(demo_mu)

    if not kampanyalar and not segmentler:
        st.info("Veri gelince kampanya ve segment özeti burada görünecek.")
        return

    ozet = ozet_hesapla(kampanyalar, segmentler)
    _bolum("pazarlama-ozeti").render()
    _render_ozet(ozet)

    _bolum("kampanya-performansi").render()
    _render_performans(kampanyalar)

    _bolum("detay-listeleri").render()
    sekme_kampanya, sekme_segment, sekme_kapsama = st.tabs(
        ["Kampanyalar", "Segmentler", "Kapsama"]
    )
    with sekme_kampanya:
        _render_kampanyalar(kampanyalar, demo_mu)
    with sekme_segment:
        _render_segmentler(segmentler, demo_mu)
    with sekme_kapsama:
        _render_segment_kampanya_eslesme(kampanyalar, segmentler)
