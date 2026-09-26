# -*- coding: utf-8 -*-
"""DASH-UX-01 Ana Kontrol Sekmesi — K4 (Mavi Müşteri + Turuncu Sistem).

Kapsam:
  - Müşteri metrikleri (mavi kart): toplam firma, aktif kullanıcı, sinyal, API çağrıları
  - Sistem metrikleri (turuncu kart): sistem durumu, DLQ, cache, query latency
  - Her metrik yanında "neyi gösterir" + operasyonel soru
  - K1 ortak şablonu: son güncelleme, yenile, "ℹ️ Bu sekme hakkında"

Kurallar:
  - kpi_karti(..., kategori=...) ile renk sınıflandırması (mavi müşteri / turuncu sistem)
  - st.cache_data(ttl=30)
  - Empty state → "Veri gelince X burada görünecek"

ADMIN-UI-09 (pilot ekran):
  Sayfa iskeleti Streamlit Playground dokümantasyon mantığına taşındı:
  ``PageHeader`` (üst etiket → H1 → giriş paragrafı) → ``SectionNav``
  ("Bu sayfada" gezinme) → ``Section`` (H2 + açıklama + ayraç) blokları.
  Renk paleti, ikon seti ve tipografi seçimleri **değişmedi**; yalnızca
  hiyerarşi disipline edildi. Aynı ekranda tek birincil buton kuralı gereği
  yalnız "Veriyi Yenile" birincil, diğer aksiyonlar ikincildir.
"""
from __future__ import annotations

import html
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from scripts.dash04_api_client import get_api, APIError  # noqa: E402

from company_master.i18n import t  # noqa: E402
from company_master.ui import PageHeader, Section, SectionNav  # noqa: E402
from company_master.ui.tokens import RENKLER  # noqa: E402
from web_dashboard.charts import (  # noqa: E402  (UI-CHART-01, KPI-EXA-02)
    KATEGORI_RENK,
    donut,
    kategori_rengi,
    kpi_karti,
    sayi_formatla,
)

#: K3-10f: blok yükseklikleri — yan yana duran iki kolon **aynı** yüksekliği
#: alır, yoksa kart altları kaymış görünür (KAHİN: "kolonlar hizalı ve eşit
#: değil"). Değerler alt yazıyı kırpmayacak kadar yüksek tutulur.
#: ponytail: sabit px; içerik taşarsa blok kendi içinde kaydırır.
_SATIR_YUKSEKLIK: dict[str, int] = {"ust": 310, "orta": 360, "alt": 340}
#: K3-10f: blok yüksekliği − başlık/altyazı payı. Donut bundan büyük olursa
#: alt yay çerçeveden kırpılır (KAHİN ekran görüntüsü, 2026-09-26).
_DONUT_YUKSEKLIK: int = _SATIR_YUKSEKLIK["alt"] - 110

# --- §8.4.1: Aksiyon butonu renkleri -----------------------------------------
# Streamlit `st.button` yalnız primary/secondary/tertiary kabul eder; kontur
# rengi için element key'inden gelen `.st-key-<key>` sınıfı kullanılır
# (Streamlit >= 1.38). Renkler yalnız `tokens.py` içinden gelir.
_AKSIYON_RENK: dict[str, str] = {
    "ovw_guncelle": RENKLER["info"],
    "ovw_saglik": RENKLER["success"],
    "ovw_export": RENKLER["warning"],
    "ovw_onay": RENKLER["danger"],
}
_AKSIYON_CSS = "<style>" + "".join(
    f'.st-key-{anahtar} button {{ border-color: {renk} !important; color: {renk} !important; }}'
    f'.st-key-{anahtar} button:hover {{ background: {renk}1a !important; }}'
    for anahtar, renk in _AKSIYON_RENK.items()
) + "</style>"

#: §8.4.2 — Overview'dan ilgili sekmeye giriş kartları (ikon, etiket, tab anahtarı).
GIRIS_KARTLARI: tuple[tuple[str, str, str], ...] = (
    ("👥", "Firmalar", "musteriler"),
    ("🧑", "Kullanıcılar", "kullanicilar"),
    ("⚠️", "Olaylar & Hatalar", "hatalar"),
    ("📊", "Metrikler", "kpi"),
)


@st.cache_data(ttl=30)
def load_kpi_data() -> dict[str, Any]:
    """KPI verisi yükle (/api/kpi endpoint'inden)."""
    try:
        data = get_api("/api/kpi")
        if isinstance(data, dict):
            return data or {}
    except (APIError, Exception):
        pass
    return {}


@st.cache_data(ttl=30)
def load_kpi_history(days: int = 7) -> dict[str, Any]:
    """KPI tarih verisi yükle (/api/kpi/history endpoint'inden)."""
    try:
        data = get_api(f"/api/kpi/history?days={days}")
        if isinstance(data, dict):
            return data or {}
    except (APIError, Exception):
        pass
    return {}


@st.cache_data(ttl=30)
def load_webhook_stats() -> dict[str, Any]:
    """Webhook istatistikleri yükle."""
    try:
        # Placeholder: webhook monitor'dan veri çek
        # Gerçek impl: file log tarama veya /api/webhook-stats endpoint
        return {
            "basarili": 0,
            "hatali": 0,
            "calisan": 0,
            "dlq_toplam": 0,
            "son_olay": None,
            "olay_toplam": 0,
            "hata_turleri": {},
        }
    except Exception:
        pass
    return {}

@st.cache_data(ttl=60)
def bekleyen_onay_sayisi(token: str | None) -> int:
    """Onay bekleyen kullanıcı sayısı. -1 = okunamadı (API/yetki yok)."""
    try:
        data = get_api("/api/admin/pending", token=token)
    except (APIError, Exception):
        return -1
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict):
        for anahtar in ("users", "items", "pending"):
            if isinstance(data.get(anahtar), list):
                return len(data[anahtar])
    return 0


#: TEK-ADRES-01 (KAHİN, 2026-09-26): "tek bir yapı tek bir adres istiyorum; sahte
#: veri koyacaksan sahte verilerin olduğu grafiğin altına yazarsın ve uyarılar
#: koyarsın, yeni veriler geldiğinde onlar otomatik değişir."
#: Bu yüzden ayrı "taslak sürüm" / ikinci port YOK. Yer tutucu **varsayılan olarak
#: açıktır**: verisi olmayan kutu sahte değerle çizilir ve hemen altına "SAHTE VERİ"
#: uyarısı basılır. Gerçek veri geldiği anda `_dolu()` True döner → kutu gerçek
#: değere geçer, uyarı kendiliğinden kaybolur (elle temizlik gerekmez).
#: `HUGINN_TASLAK=0` ile kapatılabilir (ekran görüntüsü/denetim için kaçış kapısı).
TASLAK = os.getenv("HUGINN_TASLAK", "1") != "0"

#: Yer tutucu değerler. Grep'lenebilir olsun diye sabit.
SAHTE_DEGER = "1.234"
SAHTE_YUZDE = 68.0


def _veri_etiketi(gercek: list[str], sahte: list[str]) -> None:
    """VERI-ETIKET-01 (KAHİN): her blok altına "hangi veri nereden" satırı basar.

    KAHİN: "sahte veri ve gerçek veri ayırt etmek için ikon kullan, altına
    sahte/gerçek diye yaz; böylece hangi verilerin geldiğini göreyim."
    Tek kaynak: tüm bloklar bu fonksiyonu çağırır, metin şablonu tek yerde.
    Gerçek veri geldiğinde ad `sahte` listesinden `gercek` listesine geçer,
    etiket kendiliğinden değişir.
    """
    parcalar: list[str] = []
    if gercek:
        parcalar.append(f"🟢 **GERÇEK VERİ**: {', '.join(gercek)}")
    if sahte:
        parcalar.append(f"🔴 **SAHTE VERİ**: {', '.join(sahte)} — gerçek veri geldiğinde otomatik değişir")
    if parcalar:
        st.caption(" · ".join(parcalar))


def _dolu(deger: Any) -> bool:
    """K3-10: Hücrede gerçek veri var mı?

    KAHİN kuralı: "ızgara doldurmak için sahte kutu üretmeyin." 0, None ve boş
    metin veri değildir. TEK-ADRES-01: hücre yer tutucuyla çizilir ve altına
    "SAHTE VERİ" uyarısı basılır; gerçek veri gelince burası True döner ve
    kutu kendiliğinden gerçek değere geçer.
    """
    return deger not in (None, 0, 0.0, "", "0")


def _kart_izgara(adaylar: list[dict[str, Any]], bos_mesaj: str) -> None:
    """Yalnız verisi olan kartları yan yana çizer (3 veri → 3 kolon).

    `adaylar` her öğesi `kpi_karti` kwargs sözlüğüdür. Verisi olmayan aday
    `SAHTE_DEGER` yer tutucusuyla çizilir ve altında hangi kartların sahte
    olduğu tek satırda listelenir (TEK-ADRES-01).
    """
    gecerli = [a for a in adaylar if _dolu(a.get("deger"))]
    sahte = [a for a in adaylar if not _dolu(a.get("deger"))] if TASLAK else []
    if not gecerli and not sahte:
        st.info(bos_mesaj)
        return
    cizilecek = gecerli + [{**a, "deger": SAHTE_DEGER} for a in sahte]
    # K3-10g (KAHİN: "özellikle toplam firma kartı kaymış"): sparkline kartın
    # **altına** çizilir, bu yüzden serisi olan kart komşusundan uzun kalıyordu.
    # Kural: satırdaki *tüm* kartların serisi yoksa hiçbirinde çizilmez.
    hepsinde_seri = all(len(a.get("sparkline") or []) >= 2 for a in cizilecek)
    for kolon, aday in zip(st.columns(len(cizilecek)), cizilecek):
        with kolon:
            kpi_karti(
                aday["baslik"], aday["deger"],
                sparkline=aday.get("sparkline") if hepsinde_seri else None,
                kategori=aday.get("kategori", "musteri"),
                yardim=aday.get("yardim", ""),
            )
    _veri_etiketi([a["baslik"] for a in gecerli], [a["baslik"] for a in sahte])
    if sahte:
        return
    eksik = len(adaylar) - len(gecerli)
    if eksik:
        st.caption(f"↳ {eksik} metrik henüz veri üretmedi; veri gelince kart eklenir.")


def _yuzde_halka(baslik: str, yuzde: float, kategori: str = "sistem") -> str:
    """Bağımlılıksız radial gauge — saf CSS `conic-gradient`, paket yok.

    `st-radial` (son sürüm 2022, Streamlit 1.4x'te test edilmemiş) yerine
    KAHİN'in seçtiği yol. Yüzde 0–100 aralığına kırpılır.
    KPI-RENK-03: halka **ve** ortadaki sayı kategori rengindedir.
    """
    y = max(0.0, min(100.0, float(yuzde)))
    renk = kategori_rengi(kategori)
    sayi_renk = RENKLER.get(f"{KATEGORI_RENK.get(kategori, 'primary')}-text", renk)
    return (
        '<div style="text-align:center">'
        '<div style="width:96px;height:96px;margin:0 auto;border-radius:50%;'
        f'background:conic-gradient({renk} {y}%, rgba(127,127,127,.18) 0);'
        'display:flex;align-items:center;justify-content:center">'
        f'<div style="width:74px;height:74px;border-radius:50%;background:{RENKLER["surface"]};'
        f'display:flex;align-items:center;justify-content:center;font-weight:700;color:{sayi_renk};'
        f'font-variant-numeric:tabular-nums">%{y:.0f}</div></div>'
        '<div style="font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;'
        f'color:{RENKLER["text-muted"]};margin-top:6px">{html.escape(baslik)}</div></div>'
    )


def _halka_satiri(adaylar: list[tuple[str, float | None]] | list[tuple[str, float | None, str]]) -> None:
    """Yüzde halkalarını yan yana çizer; verisi olmayan halka yer tutucuyla çizilir.

    Aday 2'li (`ad, yuzde`) ya da 3'lü (`ad, yuzde, kategori`) olabilir.
    """
    ucuz = [(a[0], a[1], a[2] if len(a) > 2 else "sistem") for a in adaylar]
    gecerli = [(ad, y, k) for ad, y, k in ucuz if y is not None]
    sahte = [(ad, k) for ad, y, k in ucuz if y is None] if TASLAK else []
    cizilecek = gecerli + [(ad, SAHTE_YUZDE, k) for ad, k in sahte]
    if not cizilecek:
        st.caption("Oran metrikleri henüz ölçülmedi; veri gelince halkalar açılır.")
        return
    for kolon, (ad, y, k) in zip(st.columns(len(cizilecek)), cizilecek):
        with kolon:
            st.markdown(_yuzde_halka(ad, y, k), unsafe_allow_html=True)
    _veri_etiketi([ad for ad, _, _ in gecerli], [ad for ad, _ in sahte])


def _yatay_bar(ogeler: list[tuple[str, float, str]]) -> str:
    """K3-10f: yatay ilerleme çubukları — tek `st.markdown`, paket yok.

    KAHİN: "her şeyi yatay planlama, biraz hareket kat, veriyi başka şekilde
    göster." En büyük değer tam genişliği alır; renk kategoriden gelir.
    """
    enb = max((d for _, d, _ in ogeler), default=0) or 1
    satirlar = []
    for ad, deger, kat in ogeler:
        renk = kategori_rengi(kat)
        sayi_renk = RENKLER.get(f"{KATEGORI_RENK.get(kat, 'primary')}-text", renk)
        genislik = max(2.0, float(deger) / enb * 100)
        satirlar.append(
            '<div style="margin-bottom:12px">'
            '<div style="display:flex;justify-content:space-between;align-items:baseline;'
            f'font-size:.76rem;letter-spacing:.04em;text-transform:uppercase;'
            f'color:{RENKLER["text-muted"]};margin-bottom:5px">'
            f'<span>{html.escape(ad)}</span>'
            f'<span style="color:{sayi_renk};font-weight:700;font-size:.95rem;'
            f'text-transform:none;font-variant-numeric:tabular-nums">'
            f'{html.escape(sayi_formatla(deger))}</span></div>'
            '<div style="height:8px;border-radius:4px;background:rgba(127,127,127,.16)">'
            f'<div style="width:{genislik:.1f}%;height:100%;border-radius:4px;'
            f'background:linear-gradient(90deg,{renk},{renk}66)"></div></div></div>'
        )
    return "".join(satirlar)


def _hareket_satiri(adaylar: list[tuple[str, Any, str]]) -> None:
    """Yatay bar bloğu; verisi olmayan satır yer tutucuyla çizilir + uyarı alır."""
    gecerli = [(ad, float(d), k) for ad, d, k in adaylar if _dolu(d)]
    sahte = [(ad, k) for ad, d, k in adaylar if not _dolu(d)] if TASLAK else []
    cizilecek = gecerli + [(ad, float(SAHTE_DEGER.replace(".", "")), k) for ad, k in sahte]
    if not cizilecek:
        st.caption("Hareket verisi henüz toplanmadı — kullanım başlayınca burada görünecek.")
        return
    st.markdown(_yatay_bar(cizilecek), unsafe_allow_html=True)
    _veri_etiketi([ad for ad, _, _ in gecerli], [ad for ad, _ in sahte])


def _icgoru_paneli(ogeler: list[tuple[str, str, str, str]]) -> None:
    """Referans paneldeki "Key Insights" rayı: ikon + başlık + tek cümle, **dikey** akar.

    KAHİN (K3-10f): "sayfa içinde hep aynı şeyleri kullanma ... dikey ilerleyen
    bir şeyler lazım." Bu panel kart/grafik değil; okunabilir metin rayıdır.
    Öğe: ``(ikon, başlık, cümle, kategori)``. Boş liste → blok çizilmez.
    """
    if not ogeler:
        st.caption("İçgörü üretecek veri henüz yok.")
        return
    parcalar: list[str] = []
    # KPI-RENK-04: zemin **boş** bırakılır — Streamlit'in etkin teması geçer,
    # aydınlık modda renk dolgusu patlamaz (KAHİN: "gündüz modunda hepsi patlar").
    for ikon, baslik, metin, kategori in ogeler:
        renk = kategori_rengi(kategori)
        parcalar.append(
            '<div style="display:flex;gap:10px;align-items:flex-start;padding:8px 0 8px 11px;'
            f'margin-bottom:6px;border-left:2px solid {renk}">'
            f'<div style="font-size:1rem;line-height:1.25;opacity:.75">{ikon}</div><div>'
            '<div style="font-weight:600;font-size:.84rem">'
            f'{html.escape(baslik)}</div>'
            f'<div style="font-size:.78rem;line-height:1.35;color:{RENKLER["text-muted"]}">'
            f'{html.escape(metin)}</div></div></div>'
        )
    st.markdown("".join(parcalar), unsafe_allow_html=True)


def _durum_ozeti(
    kpi: dict[str, Any], webhook: dict[str, Any], bekleyen: int
) -> tuple[str, str, str]:
    """(ışık, metin, renk) — trafik ışığı kararı tek yerde verilir."""
    dlq = webhook.get("dlq_toplam", 0)
    cache = kpi.get("cache_hit_rate", 0)
    if dlq:
        return "🔴", f"{dlq} DLQ kaydı işlenmedi — Olaylar & Hatalar sekmesine bakın.", "#ef4444"
    if cache and cache < 0.3:
        return "🟡", f"Cache hit %{cache * 100:.0f} — veritabanı yükü yüksek olabilir.", "#f59e0b"
    if bekleyen > 0:
        return "🟡", f"{bekleyen} kullanıcı onay bekliyor.", "#f59e0b"
    return "🟢", "Kritik uyarı yok — sistem normal çalışıyor.", "#22c55e"


def _trafik_isigi(kpi: dict[str, Any], webhook: dict[str, Any], bekleyen: int) -> None:
    """K3-10 Blok 2: tek satırda 🟢/🟡/🔴 sistem özeti."""
    isik, metin, _ = _durum_ozeti(kpi, webhook, bekleyen)
    st.markdown(f"### {isik} {metin}")


def _vurgu_paneli(isik: str, baslik: str, metin: str, renk: str, alt: str) -> str:
    """K3-10d "4+1" düzenin **+1**'i: sağdaki vurgulu (renkli) özet sütunu.

    Referans ekrandaki yeşil "Projected Launch Date" paneliyle aynı rolü oynar:
    4 eşit metrik kolonunun yanında dar, renk kodlu tek bir durum kutusu.
    CSS dosyası yok — inline `st.markdown` (KAHİN kısıtı).
    """
    # KPI-RENK-04: renk dolgusu kaldırıldı; durum rengi yalnız sol şeritte ve
    # ikonda. Zemin belirtilmez → tema ne ise o (aydınlık/karanlık güvenli).
    return (
        f'<div style="border:1px solid {RENKLER["border-strong"]};border-left:3px solid {renk};'
        'border-radius:10px;padding:14px 16px">'
        f'<div style="font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;'
        f'color:{RENKLER["text-muted"]};font-weight:600">{html.escape(baslik)}</div>'
        '<div style="font-size:1rem;font-weight:600;line-height:1.4;margin:6px 0">'
        f'{isik} {html.escape(metin)}</div>'
        f'<div style="font-size:.76rem;color:{RENKLER["text-muted"]}">{html.escape(alt)}</div>'
        '</div>'
    )


def _sonuc_yaz(tip: str, mesaj: str) -> None:
    """Aksiyon sonucunu rerun sonrası da yaşayacak biçimde saklar."""
    st.session_state["ovw_sonuc"] = (tip, mesaj, datetime.now().strftime("%H:%M:%S"))


def _veri_guncelle() -> None:
    """`scripts/refresh_pipeline.py` çalıştırır ve sonucu ekrana yazar."""
    try:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "refresh_pipeline.py")],
            capture_output=True, text=True, timeout=180, cwd=str(ROOT),
        )
    except subprocess.TimeoutExpired:
        _sonuc_yaz("error", "Veri güncelleme 180 sn içinde bitmedi, iptal edildi.")
        return
    except Exception as hata:  # script yok / yorumlayıcı hatası
        _sonuc_yaz("error", f"Veri güncelleme başlatılamadı: {hata}")
        return
    if proc.returncode == 0:
        son = (proc.stdout or "").strip().splitlines()
        _sonuc_yaz("success", f"Veri güncellendi. {son[-1] if son else 'Çıktı yok.'}")
        st.cache_data.clear()
    else:
        hata_metni = (proc.stderr or proc.stdout or "").strip().splitlines()
        _sonuc_yaz("error", f"Veri güncelleme hatası: {hata_metni[-1] if hata_metni else proc.returncode}")


def _saglik_kontrolu() -> None:
    """API ve webhook alıcısının ayakta olup olmadığını kontrol eder."""
    durumlar: list[str] = []
    saglikli = True
    for ad, uc in (("API", "/metrics"), ("Webhook", "/api/webhooks/apify/health")):
        try:
            get_api(uc)
            durumlar.append(f"{ad} 🟢")
        except (APIError, Exception):
            durumlar.append(f"{ad} 🔴")
            saglikli = False
    _sonuc_yaz("success" if saglikli else "error", " · ".join(durumlar))


def _csv_hazirla() -> None:
    """Firma listesini CSV'ye çevirip indirilmeye hazır hale getirir."""
    # ponytail: doğrudan /api/companies/export yerine JSON + pandas kullanıldı;
    # get_api yalnız JSON çözer. Büyük veri gerekince stream'li indirmeye geçilir.
    try:
        data = get_api("/api/companies", params={"limit": 1000})
    except (APIError, Exception) as hata:
        _sonuc_yaz("error", f"Dışa aktarma başarısız: {hata}")
        return
    satirlar = data if isinstance(data, list) else (data or {}).get("items") or []
    if not satirlar:
        _sonuc_yaz("info", "Dışa aktarılacak kayıt yok.")
        return
    csv_metni = pd.DataFrame(satirlar).to_csv(index=False)
    st.session_state["ovw_csv"] = csv_metni
    _sonuc_yaz("success", f"{len(satirlar)} satır hazır · {len(csv_metni) / 1_048_576:.2f} MB")


#: ADMIN-UI-09 — Sayfa bölümleri tek yerde tanımlanır; hem `SectionNav`
#: hem de gövde aynı listeyi kullanır, böylece anchor'lar asla kaymaz.
# KPI-EXA-02 (sahip, 2026-09-15): Veri Akışı diyagramı "Teknik Altyapı" sayfasına
# taşındı; bölüm açıklama cümleleri ve küçük emojiler kaldırıldı (sade başlık).
# K3-10b/K3-10f (KAHİN, 2026-09-26): bu sayfanın bölümleri **çerçeveli blok
# içinde** duruyor; `seviye=2` (H1 ölçeğinde H2) küçük kartın içinde dev başlık
# üretiyordu. `seviye=3` hem ölçeği düşürür hem `Section.ayrac = ayrac and
# seviye == 2` kuralı gereği blok üstündeki fazla ayırıcıyı kaldırır.
# Anchor'lar (`kimlik`) değişmedi — SectionNav ve koruma testleri bozulmaz.
BOLUMLER: tuple[Section, ...] = (
    Section("Müşteri", kimlik="musteri-metrikleri", seviye=3),
    Section("Sistem", kimlik="sistem-metrikleri", seviye=3),
    Section("Uyarılar", kimlik="anlik-uyarilar", seviye=3),
    Section("Webhook Akışı", kimlik="webhook-akisi", seviye=3),
)

GIRIS_METNI = t("huginn_dashboard_welcome")


def _bolum(kimlik: str) -> Section:
    """Kimliğe göre bölüm tanımını getirir (anchor tutarlılığı için)."""
    for bolum in BOLUMLER:
        if bolum.kimlik == kimlik:
            return bolum
    raise KeyError(f"Tanımsız bölüm kimliği: {kimlik}")


def render_ana_kontrol_tab() -> None:
    """DASH-UX-01 Ana Kontrol sekmesi (ADMIN-UI-09 sayfa iskeletiyle)."""
    # --- ADMIN-UI-09: Playground kalıbı — üst etiket → H1 → giriş paragrafı ---
    PageHeader(
        "Ana Kontrol",
        giris=GIRIS_METNI,
        ust_etiket="İş · Operasyon",
    ).render()

    token = st.session_state.get("admin_token")
    bekleyen = bekleyen_onay_sayisi(token)

    # --- Veri yükleme (bloklardan önce: trafik ışığı da veriyi kullanır) ---
    with st.spinner("Veriler yükleniyor..."):
        kpi = load_kpi_data()
        kpi_history = load_kpi_history(7)
        webhook = load_webhook_stats()

    # ================= BLOK 1/5 — Aksiyon şeridi (§8.4.1) =================
    with st.container(border=True):
        st.markdown(_AKSIYON_CSS, unsafe_allow_html=True)
        b1, b2, b3, b4, b5 = st.columns(5, vertical_alignment="center")
        with b1:
            # K3-10f (KAHİN): "veriyi güncelle ile veriyi yenile aynı şey değil mi,
            # mavi olan fazla gibi duruyor, onun yerine firmalar kısmını getir."
            # Yenile düğmesi kaldırıldı; önbellek temizliği Veri Güncelle'ye taşındı.
            from web_dashboard.tabs import tab_getir  # fonksiyon içi: döngüsel import yok

            _firma_tab = tab_getir("musteriler")
            st.link_button(
                "👥 Firmalar", f"/{_firma_tab.url_path}" if _firma_tab else "/",
                width="stretch", help="Firma listesine gider.",
            )
        with b2:
            if st.button("⬇ Veri Güncelle", key="ovw_guncelle", width="stretch",
                         help="Kaynaklardan veri çekme hattını çalıştırır, önbelleği temizler."):
                with st.spinner("Veri hattı çalışıyor..."):
                    _veri_guncelle()
                st.cache_data.clear()
        with b3:
            if st.button("♥ Sağlık Kontrolü", key="ovw_saglik", width="stretch",
                         help="API ve webhook alıcısının ayakta olup olmadığını sorar."):
                with st.spinner("Servisler sorgulanıyor..."):
                    _saglik_kontrolu()
        with b4:
            if st.button("⬆ Dışa Aktar (CSV)", key="ovw_export", width="stretch",
                         help="Firma listesini CSV dosyası olarak hazırlar."):
                with st.spinner("CSV hazırlanıyor..."):
                    _csv_hazirla()
        with b5:
            etiket = "✓ Bekleyen Onaylar" if bekleyen < 0 else f"✓ Bekleyen Onaylar ({bekleyen})"
            if st.button(etiket, key="ovw_onay", width="stretch",
                         help="Onay bekleyen kullanıcıları listeler."):
                st.session_state["ovw_onay_ac"] = True

        sonuc = st.session_state.get("ovw_sonuc")
        if sonuc:
            tip, mesaj, saat = sonuc
            {"success": st.success, "error": st.error}.get(tip, st.info)(f"{mesaj} · {saat}")
        if st.session_state.get("ovw_csv"):
            st.download_button(
                "CSV dosyasını indir", st.session_state["ovw_csv"],
                file_name=f"firmalar_{datetime.now():%Y%m%d_%H%M}.csv",
                mime="text/csv", key="ovw_csv_indir",
            )
        if st.session_state.pop("ovw_onay_ac", False) and bekleyen > 0:
            st.info(f"{bekleyen} kullanıcı onay bekliyor — **Müşteriler › Kullanıcılar** sekmesinden işleyin.")

    # ============ SATIR 2 — 4+1 durum şeridi (K3-10d, yatay bölme) ============
    # KAHİN: "sağ tarafı 5 bölmüşsün ama örnekte yatay bölme yapmış — 4+1 kolon."
    # Sol sütun 4 eşit metrik kolonu taşır, sağdaki dar sütun vurgulu özet panelidir.
    series = kpi_history.get("series", {})
    sol, sag = st.columns([4, 1.4], vertical_alignment="top")
    with sol:
        # K3-10f: yan yana bloklar **aynı** yükseklikte (KAHİN: "kolonlar hizalı
        # ve eşit değil ... birbirlerine hizala").
        with st.container(border=True, height=_SATIR_YUKSEKLIK["ust"]):
            _bolum("musteri-metrikleri").render()
            # KPI-RENK-03: her kart ayrı kategori rengi taşır (referans panelde
            # de her sayı farklı renkte) — renk bilgi taşır, süs değildir.
            _kart_izgara(
                [
                    {"baslik": "Toplam Firma", "deger": kpi.get("total"),
                     "sparkline": series.get("yeni_firma") or None, "kategori": "musteri",
                     "yardim": "Veritabanında kayıtlı aktif firma sayısı"},
                    {"baslik": "Aktif Kullanıcı", "deger": kpi.get("active_users"),
                     "sparkline": series.get("login") or None, "kategori": "basari",
                     "yardim": "Son 7 gün içinde api_key ile istek yapmış kullanıcılar"},
                    {"baslik": "Sinyal Sayısı", "deger": kpi.get("signal_count"),
                     "sparkline": series.get("search") or None, "kategori": "bilgi",
                     "yardim": "Oluşturulmuş toplam ticari sinyal (purchase intent vb.)"},
                    # K3-10f: etiket tek satıra sığar — iki satıra sarınca kart
                    # yüksekliği kayıyordu (KAHİN: "birbirlerine hizala").
                    {"baslik": "API Çağrısı", "deger": kpi.get("api_calls_total"),
                     "kategori": "uyari", "yardim": "Son 24 saatte yapılmış API çağrı sayısı"},
                ],
                "Müşteri metrikleri henüz veri üretmedi.",
            )
    with sag:
        with st.container(border=False, height=_SATIR_YUKSEKLIK["ust"]):
            isik, metin, renk = _durum_ozeti(kpi, webhook, bekleyen)
            st.markdown(
                _vurgu_paneli(
                    isik, "Sistem Durumu", metin, renk,
                    f"Son güncelleme {datetime.now():%H:%M} · önbellek ömrü 30 sn",
                ),
                unsafe_allow_html=True,
            )
            # K3-10g (KAHİN: "kritik uyarı yok kartının altına bir tane daha koy,
            # boşluk kapansın"): sağ sütunun kalan yüksekliğini ikinci panel doldurur.
            st.markdown("")
            kuyruk = int(webhook.get("dlq_toplam", 0) or 0)
            onay = max(bekleyen, 0)
            k_isik, k_renk = ("🟢", RENKLER["success-text"]) if kuyruk == 0 and onay == 0 else (
                ("🟡", RENKLER["warning-text"]) if kuyruk == 0 else ("🔴", RENKLER["danger-text"])
            )
            st.markdown(
                _vurgu_paneli(
                    k_isik, "Kuyruk & Onay",
                    f"{kuyruk} hatalı kayıt · {onay} onay bekliyor",
                    k_renk,
                    "DLQ boşsa yeniden deneme gerekmez · onaylar Müşteriler › Kullanıcılar",
                ),
                unsafe_allow_html=True,
            )

    # ============ 2×2 IZGARA — sistem metrikleri | oranlar / webhook | girişler ==
    dlq = webhook.get("dlq_toplam", 0)
    cache_hit = kpi.get("cache_hit_rate", 0)
    query_ms = kpi.get("avg_query_latency_ms", 0)
    # K3-10f (KAHİN, referans panel): "hep aynı şeyi mi kullanmış?" — hayır.
    # Bu satırda üç **farklı** gösterim yan yana durur:
    #   dikey içgörü rayı | KPI kartları | yüzde halkaları
    icgoruler: list[tuple[str, str, str, str]] = []
    if _dolu(kpi.get("total")):
        icgoruler.append(("🏢", "Firma Havuzu",
                          f"{sayi_formatla(kpi.get('total'))} firma kayıtlı.", "musteri"))
    if _dolu(kpi.get("active_users")):
        icgoruler.append(("👤", "Aktif Kullanıcı",
                          f"Son 7 günde {sayi_formatla(kpi.get('active_users'))} kullanıcı istek yaptı.",
                          "basari"))
    if cache_hit:
        icgoruler.append(("⚡", "Önbellek",
                          f"İsteklerin %{cache_hit * 100:.0f}'i veritabanına hiç gitmiyor.", "sistem"))
    if query_ms:
        icgoruler.append(("⏱", "Sorgu Süresi",
                          f"Ortalama {query_ms:.0f} ms — {'yavaş' if query_ms > 300 else 'normal'}.",
                          "bilgi"))
    icgoruler.append(
        ("📨", "Hata Kuyruğu", f"{dlq} kayıt DLQ'da bekliyor.", "tehlike") if dlq
        else ("📨", "Hata Kuyruğu", "DLQ boş — webhook zinciri temiz.", "basari")
    )
    if bekleyen > 0:
        icgoruler.append(("✅", "Onay Kuyruğu", f"{bekleyen} kullanıcı onay bekliyor.", "uyari"))

    g_sol, g_orta, g_sag = st.columns([1.3, 2, 1.5], vertical_alignment="top")
    with g_sol:
        with st.container(border=True, height=_SATIR_YUKSEKLIK["orta"]):
            st.markdown("##### Öne Çıkanlar")
            _icgoru_paneli(icgoruler)
    with g_orta:
        with st.container(border=True, height=_SATIR_YUKSEKLIK["orta"]):
            _bolum("sistem-metrikleri").render()
            _kart_izgara(
                [
                    # DLQ yalnız doluyken kart olur; 0 "iyi haber"dir, özet panelinde söylenir.
                    {"baslik": "DLQ", "deger": dlq or None, "kategori": "tehlike",
                     "yardim": "Hata kuyruğu — webhook işlemesi başarısız kayıt sayısı"},
                    {"baslik": "Cache Hit",
                     "deger": f"%{cache_hit * 100:.1f}" if cache_hit else None, "kategori": "sistem",
                     "yardim": "Veritabanı sorgusu yerine cache'den cevap %"},
                    {"baslik": "Sorgu Süresi",
                     "deger": f"{query_ms:.0f} ms" if query_ms else None, "kategori": "bilgi",
                     "yardim": "Veritabanı sorgularının ortalama yanıt süresi"},
                ],
                "Sistem metrikleri henüz veri üretmedi — ölçüm başlayınca kartlar açılır.",
            )
    with g_sag:
        with st.container(border=True, height=_SATIR_YUKSEKLIK["orta"]):
            st.markdown("##### Oranlar")
            # Yüzde halkaları (conic-gradient). Gerçek kaynaklar:
            #   veri tamlığı → src/company_master/tenant/health.py
            #   kalite skoru → admin_quality.load_quality_overview()["ortalama_skor"]
            _halka_satiri([
                ("Cache Hit", cache_hit * 100 if cache_hit else None, "sistem"),
                ("Veri Tamlığı", None, "bilgi"),
                ("Kalite Skoru", None, "basari"),
            ])

    a_sol, a_sag = st.columns(2, vertical_alignment="top")
    with a_sol:
        with st.container(border=True, height=_SATIR_YUKSEKLIK["alt"]):
            _bolum("webhook-akisi").render()
            flow_df = pd.DataFrame({
                "Durum": ["Başarılı", "Hatalı", "DLQ"],
                "Adet": [
                    webhook.get("basarili", 0),
                    webhook.get("hatali", 0),
                    webhook.get("dlq_toplam", 0),
                ],
            })
            # K3-10f: donut yüksekliği bloğa sığar — 280 px blok alt kenarından
            # taşıyıp halkanın alt yayını kırpıyordu.
            if flow_df["Adet"].sum() > 0:
                donut(flow_df, "Durum", "Adet", merkez_metin="olay", yukseklik=_DONUT_YUKSEKLIK)
                _veri_etiketi(["webhook dağılımı"], [])
            elif TASLAK:
                # K3-10f: blok boş kalmasın — taslakta sahte dağılım çizilir.
                donut(
                    pd.DataFrame({"Durum": ["Başarılı", "Hatalı", "DLQ"], "Adet": [820, 47, 12]}),
                    "Durum", "Adet", merkez_metin="olay", yukseklik=_DONUT_YUKSEKLIK,
                )
                _veri_etiketi([], ["webhook dağılımı"])
            else:
                st.caption("Webhook verisi henüz toplanmadı. Sistem kullanılınca burada görünecek.")
    with a_sag:
        # K3-10f (KAHİN): "her şey yatay oldu, dikey ilerleyen bir şeyler lazım —
        # örneğin bar çubuklar." Referans panelde de donut'ın yanında **dikey**
        # sütun grafiği var. `st.bar_chart` yerleşik; ek paket yok.
        with st.container(border=True, height=_SATIR_YUKSEKLIK["alt"]):
            st.markdown("##### Günlük Hacim (7 gün)")
            gunluk = {ad: seri for ad, seri in (
                ("Yeni Firma", series.get("yeni_firma")),
                ("Giriş", series.get("login")),
                ("Arama", series.get("search")),
            ) if seri}
            if gunluk:
                uzunluk = max(len(s) for s in gunluk.values())
                st.bar_chart(
                    pd.DataFrame(
                        {ad: list(s) + [0] * (uzunluk - len(s)) for ad, s in gunluk.items()},
                        index=[f"G-{uzunluk - i}" for i in range(uzunluk)],
                    ),
                    height=200,
                )
                _veri_etiketi(list(gunluk), [])
            elif TASLAK:
                st.bar_chart(
                    pd.DataFrame(
                        {"Yeni Firma": [4, 7, 5, 9, 6, 11, 8], "Giriş": [12, 9, 14, 11, 16, 13, 18]},
                        index=[f"G-{7 - i}" for i in range(7)],
                    ),
                    height=200,
                )
                _veri_etiketi([], ["günlük hacim"])
            else:
                st.caption("Günlük hacim verisi henüz toplanmadı.")

    # ---- Satır-içi barlı tablo: sayfadaki **beşinci** gösterim tipi ----------
    # Referans panelde de grafiklerin yanında mini barlı tablo var.
    # `st.column_config.ProgressColumn` yerleşiktir; ek paket/CSS yok.
    st.markdown("##### Kaynak Doluluğu")
    if TASLAK:
        st.dataframe(
            pd.DataFrame({
                "Kaynak": ["OSB Üye Listesi", "Ticaret Sicili", "Web Sitesi", "LinkedIn", "Apify Crawl"],
                "Kayıt": [8313, 6204, 4180, 2975, 1460],
                "Doluluk": [92, 71, 48, 34, 17],
            }),
            hide_index=True, width="stretch", height=215,
            column_config={
                "Kayıt": st.column_config.NumberColumn("Kayıt", format="%d"),
                "Doluluk": st.column_config.ProgressColumn(
                    "Doluluk", min_value=0, max_value=100, format="%d%%",
                ),
            },
        )
        _veri_etiketi([], ["kaynak doluluk tablosu"])
    else:
        st.caption("Kaynak doluluğu için `sources` tablosu henüz bağlanmadı.")

    # K3-10g: rehber anahtarı sayfa altında (`app.REHBER_KEY`); modül yalnız okur.
    if st.session_state.get("_hg_rehber", False):
        st.info(
            "**Bu ekran ne işe yarar?** Müşteri tarafı (kayıt, onay, kredi) ve sistem tarafı "
            "(firma sayısı, kalite skoru, görev durumu) metriklerini tek bakışta gösterir.\n\n"
            "**Nasıl kullanılır?** Kartlar veri geldikçe kendiliğinden açılır. Bölüm "
            "başlıklarından ilgili panele atlayın.\n\n"
            "**Veriler nereden gelir?** `/api/kpi` ve `/metrics` uç noktaları ile "
            "webhook izleme kayıtları. 30 saniyede bir yenilenir.\n\n"
            "**Dikkat:** Verisi henüz gelmemiş kutular yer tutucu değerle çizilir ve "
            "hemen altlarında **SAHTE VERİ** uyarısı bulunur. Gerçek veri geldiğinde "
            "kutu otomatik olarak gerçek değere geçer, uyarı kendiliğinden kaybolur."
        )
