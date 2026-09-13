# -*- coding: utf-8 -*-
"""DASH-UX-04: Paketler sekmesi (UI).

DASH-UX-03 backend'ini (src/company_master/paketler.py) gosterir.
Veritabani hazir degilse data/demo/paketler_demo.jsonl uzerinden DEMO modunda calisir (K7).

Uyulan kalibi (00_sentez.md):
  K1 - Ortak sekme basligi: ikon+baslik, son guncelleme, yenile, "Bu sekme hakkinda"
  K2 - Bos veri kurali: bos grafik yok, yer tutucu mesaj
  K3 - Her metrigin altinda tek satir Turkce aciklama + operasyonel soru
  K7 - Demo veri DEMO rozetiyle isaretlenir
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

DEMO_DOSYA = ROOT / "data" / "demo" / "paketler_demo.jsonl"


# ---------------------------------------------------------------------------
# Veri yukleme
# ---------------------------------------------------------------------------

def _demo_paketler() -> list[dict[str, Any]]:
    """Demo JSONL dosyasindan paketleri okur (K7)."""
    if not DEMO_DOSYA.exists():
        return []
    kayitlar: list[dict[str, Any]] = []
    try:
        with open(DEMO_DOSYA, encoding="utf-8") as f:
            for satir in f:
                satir = satir.strip()
                if not satir:
                    continue
                try:
                    kayitlar.append(json.loads(satir))
                except json.JSONDecodeError:
                    continue
    except OSError:
        return []
    return kayitlar


@st.cache_data(ttl=60)
def load_paketler() -> tuple[list[dict[str, Any]], bool]:
    """Paket listesini yukler.

    Donen deger: (paketler, demo_mu)
    Once DB denenir; tablo yok / baglanti yoksa demo dosyaya duser.
    """
    try:
        from company_master.paketler import paket_liste

        paketler = paket_liste(aktif_only=True)
        if paketler:
            return paketler, False
    except Exception:
        pass
    return _demo_paketler(), True


@st.cache_data(ttl=60)
def load_firma_paketleri(company_id: str) -> list[dict[str, Any]]:
    """Bir firmanin sahip oldugu paketler. DB yoksa bos liste."""
    if not company_id:
        return []
    try:
        from company_master.paketler import firma_paketleri_getir

        return firma_paketleri_getir(company_id)
    except Exception:
        return []


@st.cache_data(ttl=60)
def load_demo_firmalar() -> list[dict[str, Any]]:
    """K7: demo firma kartlari (DB yokken capraz satis denemesi icin)."""
    dosya = ROOT / "data" / "demo" / "firma_karti_demo.jsonl"
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


def _demo_firma_paketleri(
    firma: dict[str, Any], tum_paketler: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Demo firma kartindaki paket adini katalogdaki paketle eslestirir."""
    paket_adi = str(firma.get("package") or "").strip().lower()
    if not paket_adi:
        return []
    return [
        {
            "package_id": p.get("package_id"),
            "name": p.get("name"),
            "price": p.get("price"),
            "status": "active",
        }
        for p in tum_paketler
        if str(p.get("name") or "").strip().lower() == paket_adi
    ]


def _features(paket: dict[str, Any]) -> list[str]:
    """features alani JSON string veya liste olabilir; normalize eder."""
    ham = paket.get("features", [])
    if isinstance(ham, str):
        try:
            ham = json.loads(ham)
        except json.JSONDecodeError:
            return [ham] if ham else []
    if isinstance(ham, list):
        return [str(x) for x in ham]
    return []


# ---------------------------------------------------------------------------
# Capraz satis onerisi
# ---------------------------------------------------------------------------

def capraz_satis_onerisi(
    firma_paketleri: list[dict[str, Any]],
    tum_paketler: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Firmanin sahip olmadigi paketleri fiyat sirasina gore onerir.

    Basit kural (MVP): mevcut en pahali paketin ustundeki paketler "yukselt",
    altindakiler "tamamlayici" olarak isaretlenir.
    """
    sahip_ids = {p.get("package_id") for p in firma_paketleri}
    mevcut_max = max(
        [float(p.get("price") or 0) for p in firma_paketleri], default=0.0
    )
    oneriler: list[dict[str, Any]] = []
    for paket in tum_paketler:
        if paket.get("package_id") in sahip_ids:
            continue
        fiyat = float(paket.get("price") or 0)
        oneriler.append(
            {
                "package_id": paket.get("package_id"),
                "name": paket.get("name", ""),
                "price": fiyat,
                "tip": "yukselt" if fiyat > mevcut_max else "tamamlayici",
                "fark": round(fiyat - mevcut_max, 2),
            }
        )
    oneriler.sort(key=lambda x: x["price"], reverse=True)
    return oneriler


# ---------------------------------------------------------------------------
# Bolumler
# ---------------------------------------------------------------------------

def _render_baslik(demo_mu: bool) -> None:
    """K1: ortak sekme basligi kalibi."""
    col_baslik, col_zaman, col_btn = st.columns([5, 2, 1])
    with col_baslik:
        rozet = " &nbsp;`DEMO`" if demo_mu else ""
        st.subheader("📦 Paketler")
        if demo_mu:
            st.caption("🧪 DEMO VERİ — veritabanı bağlantısı yok, örnek paketler gösteriliyor.")
        else:
            st.caption(rozet or "Canlı veritabanı verisi.")
    with col_zaman:
        st.caption(f"Son güncelleme: {datetime.now().strftime('%H:%M')}")
    with col_btn:
        if st.button("🔄", key="paketler_yenile", help="Veriyi yenile"):
            st.cache_data.clear()
            st.rerun()

    with st.expander("ℹ️ Bu sekme hakkında"):
        st.markdown(
            """
**Amaç:** Satılan paketleri, fiyatlarını ve firmalara atanma durumunu tek ekranda görmek;
bir firmaya hangi paketin teklif edilebileceğini belirlemek.

**Veri kaynağı:** `packages` / `company_packages` tabloları (DASH-UX-03 backend).
Tablo yoksa `data/demo/paketler_demo.jsonl` demo verisi kullanılır.

**Kısıt:** Demo modda atama/CRUD işlemleri kapalıdır; yalnızca görüntüleme yapılır.
Fiyatlar KDV hariç ve aylık listelenmiştir.
            """
        )


def _render_ozet(paketler: list[dict[str, Any]]) -> None:
    """K3: her metrik icin tek satir aciklama + operasyonel soru."""
    fiyatlar = [float(p.get("price") or 0) for p in paketler]
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Paket Sayısı", len(paketler), help="Kataloğa tanımlı aktif paket adedi.")
        st.caption("📊 Katalog fazla mı dar mı — müşteri hangi aralıkta tıkanıyor?")
    with c2:
        ort = sum(fiyatlar) / len(fiyatlar) if fiyatlar else 0
        st.metric(
            "Ortalama Fiyat",
            f"{ort:,.0f} ₺" if fiyatlar else "—",
            help="Aktif paketlerin ortalama aylık fiyatı (KDV hariç).",
        )
        st.caption("📊 Ortalama sepet buna yakın mı, yoksa hep en ucuz paket mi satılıyor?")
    with c3:
        st.metric(
            "Fiyat Aralığı",
            f"{min(fiyatlar):,.0f} – {max(fiyatlar):,.0f} ₺" if fiyatlar else "—",
            help="En ucuz ve en pahalı paket arasındaki aralık.",
        )
        st.caption("📊 Üst segment için bir basamak daha gerekiyor mu?")


def _render_paket_karti(paket: dict[str, Any], demo_mu: bool) -> None:
    ad = paket.get("name", "İsimsiz")
    fiyat = float(paket.get("price") or 0)
    rozet = " · 🧪 DEMO" if demo_mu else ""
    with st.expander(f"**{ad}** — {fiyat:,.0f} ₺/ay{rozet}"):
        aciklama = paket.get("description") or "Açıklama girilmemiş."
        st.write(aciklama)
        ozellikler = _features(paket)
        if ozellikler:
            st.markdown("**Kapsam:**")
            for oz in ozellikler:
                st.markdown(f"- {oz}")
        else:
            st.info("Bu pakete ait özellik listesi henüz tanımlanmamış.")
        st.caption(f"ID: `{paket.get('package_id', '—')}`")


def _render_paket_tablosu(paketler: list[dict[str, Any]]) -> None:
    """K2: veri yoksa bos grafik degil, yer tutucu."""
    if not paketler:
        st.info("📭 Veri gelince paket karşılaştırma tablosu burada görünecek.")
        return
    df = pd.DataFrame(
        [
            {
                "Paket": p.get("name", ""),
                "Fiyat (₺/ay)": float(p.get("price") or 0),
                "Özellik Sayısı": len(_features(p)),
            }
            for p in paketler
        ]
    )
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.bar_chart(df.set_index("Paket")["Fiyat (₺/ay)"])
    st.caption("📊 Fiyat basamakları arasındaki fark satışta itiraz yaratıyor mu?")


def _render_capraz_satis(paketler: list[dict[str, Any]], demo_mu: bool) -> None:
    st.markdown("---")
    st.markdown("### 🎯 Firma Kartı — Çapraz Satış Önerisi")
    st.caption("Bir firmanın mevcut paketlerine bakarak teklif edilebilecek paketleri listeler.")

    firma_paketleri: list[dict[str, Any]] = []

    if demo_mu:
        demo_firmalar = load_demo_firmalar()
        if not demo_firmalar:
            st.info("📭 Demo firma kartı bulunamadı; çapraz satış önerisi hesaplanamıyor.")
            return
        secenekler = {
            f"{f.get('company_name', '-')} ({f.get('package', 'paketsiz')})": f
            for f in demo_firmalar
        }
        secim = st.selectbox(
            "Firma seç (demo)",
            list(secenekler.keys()),
            key="paketler_demo_firma",
        )
        firma = secenekler[secim]
        firma_paketleri = _demo_firma_paketleri(firma, paketler)
        st.caption(
            f"🧪 DEMO · Segment: {firma.get('segment', '-')} · "
            f"Çalışan: {firma.get('employee_count', '-')} · "
            f"Ciro: {float(firma.get('revenue') or 0):,.0f} ₺"
        )
    else:
        company_id = st.text_input(
            "Firma ID",
            key="paketler_company_id",
            placeholder="Örn: 4f3c... (firma UUID)",
        ).strip()

        if not company_id:
            st.info("📭 Firma ID girince o firmaya özel çapraz satış önerisi burada görünecek.")
            return

        firma_paketleri = load_firma_paketleri(company_id)

    if firma_paketleri:
        st.markdown("**Mevcut paketleri:**")
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Paket": p.get("name", ""),
                        "Fiyat (₺/ay)": float(p.get("price") or 0),
                        "Durum": p.get("status", "active"),
                    }
                    for p in firma_paketleri
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.caption("Bu firmaya atanmış paket bulunamadı.")

    oneriler = capraz_satis_onerisi(firma_paketleri, paketler)
    if not oneriler:
        st.success("✅ Bu firma kataloğun tamamına sahip — çapraz satış fırsatı yok.")
        return

    st.markdown("**Önerilen paketler:**")
    for oneri in oneriler[:5]:
        etiket = "⬆️ Yükseltme" if oneri["tip"] == "yukselt" else "➕ Tamamlayıcı"
        fark = oneri["fark"]
        fark_metin = f"+{fark:,.0f} ₺/ay" if fark > 0 else f"{fark:,.0f} ₺/ay"
        st.markdown(
            f"- {etiket} — **{oneri['name']}** ({oneri['price']:,.0f} ₺/ay, fark {fark_metin})"
        )
    st.caption("📊 Bu firmayı bir üst pakete taşımak için hangi ihtiyaç sinyalini bekliyoruz?")


# ---------------------------------------------------------------------------
# Ana giris
# ---------------------------------------------------------------------------

def render_paketler_tab() -> None:
    """DASH-UX-04: Paketler sekmesini cizer."""
    paketler, demo_mu = load_paketler()

    _render_baslik(demo_mu)

    if not paketler:
        st.info("📭 Veri gelince paket listesi burada görünecek. (Katalog boş veya DB bağlantısı yok.)")
        return

    _render_ozet(paketler)

    st.markdown("---")
    st.markdown("### 📋 Paket Kataloğu")
    for paket in paketler:
        _render_paket_karti(paket, demo_mu)

    st.markdown("---")
    st.markdown("### 📊 Paket Karşılaştırma")
    _render_paket_tablosu(paketler)

    _render_capraz_satis(paketler, demo_mu)
